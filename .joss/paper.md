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

# Summary

The brain orchastrates a complex ballet while engaged in a task.
Whether it is following a dot, reading a sentence, interpreting what response is required when presented a red square; the brain is evaluating input and sending motoric output to perform optimally.
We can measure and analyze this flurry of activity using functional Magnetic Resonance Imaging (fMRI).
Traditional fMRI analysis emphasizes what regions are "activated/deactivated" during a task, but does not provide information on which regions are working in sync.
Knowing what regions are syncronous during a task gives insights on the potential organization of the brain.
Additionally, the information could open new inquiries about how different tasks show different synchronicity and whether synchrony between brain regions correlates with performance on a particular task.
NiBetaSeries seeks to fill this gap by providing a method to measure how activation patterns between brain regions are correlated across trials.

NiBetaSeries is not the first or only piece of software that measures task correlations in the brain.
There are two other packages known to the author: BASCO and pybetaseries.
BASCO (BetA Series COrrelations) is a matlab toolbox that calculates task correlations, but is designed for slow event related designs (e.g. trials occur more than 10 seconds apart).
pybetaseries is a python script that is designed for fast event related designs, but is no longer actively maintained.

# Acknowledgements

# References