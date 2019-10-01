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
                       smoothing_kernel=None,
                       selected_confounds=None,
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
    smoothing_kernel : float or None
        The size of the smoothing kernel (full width/half max) applied to the bold file (in mm)
    selected_confounds : list or None
        the list of confounds to be included in regression.

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
    smooth_str = ('smoothed with a Gaussian kernel with a FWHM of {fwhm} mm,'
                  ' '.format(fwhm=smoothing_kernel)
                  if smoothing_kernel != 0. else '')
    confound_str = (', '.join(selected_confounds) + ' and ' if
                    selected_confounds else '')
    if estimator == 'lss' and hrf_model != 'fir':
        workflow.__desc__ = """\

### Beta Series Modeling

Least squares- separate (LSS) models were generated for each event in the task
following the method described in @Turner2012a, using Nistats {nistats_ver}.
Prior to modeling, preprocessed data were {smooth_str}masked,
and mean-scaled over time.
For each trial, preprocessed data were subjected to a general linear model in
which the trial was modeled in its own regressor, while all other trials from
that condition were modeled in a second regressor, and other conditions were
modeled in their own regressors. Each condition regressor was convolved with a
"{hrf}" hemodynamic response function for the model.
In addition to condition regressors, {confound_str}a
high-pass filter of {hpf} Hz (implemented using a cosine drift model) {is_mult_confs}
included in the model.
AR(1) prewhitening was applied in each model to account for temporal
autocorrelation.

After fitting each model, the parameter estimate map associated with the
target trial's regressor was retained and concatenated into a 4D image with all
other trials from that condition, resulting in a set of N 4D images of varying
sizes, where N refers to the number of conditions in the task.
""".format(nistats_ver=nistats_ver, smooth_str=smooth_str, hrf=hrf_model,
           confound_str=confound_str, hpf=high_pass,
           is_mult_confs='were' if len(confound_str) else 'was')
    elif estimator == 'lss' and hrf_model == 'fir':
        fir_delays = [0, 1, 2, 3, 4]
        workflow.__desc__ = """\

### Beta Series Modeling

Finite BOLD response- separate (FS) models were generated for each event in the
task following the method described in @Turner2012a, using Nistats
{nistats_ver}.
Prior to modeling, preprocessed data were {smooth_str}masked,
and mean-scaled over time.
For each trial, preprocessed data were subjected to a general linear model in
which the trial was modeled in its own set of finite impulse response (FIR)
regressors. In a finite impulse response model, the BOLD response for each of a
set of delays following the onset of the trial is modeled as an impulse, which
can be used to capture the hemodynamic response model associated with that
condition. In the models applied in this workflow, delay-specific FIR
regressors corresponding to {delays} volumes after the target trial were
included, while all other trials from that condition were modeled in a second
set of FIR regressors, and other conditions were modeled in their own sets of
FIR regressors.
In addition to condition regressors, {confound_str}a
high-pass filter of {hpf} Hz (implemented using a cosine drift model) {is_mult_confs}
included in the model.
AR(1) prewhitening was applied in each model to account for temporal
autocorrelation.

After fitting each model, the parameter estimate map associated with each of
the target trial's {n_delays} delay-specific FIR regressors was retained
and concatenated into delay-specific 4D images with all other trials from that
condition, resulting in a set of N * {n_delays} 4D images of varying
sizes, where N refers to the number of conditions in the task.
""".format(nistats_ver=nistats_ver, smooth_str=smooth_str, hrf=hrf_model,
           confound_str=confound_str, hpf=high_pass,
           is_mult_confs='were' if len(confound_str) else 'was',
           fir_delays=', '.join(fir_delays), n_delays=len(fir_delays))
    elif estimator == 'lsa':
        workflow.__desc__ = """\

### Beta Series Modeling

A least squares- all (LSA) model was generated following the method described in
@Rissman2004, using Nistats {nistats_ver}.
Prior to modeling, preprocessed data were {smooth_str}masked,
and mean-scaled over time.
Preprocessed data were subjected to a general linear model in which each trial
was modeled in its own regressor. Each trial-specific regressor was convolved
with a "{hrf}" hemodynamic response function for the model.
In addition to condition regressors, {confound_str}a
high-pass filter of {hpf} Hz (implemented using a cosine drift model) {is_mult_confs}
included in the model.
AR(1) prewhitening was applied in each model to account for temporal
autocorrelation.

After fitting each model, the parameter estimate map associated with the
target trial's regressor was retained and concatenated into a 4D image with all
other trials from that condition, resulting in a set of N 4D images of varying
sizes, where N refers to the number of conditions in the task.
""".format(nistats_ver=nistats_ver, smooth_str=smooth_str, hrf=hrf_model,
           confound_str=confound_str, hpf=high_pass,
           is_mult_confs='were' if len(confound_str) else 'was')

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
                hrf_model=hrf_model,
                smoothing_kernel=smoothing_kernel,
                high_pass=high_pass),
            name='betaseries_node')
    elif estimator == 'lsa':
        betaseries_node = pe.Node(LSABetaSeries(
                selected_confounds=selected_confounds,
                hrf_model=hrf_model,
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
