import os
from nilearn import plotting
from nistats.first_level_model import first_level_models_from_bids
import nibabel as nib
import argparse
import subprocess
import numpy
from glob import glob
#BIDS
# handle registration
#    transform bold to atlas
#    use same transform for brainmask
__version__ = open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                'version')).read()

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
        if line == '' and process.poll() != None:
            break
    if process.returncode != 0:
        raise Exception("Non zero return code: %d"%process.returncode)

parser = argparse.ArgumentParser(description='BetaSeries BIDS arguments')
parser.add_argument('bids_dir', help='The directory with the input dataset '
                    'formatted according to the BIDS standard.')
parser.add_argument('derivatives_pipeline', help='The pipeline that contains minimally preprocessed '
                    'img, brainmask, and confounds.tsv')
parser.add_argument('output_dir', help='The directory where the output files '
                    'should be stored. If you are running group level analysis '
                    'this folder should be prepopulated with the results of the'
                    'participant level analysis.')
parser.add_argument('analysis_level', help='Level of the analysis that will be performed. '
                    'Multiple participant level analyses can be run independently '
                    '(in parallel) using the same output_dir.',
                    choices=['participant', 'group'])
parser.add_argument('--participant_label', help='The label(s) of the participant(s) that should be analyzed. The label '
                   'corresponds to sub-<participant_label> from the BIDS spec '
                   '(so it does not include "sub-"). If this parameter is not '
                   'provided all subjects should be analyzed. Multiple '
                   'participants can be specified with a space separated list.',
                   nargs="+")
parser.add_argument('-v', '--version', action='version',
                    version='nistat_betaseries {}'.format(__version__))
# Derivative Specific Options
derivatives =  parser.add_argument_group('Options for derivatives')
derivatives.add_argument('-t', '--task_id', action='store',
                         help='select a specific task to be processed')
derivatives.add_argument('-s', '--space', action='store',
                         help='select a bold derivative in a specific space to be used')
derivatives.add_argument('--variant', action='store',
                         help='select a variant bold to process')
derivatives.add_argument('-r', '--res', action='store',
                         help='select a resolution to analyze')
# BetaSeries Specific Options
beta_series = parser.add_argument_group('Options for processing beta_series')
#
beta_series.add_argument('--hrf_model', help='',
                         choices=['glover', 'spm', 'fir',
                         'gloverDerivative',
                         'gloverDerivativeDispersion',
                         'spmDerivative'
                         'spmDerivativeDispersion'])

beta_series.add_argument()
args = parser.parse_args()

run('bids-validator %s'%args.bids_dir)

subjects_to_analyze = []
# only for a subset of subjects
if args.participant_label:
    subjects_to_analyze = args.participant_label
# for all subjects
else:
    subject_dirs = glob(os.path.join(args.bids_dir, "sub-*"))
    subjects_to_analyze = [subject_dir.split("-")[-1] for subject_dir in subject_dirs]

# running participant level
if args.analysis_level == "participant":


# check docs about hrf_model

models, models_run_imgs, models_events, models_confounds = first_level_models_from_bids(
        data_dir2, task_label, space_label,
        t_r=2.0, slice_time_ref=0.5,
        hrf_model='glover + derivative + dispersion',
        #find a general mask?
        mask='template',
        signal_scaling=0, verbose=3, n_jobs=-2,
        derivatives_folder=derivatives_folder,
        img_filters=[('variant', 'smoothAROMAnonaggr')])

for sub_idx,sub_model in enumerate(models):
    for run_idx, run_events in enumerate(models_events[sub_idx]):
        run_events.sort_values(columns=['trial_type', 'onset'],ascending=[True, True],inplace=True,axis=0)
        run_events_temp = run_events.copy()
        run_events_temp['trial_type'] = 'other_trials'
        for trial in range(len(run_events)):
            #if the condition changes (make sure to order the conditions)
            if trial != 0 and run_events.loc[trial, 'trial_type'] != run_events.loc[trial-1, 'trial_type']:

            run_events_temp.loc[trial, 'trial_type'] = run_events.loc[trial, 'trial_type']
            #fitmodel
            sub_model.fit(models_run_imgs[sub_idx][run_idx],run_events_temp)
            #compute contrast
            img = sub_model.compute_contrast(contrast_def=run_events_temp.loc[trial, 'trial_type'], output_type='effect_size')
            #save img
            nib.save(img, os.path.join(data_dir2,'derivatives/nistats_betaseries/sub-GE140_2','sub-GE140'+run_events_temp.loc[trial,'trial_type']+str(trial)))
            run_events_temp.loc[trial, 'trial_type'] = 'other_trials'
            
# running group level
elif args.analysis_level == "group":
    brain_sizes = []
    for subject_label in subjects_to_analyze:
        for brain_file in glob(os.path.join(args.output_dir, "sub-%s*.nii*"%subject_label)):
            data = nib.load(brain_file).get_data()
            # calcualte average mask size in voxels
            brain_sizes.append((data != 0).sum())
