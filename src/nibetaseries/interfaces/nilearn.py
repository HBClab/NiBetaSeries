#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

from nipype.interfaces.nilearn import NilearnBaseInterface
from nipype.interfaces.base import (
    BaseInterfaceInputSpec, TraitedSpec,
    File, SimpleInterface, traits,
    )


class CensorVolumesInputSpec(BaseInterfaceInputSpec):
    timeseries_file = File(exists=True, mandatory=True,
                           desc="a 4d nifti file")
    mask_file = File(exists=True, mandatory=True,
                     desc='binary mask for the 4d nifti file')
    threshold = traits.Float(default_value=10.0,
                             usedefault=True,
                             desc="the modified z-score to use as a threshold")


class CensorVolumesOutputSpec(TraitedSpec):
    censored_file = File(exists=True,
                         desc="a 4d nifti file with extreme volumes removed")
    outliers = traits.Array(desc="boolean array indicating which indices are noise")


class CensorVolumes(SimpleInterface):
    """remove volumes with extremely large outliers"""

    input_spec = CensorVolumesInputSpec
    output_spec = CensorVolumesOutputSpec

    def _run_interface(self, runtime):
        import nibabel as nib
        from nipype.utils.filemanip import fname_presuffix

        bold_img = nib.load(self.inputs.timeseries_file)
        bold_mask_img = nib.load(self.inputs.mask_file)

        bold_data = bold_img.get_fdata()
        bold_mask = bold_mask_img.get_fdata().astype(bool)

        outliers = is_outlier(bold_data[bold_mask].T, thresh=self.inputs.threshold)

        out = fname_presuffix(self.inputs.timeseries_file, suffix='_censored')

        bold_img.__class__(bold_data[..., ~outliers],
                           bold_img.affine, bold_img.header).to_filename(out)

        self._results['censored_file'] = out
        self._results['outliers'] = outliers

        return runtime


class AtlasConnectivityInputSpec(BaseInterfaceInputSpec):
    timeseries_file = File(exists=True, mandatory=True,
                           desc='The 4d file being used to extract timeseries data')
    atlas_file = File(exists=True, mandatory=True,
                      desc='The atlas image with each roi given a unique index')
    atlas_lut = File(exists=True, mandatory=True,
                     desc='The atlas lookup table to match the atlas image')


class AtlasConnectivityOutputSpec(TraitedSpec):
    correlation_matrix = File(exists=True,
                              desc='roi-roi fisher z transformed correlation matrix')
    correlation_fig = File(exists=True,
                           desc='svg of roi-roi fisher z transformed correlation matrix')


class AtlasConnectivity(NilearnBaseInterface, SimpleInterface):
    """Calculates correlations between regions of interest"""

    input_spec = AtlasConnectivityInputSpec
    output_spec = AtlasConnectivityOutputSpec

    def _run_interface(self, runtime):
        from nilearn.input_data import NiftiLabelsMasker
        from nilearn.connectome import ConnectivityMeasure
        from sklearn.covariance import EmpiricalCovariance
        import numpy as np
        import pandas as pd
        import os
        import matplotlib.pyplot as plt
        from mne.viz import plot_connectivity_circle
        import re

        plt.switch_backend('Agg')

        # extract timeseries from every label
        masker = NiftiLabelsMasker(labels_img=self.inputs.atlas_file,
                                   standardize=True, verbose=1)
        timeseries = masker.fit_transform(self.inputs.timeseries_file)
        # create correlation matrix
        correlation_measure = ConnectivityMeasure(cov_estimator=EmpiricalCovariance(),
                                                  kind="correlation")
        correlation_matrix = correlation_measure.fit_transform([timeseries])[0]
        np.fill_diagonal(correlation_matrix, np.NaN)

        # add the atlas labels to the matrix
        atlas_lut_df = pd.read_csv(self.inputs.atlas_lut, sep='\t')
        regions = atlas_lut_df['regions'].values
        correlation_matrix_df = pd.DataFrame(correlation_matrix, index=regions, columns=regions)

        # do a fisher's r -> z transform
        fisher_z_matrix_df = correlation_matrix_df.apply(_fisher_r_to_z)

        # write out the file.
        trial_regex = re.compile(r'.*desc-(?P<trial>[A-Za-z0-9]+)')
        title = re.search(trial_regex, self.inputs.timeseries_file).groupdict()['trial']
        template_name = 'desc-{trial}_correlation.{ext}'
        corr_mat_fname = template_name.format(trial=title, ext="tsv")
        corr_mat_path = os.path.join(runtime.cwd, corr_mat_fname)
        fisher_z_matrix_df.to_csv(corr_mat_path, sep='\t', na_rep='n/a')

        # save the filename in the outputs
        self._results['correlation_matrix'] = corr_mat_path

        # visualizations with mne
        connmat = fisher_z_matrix_df.values
        labels = list(fisher_z_matrix_df.index)

        # plot a circle visualization of the correlation matrix
        viz_mat_fname = template_name.format(trial=title, ext="svg")
        viz_mat_path = os.path.join(runtime.cwd, viz_mat_fname)

        n_lines = int(np.sum(connmat > 0) / 2)
        fig = plt.figure(figsize=(5, 5))

        plot_connectivity_circle(connmat, labels, n_lines=n_lines, fig=fig, title=title,
                                 fontsize_title=10, facecolor='white', textcolor='black',
                                 colormap='jet', colorbar=1, node_colors=['black'],
                                 node_edgecolor=['white'], show=False, interactive=False)

        fig.savefig(viz_mat_path, dpi=300)
        self._results['correlation_fig'] = viz_mat_path

        return runtime


def _fisher_r_to_z(x):
    import numpy as np
    # correct any rounding errors
    # correlations cannot be greater than 1.
    x = np.clip(x, -1, 1)

    return np.arctanh(x)


def is_outlier(points, thresh=3.5):
    """
    Returns a boolean array with True if points are outliers and False
    otherwise.

    modified from nipype:
    https://github.com/nipy/nipype/blob/b62d80/nipype/algorithms/confounds.py#L1129

    Parameters
    ----------
    points: nparray
        an numobservations by numdimensions numpy array of observations
    thresh: float
        the modified z-score to use as a threshold. Observations with
        a modified z-score (based on the median absolute deviation) greater
        than this value will be classified as outliers.

    Returns
    -------
        A bolean mask, of size numobservations-length array.

    .. note:: References
        Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
        Handle Outliers", The ASQC Basic References in Quality Control:
        Statistical Techniques, Edward F. Mykytka, Ph.D., Editor.
    """
    import numpy as np

    if len(points.shape) == 1:
        points = points[:, None]
    median = np.median(points, axis=0)
    diff = np.sum((points - median)**2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff)

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score > thresh
