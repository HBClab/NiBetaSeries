#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
Derive Beta Series Maps
^^^^^^^^^^^^^^^^^^^^^^^
.. autofunction:: init_betaseries_wf
"""
from __future__ import print_function, division, absolute_import, unicode_literals

import nipype.pipeline.engine as pe
from nipype.interfaces import utility as niu
from niworkflows.engine.workflows import LiterateWorkflow as Workflow

from nistats import __version__ as nistats_ver

from ..interfaces.nistats import LSSBetaSeries, LSABetaSeries


def init_betaseries_wf(name="betaseries_wf",
                       estimator='lss',
                       fir_delays=None,
                       hrf_model='glover',
                       high_pass=0.0078125,
                       norm_betas=False,
                       signal_scaling=0,
                       selected_confounds=None,
                       smoothing_kernel=None,
                       ):
    """Derives Beta Series Maps
    This workflow derives beta series maps from a bold file.
    Before the betas are estimated, high pass temporal filtering
    will be performed, and confounds can be added when estimating the betas.

    .. workflow::
        :graph2use: orig
        :simple_form: yes

        from nibetaseries.workflows.model import init_betaseries_wf
        wf = init_betaseries_wf(
            fir_delays=None,
            hrf_model='glover',
            high_pass=0.0078125,
            smoothing_kernel=0.0,
            selected_confounds=[''])

    Parameters
    ----------
    name : str
        Name of workflow (default: ``betaseries_wf``)
    fir_delays : list or None
        FIR delays (in scans)
    hrf_model : str
        hemodynamic response function used to model the data (default: ``glover``)
    high_pass : float
        high pass filter to apply to bold (in Hertz).
        Reminder - frequencies _lower_ than this number are kept.
    norm_betas : Bool
        If True, beta estimates are divided by the square root of their variance
    selected_confounds : list or None
        the list of confounds to be included in regression.
    signal_scaling : False or 0
        Whether (0) or not (False) to scale each voxel's timeseries
    smoothing_kernel : float or None
        The size of the smoothing kernel (full width/half max) applied to the bold file (in mm)

    Inputs
    ------

    bold_file
        The bold file from the derivatives (e.g., fmriprep) dataset.
    events_file
        The events tsv from the BIDS dataset.
    bold_mask_file
        The mask file from the derivatives (e.g., fmriprep) dataset.
    bold_metadata
        dictionary of relevant metadata of bold sequence
    confounds_file
        The tsv file from the derivatives (e.g., fmriprep) dataset.

    Outputs
    -------

    betaseries_files
        One file per trial type, with each file being
        as long as the number of events for that trial type.
        (assuming the number of trials for any trial type is above 2)

    """
    workflow = Workflow(name=name)
    workflow.__desc__ = gen_wf_description(
        nistats_ver=nistats_ver,
        fwhm=smoothing_kernel,
        hrf=hrf_model,
        hpf=high_pass,
        norm_betas=norm_betas,
        selected_confounds=selected_confounds,
        signal_scaling=signal_scaling,
        estimator=estimator,
        fir_delays=fir_delays,
    )

    input_node = pe.Node(niu.IdentityInterface(fields=['bold_file',
                                                       'events_file',
                                                       'bold_mask_file',
                                                       'bold_metadata',
                                                       'confounds_file',
                                                       ]),
                         name='input_node')

    if estimator == 'lss':
        betaseries_node = pe.Node(LSSBetaSeries(
                fir_delays=fir_delays,
                selected_confounds=selected_confounds,
                signal_scaling=signal_scaling,
                hrf_model=hrf_model,
                return_tstat=norm_betas,
                smoothing_kernel=smoothing_kernel,
                high_pass=high_pass),
            name='betaseries_node')
    elif estimator == 'lsa':
        betaseries_node = pe.Node(LSABetaSeries(
                selected_confounds=selected_confounds,
                signal_scaling=signal_scaling,
                hrf_model=hrf_model,
                return_tstat=norm_betas,
                smoothing_kernel=smoothing_kernel,
                high_pass=high_pass),
            name='betaseries_node')

    output_node = pe.Node(niu.IdentityInterface(fields=['betaseries_files']),
                          name='output_node')

    # main workflow
    workflow.connect([
        (input_node, betaseries_node, [('bold_file', 'bold_file'),
                                       ('events_file', 'events_file'),
                                       ('bold_mask_file', 'mask_file'),
                                       ('bold_metadata', 'bold_metadata'),
                                       ('confounds_file', 'confounds_file')]),
        (betaseries_node, output_node, [('beta_maps', 'betaseries_files')]),
    ])

    return workflow


def gen_wf_description(nistats_ver, fwhm, hrf, hpf,
                       selected_confounds, signal_scaling,
                       estimator, norm_betas, fir_delays=None):
    from textwrap import dedent

    smooth_str = ('smoothed with a Gaussian kernel with a FWHM of {fwhm} mm,'
                  ' '.format(fwhm=fwhm)
                  if fwhm != 0. else '')
    signal_scale_str = ', and mean-scaled over time.' if signal_scaling == 0 else '.'

    preproc_str = ('Prior to modeling, preprocessed data were {smooth_str}masked{signal_scale_str}'
                   .format(smooth_str=smooth_str, signal_scale_str=signal_scale_str))

    beta_series_tmp = dedent("""
        After fitting {n_models} model, the{normed} parameter estimate (i.e., beta) map
        associated with the target trial's regressor was retained and concatenated
        into a 4D image with all other trials from the same condition, resulting
        in a set of N 4D images where N refers to the number of conditions in the task.
        The number of volumes in each 4D image represents the number of trials in that
        condition.\
        """)

    if estimator == "lss" and hrf == "fir":
        estimator_intro = dedent("""\
            Finite BOLD response- separate (FS) models were generated
            for each event in the task following the method described
            in @Turner2012a, using Nistats {nistats_ver}.\
            """.format(nistats_ver=nistats_ver))

        estimator_str = dedent("""\
            For each trial, preprocessed data were subjected to a general linear model in
            which the trial was modeled in its own set of finite impulse response (FIR)
            regressors. In a finite impulse response model, the BOLD response for each of a
            set of delays following the onset of the trial is modeled as an impulse, which
            can be used to capture the hemodynamic response model associated with that
            condition. In the models applied in this workflow, delay-specific FIR
            regressors corresponding to {fir_delays} volumes after the target trial were
            included, while all other trials from that condition were modeled in a second
            set of FIR regressors, and other conditions were modeled in their own sets of
            FIR regressors.\
            """.format(fir_delays=[str(d) for d in fir_delays]))

        beta_series_str = dedent("""\
            After fitting each model, the{normed} parameter estimate (i.e., beta) map associated
            with each of the target trial's {n_delays} delay-specific FIR regressors
            was retained and concatenated into delay-specific 4D images with all other
            trials from the same condition, resulting in a set of N * {n_delays} 4D
            images where N refers to the number of conditions in the task.
            The number of volumes in each 4D image represents the number of trials in that
            condition.\
            """.format(n_delays=len(fir_delays),
                       normed=' normalized' if norm_betas else ''))

    elif estimator == "lss" and hrf != "fir":
        estimator_intro = dedent("""\
            Least squares- separate (LSS) models were generated for each event in the task
            following the method described in @Turner2012a, using Nistats {nistats_ver}.\
            """.format(nistats_ver=nistats_ver))

        estimator_str = dedent("""\
            For each trial, preprocessed data were subjected to a general linear model in
            which the trial was modeled in its own regressor, while all other trials from
            that condition were modeled in a second regressor, and other conditions were
            modeled in their own regressors.\
            """)

        beta_series_str = beta_series_tmp.format(n_models='each',
                                                 normed=' normalized' if norm_betas else '')

    elif estimator == "lsa":
        estimator_intro = dedent("""\
            A least squares- all (LSA) model was generated following the method described in
            @Rissman2004, using Nistats {nistats_ver}.\
            """.format(nistats_ver=nistats_ver))

        estimator_str = dedent("""\
            Preprocessed data were subjected to a general linear model in which each trial
            was modeled in its own regressor.\
            """)

        beta_series_str = beta_series_tmp.format(n_models='the',
                                                 normed=' normalized' if norm_betas else '')

    else:
        raise ValueError("{est} not a supported estimator".format(est=estimator))

    hrf_str = dedent("""\
        Each condition regressor was convolved with a
        "{hrf}" hemodynamic response function for the model.\
        """.format(hrf=hrf) if hrf != 'fir' else '')

    confound_str = (', '.join(selected_confounds) + ' and ' if
                    selected_confounds else '')

    confound_desc = dedent("""\
        In addition to condition regressors, {confound_str}a
        high-pass filter of {hpf} Hz (implemented using a cosine drift model) {is_mult_confs}
        included in the model.
        AR(1) prewhitening was applied in each model to account for temporal
        autocorrelation.\
        """.format(confound_str=confound_str,
                   hpf=hpf,
                   is_mult_confs='were' if len(confound_str) else 'was'))

    # combine all sentences
    description = dedent("""\

        ### Beta Series Modeling

        {estimator_intro}
        {preproc_str}
        {estimator_str}{hrf_str}
        {confound_desc}

        {beta_series_str}
        """).format(estimator_intro=estimator_intro,
                    preproc_str=preproc_str,
                    estimator_str=estimator_str,
                    hrf_str=hrf_str,
                    confound_desc=confound_desc,
                    beta_series_str=beta_series_str)

    return description
