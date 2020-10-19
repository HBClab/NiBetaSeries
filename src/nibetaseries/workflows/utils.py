#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
'''
Workflow for getting subject info
presumes fmriprep has run, expects directories to exist for
both BIDS data and fmriprep output
'''


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
