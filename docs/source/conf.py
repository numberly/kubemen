import os
import shutil
import sys

sys.path.insert(0, os.path.abspath('../..'))
shutil.copyfile("../../config.py", "../config.py")
shutil.copyfile("../../README.rst", "README.rst")

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinxcontrib.autohttp.flask',
    'sphinxcontrib.autohttp.flaskqref',
]

master_doc = 'index'

project = 'Kubemen'
copyright = 'Numberly'
author = 'Numberly'

html_theme = 'sphinx_rtd_theme'
