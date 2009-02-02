# -*- coding: utf-8 -*-
#
# parched documentation build configuration file, created by
# sphinx-quickstart on Mon Feb  2 15:33:13 2009.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# The contents of this file are pickled, so don't put values in the namespace
# that aren't pickleable (module imports are okay, they're removed automatically).

import sys, os

sys.path.append(os.path.abspath('../'))

# General configuration
# ---------------------

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.intersphinx']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'contents'
project = u'parched'
copyright = u'2009, Sebastian Nowicki'
version = '0.1'
release = '0.1.0pre'
exclude_trees = ['_build']
pygments_style = 'sphinx'


# Options for HTML output
# -----------------------

html_style = 'default.css'
html_static_path = ['_static']
htmlhelp_basename = 'parcheddoc'
