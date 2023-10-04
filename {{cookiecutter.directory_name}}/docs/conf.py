"""
See https://www.sphinx-doc.org/en/master/usage/configuration.html
"""
from datetime import datetime
from operator import itemgetter
from os.path import dirname
from typing import Final
import os
import sys

import tomlkit

with open(f'{dirname(__file__)}/../pyproject.toml') as f:
    authors, name, version = itemgetter('authors', 'name',
                                         'version')(tomlkit.load(f).unwrap()['poetry'])
# region Path setup
# If extensions (or modules to document with autodoc) are in another directory, add these
# directories to sys.path here. If the directory is relative to the documentation root, use
# os.path.abspath to make it absolute, like shown here.
sys.path.insert(0, os.path.abspath('..'))
# endregion
author: Final[str] = authors[0]
copyright: Final[str] = str(datetime.now().year)
project: Final[str] = name
version: Final[str] = version
release: Final[str] = f'v{version}'
extensions: Final[list[str]] = (['sphinx.ext.autodoc', 'sphinx.ext.napoleon'] +
                                (['sphinx_click'] if project.get('scripts') else []))
exclude_patterns: Final[list[str]] = []
master_doc: Final[str] = 'index'
html_static_path: Final[list[str]] = []
html_theme: Final[str] = 'alabaster'
templates_path: Final[list[str]] = ['_templates']
