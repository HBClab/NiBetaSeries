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
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/nibetaseries/badge/?version=latest
    :alt: Documentation Status
    :target: https://nibetaseries.readthedocs.io/en/latest/?badge=latest
    

.. |travis| image:: https://travis-ci.org/HBClab/NiBetaSeries.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/HBClab/NiBetaSeries

.. |codecov| image:: https://codecov.io/github/HBClab/NiBetaSeries/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/HBClab/NiBetaSeries

.. |version| image:: https://img.shields.io/pypi/v/nibetaseries.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/nibetaseries

.. |commits-since| image:: https://img.shields.io/github/commits-since/HBClab/NiBetaSeries/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/HBClab/NiBetaSeries/compare/v0.1.0...master

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
In brief, a beta coefficient is calculated for each trial (or event) resulting in a series of betas
that can be used to correlate regions of interest with each other.

NiBetaSeries takes preprocessed data as input that satisfy the
`BIDS deriviatives specification <http://bit.ly/2vKeKcp>`_.
In practical terms, NiBetaSeries uses the output of `fmriprep <http://fmriprep.readthedocs.io/en/latest/>`_,
a great BIDS compatible preprocessing tool.
Specifically, NiBetaSeries requires the input and the atlas to already be in MNI space since currently no
transformations are applied to the data.

With NiBetaSeries you receive:
- betaseries images (TODO)
- correlation matrices

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

https://NiBetaSeries.readthedocs.io/

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
