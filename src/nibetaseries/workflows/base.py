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
from ..interfaces.bids import DerivativesDataSink
from nipype.pipeline import engine as pe
from nipype.interfaces import utility as niu
from bids.grabbids import BIDSLayout


def init_nibetaseries_participant_wf(atlas_img, atlas_lut, bids_dir,
                                     derivatives_pipeline_dir, exclude_variant_label, high_pass, hrf_model, low_pass,
                                     output_dir, run_label, selected_confounds, session_label, smoothing_kernel,
                                     space_label, subject_list, task_label, variant_label, work_dir):
    """
    This workflow organizes the execution of NiBetaSeries, with a sub-workflow for
    each subject.

    Parameters
    ----------

        atlas_img : str
            Path to input atlas nifti
        atlas_lut : str
            Path to input atlas lookup table (tsv)
        bids_dir : str
            Root directory of BIDS dataset
        derivatives_pipeline_dir: str
            Root directory of the derivatives pipeline
        exclude_variant_label: str or None
            Exclude bold series containing this variant label
        high_pass : float or None
            High pass filter (Hz)
        hrf_model : str
            The model that represents the shape of the hemodynamic response function
        low_pass : float or None
            Low pass filter (Hz)
        output_dir : str
            Directory where derivatives are saved
        run_label : str or None
            Include bold series containing this run label
        selected_confounds : list
            List of confounds to be included in regression
        session_label : str or None
            Include bold series containing this session label
        smoothing_kernel : float or None
            The smoothing kernel to be applied to the bold series before beta estimation
        space_label : str or None
            Include bold series containing this space label
        subject_list : list
            List of subject labels
        task_label : str or None
            Include bold series containing this task label
        variant_label : str or None
            Include bold series containing this variant label
        work_dir : str
            Directory in which to store workflow execution state and temporary files
    """
    # setup workflow
    nibetaseries_participant_wf = pe.Workflow(name='nibetaseries_participant_wf')
    nibetaseries_participant_wf.base_dir = os.path.join(work_dir, 'NiBetaSeries_work')
    os.makedirs(nibetaseries_participant_wf.base_dir, exist_ok=True)

    # reading in derivatives and bids inputs as queryable database like objects
    derivatives_layout = BIDSLayout([(derivatives_pipeline_dir, ['bids', 'derivatives'])])
    bids_layout = BIDSLayout(bids_dir, exclude=['sourcedata', 'derivatives'])

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

        # if you want to avoid using a particular variant
        if exclude_variant_label:
            subject_derivative_data['preproc'] = [
                preproc for preproc in subject_derivative_data['preproc'] if exclude_variant_label not in preproc
            ]

        # if you only want to use a particular variant
        if variant_label:
            subject_derivative_data['preproc'] = [
                preproc for preproc in subject_derivative_data['preproc'] if variant_label in preproc
            ]

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
            events_tsv_list=subject_bids_data['events'],
            high_pass=high_pass,
            hrf_model=hrf_model,
            low_pass=low_pass,
            name='single_subject' + subject_label + '_wf',
            output_dir=output_dir,
            preproc_img_list=subject_derivative_data['preproc'],
            selected_confounds=selected_confounds,
            smoothing_kernel=smoothing_kernel,
        )

        single_subject_wf.config['execution']['crashdump_dir'] = (
            os.path.join(output_dir, "nibetaseries", "sub-" + subject_label, 'log')
        )

        for node in single_subject_wf._get_all_nodes():
            node.config = deepcopy(single_subject_wf.config)

        nibetaseries_participant_wf.add_nodes([single_subject_wf])

    return nibetaseries_participant_wf


