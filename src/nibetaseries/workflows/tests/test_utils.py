import json

from ..utils import collect_data
from bids import BIDSLayout


def test_collect_data(bids_dir, deriv_dir, sub_fmriprep,
                      sub_metadata, bold_file, preproc_file,
                      sub_events, confounds_file, brainmask_file):

    with open(sub_metadata, "r") as sm:
        metadata = json.load(sm)

    expected_out = {
            'brainmask': str(brainmask_file),
            'confounds': str(confounds_file),
            'events': str(sub_events),
            'preproc': str(preproc_file),
            'metadata': metadata
        }
    layout = BIDSLayout(str(bids_dir), derivatives=str(deriv_dir))

    subject_label = '01'

    subject_data = collect_data(layout, subject_label)[0]

    assert subject_data == expected_out
