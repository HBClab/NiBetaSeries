#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""nibetaseries setup script"""
import sys
from setuptools import setup, find_packages
import versioneer

# Give setuptools a hint to complain if it's too old a version
# 30.3.0 allows us to put most metadata in setup.cfg
# Should match pyproject.toml
# Not going to help us much without numpy or new pip, but gives us a shot
SETUP_REQUIRES = ['setuptools >= 40.8', 'cython']
# This enables setuptools to install wheel on-the-fly
SETUP_REQUIRES += ['wheel'] if 'bdist_wheel' in sys.argv else []


if __name__ == '__main__':

    setup(name='nibetaseries',
          version=versioneer.get_version(),
          cmdclass=versioneer.get_cmdclass(),
          setup_requires=SETUP_REQUIRES,
          packages=find_packages("src"),
          package_dir={"": "src"},
          )
