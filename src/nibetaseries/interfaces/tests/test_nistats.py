''' Testing module for nibetaseries.interfaces.nistats '''
import os
import shutil
import nibabel as nib
import numpy as np
import pandas as pd
from nistats.hemodynamic_models import spm_hrf

from ..nistats import BetaSeries


def test_beta_series():
    # base directory
    base_dir = os.path.join(os.getcwd(), 'tmp')
    os.makedirs(base_dir, exist_ok=True)
    bold_file = os.path.join(base_dir, 'bold.nii.gz')
    mask_file = os.path.join(base_dir, 'mask.nii.gz')
    events_file = os.path.join(base_dir, 'events.tsv')
    confounds_file = os.path.join(base_dir, 'confounds.tsv')
    selected_confounds = ['WhiteMatter', 'CSF']
    # repetition time 2 seconds
    tr = 2
    bold_metadata = {"RepetitionTime": tr, "TaskName": "whodis"}
    # time_points
    tp = 200
    ix = np.arange(tp)
    # the selected hrf model
    hrf_model = 'spm'

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

    # make the confounds tsv
    confounds_df = pd.DataFrame({'WhiteMatter': wm, 'CSF': csf})
    confounds_df.to_csv(confounds_file, index=False, sep='\t')

    # a 4d matrix with 2 identical timeseries
    img_data = np.array([[[voxel_ts, voxel_ts]]])
    # make a nifti image
    img = nib.Nifti1Image(img_data, np.eye(4))
    # save the nifti image
    img.to_filename(bold_file)

    # make the mask file
    bm_data = np.array([[[1, 1]]], dtype=np.int16)
    bm_img = nib.Nifti1Image(bm_data, np.eye(4))
    bm_img.to_filename(mask_file)

    # create event tsv
    onsets = np.multiply(np.where(task_onsets == 1), tr).reshape(5)
    durations = [1] * onsets.size
    trial_types = ['testCond'] * onsets.size

    events_df = pd.DataFrame.from_dict({'onset': onsets, 'duration': durations, 'trial_type': trial_types})
    # reorder columns
    events_df = events_df[['onset', 'duration', 'trial_type']]
    # save the events_df to file
    events_df.to_csv(events_file, index=False, sep='\t')

    beta_series = BetaSeries(bold_file=bold_file,
                             bold_metadata=bold_metadata,
                             mask_file=mask_file,
                             events_file=events_file,
                             confounds_file=confounds_file,
                             selected_confounds=selected_confounds,
                             hrf_model=hrf_model,
                             smoothing_kernel=None,
                             low_pass=None)
    res = beta_series.run()

    assert os.path.isfile(res.outputs.beta_maps)

    # clean files
    if type(res.outputs.beta_maps) is list:
        for f in res.outputs.beta_maps:
            os.remove(f)
    else:
        os.remove(res.outputs.beta_maps)

    shutil.rmtree(base_dir)
