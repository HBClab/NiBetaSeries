#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
"""
This workflow takes roi-roi correlations of the input betaseries
"""
from __future__ import print_function, division, absolute_import, unicode_literals

import nipype.pipeline.engine as pe
from nipype.interfaces import utility as niu
from niworkflows.engine.workflows import LiterateWorkflow as Workflow

from mne import __version__ as mne_ver
from nilearn import __version__ as nilearn_ver
from matplotlib import __version__ as matplotlib_ver

from ..interfaces.nilearn import AtlasConnectivity


def init_correlation_wf(name="correlation_wf"):
    """
    This workflow calculates betaseries correlations using a parcellation
    from an atlas.

    .. workflow::
        :graph2use: orig
        :simple_form: yes

        from nibetaseries.workflows.analysis import init_correlation_wf
        wf = init_correlation_wf()

    Parameters
    ----------

        name : str
            Name of workflow (default: ``correlation_wf``)

    Inputs
    ------

        betaseries_files
            list of betaseries files
        atlas_file
            atlas file with indexed regions of interest
        atlas_lut
            atlas look up table (tsv) with a column for regions
            and a column for what number the label corresponds to.

    Outputs
    -------

        correlation_matrix
            a matrix (tsv) file denoting all roi-roi correlations
        correlation_fig
            a svg file of a circular connectivity plot showing all roi-roi correlations
    """
    workflow = Workflow(name=name)

    workflow.__desc__ = """\

### Atlas Connectivity Analysis

The beta series 4D image for each condition in the task was subjected to an
ROI-to-ROI connectivity analysis to produce a condition-specific correlation
matrix.
The correlation coefficient estimator used for this step was empirical
covariance, as implemented in Nilearn {nilearn_ver} [@Abraham2014].
Correlation coefficients were converted to normally-distributed z-values using
Fisher's r-to-z conversion [@Fisher1915].
Figures for the correlation matrices were generated with
Matplotlib {matplotlib_ver} [@Hunter2007] and MNE-Python {mne_ver}
[@Gramfort2013; @Gramfort2014].
""".format(nilearn_ver=nilearn_ver,
           matplotlib_ver=matplotlib_ver,
           mne_ver=mne_ver)

    input_node = pe.MapNode(niu.IdentityInterface(fields=['betaseries_files',
                                                          'atlas_file',
                                                          'atlas_lut']),
                            iterfield=['betaseries_files'],
                            name='input_node')

    output_node = pe.Node(niu.IdentityInterface(fields=['correlation_matrix',
                                                        'correlation_fig']),
                          name='output_node')

    atlas_corr_node = pe.MapNode(AtlasConnectivity(),
                                 name='atlas_corr_node',
                                 iterfield=['timeseries_file'])

    workflow.connect([
        (input_node, atlas_corr_node, [('betaseries_files', 'timeseries_file'),
                                       ('atlas_file', 'atlas_file'),
                                       ('atlas_lut', 'atlas_lut')]),
        (atlas_corr_node, output_node, [('correlation_fig', 'correlation_fig'),
                                        ('correlation_matrix', 'correlation_matrix')])
    ])

    return workflow
