.. _workflows:

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
        bold_metadata_list=[''],
        brainmask_list=[''],
        confound_tsv_list=[''],
        events_tsv_list=[''],
        hrf_model='glover',
        low_pass=None,
        name='subtest',
        output_dir='.',
        preproc_img_list=[''],
        selected_confounds=[''],
        smoothing_kernel=None)

The general workflow for a participant models the betaseries
for each trial type for each bold file associated with the participant.
Then betas within an atlas parcel are averaged together.
This occurs as many times as there are trials for that particular trial type,
resulting in a psuedo-timeseries (e.g. each point in "time" represents an
occurrence of that trial).
All the psuedo time-series within a trial type are correlated with each other,
resulting in a final correlation (adjacency) matrix for each trial type.

BetaSeries Workflow
-------------------
.. workflow::
    :graph2use: orig
    :simple_form: yes

    from nibetaseries.workflows.model import init_betaseries_wf
    wf = init_betaseries_wf(
        hrf_model='glover',
        low_pass=None,
        smoothing_kernel=0.0,
        selected_confounds=[''])

The bold file is optionally temporally filtered (low pass)
and smoothed by nilearn before being passed into nistats for
modelling by least squares separate (LSS).


Correlation Workflow
--------------------
.. workflow::
        :graph2use: orig
        :simple_form: yes

        from nibetaseries.workflows.analysis import init_correlation_wf
        wf = init_correlation_wf()

The betaseries file has signal averaged across trials within a parcel
defined by an atlas parcellation.
After signal extraction has occurred for all parcels, the signals
are all correlated with each other to generate a correlation matrix.
