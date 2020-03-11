''' Testing module for nibetaseries.interfaces.nistats '''
import os
import json
import re

import nibabel as nib
from nilearn.image import load_img
import pandas as pd
from nistats import first_level_model
import pytest


from ..nistats import (LSSBetaSeries, LSABetaSeries,
                       _lss_events_iterator, _lsa_events_converter,
                       _select_confounds,
                       _calc_beta_map)


@pytest.mark.parametrize(
    "use_nibabel,hrf_model,return_tstat",
    [
        (True, 'spm', True),
        (False, 'spm + derivative', False),
        (False, 'spm + derivative + dispersion', True)
    ]
)
def test_lss_beta_series(sub_metadata, preproc_file, sub_events,
                         confounds_file, brainmask_file, use_nibabel,
                         hrf_model, return_tstat):
    """Test lss interface with nibabel nifti images
    """
    if use_nibabel:
        bold_file = nib.load(str(preproc_file))
        mask_file = nib.load(str(brainmask_file))
    else:
        bold_file = str(preproc_file)
        mask_file = str(brainmask_file)

    selected_confounds = ['white_matter', 'csf']
    with open(str(sub_metadata), 'r') as md:
        bold_metadata = json.load(md)

    beta_series = LSSBetaSeries(bold_file=bold_file,
                                bold_metadata=bold_metadata,
                                mask_file=mask_file,
                                events_file=str(sub_events),
                                confounds_file=str(confounds_file),
                                selected_confounds=selected_confounds,
                                signal_scaling=0,
                                hrf_model=hrf_model,
                                return_tstat=return_tstat,
                                smoothing_kernel=None,
                                high_pass=0.008)
    res = beta_series.run()

    events_df = pd.read_csv(str(sub_events), sep='\t')
    trial_types = events_df['trial_type'].unique()

    # check for the correct number of beta maps
    assert len(trial_types) == len(res.outputs.beta_maps)

    input_img_dim = load_img(bold_file).shape[:3]
    for beta_map in res.outputs.beta_maps:
        trial_type = re.search(r'desc-([A-Za-z0-9]+)_', beta_map).groups()[0]
        # check if correct trial type is made
        assert trial_type in trial_types
        # check if output is actually a file
        assert os.path.isfile(beta_map)
        # check if image dimensions are correct
        assert input_img_dim == load_img(beta_map).shape[:3]
        # check if number of trials are correct
        assert (events_df['trial_type'] == trial_type).sum() == load_img(beta_map).shape[-1]
        # clean up
        os.remove(beta_map)

    # check residual image
    assert load_img(bold_file).shape == load_img(res.outputs.residual).shape
    os.remove(res.outputs.residual)


@pytest.mark.parametrize("use_nibabel", [(True), (False)])
def test_fs_beta_series(sub_metadata, preproc_file, sub_events,
                        confounds_file, brainmask_file, use_nibabel):
    if use_nibabel:
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
                                signal_scaling=0,
                                hrf_model=hrf_model,
                                fir_delays=fir_delays,
                                return_tstat=False,
                                smoothing_kernel=None,
                                high_pass=0.008)
    res = beta_series.run()

    events_df = pd.read_csv(str(sub_events), sep='\t')
    trial_types = events_df['trial_type'].unique()

    # check for the correct number of beta maps
    assert len(trial_types) * len(fir_delays) == len(res.outputs.beta_maps)

    input_img_dim = load_img(bold_file).shape[:3]
    for beta_map in res.outputs.beta_maps:
        trial_type = re.search(r'desc-([A-Za-z0-9]+)Delay[0-9]+Vol_', beta_map).groups()[0]
        # check if correct trial type is made
        assert trial_type in trial_types
        # check if output is actually a file
        assert os.path.isfile(beta_map)
        # check if image dimensions are correct
        assert input_img_dim == load_img(beta_map).shape[:3]
        # check if number of trials are correct
        assert (events_df['trial_type'] == trial_type).sum() == load_img(beta_map).shape[-1]
        # clean up
        os.remove(beta_map)

    # check residual image
    assert load_img(bold_file).shape == load_img(res.outputs.residual).shape
    os.remove(res.outputs.residual)


@pytest.mark.parametrize(
    "use_nibabel,hrf_model,return_tstat",
    [
        (True, 'spm', True),
        (False, 'spm + derivative', False),
        (False, 'spm + derivative + dispersion', True)
    ]
)
def test_lsa_beta_series(sub_metadata, preproc_file, sub_events,
                         confounds_file, brainmask_file, use_nibabel,
                         hrf_model, return_tstat):
    if use_nibabel:
        bold_file = nib.load(str(preproc_file))
        mask_file = nib.load(str(brainmask_file))
    else:
        bold_file = str(preproc_file)
        mask_file = str(brainmask_file)

    selected_confounds = ['white_matter', 'csf']

    with open(str(sub_metadata), 'r') as md:
        bold_metadata = json.load(md)

    beta_series = LSABetaSeries(bold_file=bold_file,
                                bold_metadata=bold_metadata,
                                mask_file=mask_file,
                                events_file=str(sub_events),
                                confounds_file=str(confounds_file),
                                signal_scaling=0,
                                selected_confounds=selected_confounds,
                                hrf_model=hrf_model,
                                return_tstat=return_tstat,
                                smoothing_kernel=None,
                                high_pass=0.008)
    res = beta_series.run()

    events_df = pd.read_csv(str(sub_events), sep='\t')
    trial_types = events_df['trial_type'].unique()

    # check for the correct number of beta maps
    assert len(trial_types) == len(res.outputs.beta_maps)

    input_img_dim = load_img(bold_file).shape[:3]
    for beta_map in res.outputs.beta_maps:
        trial_type = re.search(r'desc-([A-Za-z0-9]+)_', beta_map).groups()[0]
        # check if correct trial type is made
        assert trial_type in trial_types
        # check if output is actually a file
        assert os.path.isfile(beta_map)
        # check if image dimensions are correct
        assert input_img_dim == load_img(beta_map).shape[:3]
        # check if number of trials are correct
        assert (events_df['trial_type'] == trial_type).sum() == load_img(beta_map).shape[-1]
        # clean up
        os.remove(beta_map)

    # check residual image
    assert load_img(bold_file).shape == load_img(res.outputs.residual).shape
    os.remove(res.outputs.residual)


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


@pytest.mark.parametrize(
    "hrf_model,return_tstat",
    [
        ("glover", True),
        ("glover + derivative", False),
        ("glover + derivative + dispersion", True),
    ],
)
def test_calc_beta_map(sub_metadata, preproc_file, sub_events,
                       confounds_file, brainmask_file, hrf_model,
                       return_tstat):

    model = first_level_model.FirstLevelModel(
            t_r=2,
            slice_time_ref=0,
            hrf_model=hrf_model,
            mask=str(brainmask_file),
            smoothing_fwhm=0,
            signal_scaling=False,
            high_pass=0.008,
            drift_model='cosine',
            verbose=1,
            minimize_memory=False,
        )

    lsa_df = _lsa_events_converter(str(sub_events))

    model.fit(str(preproc_file), events=lsa_df)

    i_trial = lsa_df.index[0]
    t_name = lsa_df.loc[i_trial, 'trial_type']

    beta_map = _calc_beta_map(model, t_name, hrf_model, return_tstat)

    assert beta_map.shape == nib.load(str(brainmask_file)).shape
