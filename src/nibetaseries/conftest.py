import nibabel as nib
import numpy as np
import pandas as pd
import json
from nistats.hemodynamic_models import spm_hrf
from scipy.stats import pearsonr
from scipy.optimize import minimize
import pytest
from bids.layout.writing import build_path
import pkg_resources
import os.path as op

# read in filename patterns to create valid filenames
bids_cfg = pkg_resources.resource_string("nibetaseries", op.join("data", "bids.json"))
bids_patterns = json.loads(bids_cfg.decode('utf-8'))['default_path_patterns']

deriv_cfg = pkg_resources.resource_string("nibetaseries", op.join("data", "derivatives.json"))
deriv_patterns = json.loads(deriv_cfg.decode('utf-8'))['fmriprep_path_patterns']

# building blocks for generating valid file names
subject_entities = {
    "subject": "01",
    "session": "pre",
}

bids_bold_entities = {
    **subject_entities,
    "datatype": "func",
    "task": "waffles",
    "suffix": "bold",
    "run": 1,
    "extension": "nii.gz",
}
bids_bold_fname = build_path(bids_bold_entities, bids_patterns)

bids_json_entities = {
    **bids_bold_entities,
    "extension": "json",
}
bids_json_fname = build_path(bids_json_entities, bids_patterns)

bids_rest_entities = {
    **bids_bold_entities,
    "task": "rest",
}
bids_rest_fname = build_path(bids_rest_entities, bids_patterns)

bids_rest_json_entities = {
    **bids_rest_entities,
    "extension": "json",
}
bids_rest_json_fname = build_path(bids_rest_json_entities, bids_patterns)

bids_events_entities = {
    **bids_bold_entities,
    "suffix": "events",
    "extension": "tsv",
}
bids_events_fname = build_path(bids_events_entities, bids_patterns)

deriv_bold_entities = {
    **bids_bold_entities,
    "space": "MNI152NLin2009cAsym",
    "description": "preproc",
}
deriv_bold_fname = build_path(deriv_bold_entities, deriv_patterns)

deriv_mask_entities = {
    **deriv_bold_entities,
    "suffix": "mask",
    "description": "brain",
}
deriv_mask_fname = build_path(deriv_mask_entities, deriv_patterns)

deriv_regressor_entities = {
    **subject_entities,
    "datatype": "func",
    "task": "waffles",
    "run": 1,
    "description": "confounds",
    "suffix": "regressors",
    "extension": "tsv",
}
deriv_regressor_fname = build_path(deriv_regressor_entities, deriv_patterns)

deriv_betaseries_entities = {
    **deriv_bold_entities,
    "suffix": "betaseries",
    "description": "testCond",
}
deriv_betaseries_fname = build_path(deriv_betaseries_entities, deriv_patterns)


@pytest.fixture(scope='session')
def bids_dir(tmpdir_factory):
    bids_dir = tmpdir_factory.mktemp('bids')

    dataset_json = bids_dir.ensure("dataset_description.json")

    dataset_dict = {
        "Name": "waffles and fries",
        "BIDSVersion": "1.1.1",
    }

    with open(str(dataset_json), 'w') as dj:
        json.dump(dataset_dict, dj)

    return bids_dir


@pytest.fixture(scope='session')
def sub_bids(bids_dir, example_file=bids_bold_fname):
    sub_dir = op.dirname(example_file)

    return bids_dir.ensure(sub_dir,
                           dir=True)


@pytest.fixture(scope='session')
def deriv_dir(bids_dir):
    deriv_dir = bids_dir.ensure('derivatives',
                                'fmriprep',
                                dir=True)

    dataset_json = deriv_dir.ensure("dataset_description.json")

    dataset_dict = {
        "Name": "fMRIPrep - fMRI PREProcessing workflow",
        "BIDSVersion": "1.1.1",
        "PipelineDescription": {
            "Name": "fMRIPrep",
            "Version": "1.5.0rc2+14.gf673eaf5",
            "CodeURL": "https://github.com/poldracklab/fmriprep/archive/1.5.0.tar.gz"
        },
        "CodeURL": "https://github.com/poldracklab/fmriprep",
        "HowToAcknowledge": "Please cite our paper (https://doi.org/10.1038/s41592-018-0235-4)",
        "SourceDatasetsURLs": [
            "https://doi.org/"
        ],
        "License": ""
    }

    with open(str(dataset_json), 'w') as dj:
        json.dump(dataset_dict, dj)

    return deriv_dir


