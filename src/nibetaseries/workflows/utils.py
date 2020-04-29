#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
'''
Workflow for getting subject info
presumes fmriprep has run, expects directories to exist for
both BIDS data and fmriprep output
'''
from __future__ import print_function, division, absolute_import, unicode_literals
from bids.layout.index import BIDSLayoutIndexer
from bids.layout.models import Tag, FileAssociation, Entity
from bids.utils import listify
from collections import defaultdict
import os
import json


class BIDSLayoutIndexerPatch(BIDSLayoutIndexer):
    def index_metadata(self, **filters):
        """Index metadata for all files in the BIDS dataset. """
        # Process JSON files first if we're indexing metadata
        all_files = self.layout.get(absolute_paths=True, **filters)

        # Track ALL entities we've seen in file names or metadatas
        all_entities = {}
        for c in self.config:
            all_entities.update(c.entities)

        # If key/value pairs in JSON files duplicate ones extracted from files,
        # we can end up with Tag collisions in the DB. To prevent this, we
        # store all filename/entity pairs and the value, and then check against
        # that before adding each new Tag.
        all_tags = {}
        for t in self.session.query(Tag).all():
            key = '{}_{}'.format(t.file_path, t.entity_name)
            all_tags[key] = str(t.value)

        # We build up a store of all file data as we iterate files. It looks
        # like: { extension/suffix: dirname: [(entities, payload)]}}.
        # The payload is left empty for non-JSON files.
        file_data = {}

        for bf in all_files:
            file_ents = bf.entities.copy()
            suffix = file_ents.pop('suffix', None)
            ext = file_ents.pop('extension', None)

            if suffix is not None and ext is not None:
                key = "{}/{}".format(ext, suffix)
                if key not in file_data:
                    file_data[key] = defaultdict(list)

                if ext == 'json':
                    with open(bf.path, 'r') as handle:
                        try:
                            payload = json.load(handle)
                        except json.JSONDecodeError as e:
                            msg = ("Error occurred while trying to decode JSON"
                                   " from file '{}'.".format(bf.path))
                            raise IOError(msg) from e
                else:
                    payload = None

                to_store = (file_ents, payload, bf.path)
                file_data[key][bf.dirname].append(to_store)

        # To avoid integrity errors, track primary keys we've seen
        seen_assocs = set()

        def create_association_pair(src, dst, kind, kind2=None):
            kind2 = kind2 or kind
            pk1 = '#'.join([src, dst, kind])
            if pk1 not in seen_assocs:
                self.session.add(FileAssociation(src=src, dst=dst, kind=kind))
                seen_assocs.add(pk1)
            pk2 = '#'.join([dst, src, kind2])
            if pk2 not in seen_assocs:
                self.session.add(FileAssociation(src=dst, dst=src, kind=kind2))
                seen_assocs.add(pk2)

        # TODO: Efficiency of everything in this loop could be improved
        filenames = [bf for bf in all_files if not bf.path.endswith('.json')]

        for bf in filenames:
            file_ents = bf.entities.copy()
            suffix = file_ents.pop('suffix', None)
            ext = file_ents.pop('extension', None)
            file_ent_keys = set(file_ents.keys())

            if suffix is None or ext is None:
                continue

            # Extract metadata associated with the file. The idea is
            # that we loop over parent directories, and if we find
            # payloads in the file_data store (indexing by directory
            # and current file suffix), we check to see if the
            # candidate JS file's entities are entirely consumed by
            # the current file. If so, it's a valid candidate, and we
            # add the payload to the stack. Finally, we invert the
            # stack and merge the payloads in order.
            ext_key = "{}/{}".format(ext, suffix)
            json_key = "json/{}".format(suffix)
            dirname = bf.dirname

            payloads = []
            ancestors = []

            while True:
                # Get JSON payloads
                json_data = file_data.get(json_key, {}).get(dirname, [])
                for js_ents, js_md, js_path in json_data:
                    js_keys = set(js_ents.keys())
                    if js_keys - file_ent_keys:
                        continue
                    matches = [js_ents[name] == file_ents[name]
                               for name in js_keys]
                    if all(matches):
                        payloads.append((js_md, js_path))

                # Get all files this file inherits from
                candidates = file_data.get(ext_key, {}).get(dirname, [])
                for ents, _, path in candidates:
                    keys = set(ents.keys())
                    if keys - file_ent_keys:
                        continue
                    matches = [ents[name] == file_ents[name] for name in keys]
                    if all(matches):
                        ancestors.append(path)

                parent = os.path.dirname(dirname)
                if parent == dirname:
                    break
                dirname = parent

            if not payloads:
                continue

            # Create DB records for metadata associations
            js_file = payloads[-1][1]
            create_association_pair(js_file, bf.path, 'Metadata')

            # Consolidate metadata by looping over inherited JSON files
            file_md = {}
            for pl, js_file in payloads[::-1]:
                file_md.update(pl)

            # Create FileAssociation records for JSON inheritance
            n_pl = len(payloads)
            for i, (pl, js_file) in enumerate(payloads):
                if (i + 1) < n_pl:
                    other = payloads[i + 1][1]
                    create_association_pair(js_file, other, 'Child', 'Parent')

            # Inheritance for current file
            n_pl = len(ancestors)
            for i, src in enumerate(ancestors):
                if (i + 1) < n_pl:
                    dst = ancestors[i + 1]
                    create_association_pair(src, dst, 'Child', 'Parent')

            # Files with IntendedFor field always get mapped to targets
            intended = listify(file_md.get('IntendedFor', []))
            for target in intended:
                # Per spec, IntendedFor paths are relative to sub dir.
                target = os.path.join(
                    self.root, 'sub-{}'.format(bf.entities['subject']), target)
                create_association_pair(bf.path, target, 'IntendedFor',
                                        'InformedBy')

            # Link files to BOLD runs
            if suffix in ['physio', 'stim', 'events', 'sbref']:
                images = self.layout.get(
                    extension=['nii', 'nii.gz'], suffix='bold',
                    return_type='filename', **file_ents)
                for img in images:
                    create_association_pair(bf.path, img, 'IntendedFor',
                                            'InformedBy')

            # Link files to DWI runs
            if suffix == 'sbref' or ext in ['bvec', 'bval']:
                images = self.layout.get(
                    extension=['nii', 'nii.gz'], suffix='dwi',
                    return_type='filename', **file_ents)
                for img in images:
                    create_association_pair(bf.path, img, 'IntendedFor',
                                            'InformedBy')

            # Create Tag <-> Entity mappings, and any newly discovered Entities
            for md_key, md_val in file_md.items():
                tag_string = '{}_{}'.format(bf.path, md_key)
                # Skip pairs that were already found in the filenames
                if tag_string in all_tags:
                    file_val = all_tags[tag_string]
                    if str(md_val) != file_val:
                        msg = (
                            "Conflicting values found for entity '{}' in "
                            "filename {} (value='{}') versus its JSON sidecar "
                            "(value='{}'). Please reconcile this discrepancy."
                        )
                        raise ValueError(msg.format(md_key, bf.path, file_val,
                                                    md_val))
                    continue
                if md_key not in all_entities:
                    all_entities[md_key] = Entity(md_key, is_metadata=True)
                    self.session.add(all_entities[md_key])
                tag = Tag(bf, all_entities[md_key], md_val)
                self.session.add(tag)

            if len(self.session.new) >= 1000:
                self.session.commit()

        self.session.commit()


