import os
import sys

sys.path.insert(0, os.path.abspath('..'))
import derivater

extensions = [
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
    'sphinx.ext.autodoc',
]

source_suffix = '.rst'

master_doc = 'index'

project = 'Derivater'
copyright = '2018, Akuli'
author = 'Akuli'

nitpicky = True

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
version = derivater.__version__
release = derivater.__version__

language = None
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
pygments_style = 'sphinx'


html_theme = 'alabaster'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
#
# html_theme_options = {}

html_static_path = ['_static']

intersphinx_mapping = {}#'python': ('https://docs.python.org/3', None)}
