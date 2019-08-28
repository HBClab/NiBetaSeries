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


def collect_data(layout, participant_label, ses=None,
                 task=None, run=None, space=None, variant=None):
    """
    Uses grabbids to retrieve the input data for a given participant
    """
    # get all the preprocessed fmri images.
    preproc_query = {
        'subject': participant_label,
        'modality': 'func',
        'type': 'preproc',
        'extensions': ['nii', 'nii.gz']
    }

    if task:
        preproc_query['task'] = task
    if run:
        preproc_query['run'] = run
    if ses:
        preproc_query['session'] = ses
    if space:
        preproc_query['space'] = space
    if variant:
        preproc_query['variant'] = variant

    preprocs = layout.get(**preproc_query)

    # get the relevant files for each preproc
    preproc_collector = []
    # common across all queries
    preproc_dict = {'modality': 'func', 'subject': participant_label}
    for preproc in preprocs:
        preproc_dict['task'] = getattr(preproc, 'task', None)
        preproc_dict['run'] = getattr(preproc, 'run', None)
        preproc_dict['session'] = getattr(preproc, 'session', None)
        preproc_dict['space'] = getattr(preproc, 'space', None)

        if preproc_dict['task'] == 'rest':
            print('Found resting state bold run, skipping')
            continue

        # can't use space when looking up the events file
        preproc_dict_ns = {k: v for k, v in preproc_dict.items() if k != 'space'}

        file_queries = {
            'brainmask': _combine_dict(preproc_dict, {'type': 'brainmask',
                                                      'extensions': ['nii', 'nii.gz']}),
            'confounds': _combine_dict(preproc_dict_ns, {'type': 'confounds',
                                                         'extensions': '.tsv'}),
            'events': _combine_dict(preproc_dict_ns, {'type': 'events',
                                                      'extensions': '.tsv'}),
        }

        try:
            query_res = {modality: [x.filename for x in layout.get(**query)][0]
                         for modality, query in file_queries.items()}
        except Exception as e:
            raise type(e)('Could not find required files, check BIDS structure')

        # add the preprocessed file
        query_res['preproc'] = preproc.filename

        # get metadata for the preproc
        bold_query = _combine_dict(preproc_dict_ns, {'type': 'bold',
                                                     'extensions': ['nii', 'nii.gz']})
        bold_file = layout.get(**bold_query)[0].filename

        query_res['metadata'] = layout.get_metadata(bold_file)
        preproc_collector.append(query_res)

    return preproc_collector


def _combine_dict(a, b):
    return dict(list(a.items()) + list(b.items()))
