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
from bids import BIDSLayout


def init_nibetaseries_participant_wf(
    atlas_img, atlas_lut, bids_dir,
    derivatives_pipeline_dir, exclude_description_label, hrf_model, high_pass,
    output_dir, run_label, selected_confounds, session_label, smoothing_kernel,
    space_label, subject_list, task_label, description_label, work_dir,
        ):

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
        exclude_description_label: str or None
            Exclude bold series containing this description label
        hrf_model : str
            The model that represents the shape of the hemodynamic response function
        high_pass : float
            High pass filter (Hz)
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
        description_label : str or None
            Include bold series containing this description label
        work_dir : str
            Directory in which to store workflow execution state and temporary files
    """
    # setup workflow
    nibetaseries_participant_wf = pe.Workflow(name='nibetaseries_participant_wf')
    nibetaseries_participant_wf.base_dir = os.path.join(work_dir, 'NiBetaSeries_work')
    os.makedirs(nibetaseries_participant_wf.base_dir, exist_ok=True)

    # reading in derivatives and bids inputs as queryable database like objects
    layout = BIDSLayout(bids_dir, derivatives=derivatives_pipeline_dir)

    for subject_label in subject_list:

        # collect the necessary inputs for both collect data
        subject_data = collect_data(layout,
                                    subject_label,
                                    task=task_label,
                                    run=run_label,
                                    ses=session_label,
                                    space=space_label,
                                    description=description_label)
        # collect files to be associated with each preproc
        brainmask_list = [d['brainmask'] for d in subject_data]
        confound_tsv_list = [d['confounds'] for d in subject_data]
        events_tsv_list = [d['events'] for d in subject_data]
        preproc_img_list = [d['preproc'] for d in subject_data]
        bold_metadata_list = [d['metadata'] for d in subject_data]

        single_subject_wf = init_single_subject_wf(
            atlas_img=atlas_img,
            atlas_lut=atlas_lut,
            bold_metadata_list=bold_metadata_list,
            brainmask_list=brainmask_list,
            confound_tsv_list=confound_tsv_list,
            events_tsv_list=events_tsv_list,
            hrf_model=hrf_model,
            high_pass=high_pass,
            name='single_subject' + subject_label + '_wf',
            output_dir=output_dir,
            preproc_img_list=preproc_img_list,
            selected_confounds=selected_confounds,
            smoothing_kernel=smoothing_kernel,
        )

        single_subject_wf.config['execution']['crashdump_dir'] = (
            os.path.join(output_dir, "sub-" + subject_label, 'log')
        )

        for node in single_subject_wf._get_all_nodes():
            node.config = deepcopy(single_subject_wf.config)

        nibetaseries_participant_wf.add_nodes([single_subject_wf])

    return nibetaseries_participant_wf


def init_single_subject_wf(
    atlas_img, atlas_lut, bold_metadata_list, brainmask_list, confound_tsv_list,
    events_tsv_list, hrf_model, high_pass, name, output_dir, preproc_img_list,
    selected_confounds, smoothing_kernel
        ):
    """
    This workflow completes the generation of the betaseries files
    and the calculation of the correlation matrices.
    .. workflow::
        :graph2use: orig
        :simple_form: yes

        from nibetaseries.workflows.base import init_single_subject_wf
        wf = init_single_subject_wf(
            atlas_img='',
            atlas_lut='',
            bold_metadata_list=[''],
            brainmask_list=[''],
            confound_tsv_list=[''],
            events_tsv_list=[''],
            hrf_model='',
            high_pass='',
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
        bold_metadata_list : list
            list of bold metadata associated with each preprocessed file
        brainmask_list : list
            list of brain masks in MNI space
        confound_tsv_list : list
            list of confound tsvs (e.g. from FMRIPREP)
        events_tsv_list : list
            list of event tsvs
        hrf_model : str
            hemodynamic response function used to model the data
        high_pass : float
            high pass filter to apply to bold (in Hertz).
            Reminder - frequencies _higher_ than this number are kept.
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
        bold_metadata
            bold metadata associated with the preprocessed file
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
        correlation_fig
            a svg file of a circular connectivity plot showing all roi-roi correlations
    """
    workflow = pe.Workflow(name=name)

    # name the nodes
    input_node = pe.Node(niu.IdentityInterface(fields=['atlas_img',
                                                       'atlas_lut',
                                                       'bold_metadata',
                                                       'brainmask',
                                                       'confound_tsv',
                                                       'events_tsv',
                                                       'preproc_img',
                                                       ]),
                         name='input_node',
                         iterables=[('brainmask', brainmask_list),
                                    ('confound_tsv', confound_tsv_list),
                                    ('events_tsv', events_tsv_list),
                                    ('preproc_img', preproc_img_list),
                                    ('bold_metadata', bold_metadata_list)],
                         synchronize=True)

    input_node.inputs.atlas_img = atlas_img
    input_node.inputs.atlas_lut = atlas_lut

    output_node = pe.Node(niu.IdentityInterface(fields=['correlation_matrix',
                                                        'correlation_fig',
                                                        'betaseries_file']),
                          name='output_node')

    # initialize the betaseries workflow
    betaseries_wf = init_betaseries_wf(hrf_model=hrf_model, high_pass=high_pass,
                                       selected_confounds=selected_confounds,
                                       smoothing_kernel=smoothing_kernel)

    # initialize the analysis workflow
    correlation_wf = init_correlation_wf()

    # correlation matrix datasink
    ds_correlation_matrix = pe.MapNode(DerivativesDataSink(base_directory=output_dir),
                                       iterfield=['in_file'],
                                       name='ds_correlation_matrix')

    ds_correlation_fig = pe.MapNode(DerivativesDataSink(base_directory=output_dir),
                                    iterfield=['in_file'],
                                    name='ds_correlation_fig')

    ds_betaseries_file = pe.MapNode(DerivativesDataSink(base_directory=output_dir),
                                    iterfield=['in_file'],
                                    name='ds_betaseries_file')

    # connect the nodes
    workflow.connect([
        (input_node, betaseries_wf,
            [('preproc_img', 'input_node.bold_file'),
             ('events_tsv', 'input_node.events_file'),
             ('brainmask', 'input_node.bold_mask_file'),
             ('confound_tsv', 'input_node.confounds_file'),
             ('bold_metadata', 'input_node.bold_metadata')]),
        (betaseries_wf, output_node,
            [('output_node.betaseries_files', 'betaseries_file')]),
        (betaseries_wf, correlation_wf,
            [('output_node.betaseries_files', 'input_node.betaseries_files')]),
        (input_node, correlation_wf, [('atlas_img', 'input_node.atlas_file'),
                                      ('atlas_lut', 'input_node.atlas_lut')]),

        (correlation_wf, output_node, [('output_node.correlation_matrix', 'correlation_matrix'),
                                       ('output_node.correlation_fig', 'correlation_fig')]),
        (input_node, ds_correlation_matrix, [('preproc_img', 'source_file')]),
        (output_node, ds_correlation_matrix, [('correlation_matrix', 'in_file')]),
        (input_node, ds_correlation_fig, [('preproc_img', 'source_file')]),
        (output_node, ds_correlation_fig, [('correlation_fig', 'in_file')]),
        (input_node, ds_betaseries_file, [('preproc_img', 'source_file')]),
        (output_node, ds_betaseries_file, [('betaseries_file', 'in_file')]),
    ])

    return workflow
