"""
Running NiBetaSeries using ds000164 (Stroop Task)
===============================================================

This example runs through a basic call of NiBetaSeries using
the commandline entry point ``nibs``.
While this example is using python, typically `nibs` will be
called directly on the commandline.

To run this locally, you also need ``awscli`` installed via
``pip install awscli``
"""

#############################################################################
# Import all the necessary packages
# =================================

import tempfile  # make a temporary directory for files
import os  # interact with the filesystem
from subprocess import call, Popen, PIPE, STDOUT  # enable calling commandline

import matplotlib.pyplot as plt  # manipulate figures
import seaborn as sns  # display results
import pandas as pd   # manipulate tabular data
from datalad.api import install  # use datalad for file retrieval

#############################################################################
# Download relevant data from ds000164
# ====================================

data_dir = tempfile.mkdtemp()
print('Our working directory: {}'.format(data_dir))

# here on openneuro: https://openneuro.org/datasets/ds000164/versions/00001
# I'm using openfmri since I'm getting an error with openneuro
dataset = install(data_dir, "///openfmri/ds000164")

# selecting subject that has fmriprep
bids_data = os.path.join("sub-001", "func")
dataset.get(bids_data)
events_file = os.path.join(dataset.path, bids_data,
                           "sub-001_task-stroop_events.tsv")
print("the events file: {}".format(events_file))

#############################################################################
# Manipulate events file so it satifies assumptions
# =================================================
# 1. the correct column has 1's and 0's corresponding to correct and incorrect,
# respectively.
# 2. the condition column is renamed to trial_type

#############################################################################
# read the file
# -------------
events_df = pd.read_csv(events_file, sep='\t', na_values="n/a")
events_df.head()

#############################################################################
# change the Y/N to 1/0
# ---------------------
events_df['correct'].replace({"Y": 1, "N": 0}, inplace=True)
events_df.head()

#############################################################################
# replace condition with trial_type
# ---------------------------------
events_df.rename({"condition": "trial_type"}, axis='columns', inplace=True)
events_df.head()

#############################################################################
# save the file
# -------------
# files tracked by git-annex need to be unlocked
dataset.unlock(events_file)
# save the updated event file
events_df.to_csv(events_file, sep="\t", na_rep="n/a", index=False)
# git-annex the file
dataset.save(events_file)

#############################################################################
# Download the fmriprep results
# =============================

fmriprep_res = """s3://openneuro.outputs/\
921294bd5b869b1852ab3ce886583795/4dd151e3-52d1-4fa2-9591-27c16520331c"""

# datalad command currently not working
# dataset.download_url(fmriprep_res)
# depends on user having awscli installed: https://pypi.org/project/awscli/
call([
      'aws',
      '--no-sign-request',
      's3',
      'sync',
      fmriprep_res,
      os.path.join(data_dir, 'derivatives')
     ])

# path to the downloaded results
fmriprep_path = os.path.join(dataset.path, "derivatives", "fmriprep", "sub-001", "func")
# display the files
os.listdir(fmriprep_path)

#############################################################################
# Download a parcelation atlas and region order file
# ==================================================

# Download the schaefer atlas: https://www.ncbi.nlm.nih.gov/pubmed/28981612
schaefer_base_url = """https://github.com/ThomasYeoLab/CBIG/raw/master/stable_projects/\
brain_parcellation/Schaefer2018_LocalGlobal/Parcellations/MNI/"""
schaefer_mni = "Schaefer2018_100Parcels_7Networks_order_FSLMNI152_2mm.nii.gz"
schaefer_txt = "Schaefer2018_100Parcels_7Networks_order.txt"
schaefer_mni_url = schaefer_base_url + schaefer_mni
schaefer_txt_url = schaefer_base_url + schaefer_txt
download_dir = os.path.join(dataset.path, "derivatives", "data")
os.makedirs(download_dir, exist_ok=True)
dataset.download_url([schaefer_mni_url, schaefer_txt_url],
                     path=download_dir,
                     overwrite=True)
# specify the nifti file
atlas_mni_file = os.path.join(download_dir, schaefer_mni)

#############################################################################
# Manipulate the region order file
# ================================

#############################################################################
# read the atlas file
# -------------------

atlas_txt = os.path.join(download_dir, schaefer_txt)
atlas_df = pd.read_csv(atlas_txt, sep="\t", header=None)
atlas_df.head()

#############################################################################
# drop coordinate columns
# -----------------------

atlas_df.drop([2, 3, 4, 5], axis='columns', inplace=True)
atlas_df.head()

#############################################################################
# rename columns with the approved headings: "index" and "regions"
# ----------------------------------------------------------------

atlas_df.rename({0: 'index', 1: 'regions'}, axis='columns', inplace=True)
atlas_df.head()

#############################################################################
# remove prefix "7Networks"
# -------------------------

atlas_df.replace(regex={'7Networks_(.*)': '\\1'}, inplace=True)
atlas_df.head()

#############################################################################
# write out the file
# ------------------

atlas_tsv = atlas_txt.replace(".txt", ".tsv")
atlas_df.to_csv(atlas_tsv, sep="\t", index=False)

#############################################################################
# Run nibs
# ========
out_dir = os.path.join(dataset.path, "derivatives")
cmd = """\
nibs -c WhiteMatter CSF \
--participant_label 001 \
-a {atlas_mni_file} \
-l {atlas_tsv} \
{bids_dir} \
fmriprep \
{out_dir} \
participant
""".format(atlas_mni_file=atlas_mni_file,
           atlas_tsv=atlas_tsv,
           bids_dir=dataset.path,
           out_dir=out_dir)
# call nibs
p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)

while True:
    line = p.stdout.readline()
    if not line:
        break
    print(line)

#############################################################################
# Collect results
# ===============

corr_mat_path = os.path.join(out_dir, "NiBetaSeries", "nibetaseries", "sub-001", "func")
trial_types = ['congruent', 'incongruent', 'neutral']
filename_template = "sub-001_task-stroop_bold_space-MNI152NLin2009cAsym_preproc_trialtype-{trial_type}_matrix.tsv"
pd_dict = {}
for trial_type in trial_types:
    file_path = os.path.join(corr_mat_path, filename_template.format(trial_type=trial_type))
    pd_dict[trial_type] = pd.read_csv(file_path, sep='\t', na_values="n/a", index_col=0)
# display example matrix
pd_dict[trial_type].head()

#############################################################################
# Graph the results
# =================

fig, axes = plt.subplots(nrows=3, ncols=1, sharex=True, sharey=True, figsize=(10, 30),
                         gridspec_kw={'wspace': 0.025, 'hspace': 0.075})

cbar_ax = fig.add_axes([.91, .3, .03, .4])
r = 0
for trial_type, df in pd_dict.items():
    g = sns.heatmap(df, ax=axes[r], vmin=-.5, vmax=1., square=True,
                    cbar=True, cbar_ax=cbar_ax)
    axes[r].set_title(trial_type)
    # iterate over rows
    r += 1
plt.tight_layout()
