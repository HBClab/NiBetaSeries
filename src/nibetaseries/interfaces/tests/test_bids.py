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
    return base_dir.ensure("desc-condTest_correlation.tsv")


@pytest.fixture(scope='session')
def corr_fig(base_dir):
    return base_dir.ensure("desc-condTest_correlation.svg")


@pytest.fixture(scope='session')
def bs_out(base_dir):
    return base_dir.ensure("desc-condTest_betaseries.nii.gz")


def test_derivatives_data_sink_tsv(base_dir, betaseries_file, corr_csv, preproc_file):

    # the expected output
    expected_out = os.path.join(
        str(base_dir),
        'nibetaseries',
        'sub-01',
        'ses-pre',
        'func',
        ('sub-01_ses-pre_task-waffles_run-1_space-MNI152NLin2009cAsym'
         '_desc-condTest_correlation.tsv'))

    # create and run instance of the interface
    dds = DerivativesDataSink(base_directory=str(base_dir),
                              in_file=str(corr_csv),
                              source_file=str(preproc_file))
    res = dds.run()

    assert res.outputs.out_file == expected_out


def test_derivatives_data_sink_svg(base_dir, betaseries_file, corr_fig, preproc_file):

    # the expected output
    expected_out = os.path.join(
        str(base_dir),
        'nibetaseries',
        'sub-01',
        'ses-pre',
        'func',
        ('sub-01_ses-pre_task-waffles_run-1_space-MNI152NLin2009cAsym'
         '_desc-condTest_correlation.svg'))

    # create and run instance of the interface
    dds = DerivativesDataSink(base_directory=str(base_dir),
                              in_file=str(corr_fig),
                              source_file=str(preproc_file))
    res = dds.run()

    assert res.outputs.out_file == expected_out


def test_derivatives_data_sink_bs(base_dir, betaseries_file, bs_out, preproc_file):

    # the expected output
    expected_out = os.path.join(
        str(base_dir),
        'nibetaseries',
        'sub-01',
        'ses-pre',
        'func',
        ('sub-01_ses-pre_task-waffles_run-1_space-MNI152NLin2009cAsym'
         '_desc-condTest_betaseries.nii.gz'))

    # create and run instance of the interface
    dds = DerivativesDataSink(base_directory=str(base_dir),
                              in_file=str(bs_out),
                              source_file=str(preproc_file))
    res = dds.run()

    assert res.outputs.out_file == expected_out
