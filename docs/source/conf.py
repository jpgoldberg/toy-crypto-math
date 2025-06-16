# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import tomllib
from docutils.parsers.rst import Directive

from pprint import pformat
from importlib import import_module
from docutils import nodes
from sphinx import addnodes
from sphinx.application import Sphinx

sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("../../src"))

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
copyright = f"2024–2025 {author}"

github_username = "jpgoldberg"
github_repository = "toy-crypto-math"


# From
# https://github.com/sphinx-doc/sphinx/issues/11548#issuecomment-1693689611


class PrettyPrintIterable(Directive):
    """
    Definition of a custom directive to pretty-print an iterable object.

    This is used in place of the automatic API documentation
    only for module variables which would just print a long signature.
    """

    required_arguments = 1

    def run(self):  # type: ignore
        paths = self.arguments[0].rsplit(".", 2)
        module_path = paths[0]
        module = import_module(module_path)
        member = getattr(module, paths[1])
        if len(paths) == 3:
            member = getattr(member, paths[2])

        code = pformat(
            member,
            indent=2,
            width=80,
            depth=3,
            compact=False,
            sort_dicts=False,
        )

        literal = nodes.literal_block(code, code)
        literal["language"] = "python"

        return [addnodes.desc_content("", literal)]


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions: list[str] = [
    "sphinx_toolbox.more_autodoc.augment_defaults",
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.viewcode",
    "enum_tools.autoenum",
    "sphinx_toolbox.github",
    "sphinx_toolbox.decorators",
    "sphinx_toolbox.wikipedia",
    "sphinx_toolbox.installation",
    #   "sphinx_toolbox.more_autodoc",
    "sphinx_autodoc_typehints",
    "sphinx_toolbox.more_autodoc.autoprotocol",
    "sphinx_toolbox.more_autodoc.genericalias",
    'sphinx_toolbox.more_autodoc.typevars'
]

autodoc_typehints = "both"
typehints_use_signature = True
typehints_use_signature_return = True
always_document_param_types = True
typehints_defaults = "comma"


autodoc_show_sourcelink = True

extensions.append("sphinx.ext.intersphinx")
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "dns": ("https://dnspython.readthedocs.io/en/stable/", None),
}

extensions.append("sphinxcontrib.bibtex")
bibtex_bibfiles = ["refs.bib"]
bibtex_reference_style = "author_year"


def setup(app: Sphinx) -> None:
    """Set up the final Sphinx application.

    This function loads any other customization that was added in this
    configuration file, thus making it itself a Sphinx extension.
    """
    app.add_directive("pprint", PrettyPrintIterable)


rst_prolog = f"""
.. |project| replace:: **{project}**
.. |root| replace:: :mod:`toy_crypto`
.. _pyca: https://cryptography.io/en/latest/
.. _SageMath: https://www.sagemath.org
.. _primefac: https://pypi.org/project/primefac/
.. _bitarray: https://github.com/ilanschnell/bitarray
"""


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "nature"
html_static_path = ["_static"]
