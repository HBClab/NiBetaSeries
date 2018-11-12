''' Testing module for nibetaseries.interfaces.bids '''
import os
from pathlib import Path
import shutil

from ..bids import DerivativesDataSink


def test_derivatives_data_sink():

    # creating the fake inputs
    base_directory = os.path.join(os.getcwd(), 'tmp')
    os.makedirs(base_directory, exist_ok=True)
    betaseries_file = os.path.join(base_directory, 'betaseries_trialtype-testtrial.nii.gz')
    Path(betaseries_file).touch()
    in_file = os.path.join(base_directory, 'mycsv.csv')
    Path(in_file).touch()
    source_file = os.path.join(base_directory,
                               'sub-01_ses-01_task-testtask_run-1_preproc.nii.gz')
    Path(source_file).touch()
    suffix = 'matrix'

    # the expected output
    expected_out = os.path.join(
        base_directory,
        'nibetaseries',
        'sub-01',
        'ses-01',
        'func',
        'sub-01_ses-01_task-testtask_run-1_preproc_trialtype-testtrial_matrix.csv')

    # create and run instance of the interface
    dds = DerivativesDataSink(base_directory=base_directory,
                              betaseries_file=betaseries_file,
                              in_file=in_file,
                              source_file=source_file,
                              suffix=suffix)
    res = dds.run()

    # clean up created files
    shutil.rmtree(base_directory)

    assert res.outputs.out_file == expected_out
