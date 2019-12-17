import os

import pytest
from ..run import get_parser, main


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


@pytest.mark.parametrize("estimator,fir_delays,hrf_model,part_label",
                         [('lsa', None, 'spm', '01'),
                          ('lss', None, 'spm', 'sub-01'),
                          ('lss', [0, 1, 2, 3, 4], 'fir', None)])
def test_nibs(
        bids_dir, deriv_dir, sub_fmriprep, sub_metadata, bold_file, preproc_file,
        sub_events, confounds_file, brainmask_file, atlas_file, atlas_lut,
        estimator, fir_delays, hrf_model, monkeypatch, part_label):
    import sys
    bids_dir = str(bids_dir)
    out_dir = os.path.join(bids_dir, 'derivatives')
    args = ["nibs",
            "-a", str(atlas_file),
            "-l", str(atlas_lut),
            "-c", "WhiteMatter", "CSF",
            "--high-pass", "0.008",
            "--estimator", estimator,
            "-sp", "MNI152NLin2009cAsym",
            "-sm", "0.0",
            "--hrf-model", hrf_model,
            "--session-label", "pre",
            "--task-label", "waffles",
            "--run-label", "1",
            "--description-label", "preproc",
            "--graph",
            bids_dir,
            "fmriprep",
            out_dir,
            "participant"]
    if fir_delays:
        args.append('--fir-delays')
        args.extend([str(d) for d in fir_delays])
    if part_label:
        args.extend(["--participant-label", part_label])

    monkeypatch.setattr(sys, 'argv', args)
    assert main() is None


def test_init(monkeypatch):
    from ...cli import run
    monkeypatch.setattr(run, "__name__", "__main__")
    with pytest.raises(RuntimeError):
        run.init()


def test_deriv_directory(monkeypatch):
    import sys

    parser_args = [
            'nibs',
            'bids_dir',
            'derivatives_pipeline',
            'output_dir',
            'participant',
            '-l', 'lut',
            '-a', 'img',
    ]
    monkeypatch.setattr(sys, 'argv', parser_args)
    with pytest.raises(NotADirectoryError) as no_dir:
        main()

    assert "is not an available directory" in str(no_dir.value)


def test_fir_delays(monkeypatch):
    import sys

    parser_args = [
            'nibs',
            'bids_dir',
            'derivatives_pipeline',
            'output_dir',
            'participant',
            '--hrf-model', 'fir',
    ]
    monkeypatch.setattr(sys, 'argv', parser_args)
    with pytest.raises(ValueError) as no_delays:
        main()

    assert "If the FIR HRF model is selected" in str(no_delays.value)
