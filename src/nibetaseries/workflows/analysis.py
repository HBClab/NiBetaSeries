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

    def _rename_matrix(correlation_matrix, betaseries_file):
        import os
        import re
        from shutil import copyfile

        betaseries_regex = re.compile('.*betaseries_trialtype-(?P<trial_type>[A-Za-z0-9]+).nii.gz')
        trial_type = betaseries_regex.search(betaseries_file).groupdict()['trial_type']
        out_file = os.path.join(os.getcwd(),
                                'correlation-matrix_trialtype-{trial_type}.tsv'.format(trial_type=trial_type))
        copyfile(correlation_matrix, out_file)

        return out_file

    input_node = pe.MapNode(niu.IdentityInterface(fields=['betaseries_files',
                                                          'atlas_file',
                                                          'atlas_lut']),
                            iterfield=['betaseries_files'],
                            name='input_node')

    output_node = pe.Node(niu.IdentityInterface(fields=['correlation_matrix']),
                          name='output_node')

    atlas_corr_node = pe.MapNode(AtlasConnectivity(), name='atlas_corr_node', iterfield=['timeseries_file'])

    rename_matrix_node = pe.MapNode(niu.Function(output_names=['correlation_matrix_trialtype'],
                                                 function=_rename_matrix),
                                    iterfield=['correlation_matrix', 'betaseries_file'],
                                    name='rename_matrix_node')
    workflow.connect([
        (input_node, atlas_corr_node, [('betaseries_files', 'timeseries_file'),
                                       ('atlas_file', 'atlas_file'),
                                       ('atlas_lut', 'atlas_lut')]),
        (input_node, rename_matrix_node, [('betaseries_files', 'betaseries_file')]),
        (atlas_corr_node, rename_matrix_node, [('correlation_matrix', 'correlation_matrix')]),
        (rename_matrix_node, output_node, [('correlation_matrix_trialtype', 'correlation_matrix')]),
    ])

    return workflow

