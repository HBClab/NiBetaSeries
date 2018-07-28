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


def collect_data(layout, participant_label, deriv=False, ses=None,
                 task=None, run=None, space=None):
    """
    Uses grabbids to retrieve the input data for a given participant
    """
    if deriv:
        queries = {
            'preproc': {
                'subject': participant_label,
                'modality': 'func',
                'type': 'preproc',
                'extensions': ['nii', 'nii.gz']
            },
            'brainmask': {
                'subject': participant_label,
                'modality': 'func',
                'type': 'brainmask',
                'extensions': ['nii', 'nii.gz']
            },
            'confounds': {
                'subject': participant_label,
                'modality': 'func',
                'type': 'confounds',
                'extensions': 'tsv'
            },
        }

        if task:
            queries['preproc']['task'] = task
            queries['confounds']['task'] = task
        if run:
            queries['preproc']['run'] = run
            queries['confounds']['run'] = run
        if ses:
            queries['preproc']['ses'] = ses
            queries['confounds']['ses'] = ses
        if space:
            queries['preproc']['space'] = space
            queries['brainmask']['space'] = space
    else:
        queries = {
            'events': {
                'subject': participant_label,
                'modality': 'func',
                'type': 'events',
                'extensions': 'tsv'
            },
        }

        if run:
            queries['events']['run'] = run
        if task:
            queries['events']['task'] = task
        if ses:
            queries['events']['ses'] = ses

    return {modality: [x.filename for x in layout.get(**query)]
            for modality, query in queries.items()}
