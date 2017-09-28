#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
'''
Workflow for doing preprocessing
that FMRIPREP doesn't complete, and derives residuals from bold

-
'''

from __future__ import print_function, division, absolute_import, unicode_literals

import niworkflows.nipype.pipeline.engine as pe
from niworkflows.nipype.interfaces import utility as niu
# from niworkflows.nipype.interfaces.utility import IdentityInterface
from niworkflows.nipype.interfaces.fsl import ImageStats, MultiImageMaths, SUSAN
from niworkflows.nipype.interfaces.fsl.utils import FilterRegressor
from niworkflows.nipype.interfaces.fsl.maths import MeanImage
# from niworkflows.nipype.interfaces.utility import Function
from nilearn.image import clean_img
import nibabel as nib
import pandas as pd


def init_derive_residuals_wf(name='derive_residuals_wf', t_r=2.0,
                             smooth=None, confound_names=None,
                             regfilt=False, lp=None):
    r"""
    This workflow derives the residual image from the preprocessed FMRIPREP image.

    Parameters

        name : str
            name of the workflow
        t_r : float
            time of repetition to collect a volume
        smooth : float or None
            smoothing kernel to apply to image (mm)
        confound_names : list of str or None
            Column names from FMRIPREP's confounds tsv that were selected for
            nuisance regression
        regfilt : bool
            Selects to run FilterRegressor from the output from ICA-AROMA
        lp : float or None
            The frequency to set low pass filter (in Hz)
    """
    # Steps
    # 1) brain mask
    # 2) smooth (optional)
    # 3) regfilt (optional)
    # 4) remove residuals

    inputnode = pe.Node(niu.IdentityInterface(
        fields=['bold_preproc', 'bold_mask', 'confounds', 'MELODICmix',
                'AROMAnoiseICs']),
        name='inputnode')

    outputnode = pe.Node(niu.IdentityInterface(
        fields=['bold_resid']),
        name='outputnode')

    # Function to perform confound removal
    def remove_confounds(nii, confounds, t_r=2.0, confound_names=None, lp=None):
        import nibabel as nib
        import pandas as pd
        import os
        from nilearn.image import clean_img
        img = nib.load(nii)
        confounds_pd = pd.read_csv(confounds, sep="\t")
        if confound_names is None:
            confound_names = [col for col in confounds_pd.columns
                              if 'CompCor' in col or 'X' in col or 'Y' in col or 'Z' in col]
        confounds_np = confounds_pd.as_matrix(columns=confound_names)
        kwargs = {
                  'imgs': img,
                  'confounds': confounds_np,
                  't_r': t_r
                 }
        if lp:
            kwargs['low_pass'] = lp
        cleaned_img = clean_img(**kwargs)
        working_dir = os.getcwd()
        resid_nii = os.path.join(working_dir, 'resid.nii.gz')
        nib.save(cleaned_img, resid_nii)

        return resid_nii

    # brain mask node
    mask_bold = pe.Node(MultiImageMaths(op_string='-mul %s'), name='mask_bold')
    # optional smoothing workflow
    smooth_wf = init_smooth_wf(smooth=smooth)
    # optional filtering workflow
    filt_reg_wf = init_filt_reg_wf(regfilt=regfilt)
    # residual node
    calc_resid = pe.Node(name='calc_resid',
                         interface=niu.Function(input_names=['nii',
                                                         'confounds',
                                                         't_r',
                                                         'confound_names',
                                                         'lp'],
                                            output_names=['nii_resid'],
                                            function=remove_confounds))

    # Predefined attributes
    calc_resid.inputs.t_r = t_r
    calc_resid.inputs.confound_names = confound_names
    calc_resid.inputs.lp = lp

    # main workflow
    workflow = pe.Workflow(name=name)
    workflow.connect([
        (inputnode, mask_bold, [('bold_preproc', 'in_file'),
                                ('bold_mask', 'operand_files')]),
        (mask_bold, smooth_wf, [('out_file', 'inputnode.bold')]),
        (inputnode, smooth_wf, [('bold_mask', 'inputnode.bold_mask')]),
        (smooth_wf, filt_reg_wf, [('outputnode.bold_smooth', 'inputnode.bold')]),
        (inputnode, filt_reg_wf, [('bold_mask', 'inputnode.bold_mask'),
                                  ('MELODICmix', 'inputnode.MELODICmix'),
                                  ('AROMAnoiseICs', 'inputnode.AROMAnoiseICs')]),
        (filt_reg_wf, calc_resid, [('outputnode.bold_regfilt', 'nii')]),
        (inputnode, calc_resid, [('confounds', 'confounds')]),
        (calc_resid, outputnode, [('nii_resid', 'bold_resid')]),
    ])

    return workflow