@pytest.fixture(scope='session')
def sub_fmriprep(deriv_dir, example_file=deriv_bold_fname):
    sub_dir = op.dirname(example_file)

    return deriv_dir.ensure(sub_dir,
                            dir=True)


@pytest.fixture(scope='session')
def sub_metadata(bids_dir, bids_json_fname=bids_json_fname):
    sub_json = bids_dir.ensure(bids_json_fname)
    tr = 2
    bold_metadata = {"RepetitionTime": tr, "TaskName": "waffles"}

    with open(str(sub_json), 'w') as md:
        json.dump(bold_metadata, md)

    return sub_json


@pytest.fixture(scope='session')
def sub_top_metadata(bids_dir, bids_json_fname='task-waffles_bold.json'):
    sub_json = bids_dir.ensure(bids_json_fname)
    tr = 2
    bold_metadata = {"RepetitionTime": tr, "TaskName": "waffles"}

    with open(str(sub_json), 'w') as md:
        json.dump(bold_metadata, md)

    return sub_json


@pytest.fixture(scope='session')
def sub_rest_metadata(bids_dir, bids_json_fname=bids_rest_json_fname):
    sub_json = bids_dir.ensure(bids_rest_json_fname)
    tr = 2
    bold_metadata = {"RepetitionTime": tr, "TaskName": "rest"}

    with open(str(sub_json), 'w') as md:
        json.dump(bold_metadata, md)

    return sub_json


@pytest.fixture(scope='session')
def bold_file(bids_dir, bids_bold_fname=bids_bold_fname):
    return bids_dir.ensure(bids_bold_fname)


@pytest.fixture(scope='session')
def rest_file(bids_dir, bids_rest_fname=bids_rest_fname):
    return bids_dir.ensure(bids_rest_fname)


@pytest.fixture(scope='session')
def preproc_file(deriv_dir, sub_metadata, deriv_bold_fname=deriv_bold_fname):
    deriv_bold = deriv_dir.ensure(deriv_bold_fname)
    with open(str(sub_metadata), 'r') as md:
        bold_metadata = json.load(md)
    tr = bold_metadata["RepetitionTime"]
    # time_points
    tp = 200
    ix = np.arange(tp)
    # create voxel timeseries
    task_onsets = np.zeros(tp)
    # add activations at every 40 time points
    # waffles
    task_onsets[0::40] = 1
    # fries
    task_onsets[3::40] = 1.5
    # milkshakes
    task_onsets[6::40] = 2
    signal = np.convolve(task_onsets, spm_hrf(tr))[0:len(task_onsets)]
    # csf
    csf = np.cos(2*np.pi*ix*(50/tp)) * 0.1
    # white matter
    wm = np.sin(2*np.pi*ix*(22/tp)) * 0.1
    # voxel time series (signal and noise)
    voxel_ts = signal + csf + wm
    # a 4d matrix with 2 identical timeseries
    img_data = np.array([[[voxel_ts, voxel_ts]]])
    # make a nifti image
    img = nib.Nifti1Image(img_data, np.eye(4))
    # save the nifti image
    img.to_filename(str(deriv_bold))

    return deriv_bold


@pytest.fixture(scope='session')
def sub_events(bids_dir, sub_metadata, preproc_file,
               bids_events_fname=bids_events_fname):
    events_file = bids_dir.ensure(bids_events_fname)
    # read in subject metadata to get the TR
    with open(str(sub_metadata), 'r') as md:
        bold_metadata = json.load(md)
    tr = bold_metadata["RepetitionTime"]
    # time_points
    tp = nib.load(str(preproc_file)).shape[-1]
    # create voxel timeseries
    task_onsets = np.zeros(tp)
    # add waffles at every 40 time points
    task_onsets[0::40] = 1
    # add fries at every 40 time points starting at 3
    task_onsets[3::40] = 1
    # add milkshakes at every 40 time points starting at 6
    task_onsets[6::40] = 1
    # create event tsv
    num_trials = np.where(task_onsets == 1)[0].shape[0]
    onsets = np.multiply(np.where(task_onsets == 1), tr).reshape(num_trials)
    durations = [1] * num_trials
    num_conds = 3
    trial_types = ['waffle', 'fry', 'milkshake'] * int((num_trials / num_conds))
    events_df = pd.DataFrame.from_dict({'onset': onsets,
                                        'duration': durations,
                                        'trial_type': trial_types})
    # reorder columns
    events_df = events_df[['onset', 'duration', 'trial_type']]
    # save the events_df to file
    events_df.to_csv(str(events_file), index=False, sep='\t')
    return events_file


