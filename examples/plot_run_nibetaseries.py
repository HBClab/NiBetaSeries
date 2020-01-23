"""
Running NiBetaSeries
====================

This example runs through a basic call of NiBetaSeries using
the commandline entry point ``nibs``.
While this example is using python, typically ``nibs`` will be
called directly on the commandline.
"""

#############################################################################
# Import all the necessary packages
# =================================

import tempfile  # make a temporary directory for files
import os  # interact with the filesystem
import urllib.request  # grad data from internet
import tarfile  # extract files from tar
from subprocess import Popen, PIPE, STDOUT  # enable calling commandline

import matplotlib.pyplot as plt  # manipulate figures
import seaborn as sns  # display results
import pandas as pd   # manipulate tabular data
import nibabel as nib  # load the beta maps in python
from nilearn import plotting  # plot nifti images

#############################################################################
# Download relevant data from ds000164 (and Atlas Files)
# ======================================================
# The subject data came from `openneuro
# <https://openneuro.org/datasets/ds000164/versions/00001/>`_
# :cite:`n-Verstynen2014`.
# The atlas data came from a `recently published parcellation
# <https://www.ncbi.nlm.nih.gov/pubmed/28981612>`_
# in a publically accessible github repository.

# atlas github repo for reference:
"""https://github.com/ThomasYeoLab/CBIG/raw/master/stable_projects/\
brain_parcellation/Schaefer2018_LocalGlobal/Parcellations/MNI/"""
data_dir = tempfile.mkdtemp()
print('Our working directory: {}'.format(data_dir))

# download the tar data
url = "https://www.dropbox.com/s/fvtyld08srwl3x9/ds000164-test_v2.tar.gz?dl=1"
tar_file = os.path.join(data_dir, "ds000164.tar.gz")
u = urllib.request.urlopen(url)
data = u.read()
u.close()

# write tar data to file
with open(tar_file, "wb") as f:
    f.write(data)

# extract the data
tar = tarfile.open(tar_file, mode='r|gz')
tar.extractall(path=data_dir)

os.remove(tar_file)

#############################################################################
# Display the minimal dataset necessary to run nibs
# =================================================


# https://stackoverflow.com/questions/9727673/list-directory-tree-structure-in-python
def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))


list_files(data_dir)

#############################################################################
# Manipulate events file so it satifies assumptions
# =================================================
# 1. the correct column has 1's and 0's corresponding to correct and incorrect,
# respectively.
# 2. the condition column is renamed to trial_type
# nibs currently depends on the "correct" column being binary
# and the "trial_type" column to contain the trial types of interest.

#############################################################################
# read the file
# -------------

events_file = os.path.join(data_dir,
                           "ds000164",
                           "sub-001",
                           "func",
                           "sub-001_task-stroop_events.tsv")
events_df = pd.read_csv(events_file, sep='\t', na_values="n/a")
print(events_df.head())

#############################################################################
# replace condition with trial_type
# ---------------------------------

events_df.rename({"condition": "trial_type"}, axis='columns', inplace=True)
print(events_df.head())

#############################################################################
# save the file
# -------------

events_df.to_csv(events_file, sep="\t", na_rep="n/a", index=False)

#############################################################################
# Manipulate the region order file
# ================================
# There are several adjustments to the atlas file that need to be completed
# before we can pass it into nibs.
# Importantly, the relevant column names **MUST** be named "index" and "regions".
# "index" refers to which integer within the file corresponds to which region
# in the atlas nifti file.
# "regions" refers the name of each region in the atlas nifti file.

#############################################################################
# read the atlas file
# -------------------

atlas_txt = os.path.join(data_dir,
                         "ds000164",
                         "derivatives",
                         "data",
                         "Schaefer2018_100Parcels_7Networks_order.txt")
atlas_df = pd.read_csv(atlas_txt, sep="\t", header=None)
print(atlas_df.head())

#############################################################################
# drop color coding columns
# -------------------------

atlas_df.drop([2, 3, 4, 5], axis='columns', inplace=True)
print(atlas_df.head())

#############################################################################
# rename columns with the approved headings: "index" and "regions"
# ----------------------------------------------------------------

