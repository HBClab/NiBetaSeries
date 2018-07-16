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
    correlation_matrix = File(exists=True, desc='roi-roi fisher z transformed correlation matrix')


class AtlasConnectivity(NilearnBaseInterface, SimpleInterface):
    """Calculates correlations between regions of interest"""

    input_spec = AtlasConnectivityInputSpec
    output_spec = AtlasConnectivityOutputSpec

    def _run_interface(self, runtime):
        from nilearn.input_data import NiftiLabelsMasker
        from nilearn.connectome import ConnectivityMeasure
        import numpy as np
        import pandas as pd
        import os

        # extract timeseries from every label
        masker = NiftiLabelsMasker(labels_img=self.inputs.atlas_file, standardize=True,
                                   memory='nilearn_cache', verbose=1)
        timeseries = masker.fit_transform(self.inputs.timeseries_file)

        # create correlation matrix
        correlation_measure = ConnectivityMeasure(kind='correlation')
        correlation_matrix = correlation_measure.fit_transform([timeseries])[0]
        np.fill_diagonal(correlation_matrix, np.NaN)

        # add the atlas labels to the matrix
        atlas_lut_df = pd.read_csv(self.inputs.atlas_lut, sep='\t')
        regions = atlas_lut_df['regions']
        correlation_matrix_df = pd.DataFrame(correlation_matrix, index=regions, columns=regions)

        # do a fisher's r -> z transform
        fisher_z_matrix_df = correlation_matrix_df.apply(lambda x: np.log((1+x) / (1-x)) * 0.5)

        # write out the file.
        out_file = os.path.join(runtime.cwd, 'fisher_z_correlation.tsv')
        fisher_z_matrix_df.to_csv(out_file, sep='\t')

        # save the filename in the outputs
        self._results['correlation_matrix'] = out_file

        return runtime




