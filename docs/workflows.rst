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
        estimator='lss',
        fir_delays=None,
        atlas_img='',
        atlas_lut='',
        bold_metadata_list=[''],
        brainmask_list=[''],
        confound_tsv_list=[''],
        events_tsv_list=[''],
        hrf_model='glover',
        high_pass=0.008,
        name='subtest',
        output_dir='.',
        preproc_img_list=[''],
        selected_confounds=[''],
        smoothing_kernel=None)

The general workflow for a participant models the beta series
for each trial type for each BOLD file associated with the participant.
Then betas within an atlas parcel are averaged together.
This occurs as many times as there are trials for that particular trial type,
resulting in a pseudo-time series (i.e., each point in "time" represents an
occurrence of that trial).
All the pseudo-time series within a trial type are correlated with each other,
resulting in a final correlation (adjacency) matrix for each trial type.

BetaSeries Workflow
-------------------
.. workflow::
    :graph2use: orig
    :simple_form: yes

    from nibetaseries.workflows.model import init_betaseries_wf
    wf = init_betaseries_wf(
        estimator='lss',
        fir_delays=None,
        hrf_model='glover',
        high_pass=0.008,
        smoothing_kernel=0.0,
        selected_confounds=[''])

nistats is used for modeling using the
"least squares separate" (LSS) procedure with the option
for high pass filtering and smoothing.

.. workflow::
    :graph2use: orig
    :simple_form: yes

    from nibetaseries.workflows.model import init_betaseries_wf
    wf = init_betaseries_wf(
        estimator='lss',
        fir_delays=[0, 1, 2, 3, 4],
        hrf_model='fir',
        high_pass=0.008,
        smoothing_kernel=0.0,
        selected_confounds=[''])

Additionally, NiBetaSeries can be used to perform
finite BOLD response- separate (FS) modeling by combining
the LSS estimator with a FIR HRF model and a set of FIR delays.
This model produces a 4D beta series for each condition, at each FIR delay.


Correlation Workflow
--------------------
.. workflow::
        :graph2use: orig
        :simple_form: yes

        from nibetaseries.workflows.analysis import init_correlation_wf
        wf = init_correlation_wf()

The beta series file has signal averaged across trials within a parcel
defined by an atlas parcellation.
After signal extraction has occurred for all parcels, the signals
are all correlated with each other to generate a correlation matrix.
