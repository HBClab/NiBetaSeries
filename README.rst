.. _readme:

============
NiBetaSeries
============

If you are viewing this file on GitHub, please see our
`readthedocs page <https://nibetaseries.readthedocs.io>`_
for links to render properly.

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs| |joss|
    * - tests
      - | |travis| |circleci|
        | |codecov|
    * - binder
      - | |binder|
    * - package
      - | |version| |wheel| |supported-versions|
        | |supported-implementations| |zenodo|

.. |docs| image:: https://readthedocs.org/projects/nibetaseries/badge/?version=latest
    :alt: Documentation Status
    :target: https://nibetaseries.readthedocs.io/en/latest/?badge=latest

.. |zenodo| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.2552303.svg
   :target: https://zenodo.org/record/2552303#.XFBjwN-YU8p

.. |joss| image:: https://joss.theoj.org/papers/10.21105/joss.01295/status.svg
   :target: https://doi.org/10.21105/joss.01295

.. |travis| image:: https://travis-ci.com/HBClab/NiBetaSeries.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.com/HBClab/NiBetaSeries

.. |codecov| image:: https://codecov.io/github/HBClab/NiBetaSeries/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/HBClab/NiBetaSeries

.. |circleci| image:: https://circleci.com/gh/HBClab/NiBetaSeries.svg?style=svg
    :alt: Circleci Build Status
    :target: https://circleci.com/gh/HBClab/NiBetaSeries

.. |binder| image:: https://mybinder.org/badge_logo.svg
    :target: https://mybinder.org/v2/gh/HBClab/NiBetaSeries/master?filepath=%2Fexamples

.. |version| image:: https://img.shields.io/pypi/v/nibetaseries.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/nibetaseries

.. |wheel| image:: https://img.shields.io/pypi/wheel/nibetaseries.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/nibetaseries

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/nibetaseries.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/nibetaseries

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/nibetaseries.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/nibetaseries


.. end-badges

What is NiBetaSeries?
---------------------
NiBetaSeries is BIDS_-compatible `application <https://bids-apps.neuroimaging.io/>`_
that calculates betaseries correlations.
In brief, a beta coefficient (i.e., parameter estimate) is calculated
for each trial (or event) resulting in a series of betas ("betaseries")
that can be correlated across regions of interest.

Why should I use it?
--------------------
There are potential insights hidden in your task fMRI data.
Rest fMRI enjoys a multitude of toolboxes which can be applied to task fMRI
with some effort, but there are not many toolboxes that focus on making
betaseries.
Betaseries can then be used for correlations/classifications and
a multitude of other analyses.
While a couple alternatives exist (pybetaseries_ and BASCO_), NiBetaSeries
is the only application to interface with BIDS_ organized data with the goal
of providing a command-line application experience like fMRIPrep_.

What does NiBetaSeries give me?
-------------------------------
Currently NiBetaSeries returns the beta series images and optionally
symmetric z-transformed correlation matrices with an entry for each
parcel defined in the atlas.

.. note:: The betas (i.e., parameter estimates) are generated using either
    the "Least Squares Separate" or "Least Squares All" procedures.
    Please read the :ref:`betaseries` page for more background information.

What do I need to run NiBetaSeries?
-----------------------------------
NiBetaSeries takes BIDS_ and preprocessed data as input that satisfy the
`BIDS derivatives specification <http://bit.ly/2vKeKcp>`_.
In practical terms, NiBetaSeries uses the output of fMRIPrep_,
a great BIDS-compatible preprocessing tool.
NiBetaSeries requires the input and the atlas to already
be in the same space (e.g., MNI space).
For more details, see :ref:`usage` and the tutorial
(:ref:`sphx_glr_auto_examples_plot_run_nibetaseries.py`)

Get Involved
------------
This is a very young project that still needs some tender loving care to grow.
That's where you fit in!
If you would like to contribute, please read our :ref:`code_of_conduct`
and contributing page (:ref:`contributing`).

Thanks!
-------
This project heavily leverages `nipype <http://nipype.readthedocs.io/en/latest/>`_,
`nilearn <https://nilearn.github.io/>`_, `pybids <https://bids-standard.github.io/pybids/>`_, and
`nistats <https://nistats.github.io/>`_ for development.
Please check out their pages and support the developers.

.. _BASCO: https://www.nitrc.org/projects/basco/
.. _pybetaseries: https://github.com/poldrack/pybetaseries
.. _BIDS: http://bids.neuroimaging.io/
.. _fMRIPrep: http://fmriprep.readthedocs.io/en/latest/
