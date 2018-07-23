# -*- coding: utf-8 -*-
"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -m nibetaseries` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``nibetaseries.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``nibetaseries.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
from __future__ import absolute_import
import os
import argparse
from glob import glob
from nipype import config as ncfg


def get_parser():
    """Build parser object"""

    parser = argparse.ArgumentParser(description='NiBetaSeries BIDS arguments')
    parser.add_argument('bids_dir', help='The directory with the input dataset '
                        'formatted according to the BIDS standard.')
    parser.add_argument('derivatives_pipeline', help='The pipeline that contains '
                        'minimally preprocessed img, brainmask, and confounds.tsv')
    parser.add_argument('output_dir', help='The directory where the output directory '
                        'and files should be stored. If you are running group level analysis '
                        'this folder should be prepopulated with the results of the'
                        'participant level analysis.')
    parser.add_argument('analysis_level', choices=['participant', 'group'],
                        help='Level of the analysis that will be performed '
                        'Multiple participant level analyses can be run independently '
                        '(in parallel) using the same output_dir')
    parser.add_argument('-v', '--version', action='version',
                        version='NiBetaSeries 0.1.0')

    # preprocessing options
    proc_opts = parser.add_argument_group('Options for preprocessing')
    proc_opts.add_argument('-sm', '--smoothing_kernel', action='store', type=float, default=6.0,
                           help='select a smoothing kernel (mm)')
    proc_opts.add_argument('-lp', '--low_pass', action='store', type=float,
                           default=None, help='low pass filter')
    proc_opts.add_argument('-hp', '--high_pass', action='store', type=float,
                           default=None, help='high pass filter')
    proc_opts.add_argument('-c', '--confounds', help='The confound column names '
                           'that are to be included in nuisance regression. '
                           'write the confounds you wish to include separated by a space',
                           nargs="+")
    proc_opts.add_argument('-w', '--work_dir', help='directory where temporary files '
                           'are stored')

    # Image Selection options
    image_opts = parser.add_argument_group('Options for selecting images')
    parser.add_argument('--participant_label', nargs="+",
                        help='The label(s) of the participant(s) '
                             'that should be analyzed. The label '
                             'corresponds to sub-<participant_label> from the BIDS spec '
                             '(so it does not include "sub-"). If this parameter is not '
                             'provided all subjects should be analyzed. Multiple '
                             'participants can be specified with a space separated list.')
    image_opts.add_argument('--session_label', action='store',
                            default=None, help='select a session to analyze')
    image_opts.add_argument('-t', '--task_label', action='store',
                            default=None, help='select a specific task to be processed')
    image_opts.add_argument('--run_label', action='store',
                            default=None, help='select a run to analyze')
    image_opts.add_argument('-sp', '--space_label', action='store', default='MNI152NLin2009cAsym',
                            choices=['MNI152NLin2009cAsym'],
                            help='select a bold derivative in a specific space to be used')
    image_opts.add_argument('--variant_label', action='store',
                            default=None, help='select a variant bold to process')
    image_opts.add_argument('--exclude_variant_label', action='store_true',
                            default=False, help='exclude the variant from FMRIPREP')


    # BetaSeries Specific Options
    beta_series = parser.add_argument_group('Options for processing beta_series')
    beta_series.add_argument('--hrf_model', default='glover',
                             choices=['glover', 'spm', 'fir',
                                      'glover + derivative',
                                      'glover + derivative + dispersion',
                                      'spm + derivative'
                                      'spm + derivative + dispersion'],
                             help='convolve your regressors '
                                  'with one of the following hemodynamic response functions')
    beta_series.add_argument('-a', '--atlas-img', action='store',
                             help='input atlas nifti')
    beta_series.add_argument('-l', '--atlas-lut', action='store', required=True,
                             help='atlas look up table (tsv) formatted with the columns: '
                             'index, region')

    # misc options
    misc = parser.add_argument_group('misc options')
    misc.add_argument('--graph', action='store_true', default=False,
                      help='generates a graph png of the workflow')

    return parser


def main():
    from ..workflows.base import init_nibetaseries_participant_wf

    # get commandline options
    opts = get_parser().parse_args()

    # Set up directories
    # TODO: set up some sort of versioning system
    bids_dir = os.path.abspath(opts.bids_dir)

    derivatives_pipeline_dir = os.path.join(bids_dir, 'derivatives', opts.derivatives_pipeline)

    output_dir = os.path.abspath(os.path.join(opts.output_dir, 'NiBetaSeries'))
    os.makedirs(output_dir, exist_ok=True)

    log_dir = os.path.join(output_dir, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    if opts.work_dir:
        work_dir = os.path.abspath(opts.work_dir)
    else:
        work_dir = os.path.join(os.getcwd(), 'nibetaseries_work')

    os.makedirs(work_dir, exist_ok=True)

    # only for a subset of subjects
    if opts.participant_label:
        subject_list = opts.participant_label
    # for all subjects
    else:
        subject_dirs = glob(os.path.join(bids_dir, "sub-*"))
        subject_list = [subject_dir.split("-")[-1] for subject_dir in subject_dirs]

    # Nipype plugin configuration
    plugin_settings = {'plugin': 'Linear'}

    # Nipype config (logs and execution)
    ncfg.update_config({
        'logging': {'log_directory': log_dir,
                    'log_to_file': True},
        'execution': {'crashdump_dir': log_dir,
                      'crashfile_format': 'txt',
                      'parameterize_dirs': False},
    })

    # running participant level
    if opts.analysis_level == "participant":
        nibetaseries_participant_wf = init_nibetaseries_participant_wf(
            atlas_img=os.path.abspath(opts.atlas_img),
            atlas_lut=os.path.abspath(opts.atlas_lut),
            bids_dir=bids_dir,
            derivatives_pipeline_dir=derivatives_pipeline_dir,
            exclude_variant_label=opts.exclude_variant_label,
            high_pass=opts.high_pass,
            hrf_model=opts.hrf_model,
            low_pass=opts.low_pass,
            output_dir=output_dir,
            run_label=opts.run_label,
            selected_confounds=opts.confounds,
            session_label=opts.session_label,
            smoothing_kernel=opts.smoothing_kernel,
            space_label=opts.space_label,
            subject_list=subject_list,
            task_label=opts.task_label,
            variant_label=opts.variant_label,
            work_dir=work_dir,
        )

        try:
            nibetaseries_participant_wf.run(**plugin_settings)
        except RuntimeError as e:
            if "Workflow did not execute cleanly" in str(e):
                print("Workflow did not execute cleanly")
            else:
                raise e

    elif opts.analysis_level == "group":
        raise NotImplementedError('group analysis not currently implemented')
