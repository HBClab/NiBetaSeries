#!/usr/bin/env python
# -*- encoding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function

import io
import re
from glob import glob
from os.path import dirname, join, basename, splitext
from setuptools import find_packages
from setuptools import setup
import versioneer


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='nibetaseries',
    license='MIT license',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='BetaSeries Correlations implemented in Nipype',
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S).sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    author='James Kent',
    author_email='james-kent@uiowa.edu',
    url='https://github.com/HBClab/NiBetaSeries',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
    ],
    keywords=[
        'bids',
        'fmri',
        'neuroimaging',
    ],
    install_requires=[
        'nipype~=1.1.5',
        'pybids~=0.6.4',
        'nibabel~=2.3.0',
        'nistats~=0.0.1b',
        'nilearn~=0.4.2',
        'pandas~=0.24.0',
        'numpy',
        'duecredit~=0.6.4',
        'scikit-learn~=0.19.2',
        'matplotlib~=2.2.4',
        'mne~=0.18.1',
        'pypiwin32; platform_system=="Windows"',
    ],
    extras_require={
        'test': ['tox',
                 'pytest',
                 'pytest-travis-fold',
                 'pytest-cov'],
        'dev': ['check-manifest',
                'flake8',
                'codecov',
                'coverage'],
        'doc': ['sphinx>=1.3',
                'sphinx_rtd_theme',
                'sphinx-argparse',
                'sphinx-gallery',
                'sphinxcontrib-bibtex'],
        'nb': ['matplotlib',
               'seaborn',
               'pillow']
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
    python_requires='~=3.5',
    entry_points={
        'console_scripts': [
            'nibs = nibetaseries.cli.run:main',
        ]
    },
)
