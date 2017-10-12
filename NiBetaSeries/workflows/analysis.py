#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

"""
Workflow for:
1) warping rois to subject data
2) extracting betas from rois
3) whole brain correlations
"""
from nilearn.input_data import NiftiSpheresMasker
import niworkflows.nipype.pipeline.engine as pe
from niworkflows.nipype.interfaces import utility as niu
from niworkflows.nipype.interfaces.ants import ApplyTransformsToPoints
def init_single_subject_correlation_wf():

    workflow = pe.Workflow(name=name)

    inputnode = pe.Node(niu.IdentityInterface(fields=['betas',
                                                      'bold_mask',
                                                      'mni_roi_coords',
                                                      'roi_size',
                                                      'warp']),
                        name='inputnode')

    outputnode = pe.Node(niu.IdentityInterface(fields=['zmaps_std']),
                          name='outputnode')

    # transform_mni_coords_2_t1 = pe.Node(ApplyTransformsToPoints(),
    #                            name='transform_mni_coords_2_t1')
    # input:
    #   input_file: mni_roi_coords
    #   transforms: warp
    #   dimension = 3
    # output:
    #   output_file: csv with transformed coordinates
    # TODO: check if the coordinates are resliced

    # make the rois first
    # use fslmaths -roi specify MNI coordinates, (xyz, not ijk)
    # fslmaths avg152T1.nii.gz -mul 0 -add 1 -roi 45 1 74 1 51 1 0 1 ACCpoint -odt float
    # fslmaths ACCpoint -kernel sphere 5 -fmean ACCsphere -odt float
    # fslmaths sub-controlGE154_T1w_space-MNI152NLin2009cAsym_brainmask.nii.gz -mul 0 -add 1 -roi 45 1 74 1 51 1 0 1 -kernel sphere 5 -fmean -bin sphere_test2.nii.gz
