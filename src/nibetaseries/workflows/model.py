#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
'''
Workflow for setting up the model for BetaSeries Correlatiion.
makes and executes a model using nistats.
'''
# TODO: handle cases where there aren't enough trials for a trial_type
from __future__ import print_function, division, absolute_import, unicode_literals

import nipype.pipeline.engine as pe
from nipype.interfaces import utility as niu
from nipype.interfaces.afni.preprocess import Detrend

def init_betaseries_wf(name="betaseries_wf",
                       t_r=2.0,
                       slice_time_ref=0.0,
                       hrf_model='glover'):

    workflow = pe.Workflow(name=name)

    # basic workflow
    # 1: make workflows
    # 2: load in events
    # 3: process events

    # Helpful definitions
    def run_betaseries(bold, events, bold_mask, t_r=2.0, slice_time_ref=0.0,
                       hrf_model='glover', n_jobs=1):
        from nistats.first_level_model import FirstLevelModel
        import numpy as np
        import pandas as pd
        import time
        import nibabel as nib
        import os

        def trial_events_iterator(events):
            trial_counter = dict([(t, 0) for t in np.unique(events['trial_type'])])
            for trial_id in range(len(events)):
                trial_type = events.loc[trial_id, 'trial_type']
                events_copy = events.copy()
                events_copy['trial_type'] = 'other'
                events_copy.loc[trial_id, 'trial_type'] = trial_type
                yield events_copy, trial_type, trial_counter[trial_type]
                trial_counter[trial_type] += 1

        model = FirstLevelModel(t_r=t_r, slice_time_ref=slice_time_ref, hrf_model=hrf_model,
                                mask=bold_mask, standardize=1, signal_scaling=0,
                                verbose=1, n_jobs=n_jobs)

        events_df = pd.read_csv(events, sep='\t', index_col=None)
        num_events = len(events_df)

        # initialize trial type tracker
        t_type_prev = 0
        # initialize list to contain trial estimates (betas)
        beta_list = []
        # initialize list to track betaseries files
        betaseries_files = []
        beta_path = os.getcwd()
        for t_ev_idx, (t_ev, t_type, t_idx) in enumerate(trial_events_iterator(events_df)):
            if not os.path.exists(beta_path):
                os.makedirs(beta_path)

            beta_file = os.path.join(
                os.getcwd(), 'betaseries', '%s_%03d_es.nii' % (t_type, t_idx))

            if not os.path.exists(beta_file):
                # Estimate and save model
                print('Estimating trial %03d of %03d' %
                      (t_ev_idx + 1, len(events_df)))
                start_time = time.time()
                if model.results_ is None:
                    model.fit(bold, t_ev, None)  # had to remove conf
                else:
                    model.refit_run_design(bold, t_ev, None)  # had to remove conf

            beta = model.compute_contrast(t_type, output_type='effect_size')  
            if t_type_prev != t_type and t_type_prev != 0 or t_ev_idx == (num_events-1):
                if t_ev_idx == (num_events-1):
                    beta_list.append(beta)
                # concatenate and save the 4d betaseries
                betaseries = nib.funcs.concat_images(beta_list)
                betaseries_file = os.path.join(
                    beta_path, 'trialtype-{}_betaseries.nii.gz'.format(t_type_prev))
                print('betaseries: {}'.format(betaseries_file))
                nib.save(betaseries, betaseries_file)
                # add the 4d betaseries to the output list
                betaseries_files.append(betaseries_file)
                beta_list = []

            t_type_prev = t_type
            beta_list.append(beta)
            # nib.save(beta, beta_file)

            print('Done in %d seconds' % (time.time() - start_time))

        # return the 4d betaseries files
        print("all betaseries_files: {}".format(betaseries_files))
        return betaseries_files

    inputnode = pe.Node(niu.IdentityInterface(fields=['bold',
                                                      'events',
                                                      'bold_mask']),
                        name='inputnode')

    betaseries = pe.Node(niu.Function(function=run_betaseries,
                                      input_names=['bold', 'events', 'bold_mask'],
                                      output_names=['betaseries_files']),
                         name='betaseries')

    # Set inputs to betaseries
    betaseries.inputs.t_r = t_r
    betaseries.inputs.slice_time_ref = slice_time_ref
    betaseries.inputs.hrf_model = hrf_model

    demean = pe.MapNode(Detrend(args = '-polort 0', outputtype='NIFTI_GZ'),
                        iterfield=['in_file'], name='demean')

    outputnode = pe.Node(niu.IdentityInterface(fields=['betaseries_files']),
                         name='outputnode')

    # main workflow
    workflow.connect([
        (inputnode, betaseries, [('bold', 'bold'),
                                 ('events', 'events'),
                                 ('bold_mask', 'bold_mask')]),
        (betaseries, demean, [('betaseries_files', 'in_file')]),
        (demean, outputnode, [('out_file', 'betaseries_files')]),
    ])

    return workflow
