#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
NiBetaSeries processing workflows
"""
from __future__ import print_function, division, absolute_import, unicode_literals
import sys
import os
from copy import deepcopy

from .preprocess import init_derive_residuals_wf
from niworkflows.nipype.pipeline import engine as pe
from niworkflows.nipype.interfaces import utility as niu
def init_nibetaseries_participant_wf(bids_dir, derivatives_pipeline, exclude_variant,
                                     hrf_model, omp_nthreads, output_dir, res, run,
                                     run_uuid, slice_time_ref, space, subject_list,
                                     task_id, variant, work_dir):
    """
    This workflow organizes the execution of NiBetaSeries, with a sub-workflow for
    each subject.
    .. workflow::
        from NiBetaSeries.workflows.base import init_nibetaseries_participant_wf
        wf = init_nibetaseries_participant_wf(subject_list=['NiBetaSeriesSubsTest'],
                              task_id='',
                              derivatives_pipeline='.',
                              bids_dir='.',
                              output_dir='.',
                              work_dir='.',
                              space='',
                              variant='',
                              res='',
                              hrf_model='glover',
                              slice_time_ref='0.5',
                              run_uuid='X',
                              omp_nthreads=1)
    Parameters
        subject_list : list
            List of subject labels
        task_id : str or None
            Task ID of preprocessed BOLD series to derive betas, or ``None`` to process all
        derivatives_pipeline : str
        	Directory where preprocessed derivatives live
    	bids_dir : str
            Root directory of BIDS dataset
        output_dir : str
            Directory in which to save derivatives
        work_dir : str
            Directory in which to store workflow execution state and temporary files
        space : str
        	Space of preprocessed BOLD series to derive betas, or ``None`` to process all
        variant : str
        	Variant of preprocessed BOLD series to derive betas, or ``None`` to process all
        res : str
        	resolution (XxYxZ) of preprocessed BOLD series to derive betas, or ``None`` to process all
        hrf_model : str
        	hrf model used to convolve events
        slice_time_ref : float
        	fractional representation of the slice that used as the reference during slice time correction.
        run_uuid : str
            Unique identifier for execution instance
        omp_nthreads : int
            Maximum number of threads an individual process may use
    """
    nibetaseries_participant_wf = pe.Workflow(name='nibetaseries_participant_wf')
    nibetaseries_participant_wf.base_dir = work_dir
    reportlets_dir = os.path.join(work_dir, 'reportlets')
    for subject_id in subject_list:
        subject_data = collect_data(layout,
                                    subject_id,
                                    task=task_id,
                                    run=run_id,
                                    space=space)
        # if you want to avoid using the ICA-AROMA variant
        if exclude_variant:
            subject_data['preproc'] = [preproc for preproc in subject_data['preproc'] if not 'variant' in preproc]
        # if you only want to use a particular variant
        if variant:
            subject_data['preproc'] = [preproc for preproc in subject_data['preproc'] if variant in preproc]

        # make sure the lists are the same length
        # pray to god that they are in the same order?
        # ^they appear to be in the same order
        length = len(subject_data['preproc'])
        print('\n'+subject_id)
        print('preproc:{}'.format(str(length)))
        print('confounds:{}'.format(str(len(subject_data['confounds']))))
        print('brainmask:{}'.format(str(len(subject_data['brainmask']))))
        print('AROMAnoiseICs:{}'.format(str(len(subject_data['AROMAnoiseICs']))))
        print('MELODICmix:{}'.format(str(len(subject_data['MELODICmix']))))
        if any(len(lst) != length for lst in [subject_data['brainmask'],
                                              subject_data['confounds'],
                                              subject_data['AROMAnoiseICs'],
                                              subject_data['MELODICmix']]):
            raise ValueError('input lists are not the same length!')

        single_subject_wf = init_single_subject_wf(AROMAnoiseICs=subject_data['AROMAnoiseICs'],
                                                   brainmask=subject_data['brainmask'],
                                                   confounds=subject_data['confounds'],
                                                   confound_names=confound_names,
                                                   derivatives_pipeline=derivatives_pipeline,
                                                   hrf_model=hrf_model,
                                                   low_pass=low_pass,
                                                   MELODICmix=subject_data['MELODICmix'],
                                                   name='single_subject' + subject_id + '_wf',
                                                   preproc=subject_data['preproc'],
                                                   regfilt=regfilt,
                                                   res=res,
                                                   result_dir=result_dir,
                                                   run_id=run_id,
                                                   run_uuid=run_uuid,
                                                   ses_id=ses_id,
                                                   smooth=smooth,
                                                   space=space,
                                                   subject_id=subject_id,
                                                   slice_time_ref=slice_time_ref,
                                                   task_id=task_id,
                                                   variant=variant
        )

        single_subject_wf.config['execution']['crashdump_dir'] = (
            os.path.join(output_dir, "nibetaseries", "sub-" + subject_id, 'log', run_uuid)
        )

        for node in single_subject_wf._get_all_nodes():
            node.config = deepcopy(single_subject_wf.config)

        fmriprep_wf.add_nodes([single_subject_wf])
    return nibetaseries_participant_wf

def init_single_subject_wf(AROMAnoiseICs, brainmask, confounds, confound_names,
                           derivatives_pipeline, hrf_model, low_pass, MELODICmix,
                           name, preproc, regfilt, res, result_dir, run_id, run_uuid,
                           ses_id, smooth, space, subject_id, slice_time_ref, task_id,
                           variant):

    import pkg_resources as pkgr
    from bids.grabbids import BIDSLayout
    
    single_subject_wf = pe.Workflow(name=name)


    # for querying derivatives structure
    config_file = pkgr.resource_filename('NiBetaSeries', 'utils/bids_derivatives.json')

    bids_data = BIDSLayout(bids_dir)

    derivatives_dir = os.path.join(bids_dir,'derivatives',derivatives_pipeline)
    derivatives_data = BIDSLayout(derivatives_dir,config=config_file)

    # get events file
    event_list = bids_data.get(subject=subject_id,
                               task=task_id,
                               type=events,
                               extensions='tsv',
                               return_type='file')

    if not event_list:
        raise Exception("No event files were found for participant {}".format(subject_id))
    elif len(event_list) > 1:
        raise Exception("Too many event files were found for participant {}".format(subject_id))
    else:
      events_file = event_list[0]

    # get derivatives files
    # preproc
    preproc_query = {
                     'subject': subject_id,
                     'task': task_id,
                     'type': 'preproc',
                     'return_type': 'file',
                     'extensions': ['nii', 'nii.gz']
                     }
    if variant:
        preproc_query['variant'] = variant
    if space:
        preproc_query['space'] = space
    if res:
        preproc_query['res'] = res

    preproc_list = derivatives_data.get(**preproc_query)

    if not preproc_list:
        raise Exception("No preproc files were found for participant {}".format(subject_id))
    elif len(preproc_list) > 1:
        raise Exception("Too many preproc files were found for participant {}".format(subject_id))
    else:
        preproc_file = preproc_list[0]
    # confounds
    confounds_list = derivatives_data.get(subject=subject_id,
                               task=task_id,
                               type=confounds,
                               extensions='tsv',
                               return_type='file')
    if not confounds_list:
        raise Exception("No confound files were found for participant {}".format(subject_id))
    elif len(confounds_list) > 1:
        raise Exception("Too many confound files were found for participant {}".format(subject_id))
    else:
        confound_file = confound_list[0]

    # brainmask
    brainmask_query = {
                     'subject': subject_id,
                     'task': task_id,
                     'type': 'brainmask',
                     'return_type': 'file',
                     'extensions': ['nii', 'nii.gz']
                     }
    if space:
        brainmask_query['space'] = space
    if res:
        brainmask_query['res'] = res

    brainmask_list = derivatives_data.get(**brainmask_query)
    if not brainmask_list:
        raise Exception("No brainmask files were found for participant {}".format(subject_id))
    elif len(brainmask_list) > 1:
        raise Exception("Too many brainmask files were found for participant {}".format(subject_id))
    else:
        brainmask_file = brainmask_list[0]

    workflow = pe.Workflow(name=name)

    inputnode = pe.Node(niu.IdentityInterface(fields=['subjects_dir']),
                        name='inputnode')

    return workflow
    #bidssrc = pe.Node(BIDSDataGrabber(subject_data=subject_data, anat_only=anat_only),
    #                  name='bidssrc')

    #bids_info = pe.Node(BIDSInfo(), name='bids_info', run_without_submitting=True)

    #summary = pe.Node(SubjectSummary(output_spaces=output_spaces, template=template),
    #                  name='summary', run_without_submitting=True)

    #about = pe.Node(AboutSummary(version=__version__,
    #                             command=' '.join(sys.argv)),
    #                name='about', run_without_submitting=True)

    #ds_summary_report = pe.Node(
    #    DerivativesDataSink(base_directory=reportlets_dir,
    #                        suffix='summary'),
    #    name='ds_summary_report', run_without_submitting=True)

    #ds_about_report = pe.Node(
    #    DerivativesDataSink(base_directory=reportlets_dir,
    #                        suffix='about'),
    #    name='ds_about_report', run_without_submitting=True)
