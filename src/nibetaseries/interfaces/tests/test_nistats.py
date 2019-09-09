''' Testing module for nibetaseries.interfaces.nistats '''
import os
import json

from ..nistats import BetaSeries


def test_beta_series(sub_metadata, preproc_file, sub_events,
                     confounds_file, brainmask_file):
    selected_confounds = ['WhiteMatter', 'CSF']
    hrf_model = 'spm'
    with open(str(sub_metadata), 'r') as md:
        bold_metadata = json.load(md)

    beta_series = BetaSeries(bold_file=str(preproc_file),
                             bold_metadata=bold_metadata,
                             mask_file=str(brainmask_file),
                             events_file=str(sub_events),
                             confounds_file=str(confounds_file),
                             selected_confounds=selected_confounds,
                             hrf_model=hrf_model,
                             smoothing_kernel=None,
                             high_pass=None)
    res = beta_series.run()

    assert os.path.isfile(res.outputs.beta_maps)

    os.remove(res.outputs.beta_maps)
