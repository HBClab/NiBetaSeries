''' Testing module for nibetaseries.interfaces.bids '''
import os
import pytest

from ..bids import DerivativesDataSink


@pytest.fixture(scope='session')
def base_dir(tmpdir_factory):
    base_dir = tmpdir_factory.mktemp('base')
    return base_dir


@pytest.fixture(scope='session')
def corr_csv(base_dir):
    return base_dir.ensure("mytsv.csv")


def test_derivatives_data_sink(base_dir, betaseries_file, corr_csv, preproc_file):

    # the expected output
    expected_out = os.path.join(
        str(base_dir),
        'nibetaseries',
        'sub-01',
        'ses-pre',
        'func',
        'sub-01_ses-pre_task-waffles_space-MNI152NLin2009cAsym_bold_preproc_trialtype-testCond_matrix.csv')

    # create and run instance of the interface
    dds = DerivativesDataSink(base_directory=str(base_dir),
                              betaseries_file=str(betaseries_file),
                              in_file=str(corr_csv),
                              source_file=str(preproc_file),
                              suffix='matrix')
    res = dds.run()

    assert res.outputs.out_file == expected_out
