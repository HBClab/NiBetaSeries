''' Testing module for nibetaseries.interfaces.nistats '''
import os
import json

import pytest


from ..nistats import (LSSBetaSeries, LSABetaSeries,
                       _lss_events_iterator, _lsa_events_converter,
                       _select_confounds)


@pytest.mark.parametrize("use_nibabel", [(True), (False)])
def test_lss_beta_series(sub_metadata, preproc_file, sub_events,
                         confounds_file, brainmask_file, use_nibabel):
    """Test lss interface with nibabel nifti images
    """
    if use_nibabel:
        import nibabel as nib
        bold_file = nib.load(str(preproc_file))
        mask_file = nib.load(str(brainmask_file))
    else:
        bold_file = str(preproc_file)
        mask_file = str(brainmask_file)

    selected_confounds = ['white_matter', 'csf']
    hrf_model = 'spm'
    with open(str(sub_metadata), 'r') as md:
        bold_metadata = json.load(md)

    beta_series = LSSBetaSeries(bold_file=bold_file,
                                bold_metadata=bold_metadata,
                                mask_file=mask_file,
                                events_file=str(sub_events),
                                confounds_file=str(confounds_file),
                                selected_confounds=selected_confounds,
                                hrf_model=hrf_model,
                                smoothing_kernel=None,
                                high_pass=0.008)
    res = beta_series.run()

    for beta_map in res.outputs.beta_maps:
        assert os.path.isfile(beta_map)
        os.remove(beta_map)


@pytest.mark.parametrize("use_nibabel", [(True), (False)])
def test_fs_beta_series(sub_metadata, preproc_file, sub_events,
                        confounds_file, brainmask_file, use_nibabel):
    if use_nibabel:
        import nibabel as nib
        bold_file = nib.load(str(preproc_file))
        mask_file = nib.load(str(brainmask_file))
    else:
        bold_file = str(preproc_file)
        mask_file = str(brainmask_file)

    selected_confounds = ['white_matter', 'csf']
    hrf_model = 'fir'
    fir_delays = [0, 1, 2, 3, 4]
    with open(str(sub_metadata), 'r') as md:
        bold_metadata = json.load(md)

    beta_series = LSSBetaSeries(bold_file=bold_file,
                                bold_metadata=bold_metadata,
                                mask_file=mask_file,
                                events_file=str(sub_events),
                                confounds_file=str(confounds_file),
                                selected_confounds=selected_confounds,
                                hrf_model=hrf_model,
                                fir_delays=fir_delays,
                                smoothing_kernel=None,
                                high_pass=0.008)
    res = beta_series.run()

    for beta_map in res.outputs.beta_maps:
        assert os.path.isfile(beta_map)
        os.remove(beta_map)


@pytest.mark.parametrize("use_nibabel", [(True), (False)])
def test_lsa_beta_series(sub_metadata, preproc_file, sub_events,
                         confounds_file, brainmask_file, use_nibabel):
    if use_nibabel:
        import nibabel as nib
        bold_file = nib.load(str(preproc_file))
        mask_file = nib.load(str(brainmask_file))
    else:
        bold_file = str(preproc_file)
        mask_file = str(brainmask_file)

    selected_confounds = ['white_matter', 'csf']
    hrf_model = 'spm'
    with open(str(sub_metadata), 'r') as md:
        bold_metadata = json.load(md)

    beta_series = LSABetaSeries(bold_file=bold_file,
                                bold_metadata=bold_metadata,
                                mask_file=mask_file,
                                events_file=str(sub_events),
                                confounds_file=str(confounds_file),
                                selected_confounds=selected_confounds,
                                hrf_model=hrf_model,
                                smoothing_kernel=None,
                                high_pass=0.008)
    res = beta_series.run()

    for beta_map in res.outputs.beta_maps:
        assert os.path.isfile(beta_map)
        os.remove(beta_map)


def test_lss_events_iterator(sub_events):
    # all but the first instance of waffle
    # should be changed to "other"
    t_lst = ['other', 'fry', 'milkshake'] * 5
    t_lst[0] = 'waffle'
    res = _lss_events_iterator(sub_events)
    out_df = list(res)[0][0]
    out_lst = list(out_df['trial_type'])

    assert t_lst == out_lst


def test_lsa_events_converter(sub_events):
    # each instance of waffle, fry, and milkshake
    # should have a different number
    trial_type_lst = ['waffle', 'fry', 'milkshake'] * 5
    number_lst = ['000{}'.format(x) for x in range(1, 6) for y in range(0, 3)]
    t_lst = ['_'.join([trial, num]) for trial, num in zip(trial_type_lst, number_lst)]
    res = _lsa_events_converter(sub_events)
    out_lst = list(res['trial_type'])

    assert t_lst == out_lst


def test_select_confounds_error(confounds_file, tmp_path):
    import pandas as pd
    import numpy as np

    confounds_df = pd.read_csv(str(confounds_file), sep='\t', na_values='n/a')

    confounds_df['white_matter'][0] = np.nan

    conf_file = tmp_path / "confounds.tsv"

    confounds_df.to_csv(str(conf_file), index=False, sep='\t', na_rep='n/a')

    with pytest.raises(ValueError) as val_err:
        _select_confounds(str(conf_file), ['white_matter', 'csf'])

    assert "The selected confounds contain nans" in str(val_err.value)


@pytest.mark.parametrize(
    "selected_confounds,nan_confounds,expanded_confounds",
    [
        (
            ["framewise_displacement"],
            ["framewise_displacement"],
            ["framewise_displacement"],
        ),
        (
            ["white_matter", "motion.*"],
            None,
            [
                "white_matter",
                "motion_outlier00",
                "motion_outlier01",
                "motion_outlier02",
                "motion_outlier03",
                "motion_outlier04"
            ],
        ),
        (
            ["trans.*"],
            [
                "trans_x_derivative1",
                "trans_y_derivative1",
                "trans_z_derivative1",
                "trans_x_derivative1_power2",
                "trans_y_derivative1_power2",
                "trans_z_derivative1_power2",
            ],
            [
                "trans_x",
                "trans_y",
                "trans_z",
                "trans_x_derivative1",
                "trans_y_derivative1",
                "trans_z_derivative1",
                "trans_x_derivative1_power2",
                "trans_y_derivative1_power2",
                "trans_z_derivative1_power2",
            ],
        ),
    ])
def test_select_confounds(confounds_file, selected_confounds, nan_confounds,
                          expanded_confounds):
    import pandas as pd
    import numpy as np

    confounds_df = pd.read_csv(str(confounds_file), sep='\t', na_values='n/a')

    res_df = _select_confounds(str(confounds_file), selected_confounds)

    # check if the correct columns are selected
    assert set(expanded_confounds) == set(res_df.columns)

    # check if nans are being imputed when expected
    if nan_confounds:
        for nan_c in nan_confounds:
            vals = confounds_df[nan_c].values
            expected_result = np.nanmean(vals[vals != 0])
            assert res_df[nan_c][0] == expected_result
