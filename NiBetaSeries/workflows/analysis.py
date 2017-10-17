#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

# TODO: fix the renaming of files
"""
Workflow for:
1) warping rois to subject data
2) extracting betas from rois
3) whole brain correlations (r->z stat)
4) registering the results to standard space
"""

from niworkflows.nipype.interfaces.fsl.utils import ImageMaths, ImageMeants
import niworkflows.nipype.pipeline.engine as pe
from niworkflows.nipype.interfaces import utility as niu
from niworkflows.nipype.interfaces.ants import ApplyTransforms
from niworkflows.nipype.interfaces.afni.preprocess import TCorr1D
from niworkflows.nipype.interfaces.afni.utils import Calc

# name:
#   <source_file>[_space-<space>][_res-<XxYxZ>][_atlas-<atlas_name>]\
#   [_roi-<roi_identifier>][_variant-<label>]_<deriv>.nii.gz
#   roi-<name>_pearcorr.nii.gz
# okay to get this to work correctly I need to think:
# step 1: parse_mni_roi_coords_tsv
#   inputs: nothing to iterate over
#   outputs: 2 lists of strings [op_strings], [out_name_strings]
# step 2: make_roi (need to iterate over op_strings and out_name_strings)
#   inputs: op_string, out_name_string (iterate over both)
#   outputs: roi_mni.nii.gz
#   Use MapNode to get a list of outputs
#   revised outputs: [roi1_mni.nii.gz, roi2_mni.nii.gz ... roix_mni.nii.gz]
# step 3: roi_mni2t1w_transform
#   inputs: iterate over input image
#   outputs: [roi1_bold.nii.gz, roi2_bold.nii.gz ... roix_bold.nii.gz]
#   Use MapNode to iterate over the rois
# step 4: extract_signal
#   inputs: iterate over rois (nested iterate over betaseries_files)
#   outputs: [roi1.txt, roi2.txt ... roix.txt]
#   iterables = betaseries_files (so a separate list of rois.txt corresponding
#       to each betaseries_file)
#   ^^^ how should I represent this in nipype


