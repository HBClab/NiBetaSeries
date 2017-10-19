from __future__ import absolute_import, division, print_function
from os.path import join as pjoin


# Format expected by setup.py and doc/source/conf.py: string of form "X.Y.Z"
_version_major = 0
_version_minor = 1
_version_micro = ''  # use '' for first of series, number for 1 and above
_version_extra = 'dev'
# _version_extra = ''  # Uncomment this for full releases

# Construct full version string from these.
_ver = [_version_major, _version_minor]
if _version_micro:
    _ver.append(_version_micro)
if _version_extra:
    _ver.append(_version_extra)

__version__ = '.'.join(map(str, _ver))


CLASSIFIERS = ["Development Status :: 3 - Alpha",
               "Environment :: Console",
               "Intended Audience :: Science/Research",
               "License :: OSI Approved :: MIT License",
               "Operating System :: OS Independent",
               "Programming Language :: Python",
               "Topic :: Scientific/Engineering"]

# Description should be a one-liner:
description = "NiBetaSeries: a template for small scientific Python projects"
# Long description will go up on the pypi page
long_description = """

NiBetaSeries
========
NiBetaSeries ...


To get started using these components in your own software, please go to the
repository README_.

.. _README: https://github.com/jdkent/BetaSeries/blob/master/README.md

License
=======
``NiBetaSeries`` is licensed under the terms of the MIT license. See the file
"LICENSE" for information on the history of this software, terms & conditions
for usage, and a DISCLAIMER OF ALL WARRANTIES.

All trademarks referenced herein are property of their respective holders.

Copyright (c) 2017--, James Kent, The University of Iowa
"""

NAME = "NiBetaSeries"
MAINTAINER = "James Kent"
MAINTAINER_EMAIL = "james-kent@uiowa.edu"
DESCRIPTION = description
LONG_DESCRIPTION = long_description
URL = "http://github.com/jdkent/NiBetaSeries"
DOWNLOAD_URL = ""
LICENSE = "MIT"
AUTHOR = "James Kent"
AUTHOR_EMAIL = "james-kent@uiowa.edu"
PLATFORMS = "OS Independent"
MAJOR = _version_major
MINOR = _version_minor
MICRO = _version_micro
VERSION = __version__
PACKAGE_DATA = {'NiBetaSeries': [pjoin('data', '*')]}
SETUP_REQUIRES = [
    'setuptools>=18.0',
    'numpy',
    'cython',
]

TESTS_REQUIRES = [
    "mock",
    "codecov",
    "pytest",
]

EXTRA_REQUIRES = {
    'doc': ['sphinx>=1.5.3', 'pydotplus', 'sphinx_rtd_theme', 'sphinx-argparse'],
    'tests': TESTS_REQUIRES,
    'duecredit': ['duecredit']
}

# Enable a handle to install all extra dependencies at once
EXTRA_REQUIRES['all'] = [val for _, val in list(EXTRA_REQUIRES.items())]

LINKS_REQUIRES = []

REQUIRES = [
    'networkx',
    'nipype'
]

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Science/Research',
    'Topic :: Scientific/Engineering :: Image Recognition',
    'License :: OSI Approved :: BSD License',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
]
