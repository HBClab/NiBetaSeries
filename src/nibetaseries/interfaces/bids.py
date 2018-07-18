#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
import os
from nipype.interfaces.base import (
    traits, isdefined, TraitedSpec, BaseInterfaceInputSpec,
    File, Directory, InputMultiPath, OutputMultiPath, Str,
    SimpleInterface
)

BIDS_NAME = re.compile(
    '^(.*\/)?(?P<subject_id>sub-[a-zA-Z0-9]+)(_(?P<session_id>ses-[a-zA-Z0-9]+))?'
    '(_(?P<task_id>task-[a-zA-Z0-9]+))?(_(?P<acq_id>acq-[a-zA-Z0-9]+))?'
    '(_(?P<rec_id>rec-[a-zA-Z0-9]+))?(_(?P<run_id>run-[a-zA-Z0-9]+))?'
    '(_(?P<space_id>space-[a-zA-Z0-9]+))?(_(?P<variant_id>variant-[a-zA-Z0-9]+))?')

BETASERIES_NAME = re.compile(
    '^(.*\/)?betaseries(_(?P<trialtype_id>trialtype-[a-zA-Z0-9]+))?'
)


class DerivativesDataSinkInputSpec(BaseInterfaceInputSpec):
    base_directory = traits.Directory(
        desc='Path to the base directory for storing data.')
    betaseries_file = File(exists=True, mandatory=True,
                           desc='the betaseries file')
    in_file = File(exists=True, mandatory=True)
    source_file = File(exists=False, mandatory=True, desc='the input func file')
    suffix = traits.Str('', mandatory=True, desc='suffix appended to source_file')
    extra_values = traits.List(traits.Str)


class DerivativesDataSinkOutputSpec(TraitedSpec):
    out_file = OutputMultiPath(File(exists=True, desc='written file path'))


class DerivativesDataSink(SimpleInterface):
    input_spec = DerivativesDataSinkInputSpec
    output_spec = DerivativesDataSinkOutputSpec
    out_path_base = "nibetaseries"
    _always_run = True

    def __init__(self, out_path_base=None, **inputs):
        super(DerivativesDataSink, self).__init__(**inputs)
        self._results['out_file'] = []
        if out_path_base:
            self.out_path_base = out_path_base

    def _run_interface(self, runtime):
        src_fname, _ = _splitext(self.inputs.source_file)
        betaseries_fname, _ = _splitext(self.inputs.betaseries_file)
        _, ext = _splitext(self.inputs.in_file)

        bids_dict = BIDS_NAME.search(src_fname).groupdict()

        betaseries_dict = BETASERIES_NAME.search(betaseries_dict).groupdict()
        return runtime


def _splitext(fname):
    fname, ext = op.splitext(os.path.basename(fname))
    if ext == '.gz':
        fname, ext2 = os.path.splitext(fname)
        ext = ext2 + ext
    return fname, ext
