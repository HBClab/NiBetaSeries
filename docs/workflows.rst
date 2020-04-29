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
        atlas_img='img.nii.gz',
        atlas_lut='lut.tsv',
        bold_metadata_list=[''],
        brainmask_list=[''],
        confound_tsv_list=[''],
        events_tsv_list=[''],
        hrf_model='glover',
        high_pass=0.008,
        name='subtest',
        norm_betas=False,
        output_dir='.',
        preproc_img_list=[''],
        return_residuals=False,
        selected_confounds=[''],
        signal_scaling=0,
        smoothing_kernel=None)

The general workflow for a participant models the beta series
for each trial type for each BOLD file associated with the participants.
Those beta series images are output for the user.
if ``atlas_img`` and ``atlas_lut`` are defined,
then betas within an atlas parcel are averaged together.
All the parcels are correlated with each other for each trial type,
resulting in a final correlation (adjacency) matrix for each trial type.

BetaSeries Workflow
-------------------

Least Squares- Separate (LSS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. workflow::
    :graph2use: flat
    :simple_form: no
    :include-source: yes

    from nibetaseries.workflows.model import init_betaseries_wf
    wf = init_betaseries_wf(
        estimator='lss',
        fir_delays=None,
        hrf_model='glover',
        high_pass=0.008,
        norm_betas=False,
        smoothing_kernel=0.0,
        signal_scaling=0,
        selected_confounds=[''])

nistats is used for modeling using the
"least squares- separate" (LSS) procedure with the option
for high pass filtering and smoothing.

Finite BOLD Response- Separate (FS)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. workflow::
    :graph2use: flat
    :simple_form: no
    :include-source: yes

    from nibetaseries.workflows.model import init_betaseries_wf
    wf = init_betaseries_wf(
        estimator='lss',
        fir_delays=[0, 1, 2, 3, 4],
        hrf_model='fir',
        high_pass=0.008,
        norm_betas=False,
        smoothing_kernel=0.0,
        signal_scaling=0,
        selected_confounds=[''])

Additionally, NiBetaSeries can be used to perform
finite BOLD response- separate (FS) modeling by combining
the LSS estimator with a FIR HRF model and a set of FIR delays.
This model produces a 4D beta series for each condition, at each FIR delay.

Least Squares- All (LSA)
~~~~~~~~~~~~~~~~~~~~~~~~

.. workflow::
    :graph2use: flat
    :simple_form: no
    :include-source: yes

    from nibetaseries.workflows.model import init_betaseries_wf
    wf = init_betaseries_wf(
        estimator='lsa',
        fir_delays=None,
        hrf_model='glover',
        high_pass=0.008,
        norm_betas=False,
        smoothing_kernel=0.0,
        signal_scaling=0,
        selected_confounds=[''])

For completeness, NiBetaSeries also implements least squares- all (LSA),
where each trial is given its own regressor in a single model as opposed to
LSS where there are as many models as there are trials.
While computationally faster, this method is unable to provide accurate
estimates if the trials are too close together.

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
This step is optional.
