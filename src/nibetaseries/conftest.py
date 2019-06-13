import nibabel as nib
import numpy as np
import pandas as pd
import json
import warnings
from nistats.hemodynamic_models import spm_hrf
from scipy.stats import pearsonr
from scipy.optimize import minimize
import pytest

bids_prefix = "sub-01_ses-pre_task-waffles"
deriv_prefix = bids_prefix + "_space-MNI152NLin2009cAsym"


@pytest.fixture(scope='session')
def bids_dir(tmpdir_factory):
    return tmpdir_factory.mktemp('bids')


@pytest.fixture(scope='session')
def sub_bids(bids_dir):
    return bids_dir.ensure('sub-01',
                           'ses-pre',
                           'func',
                           dir=True)


@pytest.fixture(scope='session')
def fmriprep_dir(bids_dir):
    return bids_dir.ensure('derivatives',
                           'fmriprep',
                           'sub-01',
                           'ses-pre',
                           'func',
                           dir=True)


@pytest.fixture(scope='session')
def sub_metadata(sub_bids, bids_prefix=bids_prefix):
    sub_json = sub_bids.join(bids_prefix + "_bold.json")
    tr = 2
    bold_metadata = {"RepetitionTime": tr, "TaskName": "waffles"}

    with open(str(sub_json), 'w') as md:
        json.dump(bold_metadata, md)

    return sub_json


@pytest.fixture(scope='session')
def bold_file(sub_bids, bids_prefix=bids_prefix):
    return sub_bids.ensure(bids_prefix + "_bold.nii.gz")


@pytest.fixture(scope='session')
def preproc_file(fmriprep_dir, sub_metadata, deriv_prefix=deriv_prefix):
    preproc_file = fmriprep_dir.join(deriv_prefix + "_bold_preproc.nii.gz")
    with open(str(sub_metadata), 'r') as md:
        bold_metadata = json.load(md)
    tr = bold_metadata["RepetitionTime"]
    # time_points
    tp = 200
    ix = np.arange(tp)
    # create voxel timeseries
    task_onsets = np.zeros(tp)
    # add activations at every 40 time points
    task_onsets[0::40] = 1
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
    img.to_filename(str(preproc_file))

    return preproc_file


@pytest.fixture(scope='session')
def sub_events(sub_bids, sub_metadata, preproc_file, bids_prefix=bids_prefix):
    events_file = sub_bids.join(bids_prefix + "_events.tsv")
    # read in subject metadata to get the TR
    with open(str(sub_metadata), 'r') as md:
        bold_metadata = json.load(md)
    tr = bold_metadata["RepetitionTime"]
    # time_points
    tp = nib.load(str(preproc_file)).shape[-1]
    # create voxel timeseries
    task_onsets = np.zeros(tp)
    # add activations at every 40 time points
    task_onsets[0::40] = 1
    # create event tsv
    onsets = np.multiply(np.where(task_onsets == 1), tr).reshape(5)
    durations = [1] * onsets.size
    trial_types = ['testCond'] * onsets.size
    events_df = pd.DataFrame.from_dict({'onset': onsets,
                                        'duration': durations,
                                        'trial_type': trial_types})
    # reorder columns
    events_df = events_df[['onset', 'duration', 'trial_type']]
    # save the events_df to file
    events_df.to_csv(str(events_file), index=False, sep='\t')
    return events_file


@pytest.fixture(scope='session')
def confounds_file(fmriprep_dir, preproc_file, bids_prefix=bids_prefix):
    confounds_file = fmriprep_dir.join(bids_prefix + "_bold_confounds.tsv")
    tp = nib.load(str(preproc_file)).shape[-1]
    ix = np.arange(tp)
    # csf
    csf = np.cos(2*np.pi*ix*(50/tp)) * 0.1
    # white matter
    wm = np.sin(2*np.pi*ix*(22/tp)) * 0.1
    confounds_df = pd.DataFrame({'WhiteMatter': wm, 'CSF': csf})
    confounds_df.to_csv(str(confounds_file), index=False, sep='\t')
    return confounds_file


@pytest.fixture(scope='session')
def brainmask_file(fmriprep_dir, deriv_prefix=deriv_prefix):
    brainmask_file = fmriprep_dir.join(deriv_prefix + "_bold_brainmask.nii.gz")
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
                                 'regions': ['waffle', 'fries']})
    atlas_lut_df.to_csv(str(atlas_lut), index=False, sep='\t')

    return atlas_lut


@pytest.fixture(scope='session')
def betaseries_file(tmpdir_factory):
    bfile = tmpdir_factory.mktemp("beta").join("betaseries_trialtype-testCond.nii.gz")
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

# enforce matplotlib settings
@pytest.fixture(scope='session')
def matplotlib_config():
    """Configure matplotlib for viz tests."""
    import matplotlib
    # "force" should not really be necessary but should not hurt
    kwargs = dict()
    with warnings.catch_warnings(record=True):  # ignore warning
        matplotlib.use('agg', force=True, **kwargs)  # don't pop up windows
    import matplotlib.pyplot as plt
    assert plt.get_backend() == 'agg'
