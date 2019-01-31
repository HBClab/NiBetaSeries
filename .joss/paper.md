---
title: 'NiBetaSeries: task related correlations in fMRI'
tags:
  - python
  - neuroscience
  - neuroimaging
  - BIDS
  - fMRI
authors:
  - name: James D. Kent
    orcid: 0000-0002-4892-2659
    affiliation: 1
affiliations:
 - name: Neuroscience Program, University of Iowa
   index: 1
date: 30 January 2019
bibliography: paper.bib
---

# Introduction

You may not be aware of it, but your brain is orchestrating a complex ballet of activity while reading this sentence.
Whether it is following a dot, reading a sentence, interpreting what response is required when presented a red square; the brain is evaluating input and sending motoric output to perform optimally/efficiently.
We can measure and analyze this flurry of activity using functional Magnetic Resonance Imaging (fMRI).
Traditional fMRI analysis emphasizes what regions are "activated/deactivated" during a task, but does not provide information on which regions are acting in synchrony.
Knowing what regions are synchronous during a task gives insights on the potential organization of the brain.
Additionally, the information could open new inquiries about how different tasks show different synchronicity and whether synchrony between brain regions correlates with performance on a particular task.
NiBetaSeries seeks to fill this gap by providing a method to measure how activation patterns between brain regions are correlated across trials.
That is to say if region A and region B both show high activity on trial 1, low activity on trial 2, medium activity on trial 3, and so on, then these two regions are highly correlated.

# Background

To understand NiBetaSeries we need to answer two questions: what is a "beta" and what is an "atlas parcellation"?
We have already mentioned betas by another name, activation/deactivation.
The term beta comes from its use in the Generalized Linear Model (GLM), a family of statistical models that is used to fit non-normal/non-gaussian data.
fMRI data follows a relatively stereotyped shape from the Blood Oxygen Level Dependent (BOLD) response, which is best modelled with a double-gamma function (e.g. not a gaussian/normal function).
The peak of the gamma curve (i.e. activation/deactivation) is determined by the beta coefficient.
Thus a larger betas mean greater activation, and smaller or negative betas mean less activation or deactivation.
Traditional fMRI analysis will group together all the relevant trial types and give them all one beta estimate, where variance between trials is treated as noise.
NiBetaSeries, on the other hand, gives each trial its own beta estimate treating the variance between trials as the signal of interest.
The final complication is the multiple methods we can use to derive individual beta estimates.
Two common methods are least squares all (LSA) and least squares separate (LSS).
LSA places all the trials in the same GLM, where each trial is a separate predictor.
LSA works well when the trials are far apart in time since the BOLD response take a long time to return to baseline.
When the trials are close together, however, the bold responses start to overlap and the GLM cannot accurately attribute the variance in the fMRI data to trial 1 or trial 2, leading to unreliable beta estimates.
LSS tackles this problem by making as many GLMs as there are trials.
For each trial, a GLM is created where one predictor is the trial of interest and the other predictor is the combination of the other trials.
This reduces the amount of overlap (or more accurately correlation) between predictors, leading to more reliable individual beta estimates.
NiBetaSeries currently implements LSS making it an ideal candidate for experiments with trials that occur closer together (e.g. 3-7 seconds apart on average).

The second question of what an atlas parcellation is will hopefully be easier to explain.
The brain can be cut up in many ways, either via anatomical landmarks, by which regions are activated by a task of theoretical interest, by how the brain organizes itself when not engaged in any external task, or a number of other creative methods.
However the brain is sliced up, we need to mark all the selected voxels within a brain region with the same number to uniquely identify the region.
A voxel is shortened from the term volumetric pixel, unlike typical pictures our brain images are 3 dimensional, so in order to account for the volume we use 3D voxels instead of 2D pixels.
An image with all the regions uniquely labelled is considered an atlas parcellation for the purposes of NiBetaSeries.
The unique regions will be used to average across the voxels containing beta estimates for each trial.
The averaging of beta estimates is repeated over all the trials resulting in a list of averaged beta estimates for that region.
The list of betas for each region can then be correlated with one another to measure the degree of synchrony between regions.

# Overview

NiBetaSeries presents as a command line utility written in python.
The primary way for users to interact with NiBetaSeries is by typing `nibs` in the command line.
The basic workflow of NiBetaSeries follows these steps (the files can be found in the `workflows` directory):
1) `base.py`: read and validate necessary inputs (a minimally processed fMRI file, a brain mask, an events file specifying the onsets, duration, and the trial type, an atlas parcellation, and a table connecting the numbers in the atlas parcellation with names of the regions)
2) `model.py`: construct and execute GLMs using LSS (with additional confound predictors optionally added) generating betaseries (a list of betas for each voxel)
3) `analysis.py`: apply atlas parcellation to data averaging betas within regions for each trial
4) `analysis.py`: correlate each region's list of betas with every other region.
5) `analysis.py`: r-z transform the correlations and output a symmetric correlation matrix in a `tsv` file.

The correlation matrix from NiBetaSeries can be used for graph theoretical analysis, specific region-region correlations across sessions or across different trial types, and presumably other analytic strategies.

NiBetaSeries is not the first or only piece of software that measures task related correlations in the brain.
There are two other packages known to the author: BASCO and pybetaseries [@Gottlich2015; @Poldrack2014].
BASCO (BetA Series COrrelations) is a matlab toolbox that calculates task correlations, but is designed for slow event related designs (e.g. trials occur more than 10 seconds apart).
pybetaseries is a python script that is designed for fast event related designs (like NiBetaSeries), but is no longer actively maintained.
Given the drawbacks of the alternatives, NiBetaSeries justifies its existence and utility to the neuroscience field.

# Acknowledgements

NiBetaSeries is not developed in a vacuum.

Conceptualization of the BetaSeries Method is credited to Jesse Rissman [@Rissman2004],
and the LSS method to Jeanette Mumford [@Mumford2012].
Additionally, Michelle Voss provided guidance over the entirety of the project.
The organization of the code is indebted to `fmriprep` and their developers/maintainers for inspiration [@Esteban2018a].
Neurohackademy is to thank for providing the environment to help the project grow with new contributors.
Finally, all the contributors listed in `zenodo` and `github` have contributed both code and intellectually to NiBetaSeries pushing the project to new heights.

# References