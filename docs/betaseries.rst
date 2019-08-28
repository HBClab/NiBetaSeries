.. _betaseries:

==========
Betaseries
==========

This covers the conceptual background of betaseries analysis;
check out :ref:`usage` for more on how to use NiBetaSeries.

Introduction
------------
Betaseries track the event-to-event hemodynamic fluctuations
modeled in task functional magnetic resonance imaging (task fMRI).
Betaseries fills an important analytical gap between measuring hemodynamic
fluctuations in resting-state fMRI and measuring regional activations
via cognitive subtraction in task fMRI.

Conceptual Background
---------------------
Jesse Rissman :cite:`d-Rissman2004` was the first to publish on betaseries
correlations, describing their usage in a working memory task.
In this task, participants saw a cue, a delay, and a probe, all occurring
within a short time period.
The cue was presented for one second, a delay occurred for seven seconds,
and a probe was presented for one second.
Given that the blood-oxygen-level-dependent (BOLD) response
takes approximately six seconds to reach its peak, and generally takes over
20 seconds to return to baseline, we can begin to see a problem.
The events within the events occur too close to each other to discern what
brain responses are related to encoding the cue, the delay, or the probe.
To discern how the activated brain regions form networks, Rissman
computed betaseries correlations.
Instead of having a single regressor to describe all the cue events,
a single regressor for all the delay events, and a single regressor for all the
probe events (as is done in traditional task analysis),
there is an individual regressor for every event in the experiment.
For example, if your experiment has 40 events, each with a cue, delay, and
probe event, the model will have a total of 120 regressors, fitting a beta
(i.e., parameter) estimate for each event.
Once you calculate a beta estimate for each event of a given type
(e.g., cue), you will have a four-dimensional dataset where each volume
represents the beta estimates for a particular event.

Having one regressor per event in a single model is known as "least squares all".
This method, however, has limitations in the context of fast event related
designs (e.g., designs where the events occur between 3-6
seconds apart on average).
Since each event has its own regressor, events that occur very close in time
are colinear (e.g. are very overlapping).
Benjamin Turner :cite:`d-Turner2012a` derived a solution for
the high colinearity observed in least sqaures all by using another
type of regression known as "least squares separate".
Instead of having one general linear model (GLM) with a regressor per event,
least squares separate implements a GLM per event with only two regressors:
1) one for the event of interest, and 2) one for every other event in the
experiment.
This process reduces the colinearity of the regressors and creates a more valid
estimate of how each regressor fits the data.
NiBetaSeries uses "least squares separate" and is thus optimized
for fast event related designs.


Mathematical Background
-----------------------

.. math::
   :label: glm

   \begin{equation}
        Y = X\beta + \epsilon
    \end{equation}

The above equation is the general linear model (GLM) presented using
matrix notation.
:math:`Y` represents the time-series we are attempting to explain
(for a given voxel).
:math:`X` typically represents the trial(s) of interest that you would like
to have an estimate.
For example, I would like to know how the brain responds to red squares, so
:math:`X` represents the brain response at all time points when a red square was presented.
The :math:`\beta` assumes any value that minimizes the squared error between
the modeled data and the actual data, :math:`Y`.
Finally, :math:`\epsilon` (epsilon) refers to the error that is not captured
by the model.
In a typical a GLM, event-to-event betas may be averaged for a given event type
and the variance is treated as noise.
However, those event-to-event fluctuations may also contain important
information the typical GLM will ignore/penalize.
With a couple modifications to the above equation, we arrive at calculating a
betaseries.

.. math::
    :label: lsa

    \begin{equation}
        Y = X_1\beta_1 + X_2\beta_2 + . . . + X_n\beta_n + \epsilon
    \end{equation}


With the betaseries equation, a beta is estimated for every event, instead of
for each event type (or whatever logical grouping).
This yields a series of event betas for a single event
type.
This operation is completed for all voxels, giving us as many lists of betas
as there are voxels in the data.
Essentially, this returns a ``4-D`` dataset where the fourth dimension
represents the number of events instead of time (as the fourth dimension is
represented in resting state).
Analogous to resting state data, we can perform correlations between the
voxels to discern which voxels (or which aggregation of voxels)
covary with other voxels.

There is one final concept to cover in order to understand how the betas are
estimated in ``NiBetaSeries``.
You can model individual betas using a couple different strategies;
"least squares all" (LSA) estimation represented in the above equation :eq:`lsa`,
or "least squares separate" (LSS) estimatation, in which each event receives
its own GLM.
The advantage of LSS comes from reducing the colinearity between closely spaced
events.
In LSA, if events occurred close in time, it would be difficult to model
whether the fluctuations should be attributed to one event or the other.
LSS reduces this ambiguity by only having two regressors: one for the event
of interest and another for every other event.
This reduces the colinearity between regressors and makes each beta estimate
more reliable.

.. highlight:: python
   :linenothreshold: 5