@pytest.fixture(scope='session')
def confounds_file(deriv_dir, preproc_file,
                   deriv_regressor_fname=deriv_regressor_fname):
    confounds_file = deriv_dir.ensure(deriv_regressor_fname)
    confound_dict = {}
    tp = nib.load(str(preproc_file)).shape[-1]
    ix = np.arange(tp)
    # csf
    confound_dict['csf'] = np.cos(2*np.pi*ix*(50/tp)) * 0.1
    # white matter
    confound_dict['white_matter'] = np.sin(2*np.pi*ix*(22/tp)) * 0.1
    # framewise_displacement
    confound_dict['framewise_displacement'] = np.random.random_sample(tp)
    confound_dict['framewise_displacement'][0] = np.nan
    # motion outliers
    for motion_outlier in range(0, 5):
        mo_name = 'motion_outlier0{}'.format(motion_outlier)
        confound_dict[mo_name] = np.zeros(tp)
        confound_dict[mo_name][motion_outlier] = 1
    # derivatives
    derive1 = [
        'csf_derivative1',
        'csf_derivative1_power2',
        'global_signal_derivative1_power2',
        'trans_x_derivative1',
        'trans_y_derivative1',
        'trans_z_derivative1',
        'trans_x_derivative1_power2',
        'trans_y_derivative1_power2',
        'trans_z_derivative1_power2',
    ]
    for d in derive1:
        confound_dict[d] = np.random.random_sample(tp)
        confound_dict[d][0] = np.nan

    # transformations
    for dir in ["trans_x", "trans_y", "trans_z"]:
        confound_dict[dir] = np.random.random_sample(tp)

    confounds_df = pd.DataFrame(confound_dict)
    confounds_df.to_csv(str(confounds_file), index=False, sep='\t', na_rep='n/a')
    return confounds_file


@pytest.fixture(scope='session')
def brainmask_file(deriv_dir,
                   deriv_mask_fname=deriv_mask_fname):
    brainmask_file = deriv_dir.ensure(deriv_mask_fname)
    bm_data = np.array([[[1, 1]]], dtype=np.int16)
    bm_img = nib.Nifti1Image(bm_data, np.eye(4))
    bm_img.to_filename(str(brainmask_file))
    return brainmask_file


@pytest.fixture(scope='session')
def atlas_file(tmpdir_factory):
    atlas_file = tmpdir_factory.mktemp("atlas").join("atlas.nii.gz")
    atlas_data = np.array([[[1, 2]]], dtype=np.int16)
    atlas_img = nib.Nifti1Image(atlas_data, np.eye(4))
    atlas_img.to_filename(str(atlas_file))

    return atlas_file


@pytest.fixture(scope='session')
def atlas_lut(tmpdir_factory):
    atlas_lut = tmpdir_factory.mktemp("lut").join("lut.tsv")
    # make atlas lookup table
    atlas_lut_df = pd.DataFrame({'index': [1, 2],
                                 'regions': ['mouth', 'stomach']})
    atlas_lut_df.to_csv(str(atlas_lut), index=False, sep='\t')

    return atlas_lut


@pytest.fixture(scope='session')
def bids_db_file(
        bids_dir, deriv_dir, sub_fmriprep, sub_metadata, bold_file, preproc_file,
        sub_events, confounds_file, brainmask_file, atlas_file, atlas_lut,
        ):
    from bids import BIDSLayout
    from .workflows.utils import BIDSLayoutIndexerPatch

    db_file = bids_dir / ".dbcache"

    layout = BIDSLayout(
        str(bids_dir),
        derivatives=str(deriv_dir),
        index_metadata=False,
        database_file=str(db_file),
        reset_database=True)

    # only index bold file metadata
    indexer = BIDSLayoutIndexerPatch(layout)
    metadata_filter = {
        'extension': ['nii', 'nii.gz', 'json'],
        'suffix': 'bold',
    }
    indexer.index_metadata(**metadata_filter)

    return db_file


@pytest.fixture(scope='session')
def betaseries_file(tmpdir_factory,
                    deriv_betaseries_fname=deriv_betaseries_fname):
    bfile = tmpdir_factory.mktemp("beta").ensure(deriv_betaseries_fname)
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
    bs_img.to_filename(str(bfile))

    return bfile
