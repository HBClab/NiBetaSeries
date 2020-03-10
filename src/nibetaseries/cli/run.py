#!/usr/bin/env python
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
from argparse import RawTextHelpFormatter
from glob import glob
from multiprocessing import cpu_count
from nipype import config as ncfg
from subprocess import check_call, CalledProcessError, TimeoutExpired
from pkg_resources import resource_filename as pkgrf
from shutil import copyfile
import logging
from pathlib import Path

logger = logging.getLogger('cli')


def get_parser():
    """Build parser object"""
    from ..__init__ import __version__
    import sys

    verstr = 'nibs v{}'.format(__version__)

    parser = argparse.ArgumentParser(description='NiBetaSeries BIDS arguments',
                                     formatter_class=RawTextHelpFormatter)
    parser.add_argument('bids_dir', help='The directory with the input dataset '
                        'formatted according to the BIDS standard.')
    parser.add_argument('derivatives_pipeline', help='Either the name of the pipeline '
                        '(e.g., fmriprep) or the directory path to the pipeline '
                        '(e.g., /some/dir/fmriprep) that contains the minimally preprocessed '
                        'img, brainmask, and confounds.tsv. '
                        'If you only give the name of the pipeline, it is assumed to be under '
                        'a derivatives directory within the bids directory '
                        '(e.g., /my/bids/derivatives).')
    parser.add_argument('output_dir', help='The directory where the output directory '
                        'and files should be stored. If you are running group level analysis '
                        'this folder should be prepopulated with the results of the'
                        'participant level analysis.')
    parser.add_argument('analysis_level', choices=['participant', 'group'],
                        help='Level of the analysis that will be performed '
                        'Multiple participant level analyses can be run independently '
                        '(in parallel) using the same output_dir')
    parser.add_argument('-v', '--version', action='version',
                        version=verstr)

    # Atlas Arguments (Required Options)
    atlas_args = parser.add_argument_group('Required Atlas Arguments')
    atlas_args.add_argument('-a', '--atlas-img', action='store',
                            required=('-l' in sys.argv or '--atlas-lut' in sys.argv),
                            help='input atlas nifti where each voxel within a "region" '
                                 'is labeled with the same integer and there is a unique '
                                 'integer associated with each region of interest.')
    atlas_args.add_argument('-l', '--atlas-lut', action='store',
                            required=('-a' in sys.argv or '--atlas-img' in sys.argv),
                            help='atlas look up table (tsv) formatted with the columns: '
                                  'index, regions which correspond to the regions in the '
                                  'nifti file specified by --atlas-img.')

    # preprocessing options
    proc_opts = parser.add_argument_group('Options for processing')
    proc_opts.add_argument('--estimator', default='lss',
                           choices=['lss', 'lsa'],
                           help='beta series modeling method')
    proc_opts.add_argument('-sm', '--smoothing-kernel', action='store', type=float, default=6.0,
                           help='select a smoothing kernel (mm)')
    proc_opts.add_argument('-hp', '--high-pass', action='store', type=float,
                           default=0.0078125, help='high pass filter (Hz)')
    proc_opts.add_argument('-c', '--confounds', help='The confound column names '
                           'that are to be included in nuisance regression. '
                           'write the confounds you wish to include separated by a space',
                           nargs="+")
    proc_opts.add_argument('--hrf-model', default='glover',
                           choices=['glover', 'spm', 'fir',
                                    'glover + derivative',
                                    'glover + derivative + dispersion',
                                    'spm + derivative',
                                    'spm + derivative + dispersion'],
                           help='convolve your regressors '
                                'with one of the following hemodynamic response functions')
    proc_opts.add_argument('--fir-delays', default=None,
                           nargs='+', type=int, help='FIR delays in volumes',
                           metavar='VOL')
    proc_opts.add_argument('-w', '--work-dir', help='directory where temporary files '
                           'are stored (i.e. non-essential files). '
                           'This directory can be deleted once you are reasonably '
                           'certain nibs finished as expected.')
    proc_opts.add_argument('--no-signal-scaling', action='store_true', default=False,
                           help='do not scale every voxel with respect to time meaning'
                                ' beta estimates will be in the same units as the bold'
                                ' signal')
    proc_opts.add_argument('--normalize-betas', action='store_true', default=False,
                           help='beta estimates will be divided by the square root '
                                'of their variance')

    # Image Selection options
    bids_opts = parser.add_argument_group('Options for selecting images')
    bids_opts.add_argument('--participant-label', nargs="+",
                           help='The label(s) of the participant(s) '
                                'that should be analyzed. The label '
                                'corresponds to sub-<participant_label> from the BIDS spec '
                                '(so it does not include "sub-"). If this parameter is not '
                                'provided all subjects should be analyzed. Multiple '
                                'participants can be specified with a space separated list.')
    bids_opts.add_argument('--session-label', action='store',
                           default=None, help='select a session to analyze')
    bids_opts.add_argument('-t', '--task-label', action='store',
                           default=None, help='select a specific task to be processed')
    bids_opts.add_argument('--run-label', action='store',
                           default=None, help='select a run to analyze')
    bids_opts.add_argument('-sp', '--space-label', action='store', default='MNI152NLin2009cAsym',
                           help='select a bold derivative in a specific space to be used')
    bids_opts.add_argument('--description-label', action='store',
                           default=None, help='select a bold file with particular '
                                              '`desc` label to process')
    bids_opts.add_argument('--exclude-description-label', action='store_true',
                           default=False, help='exclude this `desc` label from nibetaseries')
    bids_opts.add_argument('--database-path', action='store', default=None,
                           help="Path to directory containing SQLite database indicies "
                                "for this BIDS dataset. "
                                "If a value is passed and the file already exists, "
                                "indexing is skipped.")

    # performance options
    g_perfm = parser.add_argument_group('Options to handle performance')
    g_perfm.add_argument('--nthreads', '-n-cpus', action='store', type=int,
                         help='maximum number of threads across all processes')
    g_perfm.add_argument('--use-plugin', action='store', default=None,
                         help='nipype plugin configuration file')

    # misc options
    misc = parser.add_argument_group('misc options')
    misc.add_argument('--graph', action='store_true', default=False,
                      help='generates a graph png of the workflow')
    misc.add_argument('--boilerplate', action='store_true', default=False,
                      help='generate boilerplate without running workflow')

    return parser


