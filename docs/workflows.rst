=========
Workflows
=========

.. workflow::
    :graph2use: orig
    :simple_form: yes

        from NiBetaSeries.workflows.base import init_nibetaseries_participant_wf
        wf = init_nibetaseries_participant_wf(
            atlas_img='',
            atlas_lut='',
            bids_dir='.',
            confound_column_headers=[''],
            derivatives_pipeline_dir='.',
            exclude_variant_label='',
            high_pass='',
            hrf_model='',
            low_pass='',
            output_dir='',
            run_label='',
            session_label='',
            slice_time_ref='',
            smoothing_kernel='',
            space_label='',
            subject_list=[''],
            task_label='',
            variant_label='',
            work_dir='.')
