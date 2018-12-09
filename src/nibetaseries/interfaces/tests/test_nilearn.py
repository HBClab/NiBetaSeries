''' Testing module for nibetaseries.interfaces.nilearn '''
import nibabel as nib
import numpy as np
import pandas as pd
import os

from ..nilearn import AtlasConnectivity


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