def main():
    from ..workflows.base import init_nibetaseries_participant_wf

    # get commandline options
    opts = get_parser().parse_args()

    # check inputs
    if (opts.hrf_model == 'fir') and (opts.fir_delays is None):
        raise ValueError('If the FIR HRF model is selected, '
                         'FIR delays must be provided.')

    # Set up directories
    # TODO: set up some sort of versioning system
    bids_dir = os.path.abspath(opts.bids_dir)
    if os.path.isdir(opts.derivatives_pipeline):
        derivatives_pipeline_dir = os.path.abspath(opts.derivatives_pipeline)
    else:
        derivatives_pipeline_dir = os.path.join(bids_dir, 'derivatives', opts.derivatives_pipeline)

    if not os.path.isdir(derivatives_pipeline_dir):
        msg = "{dir} is not an available directory".format(dir=derivatives_pipeline_dir)
        raise NotADirectoryError(msg)

    output_dir = os.path.abspath(opts.output_dir)
    os.makedirs(output_dir, exist_ok=True)

    log_dir = os.path.join(output_dir, 'nibetaseries/logs')
    os.makedirs(log_dir, exist_ok=True)

    if opts.work_dir:
        work_dir = os.path.abspath(opts.work_dir)
    else:
        work_dir = os.path.join(os.getcwd(), 'nibetaseries_work')

    os.makedirs(work_dir, exist_ok=True)

    # only for a subset of subjects
    if opts.participant_label:
        subject_list = [s[4:] if s.startswith('sub-') else s
                        for s in opts.participant_label]
    # for all subjects
    else:
        subject_dirs = glob(os.path.join(bids_dir, "sub-*"))
        subject_list = [subject_dir.split("-")[-1] for subject_dir in subject_dirs]

    # Nipype plugin configuration
    # Load base plugin_settings from file if --use-plugin
    if opts.use_plugin is not None:
        from yaml import load as loadyml
        with open(opts.use_plugin) as f:
            plugin_settings = loadyml(f)
        plugin_settings.setdefault('plugin_args', {})
    else:
        # Defaults
        plugin_settings = {
            'plugin': 'MultiProc',
            'plugin_args': {
                'raise_insufficient': False,
                'maxtasksperchild': 1,
            }
        }

    # Resource management options
    # Note that we're making strong assumptions about valid plugin args
    # This may need to be revisited if people try to use batch plugins
    nthreads = plugin_settings['plugin_args'].get('n_procs')
    # Permit overriding plugin config with specific CLI options
    if nthreads is None or opts.nthreads is not None:
        nthreads = opts.nthreads
        if nthreads is None or nthreads < 1:
            nthreads = cpu_count()
        plugin_settings['plugin_args']['n_procs'] = nthreads

    # Nipype config (logs and execution)
    ncfg.update_config({
        'logging': {'log_directory': log_dir,
                    'log_to_file': True},
        'execution': {'crashdump_dir': log_dir,
                      'crashfile_format': 'txt',
                      'parameterize_dirs': False},
    })

    # check if atlas img or atlas lut exist
    if opts.atlas_img and opts.atlas_lut:
        atlas_img = os.path.abspath(opts.atlas_img)
        atlas_lut = os.path.abspath(opts.atlas_lut)
    else:
        atlas_img = atlas_lut = None

    # check if --no-signal-scaling is set
    if opts.no_signal_scaling:
        signal_scaling = False
    else:
        signal_scaling = 0

    # running participant level
    if opts.analysis_level == "participant":
        nibetaseries_participant_wf = init_nibetaseries_participant_wf(
            estimator=opts.estimator,
            atlas_img=atlas_img,
            atlas_lut=atlas_lut,
            bids_dir=bids_dir,
            database_path=opts.database_path,
            derivatives_pipeline_dir=derivatives_pipeline_dir,
            exclude_description_label=opts.exclude_description_label,
            fir_delays=opts.fir_delays,
            hrf_model=opts.hrf_model,
            high_pass=opts.high_pass,
            norm_betas=opts.normalize_betas,
            output_dir=output_dir,
            run_label=opts.run_label,
            signal_scaling=signal_scaling,
            selected_confounds=opts.confounds,
            session_label=opts.session_label,
            smoothing_kernel=opts.smoothing_kernel,
            space_label=opts.space_label,
            subject_list=subject_list,
            task_label=opts.task_label,
            description_label=opts.description_label,
            work_dir=work_dir,
        )

        if opts.graph:
            nibetaseries_participant_wf.write_graph(graph2use='colored',
                                                    format='svg',
                                                    simple_form=True)

        if not opts.boilerplate:
            try:
                nibetaseries_participant_wf.run(**plugin_settings)
            except RuntimeError as e:
                if "Workflow did not execute cleanly" in str(e):
                    print("Workflow did not execute cleanly")
                else:
                    raise e

        boilerplate = nibetaseries_participant_wf.visit_desc()
        if boilerplate:
            citation_files = {
                ext: Path(log_dir) / 'CITATION.{}'.format(ext)
                for ext in ('bib', 'tex', 'md', 'html')
            }
            # To please git-annex users and also to guarantee consistency
            # among different renderings of the same file, first remove any
            # existing one
            for citation_file in citation_files.values():
                try:
                    citation_file.unlink()
                except FileNotFoundError:
                    pass

            citation_files['md'].write_text(boilerplate)

    elif opts.analysis_level == "group":
        raise NotImplementedError('group analysis not currently implemented')

    if citation_files['md'].exists():
        # Generate HTML file resolving citations
        cmd = ['pandoc', '-s', '--bibliography',
               pkgrf('nibetaseries', 'data/references.bib'),
               '--filter', 'pandoc-citeproc',
               '--metadata', 'pagetitle="NiBetaSeries citation boilerplate"',
               str(citation_files['md']),
               '-o', str(citation_files['html'])]

        logger.info('Generating an HTML version of the citation boilerplate...')
        try:
            check_call(cmd, timeout=10)
        except (FileNotFoundError, CalledProcessError, TimeoutExpired):
            logger.warning('Could not generate CITATION.html file:\n%s',
                           ' '.join(cmd))

        # Generate LaTex file resolving citations
        cmd = ['pandoc', '-s', '--bibliography',
               pkgrf('nibetaseries', 'data/references.bib'),
               '--natbib', str(citation_files['md']),
               '-o', str(citation_files['tex'])]
        logger.info('Generating a LaTeX version of the citation boilerplate...')
        try:
            check_call(cmd, timeout=10)
        except (FileNotFoundError, CalledProcessError, TimeoutExpired):
            logger.warning('Could not generate CITATION.tex file:\n%s',
                           ' '.join(cmd))
        else:
            copyfile(pkgrf('nibetaseries', 'data/references.bib'),
                     citation_files['bib'])
    else:
        logger.warning('NiBetaSeries could not find the markdown version of '
                       'the citation boilerplate (%s). HTML and LaTeX versions'
                       ' of it will not be available', citation_files['md'])


def init():
    if __name__ == "__main__":
        raise RuntimeError("NiBetaSeries/cli/run.py should not be run directly;\n"
                           "Please `pip install` NiBetaSeries and use the `nibs` command")


init()
