#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
NiBetaSeries processing workflows
"""

import sys
import os
from copy import deepcopy

from niworkflows.nipype.pipeline import engine as pe
from niworkflows.nipype.interfaces import utility as niu
def init_nibetaseries_participant_wf(subject_list, task_id, derivatives_pipeline,
                     bids_dir, output_dir, work_dir, space, variant, res,
                     hrf_model, slice_time_ref, run_uuid, omp_nthreads):
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
        single_subject_wf = init_single_subject_wf(
        subject_list=subject_list,
        task_id=task_id,
        derivatives_pipeline=derivatives_pipeline,
        bids_dir=bids_dir,
        output_dir=output_dir,
        work_dir=work_dir,
        space=space,
        variant=variant,
        res=res,
        hrf_model=hrf_model,
        slice_time_ref=slice_time_ref,
        run_uuid=run_uuid,
        omp_nthreads=omp_nthreads
        )

        single_subject_wf.config['execution']['crashdump_dir'] = (
            os.path.join(output_dir, "nibetaseries", "sub-" + subject_id, 'log', run_uuid)
        )

        for node in single_subject_wf._get_all_nodes():
            node.config = deepcopy(single_subject_wf.config)

        fmriprep_wf.add_nodes([single_subject_wf])
    return nibetaseries_participant_wf

def init_single_subject_wf(subject_id, task_id, derivatives_pipeline,
                     bids_dir, output_dir, work_dir, space, variant, res,
                     hrf_model, slice_time_ref, run_uuid, omp_nthreads):
    
