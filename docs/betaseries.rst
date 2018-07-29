=======================
Betaseries Correlations
=======================

Betaseries correlations track the trial-to-trial hemodynamic fluctuations
that occur within a task.
In contrast to typical General Linear Models (GLMs) where the hemodynamic
fluctuations between trials of the same type are considered noise,
betaseries correlations leverage these fluctuations to provide a quantitative measure
of how synchronous they are across different brain regions identifying networks that
are activated during a task.
GLMs, by contrast, can only provide information about which brain regions are
active, but cannot tell us which of those active regions form a network.
For example, in a task where you have encode both the size and position of a stimulus,
a GLM will show you active regions that may be encoding size or position or both.
Betaseries correlations, on the other hand, could provide evidence of which
regions form a size encoding network, and which form a position encoding network.

Math Background
---------------
.. math::
   \begin{equation}
        Y = X\beta + \epsilon
    \end{equation}


The above equation is the General Linear Model (GLM) presented using matrix notation.
:math:`Y` represents the time-series we are attempting to explain.
The :math:`\beta` assumes any value that minimizes the squared error between the
modeled data and the actual data, :math:`Y`.
Finally, :math:`\epsilon` (epsilon) refers to the error that is not captured by the model.
Within a GLM, trial-to-trial betas may be averaged for a given trial type
and the variance is treated as noise.
However, those trial-to-trial fluctuations may also contain important information
that the typical GLM will ignore/penalize.
With a couple modifications to the above equation, we arrive at calculating a betaseries.

.. math::
    \begin{equation}
        Y = X_1\beta_1 + X_2\beta_2 + . . . + X_n\beta_n + \epsilon
    \end{equation}

With the betaseries equation, a beta is estimated for every trial, instead of for each
trial type (or whichever logical grouping).
This gives us the ability to align all the trial betas from a single trial type into a
list (i.e. series).
This operation is completed for all voxels, giving us as many lists of betas as there are
voxels in the data.
Essentially, we are given a ``4-D`` dataset where the fourth dimension represents
trial number instead of time (as the fourth dimension is represented in resting state).
And analogous to resting state data, we can perform correlations between the voxels
to discern which voxels (or which aggregation of voxels) synchronize best with other
voxels.

There is one final concept to cover in order to understand how the betas are estimated
in ``NiBetaSeries``.
You can model individual betas using a couple different strategies; with a least
squares all (LSA) approximation which the equation above represents, and a least
squares separate (LSS) approximation in which each trial is given it's own GLM.
The advantage of LSS comes from reducing the colinearity between closely spaced
trials.
In LSA, if trials occurred close in time then it would be difficult to model whether
the fluctuations should be attributed to one trial or the other.
LSS reduces this ambiguity by only having two regressors: one for the trial of interest
and another for every other trial.
This reduces the colinearity between regressors, and makes each beta estimate more
reliable.

.. code-block:: python

   for trial, beta in zip(trials, betas):
       data = X[trial] * beta + error

This python psuedocode demonstrates LSS where each trial is given it's own model.

