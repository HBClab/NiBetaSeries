#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" NiBetaSeries setup script """

def main():
    """ Install entry-point """
    from io import open
    from os import path as op
    from inspect import getfile, currentframe
    from setuptools import setup, find_packages
    from setuptools.extension import Extension
    from numpy import get_include

    this_path = op.dirname(op.abspath(getfile(currentframe())))

    # Python 3: use a locals dictionary
    # http://stackoverflow.com/a/1463370/6820620
    ldict = locals()
    # Get version and release info, which is all stored in NiBetaSeries/version.py
    module_file = op.join(this_path, 'NiBetaSeries', 'version.py')
    with open(module_file) as infofile:
        pythoncode = [line for line in infofile.readlines() if not line.strip().startswith('#')]
        exec('\n'.join(pythoncode), globals(), ldict)

    # extensions = [Extension(
    #     "fmriprep.utils.maths",
    #     ["fmriprep/utils/maths.pyx"],
    #     include_dirs=[get_include(), "/usr/local/include/"],
    #     library_dirs=["/usr/lib/"]),
    # ]

    setup(
        name=ldict['NAME'],
        version=ldict['__version__'],
        description=ldict['DESCRIPTION'],
        long_description=ldict['LONG_DESCRIPTION'],
        author=ldict['AUTHOR'],
        author_email=ldict['AUTHOR_EMAIL'],
        maintainer=ldict['MAINTAINER'],
        maintainer_email=ldict['MAINTAINER_EMAIL'],
        url=ldict['URL'],
        license=ldict['LICENSE'],
        classifiers=ldict['CLASSIFIERS'],
        download_url=ldict['DOWNLOAD_URL'],
        # Dependencies handling
        setup_requires=ldict['SETUP_REQUIRES'],
        install_requires=ldict['REQUIRES'],
        tests_require=ldict['TESTS_REQUIRES'],
        extras_require=ldict['EXTRA_REQUIRES'],
        dependency_links=ldict['LINKS_REQUIRES'],
        package_data={'NiBetaSeries': ['data/*.json', 'data/*.nii.gz', 'data/*.mat',
                                   'viz/*.tpl', 'viz/*.json']},
        entry_points={'console_scripts': [
            'NIBS=NiBetaSeries.cli.run:main'
        ]},
        packages=find_packages(exclude=("tests",)),
        zip_safe=False
    )


if __name__ == '__main__':
    main()
# import os
# from setuptools import setup, find_packages
# PACKAGES = find_packages()

# # Get version and release info, which is all stored in BetaSeries/version.py
# ver_file = os.path.join('NiBetaSeries', 'version.py')
# with open(ver_file) as f:
#     exec(f.read())

# opts = dict(name=NAME,
#             maintainer=MAINTAINER,
#             maintainer_email=MAINTAINER_EMAIL,
#             description=DESCRIPTION,
#             long_description=LONG_DESCRIPTION,
#             url=URL,
#             download_url=DOWNLOAD_URL,
#             license=LICENSE,
#             classifiers=CLASSIFIERS,
#             author=AUTHOR,
#             author_email=AUTHOR_EMAIL,
#             platforms=PLATFORMS,
#             version=VERSION,
#             packages=PACKAGES,
#             package_data=PACKAGE_DATA,
#             install_requires=REQUIRES,
#             requires=REQUIRES)


# if __name__ == '__main__':
#     setup(**opts)
