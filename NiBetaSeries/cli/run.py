#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
from multiprocessing import cpu_count
# from nilearn import plotting
# import nibabel as nib
import argparse
import subprocess
# import numpy
from glob import glob
# from bids.grabbids import BIDSLayout
from niworkflows.nipype import config as ncfg
from time import strftime
import uuid
from ..version import __version__
# BIDS
# handle registration
#    transform bold to atlas
#    use same transform for brainmask
# __version__ = open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
# 'version')).read()


def run(command, env={}):
    merged_env = os.environ
    merged_env.update(env)
    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, shell=True,
                               env=merged_env)
    while True:
        line = process.stdout.readline()
        line = str(line, 'utf-8')[:-1]
        print(line)
        if line == '' and process.poll() is not None:
            break
    if process.returncode != 0:
        raise Exception("Non zero return code: %d" % process.returncode)


def get_parser():
    """Build parser object"""

    verstr = 'NiBetaSeries v{}'.format(__version__)

    parser = argparse.ArgumentParser(description='NiBetaSeries BIDS arguments')
    parser.add_argument('bids_dir', help='The directory with the input dataset '
                        'formatted according to the BIDS standard.')
    parser.add_argument('derivatives_pipeline', help='The pipeline that contains '
                        'minimally preprocessed img, brainmask, and confounds.tsv')
    parser.add_argument('output_dir', help='The directory where the output files '
                        'should be stored. If you are running group level analysis '
                        'this folder should be prepopulated with the results of the'
                        'participant level analysis.')
    parser.add_argument('analysis_level', help='Level of the analysis that will be performed '
                        'Multiple participant level analyses can be run independently '
                        '(in parallel) using the same output_dir',
                        choices=['participant', 'group'])
    parser.add_argument('--participant_label', help='The label(s) of the participant(s) '
                        'that should be analyzed. The label '
                        'corresponds to sub-<participant_label> from the BIDS spec '
                        '(so it does not include "sub-"). If this parameter is not '
                        'provided all subjects should be analyzed. Multiple '
                        'participants can be specified with a space separated list.',
                        nargs="+")
    parser.add_argument('-v', '--version', action='version',
                        version='NiBetaSeries {}'.format(__version__))

    # preprocessing options
    proc_opts = parser.add_argument_group('Options for preprocessing')
    proc_opts.add_argument('-sm', '--smooth', action='store', type=float,
                           help='select a smoothing kernel (mm)')
    proc_opts.add_argument('-l', '--low_pass', action='store', type=float,
                           default=None, help='low pass filter')
    proc_opts.add_argument('-f', '--regfilt', action='store_true', default=False,
                           help='Do non-aggressive filtering from ICA-AROMA')
    proc_opts.add_argument('-c', '--confounds', help='The confound column names '
                           'that are to be included in nuisance regression. '
                           'write the confounds you wish to include separated by a space',
                           nargs="+")

    # Image Selection options
    image_opts = parser.add_argument_group('Options for selecting images')
    image_opts.add_argument('-t', '--task_id', action='store',
                            default=None, help='select a specific task to be processed')
    image_opts.add_argument('-sp', '--space', action='store',
                            default=None, help='select a bold derivative in a '
                                               'specific space to be used')
    image_opts.add_argument('--variant', action='store',
                            default=None, help='select a variant bold to process')
    image_opts.add_argument('--exclude_variant', action='store_true',
                            default=False, help='exclude the variant from FMRIPREP')
    image_opts.add_argument('-r', '--res', action='store',
                            default=None, help='select a resolution to analyze')
    image_opts.add_argument('--run', action='store',
                            default=None, help='select a run to analyze')
    image_opts.add_argument('--ses', action='store',
                            default=None, help='select a session to analyze')

    # BetaSeries Specific Options
    beta_series = parser.add_argument_group('Options for processing beta_series')
    beta_series.add_argument('--hrf_model', help='convolve your regressors '
                             'with one of the following hrfs',
                             choices=['glover', 'spm', 'fir',
                                      'gloverDerivative',
                                      'gloverDerivativeDispersion',
                                      'spmDerivative'
                                      'spmDerivativeDispersion'])
    beta_series.add_argument('--slice_time_ref', help='If slice time correction '
                             'was applied select the reference slice: '
                             'the reference slice is idenfied as a percentage of '
                             'the scan volume, for example, if the '
                             'refenence slice is the beginning then the value is '
                             '0, if it is in the middle, the value is '
                             '0.5, and if the reference slice is at the end, the value is 1',
                             action='store', default=0.5)

    # performance options
    g_perfm = parser.add_argument_group('Options to handle performance')
    g_perfm.add_argument('--nthreads', '--n_cpus', '-n-cpus', action='store', default=0, type=int,
                         help='maximum number of threads across all processes')
    g_perfm.add_argument('--omp-nthreads', action='store', type=int, default=0,
                         help='maximum number of threads per-process')
    g_perfm.add_argument('--mem_mb', '--mem-mb', action='store', default=0, type=int,
                         help='upper bound memory limit for NiBetaSeries processes')
    g_perfm.add_argument('--use-plugin', action='store', default=None,
                         help='nipype plugin configuration file')

    # misc options
    misc = parser.add_argument_group('misc options')
    misc.add_argument('--bids_check', help='Validates the input bids dataset, '
                      'requires the installation of \'bids-validator\'',
                      action='store_true')
    misc.add_argument('--graph', action='store_true', default=False,
                      help='generates a graph png of the workflow')

    return parser


def validate_bids_ds(bids_dir):
    """validate bids dataset"""
    run('bids-validator %s' % bids_dir)


