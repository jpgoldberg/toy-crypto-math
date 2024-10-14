# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import tomllib

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("../.."))

import toy_crypto  # noqa

from toy_crypto import __about__  # noqa: E402

version = __about__.__version__

# Pull general sphinx project info from pyproject.toml
# Modified from https://stackoverflow.com/a/75396624/1304076
with open("../../pyproject.toml", "rb") as f:
    toml = tomllib.load(f)

pyproject = toml["project"]

project = pyproject["name"]
release = version
author = ",".join([author["name"] for author in pyproject["authors"]])
copyright = f"2024 {author}"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions: list[str] = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
]

extensions.append("sphinx_autodoc_typehints")
type_hints_use_signature = True
typehints_use_signature_return = True

extensions.append("sphinx.ext.intersphinx")
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "dns": ("https://dnspython.readthedocs.io/en/stable/", None),
}

st_prolog = f"""
.. |project| replace:: **{project}**
.. |root| replace:: :mod:`hostname`
.. |True| replace:: :py:const:`True`
.. |False| replace:: :py:const:`False`
"""


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "nature"
html_static_path = ["_static"]