def init_single_subject_wf(atlas_img, atlas_lut, brainmask_list, confound_tsv_list, events_tsv_list, high_pass,
                           hrf_model, low_pass, name, output_dir, preproc_img_list, selected_confounds,
                           smoothing_kernel):
    """
    This workflow completes the generation of the betaseries files and the calculation of the correlation matrices.
    .. workflow::
        :graph2use: orig
        :simple_form: yes

        from nibetaseries.workflows.base import init_single_subject_wf
        wf = init_single_subject_wf(
            atlas_img='',
            atlas_lut='',
            brainmask_list=[''],
            confound_tsv_list=[''],
            events_tsv_list=[''],
            high_pass='',
            hrf_model='',
            low_pass='',
            name='subtest',
            output_dir='.',
            preproc_img_list=[''],
            selected_confounds=[''],
            smoothing_kernel=0.0)

    Parameters
    ----------

        atlas_img : str
            path to input atlas nifti
        atlas_lut : str
            path to input atlas lookup table (tsv)
        brainmask_list : list
            list of brain masks in MNI space
        confound_tsv_list : list
            list of confound tsvs (e.g. from FMRIPREP)
        events_tsv_list : list
            list of event tsvs
        high_pass : float or None
            high pass filter to apply to bold (in Hertz). Reminder - frequencies _higher_ than this number are kept.
        hrf_model : str
            hemodynamic response function used to model the data
        low_pass : float or None
            low pass filter to apply to bold (in Hertz). Reminder - frequencies _lower_ than this number are kept.
        name : str
            name of the workflow (e.g. ``subject-01_wf``)
        output_dir : str
            Directory where derivatives are saved
        preproc_img_list : list
            list of preprocessed bold files
        selected_confounds : list or None
            the list of confounds to be included in regression
        smoothing_kernel : float or None
            the size of the smoothing kernel (full width/half max) applied to the bold file (in mm)

   Inputs
   ------

        atlas_img
            path to input atlas nifti
        atlas_lut
            path to input atlas lookup table (tsv)
        brainmask
            binary mask in MNI space for the participant
        confound_tsv
            tsv containing all the generated confounds
        events_tsv
            tsv containing all of the events that occurred during the bold run
        preproc_img
            preprocessed bold files

    Outputs
    -------

        correlation_matrix
            a matrix (tsv) file denoting all roi-roi correlations
    """
    workflow = pe.Workflow(name=name)

    # name the nodes
    input_node = pe.Node(niu.IdentityInterface(fields=['atlas_img',
                                                       'atlas_lut',
                                                       'brainmask',
                                                       'confound_tsv',
                                                       'events_tsv',
                                                       'preproc_img',
                                                       ]),
                         name='input_node',
                         iterables=[('brainmask', brainmask_list),
                                    ('confound_tsv', confound_tsv_list),
                                    ('events_tsv', events_tsv_list),
                                    ('preproc_img', preproc_img_list)],
                         synchronize=True)

    input_node.inputs.atlas_img = atlas_img
    input_node.inputs.atlas_lut = atlas_lut

    output_node = pe.Node(niu.IdentityInterface(fields=['correlation_matrix']),
                          name='output_node')

    # initialize the betaseries workflow
    betaseries_wf = init_betaseries_wf(hrf_model=hrf_model, low_pass=low_pass, high_pass=high_pass,
                                       selected_confounds=selected_confounds, smoothing_kernel=smoothing_kernel)

    # initialize the analysis workflow
    correlation_wf = init_correlation_wf()

    # correlation matrix datasink
    ds_correlation_matrix = pe.MapNode(DerivativesDataSink(base_directory=output_dir,
                                                           suffix='matrix'),
                                       iterfield=['betaseries_file', 'in_file'],
                                       name='ds_correlation_matrix')

    # connect the nodes
    workflow.connect([
        (input_node, betaseries_wf,
            [('preproc_img', 'input_node.bold_file'),
             ('events_tsv', 'input_node.events_file'),
             ('brainmask', 'input_node.bold_mask_file'),
             ('confound_tsv', 'input_node.confounds_file')]),
        (betaseries_wf, correlation_wf,
            [('output_node.betaseries_files', 'input_node.betaseries_files')]),
        (input_node, correlation_wf, [('atlas_img', 'input_node.atlas_file'),
                                      ('atlas_lut', 'input_node.atlas_lut')]),
        (correlation_wf, output_node, [('output_node.correlation_matrix', 'correlation_matrices')]),
        (input_node, ds_correlation_matrix, [('preproc_img', 'source_file')]),
        (betaseries_wf, ds_correlation_matrix, [('output_node.betaseries_files', 'betaseries_file')]),
        (output_node, ds_correlation_matrix, [('correlation_matrices', 'in_file')]),
    ])

    return workflow
