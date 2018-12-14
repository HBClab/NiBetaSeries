# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import re

import nibetaseries

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
]
if os.getenv('SPELLCHECK'):
    extensions += 'sphinxcontrib.spelling',
    spelling_show_suggestions = True
    spelling_lang = 'en_US'

sphinx_gallery_conf = {
     # path to your examples scripts
     'examples_dirs': '../examples',
     # path where to save gallery generated examples
     'gallery_dirs': 'auto_examples',
}

# setting for sphinx-versioning
scv_whitelist_branches = ('master', 'latest')
scv_whitelist_tags = (re.compile(r'^v\d+\.\d+\.\d+$'),)
scv_priority = 'tags'

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
html_theme_options = {
    'githuburl': 'https://github.com/HBClab/NiBetaSeries/'
}

html_use_smartypants = True
html_split_index = False
html_sidebars = {
   '**': ['searchbox.html', 'globaltoc.html', 'sourcelink.html'],
}
html_short_title = '%s-%s' % (project, version)

napoleon_use_ivar = True
napoleon_use_rtype = False
napoleon_use_param = False
