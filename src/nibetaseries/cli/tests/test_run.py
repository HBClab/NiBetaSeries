from subprocess import call
import os

import pytest
from ..run import get_parser


def test_get_parser():
    with pytest.raises(SystemExit):
        get_parser().parse_args(['-h'])


def test_conditional_arguments(monkeypatch):
    import sys
    parser_args = [
            'bids_dir',
            'derivatives_pipeline',
            'output_dir',
            'participant',
            '-l', 'lut',
            '-a', 'img'
    ]

    # normal call
    get_parser().parse_args(parser_args)

    # remove the lut arguments
    no_lut = [a for a in parser_args if a != "-l" and a != "lut"]
    monkeypatch.setattr(sys, 'argv', no_lut)
    with pytest.raises(SystemExit):
        get_parser().parse_args(no_lut)

    # remove the atlas-img arguments
    no_img = [a for a in parser_args if a != "-a" and a != "img"]
    monkeypatch.setattr(sys, 'argv', no_img)
    with pytest.raises(SystemExit):
        get_parser().parse_args(no_img)


def test_nibs_lss(bids_dir, atlas_file, atlas_lut, deriv_dir):
    bids_dir = str(bids_dir)
    out_dir = os.path.join(bids_dir, 'derivatives')
    assert call(["nibs",
                 "-a " + str(atlas_file),
                 "-l " + str(atlas_lut),
                 "-c WhiteMatter CSF",
                 "--high-pass 0.008",
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


def test_nibs_fs(bids_dir, atlas_file, atlas_lut, deriv_dir):
    bids_dir = str(bids_dir)
    out_dir = os.path.join(bids_dir, 'derivatives')
    assert call(["nibs",
                 "-a " + str(atlas_file),
                 "-l " + str(atlas_lut),
                 "-c WhiteMatter CSF",
                 "--high-pass 0.008",
                 "--estimator lss",
                 "-sp MNI152NLin2009cAsym",
                 "-sm 0.0",
                 "--hrf-model fir",
                 "--fir-delays 0 1 2 3 4"
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
                 "--high-pass 0.008",
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
