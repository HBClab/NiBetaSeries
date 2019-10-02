# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

import nibetaseries

# Patch sphinx_gallery.binder.gen_binder_rst so as to point to .py file in repository
import sphinx_gallery.binder


def patched_gen_binder_rst(fpath, binder_conf, gallery_conf):
    """Generate the RST + link for the Binder badge.
    Parameters
    ----------
    fpath: str
        The path to the `.py` file for which a Binder badge will be generated.
    binder_conf: dict or None
        If a dictionary it must have the following keys:
        'binderhub_url'
            The URL of the BinderHub instance that's running a Binder service.
        'org'
            The GitHub organization to which the documentation will be pushed.
        'repo'
            The GitHub repository to which the documentation will be pushed.
        'branch'
            The Git branch on which the documentation exists (e.g., gh-pages).
        'dependencies'
            A list of paths to dependency files that match the Binderspec.
    Returns
    -------
    rst : str
        The reStructuredText for the Binder badge that links to this file.
    """
    binder_conf = sphinx_gallery.binder.check_binder_conf(binder_conf)
    binder_url = sphinx_gallery.binder.gen_binder_url(fpath, binder_conf, gallery_conf)
    binder_url = binder_url.replace(
        gallery_conf['gallery_dirs'] + os.path.sep, "").replace("ipynb", "py")

    rst = (
        "\n"
        "  .. container:: binder-badge\n\n"
        "    .. image:: https://mybinder.org/badge_logo.svg\n"
        "      :target: {}\n"
        "      :width: 150 px\n").format(binder_url)
    return rst


sphinx_gallery.binder.gen_binder_rst = patched_gen_binder_rst

sphinx_gallery_conf = {
        # path to your examples scripts
        'examples_dirs': '../examples',
        # path where to save gallery generated examples
        'gallery_dirs': 'auto_examples',
        'binder': {
                'org': 'HBClab',
                'repo': 'NiBetaSeries',
                'branch': 'master',
                'binderhub_url': 'https://mybinder.org',
                'dependencies': ['../binder/requirements.txt'],
                'notebooks_dir': 'examples',
        }
}

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.extlinks',
    'sphinx.ext.ifconfig',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
    'nipype.sphinxext.plot_workflow',
    'sphinx_gallery.gen_gallery',
    'sphinxarg.ext',
    'sphinx.ext.mathjax',
    'sphinxcontrib.bibtex',
]
if os.getenv('SPELLCHECK'):
    extensions += 'sphinxcontrib.spelling',
    spelling_show_suggestions = True
    spelling_lang = 'en_US'

source_suffix = '.rst'
master_doc = 'index'
project = 'NiBetaSeries'
year = '2018'
author = 'James Kent'
copyright = '{0}, {1}'.format(year, author)
version = release = nibetaseries.__version__

pygments_style = 'trac'
templates_path = ['.']
extlinks = {
    'issue': ('https://github.com/HBClab/NiBetaSeries/issues/%s', '#'),
    'pr': ('https://github.com/HBClab/NiBetaSeries/pull/%s', 'PR #'),
}
html_theme = "sphinx_rtd_theme"

html_sidebars = {
   '**': ['searchbox.html', 'globaltoc.html', 'sourcelink.html'],
}
html_short_title = '%s-%s' % (project, version)

html_static_path = ['development/_static']

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False