# fsl regfilt workflow
def init_filt_reg_wf(name='filt_reg_wf', regfilt=None):
    inputnode = pe.Node(niu.IdentityInterface(
        fields=['bold', 'bold_mask', 'MELODICmix', 'AROMAnoiseICs']),
        name='inputnode')

    outputnode = pe.Node(niu.IdentityInterface(
        fields=['bold_regfilt']),
        name='outputnode')

    workflow = pe.Workflow(name=name)
    if regfilt:
        def csv_to_list(csv_f):
            import csv
            with open(csv_f) as f:
                reader = csv.reader(f, delimiter=str(','))
                mlist = list(reader)[0]
            return [int(x) for x in mlist]

        filter_regressor = pe.Node(FilterRegressor(), name='filter_regressor')
        workflow.connect([
            (inputnode, filter_regressor, [('bold', 'in_file'),
                                           ('bold_mask', 'mask'),
                                           ('MELODICmix', 'design_file'),
                                           (('AROMAnoiseICs', csv_to_list), 'filter_columns')]),
            (filter_regressor, outputnode, [('out_file', 'bold_regfilt')]),
        ])
    else:
        workflow.connect([
            (inputnode, outputnode, [('bold', 'bold_regfilt')]),
        ])

    return workflow


# smoothing workflow
def init_smooth_wf(name='smooth_wf', smooth=None):
    workflow = pe.Workflow(name=name)
    inputnode = pe.Node(niu.IdentityInterface(
        fields=['bold', 'bold_mask']),
        name='inputnode')

    outputnode = pe.Node(niu.IdentityInterface(
        fields=['bold_smooth']),
        name='outputnode')

    if smooth:
        calc_median_val = pe.Node(ImageStats(op_string='-k %s -p 50'), name='calc_median_val')
        calc_bold_mean = pe.Node(MeanImage(), name='calc_bold_mean')

        def getusans_func(image, thresh):
            return [tuple([image, thresh])]

        def _getbtthresh(medianval):
            return 0.75 * medianval
        getusans = pe.Node(niu.Function(function=getusans_func, output_names=['usans']),
                           name='getusans', mem_gb=0.01)

        smooth = pe.Node(SUSAN(fwhm=smooth), name='smooth')

        workflow.connect([
            (inputnode, calc_median_val, [('bold', 'in_file'),
                                          ('bold_mask', 'mask_file')]),
            (inputnode, calc_bold_mean, [('bold', 'in_file')]),
            (calc_bold_mean, getusans, [('out_file', 'image')]),
            (calc_median_val, getusans, [('out_stat', 'thresh')]),
            (inputnode, smooth, [('bold', 'in_file')]),
            (getusans, smooth, [('usans', 'usans')]),
            (calc_median_val, smooth, [(('out_stat', _getbtthresh), 'brightness_threshold')]),
            (smooth, outputnode, [('smoothed_file', 'bold_smooth')]),
        ])
    else:
        workflow.connect([
            (inputnode, outputnode, [('bold', 'bold_smooth')]),
        ])

    return workflow
