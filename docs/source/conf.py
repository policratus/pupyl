# -- Path setup --------------------------------------------------------------
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.abspath('../..'))

# -- Project information -----------------------------------------------------

project = '🧿 pupyl'
copyright = f'{datetime.today().year}, Nelson Forte'
author = 'Nelson Forte'

release = '0.13.5'
version = release

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.napoleon',
    'sphinx.ext.autodoc',
    'sphinx.ext.autosectionlabel'
]

# -- Options for HTML output -------------------------------------------------

html_theme = 'press'

html_static_path = ['_static']

# -- Napoleon specific configurations -----------------------------------------

napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = True
napoleon_attr_annotations = True

# -- Options for autosectionlabel --------------------------------------------
# Make sure the target is unique
autosectionlabel_prefix_document = True
