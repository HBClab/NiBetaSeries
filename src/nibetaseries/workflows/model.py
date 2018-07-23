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
                       high_pass=None,
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
            high_pass=None,
            smoothing_kernel=None,
            selected_confounds=None)

    Parameters
    ----------
    name : str
        Name of workflow (default: ``betaseries_wf``)
    hrf_model : str
        hemodynamic response function used to model the data (default: ``glover``)
    low_pass : float or None
        low pass filter to apply to bold (in Hertz). Reminder - frequencies _lower_ than this number are kept.
    high_pass : float or None
        high pass filter to apply to bold (in Hertz). Reminder - frequencies _higher_ than this number are kept.
    smoothing_kernel : float or None
        The size of the smoothing kernel (full width/half max) applied to the bold file (in mm)
    selected_confounds : list or None
        The list of confounds selected to be included in analysis.

    Inputs
    ------

    bold_file
        The bold file from the derivatives (e.g. fmriprep) dataset.
    events_file
        The events tsv from the BIDS dataset.
    bold_mask_file
        The mask file from the derivatives (e.g. fmriprep) dataset.
    confounds_file
        The tsv file from the derivatives (e.g. fmriprep) dataset.
    bold_info
        dictionary of information pulled from the BIDS json file connected to the bold file.

    Outputs
    -------

    betaseries_files
        One file per trial type, with each file being as long as the number of events for that trial type.
        (assuming the number of trials for any trial type is above 2)

    """
    workflow = pe.Workflow(name=name)

    input_node = pe.Node(niu.IdentityInterface(fields=['bold_file',
                                                       'events_file',
                                                       'bold_mask_file',
                                                       'confounds_file',
                                                       'bold_info'
                                                       ]),
                         name='input_node')
    # TODO: fix this hardcoding
    input_node.inputs.bold_info = {'RepetitionTime': 2.0}

    # function for temporal filtering
    def _temporal_filter(bold, lp, hp):
        from nilearn.image import clean_img
        import nibabel as nib
        import os

        tfilt_niimg = clean_img(bold,  low_pass=lp, high_pass=hp)
        out_path = os.getcwd()
        out_file = os.path.join(out_path, 'bold_tfilt.nii.gz')
        nib.save(tfilt_niimg, out_file)
        return out_file

    temp_filt_node = pe.Node(niu.Function(output_names=['bold_tfilt_file'],
                                          function=_temporal_filter),
                             name='temp_filt_node')
    temp_filt_node.inputs.lp = low_pass
    temp_filt_node.inputs.hp = high_pass

    betaseries_node = pe.Node(BetaSeries(selected_confounds=selected_confounds,
                                         hrf_model=hrf_model,
                                         smoothing_kernel=smoothing_kernel),
                              name='betaseries_node')

    output_node = pe.Node(niu.IdentityInterface(fields=['betaseries_files']),
                          name='output_node')

    # main workflow
    workflow.connect([
        (input_node, temp_filt_node, [('bold_file', 'bold')]),
        (input_node, betaseries_node, [('events_file', 'events_file'),
                                       ('bold_mask_file', 'mask_file'),
                                       ('bold_info', 'bold_info'),
                                       ('confounds_file', 'confounds_file')]),
        (temp_filt_node, betaseries_node, [('bold_tfilt_file', 'bold_file')]),
        (betaseries_node, output_node, [('beta_maps', 'betaseries_files')]),
    ])

    return workflow
