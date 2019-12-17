import json

from ..utils import collect_data, BIDSLayoutIndexerPatch
from bids import BIDSLayout


def test_collect_data(bids_dir, deriv_dir, sub_fmriprep,
                      sub_metadata, bold_file, preproc_file,
                      sub_events, confounds_file, brainmask_file,
                      sub_rest_metadata, rest_file):

    with open(str(sub_metadata), "r") as sm:
        metadata = json.load(sm)

    expected_out = {
            'brainmask': str(brainmask_file),
            'confounds': str(confounds_file),
            'events': str(sub_events),
            'preproc': str(preproc_file),
            'metadata': metadata
        }
    layout = BIDSLayout(
        str(bids_dir),
        derivatives=str(deriv_dir),
        index_metadata=False)

    # only index bold file metadata
    indexer = BIDSLayoutIndexerPatch(layout)
    metadata_filter = {
        'extension': ['nii', 'nii.gz', 'json'],
        'suffix': 'bold',
    }
    indexer.index_metadata(**metadata_filter)

    subject_label = '01'
    session = 'pre'
    task = 'waffles'
    run = '1'
    space = 'MNI152NLin2009cAsym'
    desc = 'preproc'
    subject_data = collect_data(layout, subject_label, ses=session,
                                task=task, run=run, space=space,
                                description=desc)[0]

    assert subject_data == expected_out