def collect_data(layout, participant_label, ses=None,
                 task=None, run=None, space=None, description=None):
    """
    Uses pybids to retrieve the input data for a given participant
    """
    # get all the preprocessed fmri images.
    preproc_query = {
        'subject': participant_label,
        'datatype': 'func',
        'suffix': 'bold',
        'extension': ['nii', 'nii.gz'],
        'scope': 'derivatives',
    }

    if task:
        preproc_query['task'] = task
    if run:
        preproc_query['run'] = run
    if ses:
        preproc_query['session'] = ses
    if space:
        preproc_query['space'] = space
    if description:
        preproc_query['desc'] = description

    preprocs = layout.get(**preproc_query)

    if not preprocs:
        msg = "could not find preprocessed outputs: " + str(preproc_query)
        raise ValueError(msg)

    # get the relevant files for each preproc
    preproc_collector = []
    # common across all queries
    preproc_dict = {'datatype': 'func', 'subject': participant_label}
    for preproc in preprocs:
        preproc_dict['task'] = getattr(preproc, 'task', None)
        preproc_dict['run'] = getattr(preproc, 'run', None)
        preproc_dict['session'] = getattr(preproc, 'session', None)
        preproc_dict['space'] = getattr(preproc, 'space', None)

        if preproc_dict['task'] == 'rest':
            print('Found resting state bold run, skipping')
            continue

        # event files and confounds are the same regardless of space
        preproc_dict_ns = {k: v for k, v in preproc_dict.items() if k != 'space'}

        file_queries = {
            'brainmask': _combine_dict(preproc_dict, {'suffix': 'mask',
                                                      'desc': 'brain',
                                                      'extension': ['nii', 'nii.gz']}),
            'confounds': _combine_dict(preproc_dict_ns, {'suffix': 'regressors',
                                                         'desc': 'confounds',
                                                         'extension': '.tsv'}),
            'events': _combine_dict(preproc_dict_ns, {'suffix': 'events',
                                                      'extension': '.tsv'}),
        }

        query_res = {modality: _exec_query(layout, **query)
                     for modality, query in file_queries.items()}

        # add the preprocessed file
        query_res['preproc'] = preproc.path

        # get metadata for the preproc
        bold_query = _combine_dict(preproc_dict_ns, {'suffix': 'bold',
                                                     'extension': ['nii', 'nii.gz'],
                                                     'desc': None})
        bold_file = layout.get(**bold_query)[0]

        query_res['metadata'] = bold_file.get_metadata()
        preproc_collector.append(query_res)

    return preproc_collector


def _combine_dict(a, b):
    return dict(list(a.items()) + list(b.items()))


def _exec_query(layout, **query):
    """raises error if file is not found for the query"""
    try:
        res = layout.get(**query)[0]
    except Exception as e:
        msg = "could not find file matching these criteria: {q}".format(q=query)
        raise Exception(msg) from e

    return res.path
