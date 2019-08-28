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
Whether it is following a dot, reading a sentence, interpreting what response is required when presented with a red square; the brain is evaluating input and sending motoric output to perform optimally/efficiently.
We can measure and analyze this flurry of activity using functional Magnetic Resonance Imaging (fMRI).
Traditional fMRI analysis emphasizes what regions are "activated/deactivated" during a task, but does not provide information on which regions are acting in synchrony.
Knowing what regions are synchronous during a task gives insights on the potential organization of the brain.
NiBetaSeries seeks to fill this gap by providing a method to measure how activation patterns between brain regions are correlated across trials.
That is to say if region A and region B both show high activity on trial 1, low activity on trial 2, medium activity on trial 3, and so on, then these two regions are highly correlated.

# Background

To understand NiBetaSeries we need to answer two questions: what is a "beta" (or parameter estimate) and how can we analyze a series of betas?
We have already mentioned betas by another name, activation/deactivation.
The term beta comes from its use in the Generalized Linear Model (GLM), a family of statistical models that is used to fit non-normal/non-gaussian data.
fMRI signal evoked by a stimulus follows a relatively stereotyped shape from the Blood Oxygen Level Dependent (BOLD) response, which is best modelled with a double-gamma function (e.g. not a gaussian/normal function).
The peak of the gamma curve (i.e. activation/deactivation) is determined by the beta coefficient.
Thus larger betas mean greater activation, and smaller or negative betas mean less activation or deactivation.
Traditional fMRI analysis will group together all the relevant trial types and give them all one beta estimate, where variance between trials is treated as noise.
NiBetaSeries, on the other hand, gives each trial its own beta estimate treating the variance between trials as the signal of interest.
The final complication to understand betas is the multiple methods we can use to derive individual beta estimates.
Two common methods are least squares all (LSA) and least squares separate (LSS).
LSA places all the trials in the same GLM, where each trial is a separate predictor.
LSA works well when the trials are far apart in time since the BOLD response takes a long time to return to baseline.
When the trials are close together, however, the bold responses start to overlap and the GLM cannot accurately attribute the variance in the fMRI data to trial 1 or trial 2, leading to unreliable beta estimates.
LSS tackles this problem by making as many GLMs as there are trials.
For each trial, a GLM is created where one predictor is the trial of interest and the other predictor is the combination of the other trials.
This reduces the amount of overlap (or more accurately correlation) between predictors, leading to more reliable individual beta estimates.
NiBetaSeries currently implements LSS making it a more reasonable analysis choice for
experiments with trials that occur closer together (e.g. 3-7 seconds apart on average).
The output of LSS is a beta series for each voxel in our dataset.

There is a wealth of analysis methods we can apply to beta series datasets.
To summarize our data, we have a beta estimate for each trial within each voxel of the brain,
resulting in a 4-dimensional dataset.
Three dimensions make up the brain voxels, and the 4th dimension represents the number of trials.
For many intents and purposes, the ``4D`` beta series can analyzed similarly to a ``4D``
resting state dataset where the 4th dimension represents time.
Traditional analysis strategies applied to resting state such as seed based correlation,
independent components analysis, regional homogeniety, and graph theory can be applied to
beta series [@Cole2010;vanWijk2010].
Recycling these methods for beta series provides a new lens to observe the organization of the brain during a task and may lead to additional insights.
Graph theoretical and seed based correlation measures often depend on voxels
being grouped into homogenous "parcels".
That is, the betas from several voxels in close spatial proximity are averaged together
to reduce the 20,000 voxels to a couple 100 or fewer parcels.
Each parcel is labelled with a unique integer in a 3-dimensional parcellation atlas
(e.g. the voxels within the left insula may all be labelled with the integer 12).
The collection of parcels--a parcellation--identifies all the unique brain areas of interest and that image is used in NiBetaSeries to provide usable output.

Putting betas and atlas parcellations together, we have a recipe to create betaseries correlations in NiBetaSeries.
Applying the GLM to the fMRI data results in voxelwise beta estimates for each trial.
Voxels are averaged together within each parcel separately for all trials, resulting in a ``2D`` dataset.
One dimension represents the parcel and the other represents the trial.
As mentioned above, many graph theoretical measures could be applied, but currently
NiBetaSeries only performs correlations between parcels.
Other analysis methods are on the roadmap for NiBetaSeries, which will make the tool
useful for a variety of scientific questions.

# Overview

NiBetaSeries presents as a command line utility written in python following the template of a BIDS-App [@Gorgolewski2017].
The primary way for users to interact with NiBetaSeries is by typing `nibs` in the command line.
The basic workflow of NiBetaSeries follows these steps (the files can be found in the `workflows` directory):

1) `base.py`: read and validate necessary inputs (a minimally processed fMRI file, a brain mask, an events file specifying the onsets, duration, and the trial type, an atlas parcellation, and a table connecting the numbers in the atlas parcellation with names of the regions).
2) `model.py`: construct and execute GLMs using LSS (with additional confound predictors optionally added) generating a betaseries (a list of betas for each voxel).
3) `analysis.py`: apply atlas parcellation to data averaging betas within regions for each trial.
4) `analysis.py`: correlate each region's list of betas with every other region.
5) `analysis.py`: r-z transform the correlations and output a symmetric correlation matrix in a `tsv` file.

The correlation matrix from NiBetaSeries can be used for graph theoretical analysis, specific region-region correlations across different trial types, and other analytic strategies.

NiBetaSeries is not the first or only piece of software that measures task related correlations in the brain.
There are two other packages known to the author: BASCO and pybetaseries [@Gottlich2015; @Poldrack2014].
BASCO (BetA Series COrrelations) is a matlab toolbox that calculates task correlations, but is designed for slow event related designs (e.g. trials occur more than 10 seconds apart).
pybetaseries is a python script that is designed for fast event related designs (like NiBetaSeries), but is no longer actively maintained.
Given the drawbacks of the alternatives, NiBetaSeries justifies its existence and utility to the neuroscience field.

# Acknowledgements

NiBetaSeries is not developed in a vacuum.

Conceptualization of the BetaSeries Method is credited to Jesse Rissman [@Rissman2004],
and the LSS method to Benjamin Turner [@Turner2012a] with validation by Jeanette Mumford [@Mumford2012] and Hunar Abdulrahman [@Abdulrahman2016].
Additionally, Michelle Voss provided guidance over the entirety of the project.
The organization of the code is indebted to `fmriprep` and their developers/maintainers for inspiration [@Esteban2019].
Neurohackademy is to thank for providing the environment to help the project grow with new contributors.
Finally, all the contributors listed in `zenodo` and `github` have contributed both code and intellectually to NiBetaSeries pushing the project to new heights.

# References