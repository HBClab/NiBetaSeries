''' Testing module for nibetaseries.interfaces.nilearn '''
import nibabel as nib
import numpy as np
import pandas as pd
import os

from ..nilearn import AtlasConnectivity, CensorVolumes


def test_censor_volumes(tmp_path, betaseries_file, brainmask_file):
    outlier_file = tmp_path / 'betaseries_outlier.nii.gz'

    # make an outlier volume
    outlier_idx = 6
    beta_img = nib.load(str(betaseries_file))
    beta_data = beta_img.get_fdata()
    beta_data[..., outlier_idx] += 1000

    beta_img.__class__(
        beta_data, beta_img.affine, beta_img.header).to_filename(str(outlier_file))

    censor_volumes = CensorVolumes(timeseries_file=str(outlier_file),
                                   mask_file=str(brainmask_file))

    res = censor_volumes.run()

    assert nib.load(res.outputs.censored_file).shape[-1] == beta_img.shape[-1] - 1
    assert res.outputs.outliers[outlier_idx]


def test_atlas_connectivity(betaseries_file, atlas_file, atlas_lut):
    # read in test files
    bs_data = nib.load(str(betaseries_file)).get_data()
    atlas_lut_df = pd.read_csv(str(atlas_lut), sep='\t')

    # expected output
    pcorr = np.corrcoef(bs_data.squeeze())
    np.fill_diagonal(pcorr, np.NaN)
    regions = atlas_lut_df['regions'].values
    pcorr_df = pd.DataFrame(pcorr, index=regions, columns=regions)
    expected_zcorr_df = pcorr_df.apply(lambda x: (np.log(1 + x) - np.log(1 - x)) * 0.5)

    # run instance of AtlasConnectivity
    ac = AtlasConnectivity(timeseries_file=str(betaseries_file),
                           atlas_file=str(atlas_file),
                           atlas_lut=str(atlas_lut))

    res = ac.run()

    output_zcorr_df = pd.read_csv(res.outputs.correlation_matrix,
                                  na_values='n/a',
                                  delimiter='\t',
                                  index_col=0)

    os.remove(res.outputs.correlation_matrix)
    # test equality of the matrices up to 3 decimals
    pd.testing.assert_frame_equal(output_zcorr_df, expected_zcorr_df,
                                  check_less_precise=3)
