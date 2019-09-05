#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
import os
from shutil import copy
from nipype.interfaces.base import (
    traits, isdefined, TraitedSpec, BaseInterfaceInputSpec,
    File, SimpleInterface
)


class DerivativesDataSinkInputSpec(BaseInterfaceInputSpec):
    base_directory = traits.Directory(
        desc='Path to the base directory for storing data.')
    in_file = File(exists=True, mandatory=True)
    source_file = File(exists=False, mandatory=True, desc='the input func file')


class DerivativesDataSinkOutputSpec(TraitedSpec):
    out_file = File(exists=True, desc='written file path')


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
        import json
        import os.path as op
        import pkg_resources
        from bids.layout import parse_file_entities
        from bids.layout.writing import build_path

        deriv_cfg = pkg_resources.resource_string("nibetaseries",
                                                  op.join("data", "derivatives.json"))
        deriv_patterns = json.loads(deriv_cfg.decode('utf-8'))['fmriprep_path_patterns']

        subject_entities = parse_file_entities(self.inputs.source_file)
        betaseries_entities = parse_file_entities(self.inputs.in_file)
        # hotfix
        betaseries_entities['description'] = betaseries_entities['desc']

        subject_entities.update(betaseries_entities)

        out_file = build_path(subject_entities, deriv_patterns)

        if not out_file:
            raise ValueError("the provided entities do not make a valid file")

        base_directory = runtime.cwd
        if isdefined(self.inputs.base_directory):
            base_directory = os.path.abspath(self.inputs.base_directory)

        out_path = op.join(base_directory, self.out_path_base, out_file)

        os.makedirs(op.dirname(out_path), exist_ok=True)

        # copy the file to the output directory
        copy(self.inputs.in_file, out_path)

        self._results['out_file'] = out_path

        return runtime
