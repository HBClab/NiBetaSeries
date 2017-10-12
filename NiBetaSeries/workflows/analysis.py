#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

"""
Workflow for:
1) warping rois to subject data
2) extracting betas from rois
3) whole brain correlations (r->z stat)
4) registering the results to standard space
"""

from nipype.interface.fsl.utils import ImageMaths, ImageMeants
import niworkflows.nipype.pipeline.engine as pe
from niworkflows.nipype.interfaces import utility as niu
from niworkflows.nipype.interfaces.ants import ApplyTransforms
from niworkflows.nipype.interfaces.afni.preprocess import TCorr1D
from niworkflows.nipype.interfaces.afni.utils import Calc

def init_single_subject_correlation_wf():

    def parse_mni_roi_coords_tsv(mni_roi_coords, radius):
        import csv
        # return op_string
        # return name of roi
        op_string = """\
                  -mul 0 -add 1 -roi {x} 1 {y} 1 {z} 1 0 1 \
                  -kernel sphere {radius} -fmean -bin \
                  """
        # op_string to pass to ImageMaths
        op_inputs = []
        # out_file to pass to ImageMaths
        out_names = []
        with open(mni_roi_coords) as tsvfile:
            reader = csv.DictReader(tsvfile, delimiter='\t')
            for row in reader:
                out_names.append(row.pop('name')+'_{}.nii.gz'.format(radius))
                op_inputs.append(op_string.format(**row, radius=radius))

        return op_inputs, out_names

    workflow = pe.Workflow(name=name)

    inputnode = pe.Node(niu.IdentityInterface(fields=['betas',
                                                      'bold_mask',
                                                      'mni_roi_coords',
                                                      'roi_size',
                                                      'target_t1w_warp'
                                                      'target_mni_warp']),
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

    make_roi = pe.Node(interface=ImageMaths())

    parse_roi_tsv = pe.Node(niu.Function(input_names=['mni_roi_coords', 'radius'],
                                         output_names=['op_inputs', 'out_names'],
                                         function=parse_mni_roi_coords_tsv),
                            name='parse_roi_tsv')

    # transform rois to subject space
    # iterfield is infile
    roi_mni2t1w_transform = pe.MapNode(interface=ApplyTransforms(),
                                       name='roi_mni2t1w_transform')

    # get the mean signal from a subject roi
    extract_signal = pe.MapNode(ImageMeants())

    # correlation
    corr = pe.Node(interface=TCorr1D(outputtype='NIFTI_GZ', pearson=True),
                      name='3dTCorr1D')

    # pearson's r to z transfer
    # 3dcalc -a Corr_subj01+tlrc -expr 'log((1+a)/(1-a))/2' -prefix Corr_subj01_Z+tlrc
    p_to_z = pe.Node(interface=Calc(expr='log((1+a)/(1-a))/2'))


    # TODO: rename warps ds005/out/fmriprep/sub-01/anat/sub-01_T1w_target-MNI152NLin2009cAsym_warp.h5
    # transform to standard space
    zmap_t1w2mni_transform = pe.MapNode(interface=ApplyTransforms(),
                                        name='zmap_t1w2mni_transform')
