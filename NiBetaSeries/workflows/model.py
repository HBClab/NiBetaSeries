#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
'''
Workflow for setting up the model for BetaSeries Correlatiion.
makes and executes a model within the fsl pipeline.
'''
from __future__ import print_function, division, absolute_import, unicode_literals

from niworkflows.nipype.pipeline.engine as pe
from niworkflows.nipype.interfaces import io as nio
from niworkflows.nipype.interfaces.base import Bunch
from niworkflows.nipype.algorithms.modelgen import  SpecifyModel
from niworkflows.nipype.interfaces.utility import IdentityInterface,Function
from niworkflows.nipype.interfaces.fsl.model import Level1Design,FEATModel

from bids.grabbids import BIDSLayout
import numpy as np
import pandas as pd

def init_model_wf(name="model_wf"):

    # inputs to workflow
    input_node = pe.Node(IdentityInterface(
                        fields=['subject_info', 'processed_fmri_bold',
                                'time_repetition', 'high_pass_filter_cutoff',
                                'hrf_model']),
                                #hrf model: {'dgamma':{'derivs': True}}
                        name='input_node')

    # outputs to workflow
    output_node = pe.Node(IdentityInterface(
                         fields=['fsl_des_mat', 'evs']),
                         name='output_node')

    # specify the model
    specify_model_node = pe.Node(mg.SpecifyModel(input_units='secs'),
                                 name='model_node')
    # create fsf file
    # model_serial_correlations: throwaway option since we aren't using the fsf file
    level_one_design_node = pe.Node(Level1Design(model_serial_correlations=True),
                               name='level_one_design_node')
    # create mat file
    feat_model_node = pe.Node(FEATModel(),
                         name='feat_model_node')

    workflow = pe.Workflow(name=name)
    workflow.connect([
    (input_node, specify_model_node, [('subject_info', 'subject_info'),
                                      ('processed_fmri_bold', 'functional_runs'),
                                      ('time_repetition', 'time_repetition'),
                                      ('high_pass_filter_cutoff', 'high_pass_filter_cutoff')]),
    (specify_model_node, level_one_design_node, [('session_info', 'session_info'),
                                                 ('hrf_model', 'bases')]),
    (level_one_design_node, feat_model_node, [('ev_files', 'ev_files',
                                              ('fsf_files', 'fsf_file'))])
    ])

    return workflow
