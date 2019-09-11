import os
import sys

sys.path.insert(0, os.path.abspath('../..'))

extensions = [
    'sphinxcontrib.autohttp.flask',
    'sphinxcontrib.autohttp.flaskqref'
]
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = 'Kubemen'
copyright = '2019, Numberly'
author = 'Numberly'

html_theme = 'alabaster'
html_sidebars = {
    '**': [
        'sidebarlogo.html',
        'navigation.html',
        'searchbox.html',
        'github-corners.html'
    ]
}
htmlhelp_basename = 'kubemen'
