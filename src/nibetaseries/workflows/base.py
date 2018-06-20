#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
NiBetaSeries processing workflows
"""
from __future__ import print_function, division, absolute_import, unicode_literals
import os
from copy import deepcopy
from .utils import collect_data
from .model import init_betaseries_wf
from .analysis import init_correlation_wf
from nipype.pipeline import engine as pe
from nipype.interfaces import utility as niu
import pkg_resources as pkgr
from bids.grabbids import BIDSLayout


def init_nibetaseries_participant_wf(atlas_img, atlas_lut, bids_dir, confound_column_headers,
                                     derivatives_pipeline_dir, exclude_variant_label, high_pass, hrf_model, low_pass,
                                     output_dir, run_label, session_label, slice_time_ref, smoothing_kernel,
                                     space_label, subject_list, task_label, variant_label, work_dir):
    """
    This workflow organizes the execution of NiBetaSeries, with a sub-workflow for
    each subject.
    .. workflow::
        from NiBetaSeries.workflows.base import init_nibetaseries_participant_wf
        wf = init_nibetaseries_participant_wf(
            atlas_img='',
            atlas_lut='',
            bids_dir='.',
            confound_column_headers=[''],
            derivatives_pipeline_dir='.',
            exclude_variant_label='',
            high_pass='',
            hrf_model='',
            low_pass='',
            output_dir='',
            run_label='',
            session_label='',
            slice_time_ref='',
            smoothing_kernel='',
            space_label='',
            subject_list=[''],
            task_label='',
            variant_label='',
            work_dir='.')

    Parameters
        atlas_img: str
            Path to input atlas nifti
        atlas_lut: str
            Path to input atlas lookup table (tsv)
        bids_dir : str
            Root directory of BIDS dataset
        confound_column_headers: list
            The confound column names that are to be included in nuisance regression of the bold series
        derivatives_pipeline_dir: str
            Root directory of the derivatives pipeline
        exclude_variant_label: str or None
            Exclude bold series containing this variant label
        high_pass: float or None
            High pass filter (Hz)
        hrf_model: str
            The model that represents the shape of the hemodynamic response function
        low_pass: float or None
            Low pass filter (Hz)
        output_dir: str
            Directory where derivatives are saved
        run_label: str or None
            Include bold series containing this run label
        session_label: str or None
            Include bold series containing this session label
        slice_time_ref: float
            The reference slice for slice time correction
        smoothing_kernel: float or None
            The smoothing kernel to be applied to the bold series before beta estimation
        space_label: str or None
            Include bold series containing this space label
        subject_list: list
            List of subject labels
        task_label: str or None
            Include bold series containing this task label
        variant_label: str or None
            Include bold series containing this variant label
        work_dir: str
            Directory in which to store workflow execution state and temporary files
    """
    # setup workflow
    nibetaseries_participant_wf = pe.Workflow(name='nibetaseries_participant_wf')
    nibetaseries_participant_wf.base_dir = os.path.join(work_dir, 'NiBetaSeries_work')
    os.makedirs(nibetaseries_participant_wf.base_dir, exist_ok=True)

    # reading in derivatives and bids inputs as queryable database like objects
    derivatives_specification = pkgr.resource_filename('NiBetaSeries', 'data/bids_derivatives.json')
    derivatives_layout = BIDSLayout(derivatives_pipeline_dir, config=derivatives_specification)
    bids_layout = BIDSLayout(bids_dir)

    for subject_label in subject_list:

        # collect the necessary inputs for both collect data
        subject_derivative_data = collect_data(derivatives_layout,
                                               subject_label,
                                               task=task_label,
                                               run=run_label,
                                               ses=session_label,
                                               space=space_label,
                                               deriv=True)
        subject_bids_data = collect_data(bids_layout,
                                         subject_label,
                                         task=task_label,
                                         run=run_label,
                                         ses=session_label)

        # if you want to avoid using the ICA-AROMA variant
        if exclude_variant_label:
            subject_derivative_data['preproc'] = [
                preproc for preproc in subject_derivative_data['preproc'] if exclude_variant_label not in preproc
            ]
        # if you only want to use a particular variant
        if variant_label:
            subject_derivative_data['preproc'] = [
                preproc for preproc in subject_derivative_data['preproc'] if variant_label in preproc
            ]

        # make sure the lists are the same length
        # pray to god that they are in the same order?
        # ^they appear to be in the same order
        length = len(subject_derivative_data['preproc'])

        if any(len(lst) != length for lst in [subject_derivative_data['brainmask'],
                                              subject_derivative_data['confounds'],
                                              subject_bids_data['events']]):
            raise ValueError('input lists are not the same length!')

        single_subject_wf = init_single_subject_wf(
            atlas_img=atlas_img,
            atlas_lut=atlas_lut,
            brainmask_list=subject_derivative_data['brainmask'],
            confound_tsv_list=subject_derivative_data['confounds'],
            confound_column_headers=confound_column_headers,
            events_tsv_list=subject_bids_data['events'],
            high_pass=high_pass,
            hrf_model=hrf_model,
            low_pass=low_pass,
            name='single_subject' + subject_label + '_wf',
            preproc_img_list=subject_derivative_data['preproc'],
            run_label=run_label,
            session_label=ses_label,
            smoothing_kernel=smoothing_kernel,
            space_label=space_label,
            subject_label=subject_label,
            slice_time_ref=slice_time_ref,
            task_label=task_label,
            variant_label=variant_label,
        )

        single_subject_wf.config['execution']['crashdump_dir'] = (
            os.path.join(output_dir, "nibetaseries", "sub-" + subject_label, 'log')
        )

        for node in single_subject_wf._get_all_nodes():
            node.config = deepcopy(single_subject_wf.config)

        nibetaseries_participant_wf.add_nodes([single_subject_wf])

    return nibetaseries_participant_wf


def init_single_subject_wf(atlas_img, atlas_lut, brainmask_list,
                           confound_tsv_list, confound_column_headers, events_tsv_list, high_pass,
                           hrf_model, low_pass, name, preproc_img_list, smoothing_kernel, slice_time_ref):

    workflow = pe.Workflow(name=name)

    # name the nodes
    inputnode = pe.Node(niu.IdentityInterface(fields=['brainmask',
                                                      'confound_tsv',
                                                      'events_tsv',
                                                      'preproc_img',
                                                      'atlas_img',
                                                      'atlas_lut']),
                        name='inputnode',
                        iterables=[('brainmask', brainmask_list),
                                   ('confound_tsv', confound_tsv_list),
                                   ('events_tsv', events_tsv_list),
                                   ('preproc_img', preproc_img_list)],
                        synchronize=True)

    inputnode.inputs.atlas_img = atlas_img
    inputnode.inputs.atlas_lut = atlas_lut

    outputnode = pe.Node(niu.IdentityInterface(fields=['zmaps']),
                         name='outputnode')


    # initialize the betaseries workflow
    betaseries_wf = init_betaseries_wf(hrf_model=hrf_model, low_pass=low_pass, high_pass=high_pass,
                                       smoothing_kernel=smoothing_kernel,
                                       confound_column_headers=confound_column_headers,
                                       slice_time_ref=slice_time_ref)

    # initialize the analysis workflow
    correlation_wf = init_correlation_wf()
    # connect the nodes
    workflow.connect([
        (inputnode, betaseries_wf,
            [('preproc_img', 'inputnode.bold_img'),
             ('events_tsv', 'inputnode.events_tsv'),
             ('brainmask', 'inputnode.brainmask'),
             ('confound_tsv', 'inputnode.confound_tsv')]),
        (betaseries_wf, correlation_wf,
            [('outputnode.betaseries_img_list', 'inputnode.betaseries_img_list')]),
        (inputnode, correlation_wf, [('brainmask', 'inputnode.brainmask'),
                                     ('atlas_img', 'inputnode.atlas_img'),
                                     ('atlas_lut', 'inputnode.atlas_lut'),
        (correlation_wf, outputnode, [('outputnode.zmaps', 'zmaps')]),
    ])

    return workflow
