============
NiBetaSeries
============

.. start-badges

.. list-table::
    :stub-columns: 1
    * - docs
      - |docs|
    * - tests
      - | |travis|
        | |codecov|
    * - package
      - | |version| |wheel| |supported-versions|
        | |supported-implementations| |zenodo|

.. |docs| image:: https://readthedocs.org/projects/nibetaseries/badge/?version=latest
    :alt: Documentation Status
    :target: https://nibetaseries.readthedocs.io/en/latest/?badge=latest

.. |zenodo| image:: https://zenodo.org/badge/95605121.svg
   :target: https://zenodo.org/badge/latestdoi/95605121

.. |travis| image:: https://travis-ci.org/HBClab/NiBetaSeries.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/HBClab/NiBetaSeries

.. |codecov| image:: https://codecov.io/github/HBClab/NiBetaSeries/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/HBClab/NiBetaSeries

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

NiBetaSeries is `BIDS <http://bids.neuroimaging.io/>`_ compatible `application <https://bids-apps.neuroimaging.io/>`_
that calculates betaseries correlations.
In brief, a beta coefficient is calculated for each trial
(or event) resulting in a series of betas
that can be used to correlate regions of interest with each other.

NiBetaSeries takes preprocessed data as input that satisfy the
`BIDS deriviatives specification <http://bit.ly/2vKeKcp>`_.
In practical terms, NiBetaSeries uses the output of `fmriprep <http://fmriprep.readthedocs.io/en/latest/>`_,
a great BIDS compatible preprocessing tool.
NiBetaSeries requires the input and the atlas to already
be in MNI space since currently no
transformations are applied to the data.
You can use any arbitrary atlas as long as it is in MNI space
(the same space as the preprocessed data).

With NiBetaSeries you can receive:

* betaseries images (TODO)
* correlation matrices

This is a very young project that still needs some tender loving care to grow.
That's where you fit in!
If you would like to contribute, please read our code of conduct
and contributing page.

This project heavily leverages `nipype <http://nipype.readthedocs.io/en/latest/>`_,
`nilearn <https://nilearn.github.io/>`_, `pybids <https://incf.github.io/pybids/>`_, and
`nistats <https://nistats.github.io/>`_ for development.
Please check out their pages and support the developers.


* Free software: MIT license

Installation
============

::

    pip install nibetaseries

Documentation
=============

https://nibetaseries.readthedocs.io

If you're interested in contributing to this project, here are some guidelines for `contributing <https://hbclab.github.io/NiBetaSeries/contributing.html>`_.
Another good place to start is by checking out the open `issues <https://github.com/HBClab/NiBetaSeries/issues>`_.

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
