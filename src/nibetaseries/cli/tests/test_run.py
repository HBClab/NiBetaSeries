from subprocess import call
import os
from ..run import get_parser


def test_get_parser():
    try:
        get_parser().parse_args(['-h'])
    except SystemExit:
        print('success')


def test_nibs(bids_dir, atlas_file, atlas_lut, fmriprep_dir):
    bids_dir = str(bids_dir)
    out_dir = os.path.join(bids_dir, 'derivatives')
    assert call(["nibs",
                 "-a " + str(atlas_file),
                 "-l " + str(atlas_lut),
                 "-c WhiteMatter CSF",
                 "-lp 0.01",
                 bids_dir,
                 "fmriprep",
                 out_dir,
                 "participant"])
