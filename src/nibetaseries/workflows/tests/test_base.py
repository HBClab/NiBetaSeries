import os.path as op
from nipype import config as ncfg

from ..base import init_nibetaseries_participant_wf


def test_init_nibetaseries_participant_wf(
        bids_dir, deriv_dir, sub_fmriprep, sub_metadata, bold_file, preproc_file,
        sub_events, confounds_file, brainmask_file, atlas_file, atlas_lut,
        ):

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
        atlas_img=str(atlas_file),
        atlas_lut=str(atlas_lut),
        bids_dir=str(bids_dir),
        derivatives_pipeline_dir=deriv_dir,
        exclude_description_label=None,
        hrf_model='spm',
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
