import os
from nipype import config as ncfg


from ..base import init_nibetaseries_participant_wf


def test_init_nibetaseries_participant_wf(bids_dir, atlas_file, atlas_lut, bold_file):
    output_dir = os.path.join(str(bids_dir), 'derivatives', 'atlasCorr')
    work_dir = os.path.join(str(bids_dir), 'derivatives', 'work')
    deriv_dir = os.path.join(str(bids_dir), 'derivatives', 'fmriprep')
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
        exclude_variant_label=None,
        hrf_model='spm',
        low_pass=None,
        output_dir=output_dir,
        run_label=None,
        selected_confounds=['WhiteMatter', 'CSF'],
        session_label=None,
        smoothing_kernel=None,
        space_label=None,
        subject_list=["01"],
        task_label=None,
        variant_label=None,
        work_dir=work_dir)

    assert test_np_wf.run()