atlas_df.rename({0: 'index', 1: 'regions'}, axis='columns', inplace=True)
print(atlas_df.head())

#############################################################################
# remove prefix "7Networks"
# -------------------------

atlas_df.replace(regex={'7Networks_(.*)': '\\1'}, inplace=True)
print(atlas_df.head())

#############################################################################
# write out the file as .tsv
# --------------------------

atlas_tsv = atlas_txt.replace(".txt", ".tsv")
atlas_df.to_csv(atlas_tsv, sep="\t", index=False)

#############################################################################
# Run nibs
# ========
# This demonstration mimics how you would use nibs on the command line
# If you only wanted the beta maps and not the correlation matrices, do not
# include the atlas (-a) and lookup table options (-l)

out_dir = os.path.join(data_dir, "ds000164", "derivatives")
work_dir = os.path.join(out_dir, "work")
atlas_mni_file = os.path.join(data_dir,
                              "ds000164",
                              "derivatives",
                              "data",
                              "Schaefer2018_100Parcels_7Networks_order_FSLMNI152_2mm.nii.gz")
cmd = """\
nibs -c WhiteMatter CSF \
--participant-label 001 \
--estimator lsa \
--hrf-model glover \
-w {work_dir} \
-a {atlas_mni_file} \
-l {atlas_tsv} \
{bids_dir} \
fmriprep \
{out_dir} \
participant
""".format(atlas_mni_file=atlas_mni_file,
           atlas_tsv=atlas_tsv,
           bids_dir=os.path.join(data_dir, "ds000164"),
           out_dir=out_dir,
           work_dir=work_dir)

# Since we cannot run bash commands inside this tutorial
# we are printing the actual bash command so you can see it
# in the output
print("The Example Command:\n", cmd)

# call nibs
p = Popen(cmd, shell=True, stdout=PIPE, stderr=STDOUT)

while True:
    line = p.stdout.readline()
    if not line:
        break
    print(line)

#############################################################################
# Observe generated outputs
# =========================

list_files(data_dir)

#############################################################################
# Collect correlation results
# ===========================

output_path = os.path.join(out_dir, "nibetaseries", "sub-001", "func")
trial_types = ['congruent', 'incongruent', 'neutral']
filename_template = ('sub-001_task-stroop_space-MNI152NLin2009cAsym_'
                     'desc-{trial_type}_{suffix}.{ext}')

pd_dict = {}
for trial_type in trial_types:
    fname = filename_template.format(trial_type=trial_type, suffix='correlation', ext='tsv')
    file_path = os.path.join(output_path, fname)
    pd_dict[trial_type] = pd.read_csv(file_path, sep='\t', na_values="n/a", index_col=0)
# display example matrix
print(pd_dict[trial_type].head())

#############################################################################
# Graph the correlation results
# =============================

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

#############################################################################
# Collect beta map results
# ========================

nii_dict = {}
for trial_type in trial_types:
    fname = filename_template.format(trial_type=trial_type, suffix='betaseries', ext='nii.gz')
    file_path = os.path.join(output_path, fname)
    nii_dict[trial_type] = nib.load(file_path)

# view incongruent beta_maps
nib.viewers.OrthoSlicer3D(nii_dict['incongruent'].get_fdata(),
                          title="Incongruent Betas").set_position(10, 13, 10)

#############################################################################
# Graph beta map standard deviation
# =================================
# We can find where the betas have the highest standard deviation for each trial type.
# Unsuprisingly, the largest deviations are near the edge of the brain mask and
# the subcortical regions.

# standard deviations for each trial type
std_dict = {tt: nib.Nifti1Image(img.get_fdata().std(axis=-1), img.affine, img.header)
            for tt, img in nii_dict.items()}

fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(10, 20))

for idx, (trial_type, nii) in enumerate(std_dict.items()):
    plotting.plot_stat_map(nii, title=trial_type, cut_coords=(0, 0, 0),
                           threshold=5, vmax=20, axes=axes[idx])
#############################################################################
# References
# ==========
# .. bibliography:: ../../src/nibetaseries/data/references.bib
#    :style: plain
#    :labelprefix: notebook-
#    :keyprefix: n-
#