.. code-block:: python
    :emphasize-lines: 20,37

    import numpy as np

    # the design of the brain response.
    # each row represents a time point.
    # each column represents a trial.
    # the trials overlap each other.
    X = np.array([[1, 0, 0, 0],
                  [1, 1, 0, 0],
                  [0, 1, 1, 0],
                  [0, 0, 1, 1]])

    # the trial in the order they were seen
    trial_types = ["red", "blue", "red", "blue"]

    # the observed brain data (transposed so data points are in one column)
    Y = np.array([[2, 1, 5, 3]]).T

    # least squares all (LSA)
    # there is one beta estimate per trial
    lsa_betas, _, _, _ = np.linalg.lstsq(X, Y)

    # least square separate (LSS)
    lss_betas = []
    # for each trial...
    for index, _ in enumerate(trial_types):
        # select the trial (column) of interest
        X_interest = X[:,index]

        # select all the other trials (columns) and sum over them to create a single column
        X_other = np.delete(X, index, axis=1).sum(axis=1)

        # combine the two columns such that:
        # the first column is the trial of interest
        # the second column represents all other trials
        X_trial = np.vstack([X_interest, X_other]).T
        # solve for the beta estimates
        betas, _, _, _ = np.linalg.lstsq(X_trial, Y)
        # add the beta for the trial of interest to the list
        lss_betas.append(betas[0][0])


This python code demonstrates LSA (line 20) and LSS where each event is given its own GLM model.
Note the GLM model written in python (line 37) has the form as the equation at the
beginning of "Mathematical Background" :eq:`glm`, but ``X`` (specifically ``X_trial``)
has the particular representation of one column being the trial of interest and the
other column being all remaining trials.


Relationship to Resting-State Functional Connectivity
-----------------------------------------------------

Betaseries is similar to resting-state functional connectivity (time-series correlations)
because the same analyses typically applied to resting-state data can ostensibly be applied
to betaseries.
At the core of both resting-state functional connectivity and betaseries we are working with
a vector of numbers at each voxel.
We can correlate, estimate regional homogeneity, perform independent
components analysis, or perform a number of different analyses
with the data in each voxel.
However, betaseries deviates from the time-series correlations used for resting-state
analysis in two important ways.
First, you can do cognitive subtraction using betaseries.
Since there is no explicit task in resting state, there are no
cognitive states to compare.
Second, the interpretations of
resting-state connectivity and betaseries differ.
Resting state measures the unmodelled hemodynamic fluctuations that occur
without explicit stimuli or task.
Betaseries, on the other hand, measures the modelled hemodynamic fluctuations
that occur in response to an explicit stimulus.
Both resting-state analyses and betaseries may measure intrinsic connectivity
(e.g., the functional structure of the brain independent of task),
but betaseries may also measure the task evoked connectivity
(e.g., connectivity between regions that is increased during some
cognitive process).

Relationship to Traditional Task Analysis
-----------------------------------------
Betaseries is also similar to traditional task analysis because
cognitive subtraction can be used in both.
As with resting-state analysis, betaseries deviates from traditional task analysis
in several important ways.
Say we are interested in observing how the brain responds to faces
versus houses.
The experimenter has a timestamp of exactly when and how long
a face or house is presented.
That timestamp information is typically convolved with a hemodynamic
response function (HRF) to represent how the brain stereotypically responds to
any stimulus resulting in a model of how we expect the brain to respond
to places and/or faces.
This is where traditional task analysis and betaseries diverge.
In traditional task analysis all the face events are estimated at once,
giving one summary measure for how strongly each voxel was activated
(same for house events).
The experimenter can subtract the summary measure of faces from houses
to see which voxels are more responsive to houses relative to faces
(i.e., cognitive subtraction).
In betaseries analysis, each event is estimated separately and each voxel has as many
estimates at there are events (which can be labelled as either
face or house events).
The experimenter can now reduce the series of estimates (a betaseries)
for each voxel into a summary measure such as correlations among
regions of interest.
The correlation map for faces can be subtracted from houses, giving
voxels that are more correlated with the region of interest for houses
relative to faces.
Whereas traditional task analysis treats the variance of brain responses
between events of the same type (e.g. face or house) as noise,
betaseries leverages this variance to make conclusions about which brain
regions may communicate with each other during a particular event type
(e.g. faces or houses).

Summary
-------
Betaseries is not in opposition to resting state or traditional task analysis;
the methods are complementary.
For example, network parcelations derived from resting state data can be
used on betaseries data to ascertain if the networks observed in resting state
follow a similar pattern with betaseries.
Additionally, regions determined from traditional task analysis
can be used as regions of interest for betaseries analysis.
Betaseries straddles the line between traditional task analysis and
resting-state functional connectivity, observing task data through a network lens.


Relevent Software
-----------------
- BASCO_ (BetA Series COrrelations) is a MATLAB program that also performs
  betaseries correlations
- pybetaseries_ is a python script that runs on files that have
  been processed by FSL's FEAT

.. _BASCO: https://www.nitrc.org/projects/basco/
.. _pybetaseries: https://github.com/poldrack/pybetaseries

Other Relevant Readings
-----------------------
- :cite:`d-Cisler2012`: A comparison of psychophysiological
  interactions and LSS
- :cite:`d-Gottlich2015`: The BASCO paper
- :cite:`d-Abdulrahman2016`: evaluation of LSS (and other methods)


References
----------

.. bibliography:: references.bib
    :style: plain
    :labelprefix: docs-
    :keyprefix: d-