def main():
    from ..workflows.base import init_nibetaseries_participant_wf
    # Set up some instrumental utilities
    errno = 0
    run_uuid = strftime('%Y%m%d-%H%M%S_') + str(uuid.uuid4())

    # get commandline options
    opts = get_parser().parse_args()

    bids_dir = os.path.abspath(opts.bids_dir)

    # check if bids directory is valid
    if opts.bids_check:
        validate_bids_ds(opts.bids_dir)

    # Set up directories
    # TODO: set up some sort of versioning system
    output_dir = os.path.abspath(opts.output_dir)
    log_dir = os.path.join(output_dir, 'NiBetaSeries', 'logs')
    work_dir = os.path.abspath(opts.work_dir)

    # Nipype config (logs and execution)
    ncfg.update_config({
        'logging': {'log_directory': log_dir,
                    'log_to_file': True},
        'execution': {'crashdump_dir': log_dir,
                      'crashfile_format': 'txt'},
    })

    # only for a subset of subjects
    if opts.participant_label:
        subject_list = opts.participant_label
    # for all subjects
    else:
        subject_dirs = glob(os.path.join(opts.bids_dir, "sub-*"))
        subject_list = [subject_dir.split("-")[-1] for subject_dir in subject_dirs]

    # Nipype plugin configuration
    plugin_settings = {'plugin': 'Linear'}
    nthreads = opts.nthreads
    if opts.use_plugin is not None:
        from yaml import load as loadyml
        with open(opts.use_plugin) as f:
            plugin_settings = loadyml(f)
    else:
        # Setup multiprocessing
        nthreads = opts.nthreads
        if nthreads == 0:
            nthreads = cpu_count()

        if nthreads > 1:
            plugin_settings['plugin'] = 'MultiProc'
            plugin_settings['plugin_args'] = {'n_procs': nthreads}
            if opts.mem_mb:
                plugin_settings['plugin_args']['memory_gb'] = opts.mem_mb / 1024

    omp_nthreads = opts.omp_nthreads
    if omp_nthreads == 0:
        omp_nthreads = min(nthreads - 1 if nthreads > 1 else cpu_count(), 8)

    if 1 < nthreads < omp_nthreads:
        raise RuntimeError(
            'Per-process threads (--omp-nthreads={:d}) cannot exceed total '
            'threads (--nthreads/--n_cpus={:d})'.format(omp_nthreads, nthreads))

    # running participant level
    if opts.analysis_level == "participant":

        nibetaseries_participant_wf = init_nibetaseries_participant_wf(
            bids_dir=bids_dir,
            derivatives_pipeline=opts.derivatives_pipeline,
            exclude_variant=opts.exclude_variant,
            hrf_model=opts.hrf_model,
            omp_nthreads=omp_nthreads,
            output_dir=output_dir,
            res=opts.res,
            run=opts.run,
            run_uuid=run_uuid,
            slice_time_ref=opts.slice_time_ref,
            space=opts.space,
            subject_list=subject_list,
            task_id=opts.task_id,
            variant=opts.variant,
            work_dir=work_dir,
        )

    try:
        nibetaseries_participant_wf.run(**plugin_settings)
    except RuntimeError as e:
        if "Workflow did not execute cleanly" in str(e):
            # variable currently not used
            errno = 1
        else:
            raise(e)

    # models, models_run_imgs, models_events, models_confounds = first_level_models_from_bids(
    #         data_dir2, task_label, space_label,
    #         t_r=2.0, slice_time_ref=0.5,
    #         hrf_model='glover + derivative + dispersion',
    #         #find a general mask?
    #         mask='template',
    #         signal_scaling=0, verbose=3, n_jobs=-2,
    #         derivatives_folder=derivatives_folder,
    #         img_filters=[('variant', 'smoothAROMAnonaggr')])

    # for sub_idx,sub_model in enumerate(models):
    #     for run_idx, run_events in enumerate(models_events[sub_idx]):
    #         run_events.sort_values(columns=['trial_type', 'onset'],
    #                                ascending=[True, True],inplace=True,axis=0)
    #         run_events_temp = run_events.copy()
    #         run_events_temp['trial_type'] = 'other_trials'
    #         for trial in range(len(run_events)):
    #             #if the condition changes (make sure to order the conditions)
    #             if trial != 0 and
    #                 run_events.loc[trial, 'trial_type'] !=
    #                 run_events.loc[trial-1, 'trial_type']:

    #             run_events_temp.loc[trial, 'trial_type'] = run_events.loc[trial, 'trial_type']
    #             #fitmodel
    #             sub_model.fit(models_run_imgs[sub_idx][run_idx],run_events_temp)
    #             #compute contrast
    #             img = sub_model.compute_contrast(
    #                contrast_def=run_events_temp.loc[trial, 'trial_type'],
    #                output_type='effect_size')
    #             #save img
    #             nib.save(img,
    #                      os.path.join(data_dir2,'derivatives/nistats_betaseries/sub-GE140_2',
    #                      'sub-GE140'+run_events_temp.loc[trial,'trial_type']+str(trial)))
    #             run_events_temp.loc[trial, 'trial_type'] = 'other_trials'

    # # running group level
    # elif args.analysis_level == "group":
    #     brain_sizes = []
    #     for subject_label in subjects_to_analyze:
    #         for brain_file in glob(os.path.join(args.output_dir, "sub-%s*.nii*"%subject_label)):
    #             data = nib.load(brain_file).get_data()
    #             # calcualte average mask size in voxels
    #             brain_sizes.append((data != 0).sum())


if __name__ == '__main__':
    raise RuntimeError("fmriprep/cli/run.py should not be run directly;\n"
                       "Please `pip install` fmriprep and use the `fmriprep` command")
