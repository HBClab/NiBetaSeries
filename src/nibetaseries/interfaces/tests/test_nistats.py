''' Testing module for nibetaseries.interfaces.nistats '''
import os
import json

from ..nistats import LSSBetaSeries, LSABetaSeries
from ..nistats import _lss_events_iterator, _lsa_events_converter


def test_lss_beta_series(sub_metadata, preproc_file, sub_events,
                         confounds_file, brainmask_file):
    selected_confounds = ['WhiteMatter', 'CSF']
    hrf_model = 'spm'
    with open(str(sub_metadata), 'r') as md:
        bold_metadata = json.load(md)

    beta_series = LSSBetaSeries(bold_file=str(preproc_file),
                                bold_metadata=bold_metadata,
                                mask_file=str(brainmask_file),
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


def test_lsa_beta_series(sub_metadata, preproc_file, sub_events,
                         confounds_file, brainmask_file):
    selected_confounds = ['WhiteMatter', 'CSF']
    hrf_model = 'spm'
    with open(str(sub_metadata), 'r') as md:
        bold_metadata = json.load(md)

    beta_series = LSABetaSeries(bold_file=str(preproc_file),
                                bold_metadata=bold_metadata,
                                mask_file=str(brainmask_file),
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
