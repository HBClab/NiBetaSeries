from subprocess import call
import os

import pytest
from ..run import get_parser


def test_get_parser():
    try:
        get_parser().parse_args(['-h'])
    except SystemExit:
        print('success')


def test_nibs_lss(bids_dir, atlas_file, atlas_lut, deriv_dir):
    bids_dir = str(bids_dir)
    out_dir = os.path.join(bids_dir, 'derivatives')
    assert call(["nibs",
                 "-a " + str(atlas_file),
                 "-l " + str(atlas_lut),
                 "-c WhiteMatter CSF",
                 "-hp 0.008",
                 "--estimator lss",
                 "-sp MNI152NLin2009cAsym",
                 "-sm 0.0",
                 "--hrf-model spm",
                 "--session-label pre",
                 "--task-label waffles",
                 "--run-label 1",
                 "--description-label preproc",
                 "--graph",
                 bids_dir,
                 "fmriprep",
                 out_dir,
                 "participant"])


def test_nibs_lsa(bids_dir, atlas_file, atlas_lut, deriv_dir):
    bids_dir = str(bids_dir)
    out_dir = os.path.join(bids_dir, 'derivatives')
    assert call(["nibs",
                 "-a " + str(atlas_file),
                 "-l " + str(atlas_lut),
                 "-c WhiteMatter CSF",
                 "-hp 0.008",
                 "--estimator lsa",
                 "-sp MNI152NLin2009cAsym",
                 "-sm 0.0",
                 "--hrf-model spm",
                 "--session-label pre",
                 "--task-label waffles",
                 "--run-label 1",
                 "--description-label preproc",
                 "--graph",
                 bids_dir,
                 "fmriprep",
                 out_dir,
                 "participant"])


def test_init(monkeypatch):
    from ...cli import run
    monkeypatch.setattr(run, "__name__", "__main__")
    with pytest.raises(RuntimeError):
        run.init()
