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
from ..interfaces.nistats import BetaSeries


def init_betaseries_wf(name="betaseries_wf",
                       hrf_model='glover',
                       low_pass=None,
                       smoothing_kernel=None,
                       selected_confounds=None,
                       ):
    """Derives Beta Series Maps
    This workflow derives beta series maps from a bold file.
    Before the betas are estimated, low/high pass temporal filtering
    will be performed, and confounds can be added when estimating the betas.

    .. workflow::
        :graph2use: orig
        :simple_form: yes

        from nibetaseries.workflows.model import init_betaseries_wf
        wf = init_betaseries_wf(
            hrf_model='glover',
            low_pass=None,
            smoothing_kernel=0.0,
            selected_confounds=[''])

    Parameters
    ----------
    name : str
        Name of workflow (default: ``betaseries_wf``)
    hrf_model : str
        hemodynamic response function used to model the data (default: ``glover``)
    low_pass : float or None
        low pass filter to apply to bold (in Hertz).
        Reminder - frequencies _lower_ than this number are kept.
    smoothing_kernel : float or None
        The size of the smoothing kernel (full width/half max) applied to the bold file (in mm)
    selected_confounds : list or None
        the list of confounds to be included in regression.

    Inputs
    ------

    bold_file
        The bold file from the derivatives (e.g. fmriprep) dataset.
    events_file
        The events tsv from the BIDS dataset.
    bold_mask_file
        The mask file from the derivatives (e.g. fmriprep) dataset.
    bold_metadata
        dictionary of relevant metadata of bold sequence
    confounds_file
        The tsv file from the derivatives (e.g. fmriprep) dataset.

    Outputs
    -------

    betaseries_files
        One file per trial type, with each file being
        as long as the number of events for that trial type.
        (assuming the number of trials for any trial type is above 2)

    """
    workflow = pe.Workflow(name=name)

    input_node = pe.Node(niu.IdentityInterface(fields=['bold_file',
                                                       'events_file',
                                                       'bold_mask_file',
                                                       'bold_metadata',
                                                       'confounds_file',
                                                       ]),
                         name='input_node')

    betaseries_node = pe.Node(BetaSeries(selected_confounds=selected_confounds,
                                         hrf_model=hrf_model,
                                         smoothing_kernel=smoothing_kernel,
                                         low_pass=low_pass),
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
