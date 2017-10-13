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
    def xyz2ijk(xyz, affine):
        import numpy as np
        M_prime = np.linalg.inv(affine[:3, :3])
        abc = affine[:3, 3]
        return M_prime.dot(xyz) - abc

    def ijk2xyz(ijk, affine):
        M = affine[:3, :3]
        abc = affine[:3, 3]
        return M.dot(ijk) + abc


    def parse_mni_roi_coords_tsv(mni_roi_coords, radius, mni_img):
        import csv
        import nibabel as nib
        # return op_string
        # return name of roi
        op_string = """\
                  -mul 0 -add 1 -roi {x} 1 {y} 1 {z} 1 0 1 \
                  -kernel sphere {radius} -fmean -bin \
                  """
        # mni_img (voxels t1w size)
        nib_img = nib.load(mni_img)
        # op_string to pass to ImageMaths
        op_inputs = []
        # out_file to pass to ImageMaths
        out_names = []
        with open(mni_roi_coords) as tsvfile:
            reader = csv.DictReader(tsvfile, delimiter='\t')
            for row in reader:
                out_names.append(row.pop('name')+'_{}.nii.gz'.format(radius))
                ijk_row = {coord : int(round(point))
                    for coord,point in
                    zip(['x', 'y', 'z'], xyz2ijk([row['x'], row['y'], row['z']], affine))}
                op_inputs.append(op_string.format(**ijk_row, radius=radius))

        return op_inputs, out_names

    workflow = pe.Workflow(name=name)

    inputnode = pe.Node(niu.IdentityInterface(fields=['betas',
                                                      'bold_mask',
                                                      'mni_roi_coords',
                                                      'roi_radius',
                                                      't1w_space_mni_mask',
                                                      'target_t1w_warp',
                                                      'target_mni_warp']),
                        name='inputnode')

    outputnode = pe.Node(niu.IdentityInterface(fields=['zmaps_mni']),
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

    make_roi = pe.MapNode(ImageMaths())

    parse_roi_tsv = pe.Node(niu.Function(input_names=['mni_roi_coords', 'radius', 'mni_img'],
                                         output_names=['op_inputs', 'out_names'],
                                         function=parse_mni_roi_coords_tsv),
                            name='parse_roi_tsv')

    # transform rois to subject space
    # iterfield is infile
    roi_mni2t1w_transform = pe.MapNode(ApplyTransforms(interpolation='NearestNeighbor'),
                                       name='roi_mni2t1w_transform')

    # get the mean signal from a subject roi
    extract_signal = pe.MapNode(ImageMeants())

    # correlation
    pearsons_corr = pe.Node(TCorr1D(outputtype='NIFTI_GZ', pearson=True),
                      name='3dTCorr1D')

    # pearson's r to z transfer
    # 3dcalc -a Corr_subj01+tlrc -expr 'log((1+a)/(1-a))/2' -prefix Corr_subj01_Z+tlrc
    p_to_z = pe.Node(Calc(expr='log((1+a)/(1-a))/2'))


    # TODO: rename warps ds005/out/fmriprep/sub-01/anat/sub-01_T1w_target-MNI152NLin2009cAsym_warp.h5
    # transform to standard space
    zmap_t1w2mni_transform = pe.MapNode(ApplyTransforms(interpolation="LanczosWindowedSinc"),
                                        name='zmap_t1w2mni_transform')

    workflow.connect([
        (inputnode, parse_roi_tsv, [('mni_roi_coords', 'mni_roi_coords'),
                                    ('roi_radius', 'radius'),
                                    ('t1w_space_mni_mask', 'mni_img')]),
        (parse_roi_tsv, make_roi, [('op_inputs', 'op_string'),
                                   ('out_names', 'out_file'])),
        (inputnode, make_roi, [('t1w_space_mni_mask', 'in_file')]),
        (make_roi, roi_mni2t1w_transform, [('out_file', 'input_image')]),
        (inputnode, roi_mni2t1w_transform, [('bold_mask', 'reference_image'),
                                            ('target_t1w_warp', 'transforms')]),
        (roi_mni2t1w_transform, extract_signal, [('output_image', 'mask')]),
        (inputnode, extract_signal, [('betas', 'in_file')]),
        (inputnode, pearsons_corr, [('betas', 'xset')]),
        (extract_signal, pearsons_corr, [('out_file', 'y_1d')]),
        (pearsons_corr, p_to_z, [('out_file', 'in_file_a')]),
        (p_to_z, zmap_t1w2mni_transform, [('out_file', 'input_image')]),
        (inputnode, zmap_t1w2mni_transform, [('t1w_space_mni_mask', 'reference_image'),
                                             ('target_mni_warp', 'transforms')]),
        (zmap_t1w2mni_transform, outputnode, [('output_image', 'zmaps_mni')]),

    ])

    return workflow
