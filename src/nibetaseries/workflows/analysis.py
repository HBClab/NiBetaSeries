#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:

# TODO: fix the renaming of files
"""
This workflow takes roi-roi correlations of the input betaseries
"""

from __future__ import print_function, division, absolute_import, unicode_literals
import nipype.pipeline.engine as pe
from nipype.interfaces import utility as niu
from ..interfaces.nilearn import AtlasConnectivity


def init_correlation_wf(name="correlation_wf"):
    """
    This workflow calculates betaseries correlations using an atlas

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
            atlas look up table (tsv) with a column for regions and a column for what number the label corresponds to.

    Outputs
    -------

        correlation_matrix
            a matrix (tsv) file denoting all roi-roi correlations
    """
    workflow = pe.Workflow(name=name)

    input_node = pe.Node(niu.IdentityInterface(fields=['betaseries_file',
                                                       'atlas_file',
                                                       'atlas_lut']),
                         name='input_node')

    output_node = pe.Node(niu.IdentityInterface(fields=['correlation_matrix']),
                          name='output_node')

    atlas_corr_node = pe.Node(AtlasConnectivity, name='atlas_corr_node')

    workflow.connect([
        (input_node, atlas_corr_node, [('betaseries_file', 'timeseries_file'),
                                       ('atlas_file', 'atlas_file'),
                                       ('atlas_lut', 'atlas_lut')]),
        (atlas_corr_node, output_node, [('correlation_matrix', 'correlation_matrix')]),
    ])

    return workflow

