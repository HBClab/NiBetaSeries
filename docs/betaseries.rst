.. _betaseries:

==========
Betaseries
==========

:ref:`usage`

Introduction
------------
Betaseries track the event-to-event modelled hemodynamic fluctuations
that occur within task functional magnetic resonance imaging (task fMRI).
Betaseries fills an important analytical gap between measuring hemodynamic
fluctuations in resting state fMRI and measuring regional activations
via cognitive subtraction in task fMRI.

Conceptual Background
---------------------
Jesse Rissman [Rissman2004]_ was the first to publish on betaseries
correlations describing their usage in a working memory task.
In this task, participants saw a cue, a delay, and a probe, all occurring
within a short time period.
A cue was presented for one second, a delay occurred for seven seconds,
and a probe was presented for one second.
Given the Blood Oxygen-Level Dependent (BOLD) response
takes approximately six seconds to reach its peak, and generally takes over
20 seconds to return to baseline, we can begin to see a problem.
The events within the events occur too close to each other to discern what
brain responses are related to encoding the cue, the delay, or the probe.
To discern how the activated brain regions form networks, Rissman
created betaseries correlations.
Instead of having a single regressor to describe all the cue events,
a single regressor for all the delay events, and a single regressor for all the
probe events (as is done in traditional task analysis),
there is an individual regressor for every event in the experiment.
For example, if your experiment has 40 events, each with a cue, delay, and
probe event, the model will have a total of 120 regressors, fitting a beta
(a.k.a. parameter) estimate for each event.
Once you calculate a beta estimate for each event of a given event type
(e.g. cue), at the end you will have four dimensional dataset where each volume
represents the beta estimates for a particular event, and each voxel represents
a specific beta estimate.

Having one regressor per event in a single model is known as least squares all.
This method, however, has limitations in the context of fast event related
designs (e.g. designs where the events occur between 3-6
seconds apart on average).
Since each event has its own regressor, events that occur very close in time
are colinear (e.g. are very overlapping).
Jeanette Mumford et al. [Mumford2012]_ derived a solution for
the high colinearity observed in least sqaures all by using another
type of regression known as least squares separate.
Instead of having one General Linear Model (GLM) with a regressor per event,
least squares separate implements a GLM per event with only two regressors:
1) one for the event of interest, and 2) one for every other event in the
experiment.
This process reduces the colinearity of the regressors and creates a more valid
estimate of how each regressor fits the data.
NiBetaSeries uses least squares separate and is thus optimized
for fast event related designs.


Math Background
---------------
.. math::
   \begin{equation}
        Y = X\beta + \epsilon
    \end{equation}

The above equation is the General Linear Model (GLM) presented using
matrix notation.
:math:`Y` represents the time-series we are attempting to explain.
The :math:`\beta` assumes any value that minimizes the squared error between
the modeled data and the actual data, :math:`Y`.
Finally, :math:`\epsilon` (epsilon) refers to the error that is not captured
by the model.
Within a GLM, event-to-event betas may be averaged for a given event type
and the variance is treated as noise.
However, those event-to-event fluctuations may also contain important
information the typical GLM will ignore/penalize.
With a couple modifications to the above equation, we arrive at calculating a
betaseries.

.. math::
    \begin{equation}
        Y = X_1\beta_1 + X_2\beta_2 + . . . + X_n\beta_n + \epsilon
    \end{equation}

With the betaseries equation, a beta is estimated for every event, instead of
for each event type (or whatever logical grouping).
This gives us the ability to align all the event betas from a single event
type into a list (i.e. series).
This operation is completed for all voxels, giving us as many lists of betas
as there are voxels in the data.
Essentially, we are given a ``4-D`` dataset where the fourth dimension
represents event number instead of time (as the fourth dimension is
represented in resting state).
And analogous to resting state data, we can perform correlations between the
voxels to discern which voxels (or which aggregation of voxels) synchronize
best with other voxels.

There is one final concept to cover in order to understand how the betas are
estimated in ``NiBetaSeries``.
You can model individual betas using a couple different strategies; with a
least squares all (LSA) approximation which the equation above represents,
and a least squares separate (LSS) approximation in which each event is given
it's own GLM.
The advantage of LSS comes from reducing the colinearity between closely spaced
events.
In LSA, if events occurred close in time then it would be difficult to model
whether the fluctuations should be attributed to one event or the other.
LSS reduces this ambiguity by only having two regressors: one for the event
of interest and another for every other event.
This reduces the colinearity between regressors and makes each beta estimate
more reliable.

.. code-block:: python

   for event, beta in zip(events, betas):
       data = X[event] * beta + error

This python psuedocode demonstrates LSS where each event
is given it's own model.

Relationship to Resting State
-----------------------------
Betaseries is similar to resting state because the same analyses
applied to resting state data can ostensibly be applied to betaseries.
At the core of both resting state and betaseries we are working with
a list of numbers at each voxel.
We can correlate, estimate regional homogeneity, perform independent
components analysis, or perform a number of different analyses
with the data in each voxel.
However, betaseries deviates from resting state in two important ways.
First, you can do cognitive subtraction using betaseries.
Since there is no explicit task in resting state, there are no
cognitive states to compare.
Second, interpretation of the lists of numbers are different for
resting state and betaseries.
Resting state measures the unmodelled hemodynamic fluctuations that occur
without explicit stimuli or task.
Betaseries, on the other hand, measures the modelled hemodynamic fluctuations
that occur in response to an explicit stimulus.
Both resting state and betaseries may measure intrinsic connectivity
(e.g. the functional structure of the brain independent of task),
but betaseries may also measure the task evoked connectivity
(e.g. connectivity between regions that is increased during some
cognitive process).

Relationship to Traditional Task Analysis
-----------------------------------------
Betaseries is also similar to traditional task analysis because
cognitive subtraction can be used in both.
As with resting state, betaseries deviates from traditional task analysis
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
(i.e. cognitive subtraction).
In betaseries each event is estimated separately each voxel has as many
estimates at there are events (which can be labelled as either
face or house events).
The experimenter can now reduce the series of estimates (a betaseries)
for each voxel into a summary measure such as a correlation with
region(s) of interest.
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
Betaseries is not in opposition to resting state or traditional task analysis,
the methods are complementary.
For example, network parcelations derived from resting state data can be
used on betaseries data to ascertain if the networks observed in resting state
follow a similar pattern with betaseries.
Additionally, regions determined from traditional task analysis
can be used as regions of interest for betaseries analysis.
Betaseries straddles the line between traditional task analysis and
resting state, observing task data through a network lens.


Relevent Software
-----------------
BASCO_ (BetA Series COrrelations) is a matlab program that also performs
betaseries correlations


Other Relevant Readings
-----------------------
- [Cisler2014]_
- [Gottlich2015]_
- [Abdulrahman2016]_

References
----------

.. [Rissman2004] https://www.ncbi.nlm.nih.gov/pubmed/15488425

.. [Mumford2012] https://www.ncbi.nlm.nih.gov/pubmed/21924359

.. [Cisler2014] https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4019671/

.. [Gottlich2015] https://www.frontiersin.org/articles/10.3389/fnsys.2015.00126/full

.. [Abdulrahman2016] https://www.ncbi.nlm.nih.gov/pubmed/26549299

.. _BASCO: https://www.nitrc.org/projects/basco/
