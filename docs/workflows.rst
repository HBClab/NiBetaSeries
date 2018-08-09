=========
Workflows
=========

Participant Workflow
--------------------
.. workflow::
    :graph2use: orig
    :simple_form: yes

    from nibetaseries.workflows.base import init_single_subject_wf
    wf = init_single_subject_wf(
        atlas_img='',
        atlas_lut='',
        brainmask_list=[''],
        confound_tsv_list=[''],
        events_tsv_list=[''],
        high_pass='',
        hrf_model='',
        low_pass='',
        name='subtest',
        output_dir='.',
        preproc_img_list=[''],
        selected_confounds=[''],
        smoothing_kernel=0.0)

The general workflow for a participant models the betaseries for each trial type
for each bold file associated with the participant.
Then betas within a region of interest based off a parcellation are averaged together.
This occurs as many times as there are trials for that particular trial type, resulting
in a psuedo-timeseries (e.g. each point in "time" represents an occurrence of
that trial).
All the psuedo time-series within a trial type are correlated with each other,
resulting in a final correlation (adjacency) matrix.

BetaSeries Workflow
-------------------
.. workflow::
    :graph2use: orig
    :simple_form: yes

    from nibetaseries.workflows.model import init_betaseries_wf
    wf = init_betaseries_wf(
        hrf_model='glover',
        low_pass=None,
        high_pass=None,
        smoothing_kernel=0.0,
        selected_confounds=[''])

The bold file is temporally filtered by nilearn (high pass and/or low pass) before being
passed into nistats for modelling by least squares separate.


Correlation Workflow
--------------------
.. workflow::
        :graph2use: orig
        :simple_form: yes

        from nibetaseries.workflows.analysis import init_correlation_wf
        wf = init_correlation_wf()

The betaseries file has signal averaged across trials within a region defined by
an atlas parcellation.
After signal extraction has occurred for all regions, the signals are all correlated
with each other to generate a correlation matrix.
