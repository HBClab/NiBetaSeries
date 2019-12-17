import os.path as op
from nipype import config as ncfg
import pytest

from ..base import init_nibetaseries_participant_wf


@pytest.mark.parametrize("estimator,fir_delays,hrf_model",
                         [('lsa', None, 'spm'),
                          ('lss', None, 'spm'),
                          ('lss', [0, 1, 2, 3, 4], 'fir')])
def test_valid_init_nibetaseries_participant_wf(
        bids_dir, deriv_dir, sub_fmriprep, sub_metadata, bold_file, preproc_file,
        sub_events, confounds_file, brainmask_file, atlas_file, atlas_lut, bids_db_file,
        estimator, fir_delays, hrf_model):

    output_dir = op.join(str(bids_dir), 'derivatives', 'atlasCorr')
    work_dir = op.join(str(bids_dir), 'derivatives', 'work')
    deriv_dir = op.join(str(bids_dir), 'derivatives', 'fmriprep')
    ncfg.update_config({
        'logging': {'log_directory': work_dir,
                    'log_to_file': True},
        'execution': {'crashdump_dir': work_dir,
                      'crashfile_format': 'txt',
                      'parameterize_dirs': False},
    })

    test_np_wf = init_nibetaseries_participant_wf(
        estimator=estimator,
        fir_delays=fir_delays,
        atlas_img=str(atlas_file),
        atlas_lut=str(atlas_lut),
        bids_dir=str(bids_dir),
        database_path=bids_db_file,
        derivatives_pipeline_dir=deriv_dir,
        exclude_description_label=None,
        hrf_model=hrf_model,
        high_pass=0.008,
        output_dir=output_dir,
        run_label=None,
        selected_confounds=['WhiteMatter', 'CSF'],
        session_label=None,
        smoothing_kernel=None,
        space_label=None,
        subject_list=["01"],
        task_label=None,
        description_label=None,
        work_dir=work_dir)

    assert test_np_wf.run()


@pytest.mark.parametrize("session_label,task_label,run_label,space_label,description_label",
                         [('these', 'are', 'not', 'valid', 'filters'),
                          (123, 123, 123, 123, 123)])
def test_filters_init_nibetaseries_participant_wf(
        bids_dir, deriv_dir, sub_fmriprep, sub_metadata, bold_file, preproc_file,
        sub_events, confounds_file, brainmask_file,
        session_label, task_label, run_label, space_label, description_label):

    output_dir = op.join(str(bids_dir), 'derivatives', 'atlasCorr')
    work_dir = op.join(str(bids_dir), 'derivatives', 'work')
    deriv_dir = op.join(str(bids_dir), 'derivatives', 'fmriprep')
    ncfg.update_config({
        'logging': {'log_directory': work_dir,
                    'log_to_file': True},
        'execution': {'crashdump_dir': work_dir,
                      'crashfile_format': 'txt',
                      'parameterize_dirs': False},
    })
    with pytest.raises(ValueError) as val_err:
        init_nibetaseries_participant_wf(
            estimator='lsa',
            fir_delays=None,
            atlas_img=None,
            atlas_lut=None,
            bids_dir=str(bids_dir),
            database_path=None,
            derivatives_pipeline_dir=deriv_dir,
            exclude_description_label=None,
            hrf_model='spm',
            high_pass=0.008,
            output_dir=output_dir,
            run_label=run_label,
            selected_confounds=['WhiteMatter', 'CSF'],
            session_label=session_label,
            smoothing_kernel=None,
            space_label=space_label,
            subject_list=["01"],
            task_label=task_label,
            description_label=description_label,
            work_dir=work_dir)

    assert "could not find preprocessed outputs:" in str(val_err.value)
