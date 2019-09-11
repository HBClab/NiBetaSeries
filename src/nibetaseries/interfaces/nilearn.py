#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

from nipype.interfaces.nilearn import NilearnBaseInterface
from nipype.interfaces.base import (
    BaseInterfaceInputSpec, TraitedSpec,
    File, SimpleInterface
    )


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
