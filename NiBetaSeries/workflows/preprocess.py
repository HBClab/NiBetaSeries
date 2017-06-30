#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
'''
Workflow for preprocessing the data
performing basic preprocessing.
- smoothing (fmriprep takes care of the rest)
- highpass filter
- prewhiten?
'''
from __future__ import print_function, division, absolute_import, unicode_literals

from niworkflows.nipype.pipeline.engine as pe
from niworkflows.nipype.interfaces.utility import IdentityInterface, Merge
from niworkflows.nipype.interfaces.fsl.model import Level1Design, FEATModel
from niworkflows.nipype.interfaces.fsl import ImageStats, ImageMaths, SUSAN

def getusans(x):
    return [[tuple([val[0], 0.75 * val[1]])] for val in x]

def getbtthresh(medianvals):
    return [0.75 * val for val in medianvals]

def init_preprocess_wf(name='preprocess_wf'):

    # inputs
    input_node = pe.Node(IdentityInterface(
                         fields=['fmri_bold', 'fmri_bold_mask', 'fwhm', 'tr']),
                         name='input_node')

    # outputs
    output_node = pe.Node(IdentityInterface(
                         fields=['processed_fmri_bold']),
                         name='output_node')
    # mask the bold file
    mask_node = pe.Node(interface=ImageMaths(suffix='_mask'
                                             op_string='-mas'))

    # calculate the median value of fmri_bold
    median_node = pe.Node(interface=ImageStats(op_string='-k %s -p 50'),
                             name='median_node')

    # calculate the mean functional of fmri_bold
    meanfunc_node = pe.Node(interface=ImageMaths(op_string='-Tmean',
                                                        suffix='_mean'),
                               name='meanfunc_node')

    # combine the median value and mean func of fmri_bold
    merge_node = pe.Node(interface=Merge(2, axis='hstack'),
                         name='merge_node')

    # Susan smoothing
    smooth_node = pe.Node(interface=SUSAN(),
                          name='smooth_node')

    workflow = pe.Workflow(name=name)
    workflow.connect([
    # prereqs for SUSAN
    (input_node, mask_node, [('fmri_bold', 'in_file'),
                             ('fmri_bold_mask', 'in_file2')])
    (mask_node, meanfunc_node, [('out_file', 'in_file')]),
    (input_node, median_node, [('fmri_bold', 'in_file'),
                               ('fmri_bold_mask', 'mask_file')]),
    (meanfunc_node, merge, [('out_file', 'in1')]),
    (median_node, merge, [('out_stat', 'in2')]),
    # Send inputs to SUSAN
    (input_node, smooth, [('fwhm', 'fwhm' )]),
    (merge, smooth, [(('out', getusans), 'usans')]),
    (median_node, smooth_node, [(('out_stat', getbtthresh), 'brightness_threshold')]),
    (smooth_node, output_node, [('smoothed_file', 'processed_fmri_bold')])
    ])

    return workflow