def init_correlation_wf(roi_radius=12, name="correlation_wf"):
    """
    This workflow calculates betaseries correlations using regions of interest defined in
    MNI space.

    **Parameters**

        roi_radius: int
            radius of region of interest

    **Inputs**

        betaseries_files
            list with full path and name to betaseries files
        bold_mask
            binary mask of the BOLD series in T1w space
        mni_roi_coords
            tsv with the headings x,y,z,name corresponding to MNI (mm)
            coordinates in the x,y,z planes and the name associated with the roi.
        t1w_space_mni_mask
            binary mask of the T1w image in MNI space.
        target_t1w_warp
            concatonated linear+non-linear transforms from MNI->T1w space
        target_mni_warp
            concatonated linear+non-linear transforms from T1w->MNI space

    **Outputs**

        zmaps_mni
            3D z-statistic map for each roi within each betaseries file
    """
    # mixes the rois and betaseries_files so I can run all combinations
    def cart(rois, bsfiles):
        import os
        bsfile_names = [os.path.basename(bsfile).replace('.nii.gz','') for bsfile in bsfiles]
        roi_names = [os.path.basename(roi).replace('.nii.gz','') for roi in rois]
        rois_x_bsfiles = [roi for roi in rois for bsfile in bsfiles]
        bsfiles_x_rois = [bsfile for roi in rois for bsfile in bsfiles]
        rois_x_bsfiles_names = [
            roi + '_' + bsfile + '.nii.gz' for roi in roi_names for bsfile in bsfile_names
        ]
        bsfiles_x_rois_names = [
            bsfile + '_' + roi + '.nii.gz' for roi in roi_names for bsfile in bsfile_names
        ]

        #bsfiles_x_rois_names = [
        #    os.path.basename(bsfile).replace('.nii.gz', roi+'.nii.gz')
        #    for roi in rois for bsfile in bsfiles
        #]
        print('bsfiles_x_rois_names: {}'.format(bsfiles_x_rois_names))
        return rois_x_bsfiles, bsfiles_x_rois, bsfiles_x_rois_names


    # provides the input to make the roi using ImageMaths
    def parse_mni_roi_coords_tsv(mni_roi_coords, radius, mni_img):
        import csv
        import nibabel as nib

        # transform subject coordinates (mm) to voxel coordinates
        def xyz2ijk(xyz, affine):
            import numpy as np
            xyz = [int(p) for p in xyz]
            M_prime = np.linalg.inv(affine[:3, :3])
            abc = affine[:3, 3]
            return M_prime.dot(xyz) - abc

        # transform voxel coordinates to subject coordinates (mm)
        def ijk2xyz(ijk, affine):
            ijk = [int(p) for p in ijk]
            M = affine[:3, :3]
            abc = affine[:3, 3]
            return M.dot(ijk) + abc

        # base string for ImageMaths command
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
            reader = csv.DictReader(tsvfile, delimiter=str('\t'))
            for row in reader:
                out_names.append('roi-'+row.pop('name'))
                # transfer the subject coordinates in the tsv to
                # voxel coordinates for the image
                ijk_row = {
                           coord: int(round(point))
                           for coord, point in
                           zip(['x', 'y', 'z'],
                               xyz2ijk([row['x'], row['y'], row['z']],
                                       nib_img.affine))
                }
                # add radius to args dictionary
                ijk_row['radius'] = radius
                op_inputs.append(op_string.format(**ijk_row))
        # add usable filenames
        out_filenames = [name+'.nii.gz' for name in out_names]
        return op_inputs, out_names, out_filenames

    # rename outputs
    # see http://bit.ly/2xNNDAM
    def rename(f_list, s1, s2):
        return [os.path.basename(f).replace(s1, s2) for f in f_list]
    workflow = pe.Workflow(name=name)

    inputnode = pe.Node(niu.IdentityInterface(fields=['betaseries_files',
                                                      'bold_mask',
                                                      'mni_roi_coords',
                                                      't1w_space_mni_mask',
                                                      'target_t1w_warp',
                                                      'target_mni_warp']),
                        name='inputnode')

    outputnode = pe.Node(niu.IdentityInterface(fields=['zmaps_mni']),
                         name='outputnode')

    # prep the input for make_roi
    parse_roi_tsv = pe.Node(niu.Function(input_names=['mni_roi_coords', 'radius', 'mni_img'],
                                         output_names=['op_inputs', 'out_names', 'out_filenames'],
                                         function=parse_mni_roi_coords_tsv),
                            name='parse_roi_tsv')
    # set input radius
    parse_roi_tsv.inputs.radius = roi_radius
    # make the rois first
    # fslmaths -roi uses ijk coordinates
    # iterate over roi coordinate + name of roi
    make_roi = pe.MapNode(ImageMaths(),
                          name='make_roi',
                          iterfield=['op_string', 'out_file'])

    # transform rois to subject space
    # iterfield is input_image
    roi_mni2t1w_transform = pe.MapNode(ApplyTransforms(interpolation='NearestNeighbor'),
                                       name='roi_mni2t1w_transform',
                                       iterfield=['input_image'])

    cartisian_product = pe.Node(niu.Function(input_names=['rois', 'bsfiles'],
                                             output_names=['rois_x_bsfiles',
                                                           'bsfiles_x_rois',
                                                           'bsfiles_x_rois_names'],
                                             function=cart),
                                name='cartisian_product')

    # get the mean signal from a subject roi
    extract_signal = pe.MapNode(ImageMeants(),
                                name='extract_signal',
                                iterfield=['in_file', 'mask'])

    # correlation
    pearsons_corr = pe.MapNode(TCorr1D(outputtype='NIFTI_GZ', pearson=True),
                               name='3dTCorr1D',
                               iterfield=['xset', 'y_1d', 'out_file'])

    # pearson's r to z transform
    p_to_z = pe.MapNode(Calc(expr='log((1+a)/(1-a))/2'),
                        name='p_to_z',
                        iterfield=['in_file_a', 'out_file'])

    # ds005/out/fmriprep/sub-01/anat/sub-01_T1w_target-MNI152NLin2009cAsym_warp.h5
    # transform to standard space
    zmap_t1w2mni_transform = pe.MapNode(ApplyTransforms(interpolation="LanczosWindowedSinc"),
                                        name='zmap_t1w2mni_transform',
                                        iterfield=['input_image', 'output_image'])

    workflow.connect([
        # set up the rois (same rois will be used for each 4d betaseries file)
        (inputnode, parse_roi_tsv, [('mni_roi_coords', 'mni_roi_coords'),
                                    ('t1w_space_mni_mask', 'mni_img')]),
        # parse_roi_tsv returns a list
        (parse_roi_tsv, make_roi, [('op_inputs', 'op_string'),
                                   ('out_filenames', 'out_file')]),
        (inputnode, make_roi, [('t1w_space_mni_mask', 'in_file')]),
        # iterate over rois
        (make_roi, roi_mni2t1w_transform, [('out_file', 'input_image')]),
        (inputnode, roi_mni2t1w_transform, [('bold_mask', 'reference_image'),
                                            ('target_t1w_warp', 'transforms')]),
        (roi_mni2t1w_transform, cartisian_product, [('output_image', 'rois')]),
        (inputnode, cartisian_product, [('betaseries_files', 'bsfiles')]),
        (cartisian_product, extract_signal, [('rois_x_bsfiles', 'mask')]),
        (cartisian_product, extract_signal, [('bsfiles_x_rois', 'in_file')]),
        (cartisian_product, pearsons_corr,
            [('bsfiles_x_rois', 'xset'),
             (('bsfiles_x_rois_names', rename, '.nii.gz', '_pearcorr.nii.gz'),
             'out_file')]),
        (extract_signal, pearsons_corr, [('out_file', 'y_1d')]),
        (pearsons_corr, p_to_z, [('out_file', 'in_file_a'),
                                 (('out_file', rename, '_pearcorr', 'variant-zmap_pearcorr'),
                                 'out_file')]),
        (p_to_z, zmap_t1w2mni_transform,
            [('out_file', 'input_image'),
             (('out_file', rename, 'variant', 'space-MNI_variant'), 'output_image')]),
        (inputnode, zmap_t1w2mni_transform, [('t1w_space_mni_mask', 'reference_image'),
                                             ('target_mni_warp', 'transforms')]),
        (zmap_t1w2mni_transform, outputnode, [('output_image', 'zmaps_mni')]),
    ])

    return workflow
