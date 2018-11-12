''' Testing module for nibetaseries.interfaces.nilearn '''
import os
import shutil
import nibabel as nib
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from scipy.optimize import minimize

from ..nilearn import AtlasConnectivity


def test_atlas_connectivity():
    # basedir
    base_dir = os.path.join(os.getcwd(), 'tmp')
    os.makedirs(base_dir, exist_ok=True)
    # timeseries_file (beta series)
    timeseries_file = os.path.join(base_dir,
                                   'betaseries.nii.gz')
    # atlas_file
    atlas_file = os.path.join(base_dir,
                              'atlas.nii.gz')
    # atlas_lut
    atlas_lut_file = os.path.join(base_dir,
                                  'lut.tsv')

    # dummy series of betas
    # set how the betaseries will be defined
    np.random.seed(3)
    num_trials = 40
    tgt_corr = 0.1
    bs1 = np.random.rand(num_trials)
    # create another betaseries with a target correlation
    bs2 = minimize(lambda x: abs(tgt_corr - pearsonr(bs1, x)[0]),
                   np.random.rand(num_trials)).x

    # two identical beta series
    bs_data = np.array([[[bs1, bs2]]])

    # the nifti image
    bs_img = nib.Nifti1Image(bs_data, np.eye(4))
    bs_img.to_filename(timeseries_file)

    # make atlas nifti
    atlas_data = np.array([[[1, 2]]], dtype=np.int16)
    atlas_img = nib.Nifti1Image(atlas_data, np.eye(4))
    atlas_img.to_filename(atlas_file)

    # make atlas lookup table
    atlas_lut_df = pd.DataFrame({'index': [1, 2], 'regions': ['waffle', 'fries']})
    atlas_lut_df.to_csv(atlas_lut_file, index=False, sep='\t')

    # expected output
    pcorr = np.corrcoef(bs_data.squeeze())
    np.fill_diagonal(pcorr, np.NaN)
    regions = atlas_lut_df['regions'].values
    pcorr_df = pd.DataFrame(pcorr, index=regions, columns=regions)
    expected_zcorr_df = pcorr_df.apply(lambda x: (np.log(1 + x) - np.log(1 - x)) * 0.5)

    # run instance of AtlasConnectivity
    ac = AtlasConnectivity(timeseries_file=timeseries_file,
                           atlas_file=atlas_file,
                           atlas_lut=atlas_lut_file)

    res = ac.run()

    output_zcorr_df = pd.read_csv(res.outputs.correlation_matrix, na_values='n/a', delimiter='\t', index_col=0)

    # clean up files
    shutil.rmtree(base_dir)
    os.remove(res.outputs.correlation_matrix)

    # test equality of the matrices up to 3 decimals
    pd.testing.assert_frame_equal(output_zcorr_df, expected_zcorr_df,
                                  check_less_precise=3)
