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
import os


class BIDSError(ValueError):
    def __init__(self, message, bids_root):
        indent = 10
        header = '{sep} BIDS root folder: "{bids_root}" {sep}'.format(
            bids_root=bids_root, sep=''.join(['-'] * indent))
        self.msg = '\n{header}\n{indent}{message}\n{footer}'.format(
            header=header, indent=''.join([' '] * (indent + 1)),
            message=message, footer=''.join(['-'] * len(header))
        )
        super(BIDSError, self).__init__(self.msg)
        self.bids_root = bids_root


class BIDSWarning(RuntimeWarning):
    pass


def collect_participants(bids_dir, participant_label=None, strict=False):
    """
    List the participants under the BIDS root and checks that participants
    designated with the participant_label argument exist in that folder.
    Returns the list of participants to be finally processed.
    Requesting all subjects in a BIDS directory root:
    >>> collect_participants('ds114')
    ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
    Requesting two subjects, given their IDs:
    >>> collect_participants('ds114', participant_label=['02', '04'])
    ['02', '04']
    Requesting two subjects, given their IDs (works with 'sub-' prefixes):
    >>> collect_participants('ds114', participant_label=['sub-02', 'sub-04'])
    ['02', '04']
    Requesting two subjects, but one does not exist:
    >>> collect_participants('ds114', participant_label=['02', '14'])
    ['02']
    >>> collect_participants('ds114', participant_label=['02', '14'],
    ...                      strict=True)  # doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    fmriprep.utils.bids.BIDSError:
    ...
    """
    bids_dir = os.path.abspath(bids_dir)
    all_participants = sorted(
        [subdir[4:] for subdir in os.listdir(bids_dir)
         if os.path.isdir(os.path.join(bids_dir, subdir)) and subdir.startswith('sub-')])

    # Error: bids_dir does not contain subjects
    if not all_participants:
        raise BIDSError(
            'Could not find participants. Please make sure the BIDS data '
            'structure is present and correct. Datasets can be validated online '
            'using the BIDS Validator (http://incf.github.io/bids-validator/).\n'
            'If you are using Docker for Mac or Docker for Windows, you '
            'may need to adjust your "File sharing" preferences.', bids_dir)

    # No --participant-label was set, return all
    if participant_label is None or not participant_label:
        return all_participants

    if isinstance(participant_label, str):
        participant_label = [participant_label]

    # Drop sub- prefixes
    participant_label = [sub[4:] if sub.startswith('sub-') else sub for sub in participant_label]
    # Remove duplicates
    participant_label = sorted(set(participant_label))
    # Remove labels not found
    found_label = sorted(set(participant_label) & set(all_participants))
    if not found_label:
        raise BIDSError('Could not find participants [{}]'.format(
            ', '.join(participant_label)), bids_dir)

    # Warn if some IDs were not found
    notfound_label = sorted(set(participant_label) - set(all_participants))
    if notfound_label:
        exc = BIDSError('Some participants were not found: {}'.format(
            ', '.join(notfound_label)), bids_dir)
        if strict:
            raise exc
        # warnings.warn(exc.msg, BIDSWarning)

    return found_label


def collect_data(layout, participant_label, deriv=False, ses=None,
                 task=None, run=None, space=None):
    """
    Uses grabbids to retrieve the input data for a given participant
    >>> bids_root, _ = collect_data('ds054', '100185')
    >>> bids_root['fmap']  # doctest: +ELLIPSIS
    ['.../ds054/sub-100185/fmap/sub-100185_magnitude1.nii.gz', \
'.../ds054/sub-100185/fmap/sub-100185_magnitude2.nii.gz', \
'.../ds054/sub-100185/fmap/sub-100185_phasediff.nii.gz']
    >>> bids_root['bold']  # doctest: +ELLIPSIS
    ['.../ds054/sub-100185/func/sub-100185_task-machinegame_run-01_bold.nii.gz', \
'.../ds054/sub-100185/func/sub-100185_task-machinegame_run-02_bold.nii.gz', \
'.../ds054/sub-100185/func/sub-100185_task-machinegame_run-03_bold.nii.gz', \
'.../ds054/sub-100185/func/sub-100185_task-machinegame_run-04_bold.nii.gz', \
'.../ds054/sub-100185/func/sub-100185_task-machinegame_run-05_bold.nii.gz', \
'.../ds054/sub-100185/func/sub-100185_task-machinegame_run-06_bold.nii.gz']
    >>> bids_root['sbref']  # doctest: +ELLIPSIS
    ['.../ds054/sub-100185/func/sub-100185_task-machinegame_run-01_sbref.nii.gz', \
'.../ds054/sub-100185/func/sub-100185_task-machinegame_run-02_sbref.nii.gz', \
'.../ds054/sub-100185/func/sub-100185_task-machinegame_run-03_sbref.nii.gz', \
'.../ds054/sub-100185/func/sub-100185_task-machinegame_run-04_sbref.nii.gz', \
'.../ds054/sub-100185/func/sub-100185_task-machinegame_run-05_sbref.nii.gz', \
'.../ds054/sub-100185/func/sub-100185_task-machinegame_run-06_sbref.nii.gz']
    >>> bids_root['t1w']  # doctest: +ELLIPSIS
    ['.../ds054/sub-100185/anat/sub-100185_T1w.nii.gz']
    >>> bids_root['t2w']  # doctest: +ELLIPSIS
    []
    """
    if deriv:
        queries = {
            'preproc': {
                'subject': participant_label,
                'modality': 'func',
                'type': 'preproc',
                'extensions': ['nii', 'nii.gz']
            },
            'bold_brainmask': {
                'subject': participant_label,
                'modality': 'func',
                'type': 'brainmask',
                'extensions': ['nii', 'nii.gz']
            },
            'mni_brainmask': {
                'subject': participant_label,
                'modality': 'anat',
                'type': 'brainmask',
                'space': 'MNI152NLin2009cAsym',
                'extensions': ['nii', 'nii.gz']
            },
            'AROMAnoiseICs': {
                'subject': participant_label,
                'modality': 'func',
                'type': 'AROMAnoiseICs',
                'extensions': '.csv'
            },
            'MELODICmix': {
                'subject': participant_label,
                'modality': 'func',
                'type': 'MELODICmix',
                'extensions': 'tsv'
            },
            'confounds': {
                'subject': participant_label,
                'modality': 'func',
                'type': 'confounds',
                'extensions': 'tsv'
            },
            'target_t1w_warp': {
                'subject': participant_label,
                'modality': 'anat',
                'type': 'warp',
                'target': 'T1w',
                'extensions': 'h5'
            },
            'target_mni_warp': {
                'subject': participant_label,
                'modality': 'anat',
                'type': 'warp',
                'target': 'MNI152NLin2009cAsym',
                'extensions': 'h5'
            },
        }

        if task:
            queries['preproc']['task'] = task
            queries['bold_brainmask']['task'] = task
            queries['AROMAnoiseICs']['task'] = task
            queries['MELODICmix']['task'] = task
            queries['confounds']['task'] = task
        if run:
            queries['preproc']['run'] = run
            queries['bold_brainmask']['run'] = run
            queries['AROMAnoiseICs']['run'] = run
            queries['MELODICmix']['run'] = run
            queries['confounds']['run'] = run
        if space:
            queries['preproc']['space'] = space
            queries['bold_brainmask']['space'] = space
        if ses:
            queries['preproc']['ses'] = ses
            queries['bold_brainmask']['ses'] = ses
            queries['AROMAnoiseICs']['ses'] = ses
            queries['MELODICmix']['ses'] = ses
            queries['confounds']['ses'] = ses

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
