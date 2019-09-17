---
title: 'NiBetaSeries: task related correlations in fMRI'
tags:
  - Python
  - neuroscience
  - neuroimaging
  - BIDS
  - fMRI
authors:
  - name: James D. Kent
    orcid: 0000-0002-4892-2659
    affiliation: 1
  - name: Peer Herholz
    orcid: 0000-0002-9840-6257
    affiliation: 2
affiliations:
 - name: Interdisciplinary Graduate Program in Neuroscience, University of Iowa, Iowa City, United states of America
   index: 1
 - name: Montréal Neurological Institute, McGill University Health Centre, Montreal, Quebec, Canada
   index: 2
date: 30 January 2019
bibliography: paper.bib
---

# Background

You may not be aware of it, but your brain is orchestrating a complex ballet of activity while reading this sentence.
Whether it is following a dot or reading a sentence; the brain is evaluating input and sending motoric output to perform optimally/efficiently.
We can measure this flurry of activity using functional Magnetic Resonance Imaging (fMRI).
Traditional fMRI analysis emphasizes what regions are "activated/deactivated" during a task, but it does not provide information about which regions are acting in synchrony or are being segregated.
Knowing the synchronous/segregated brain regions during a task gives insights on the potential organization of the brain.
**NiBetaSeries seeks to provide information about the organization of the brain by correlating activation/deactivation patterns between brain regions during a task.**

To understand NiBetaSeries we need to answer two questions: what is a "beta" (or parameter estimate) and how can we analyze a series of betas?
We have already mentioned betas by another name, activation/deactivation.
The term beta comes from its use in the General Linear Model (GLM), which is an extension of linear regression.
fMRI signal evoked by a stimulus follows a relatively stereotyped shape from the Blood Oxygen Level Dependent (BOLD) response, which is reasonably modeled with a double-gamma function.
The overall amplitude (i.e., activation/deactivation) of the double gamma function is determined by the beta coefficient.
Thus larger betas mean greater activation and smaller or negative betas mean less activation or deactivation relative to a baseline.
Traditional fMRI analysis will group together all trials of a single type and give them all one beta estimate, where variance between trials is treated as noise.
NiBetaSeries, on the other hand, gives each trial its own beta estimate treating the variance between trials as the signal of interest.

Two common methods for deriving single trial beta estimates are least squares all (LSA) and least squares separate (LSS) [@Mumford2012;@Turner2012a].
LSA places all the trials in the same GLM, where each trial is a separate predictor.
LSA works well when the trials are far apart in time because the BOLD response takes a long time to return to baseline.
When the trials are close together, however, the bold responses start to overlap and the GLM cannot accurately attribute the variance in the fMRI data to a single trial, leading to unreliable beta estimates.
LSS tackles this problem by making as many GLMs as there are trials.
For each trial, a GLM is created with two predictors: one is the trial of interest and the second is the combination of all the other trials.
LSS reduces the amount of overlap (or more accurately correlation) between predictors, leading to more reliable individual beta estimates.
NiBetaSeries currently implements LSS making the software a reasonable analysis choice for
experiments with trials that occur close together (e.g., 3-7 seconds apart on average).
The output of LSA or LSS is a beta series for each voxel in the dataset.

There is a wealth of analysis methods applicable to beta series datasets.
To review the structure of our data, we have a beta estimate for each trial within every voxel in the brain, resulting in a 4-dimensional (`4D`) dataset.
The first three dimensions represent the voxel dimensions, and the 4th dimension represents the number of trials.
For many intents and purposes, the `4D` beta series can be analyzed similarly to a `4D`
resting state dataset where the 4th dimension represents time.
Traditional analysis strategies applied to resting state such as seed based correlation,
independent components analysis, regional homogeneity, and graph theory can be applied to
beta series [@Cole2010;@vanWijk2010].
Recycling these methods for beta series provides a new lens to observe the organization of the brain during a task and may lead to additional insights.

# Software Overview

NiBetaSeries presents as a command line utility written in Python following the template of a BIDS-App [@Gorgolewski2017].
NiBetaSeries is available on [pypi](https://pypi.org/project/nibetaseries/) and as an container
on [dockerhub](https://hub.docker.com/r/hbclab/nibetaseries) with [comprehensive documentation](https://nibetaseries.readthedocs.io/en/latest/) complete with an interactive example.
The primary way to interact with NiBetaSeries is typing `nibs` in the command line.
The basic workflow of NiBetaSeries follows these steps (the files can be found in the `workflows` directory):

1) `base.py`: Read and validate necessary inputs (a minimally processed fMRI file, a brain mask, an events file specifying the onsets, duration, and the trial type, an atlas parcellation, and a table connecting the numbers in the atlas parcellation with names of the regions).
2) `model.py`: Construct and execute GLMs using LSS (with additional confound predictors optionally added) generating a beta series (a list of betas for each voxel).
3) `analysis.py`: Apply atlas parcellation to data averaging betas within regions for each trial.
4) `analysis.py`: Correlate each region's list of betas with every other region.
5) `analysis.py`: r-z transform the correlations and output a symmetric correlation matrix in a `tsv` file.

The correlation matrix from NiBetaSeries can be used for graph theoretical applications, specific region-region correlations across different trial types, and other analyses.

NiBetaSeries is not the first or only piece of software that measures task related correlations in the brain.
There are two other packages known to the authors: BASCO and Pybetaseries [@Gottlich2015; @Poldrack2014].
BASCO (BetA Series COrrelations) is a Matlab toolbox that calculates task correlations, but is designed for slow event related designs (e.g., trials occur more than 10 seconds apart).
Pybetaseries is a Python script that is designed for fast event related designs (like NiBetaSeries), but is no longer actively maintained.
Given the drawbacks of the alternatives, NiBetaSeries justifies its existence and utility to the neuroscience field.

# Acknowledgements

Conceptualization of the BetaSeries Method is credited to Jesse Rissman [@Rissman2004],
and the LSS method to Benjamin Turner [@Turner2012a] with validation by Jeanette Mumford [@Mumford2012] and Hunar Abdulrahman [@Abdulrahman2016].
Michelle Voss provided guidance over the entirety of the project with funding from the National Institutes of Health (5R01AG055500).
The organization of the code is indebted to `fmriprep` and their developers/maintainers for inspiration [@Esteban2019].
Thanks to Neurohackademy for providing new contributors.
Neurohackademy is funded by the National Institute of Mental Health through a grant to Ariel Rokem and Tal Yarkoni (R25MH112480).
Finally, all the contributors listed in `zenodo` and `github` have contributed code and intellectual labor to NiBetaSeries pushing the project to new heights.

# References