#!/usr/bin/env python
# -*- coding: utf-8 -*-
# emacs: -*- mode: python; py-indent-offset: 4; indent-tabs-mode: nil -*-
# vi: set ft=python sts=4 ts=4 sw=4 et:
from nipype.interfaces.base import (
    traits, isdefined, TraitedSpec, BaseInterfaceInputSpec,
    File, Directory, InputMultiPath, OutputMultiPath, Str,
    SimpleInterface
)

class DerivativesDataSinkInputSpec(BaseInterfaceInputSpec):
    pass

class DerivativesDataSinkOutputSpec(TraitedSpec):
    pass

class DerivativesDataSink(SimpleInterface):
    input_spec = DerivativesDataSinkInputSpec
    output_spec = DerivativesDataSinkOutputSpec

    def _run_interface(self, runtime):

        return runtime
