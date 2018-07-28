========
Overview
========

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

.. |docs| image:: https://readthedocs.org/projects/NiBetaSeries/badge/?style=flat
    :target: https://readthedocs.org/projects/nibetaseries
    :alt: Documentation Status

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

BetaSeries Correlations implemented in Nipype

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
