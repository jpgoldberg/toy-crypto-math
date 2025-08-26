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

project = "ToyCrypto"
release = version
author = ",".join([author["name"] for author in pyproject["authors"]])
copyright = f"2024–2025 {author}"

github_username = "jpgoldberg"
github_repository = "toy-crypto-math"

cwd = os.path.abspath(".")
test_data_path: str = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "test_data")
)

doctest_global_setup = f"""
import os
BASE_TEST_DATA = '{test_data_path}'
"""


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
    # "sphinx_toolbox.installation",
    # "sphinx_toolbox.more_autodoc.typehints",
    "sphinx_autodoc_typehints",
    "sphinx_toolbox.more_autodoc.autoprotocol",
    "sphinx_toolbox.more_autodoc.genericalias",
    "sphinx_toolbox.more_autodoc.typevars",
    # "sphinx_toolbox.more_autodoc.variables",
    "sphinx_reredirects",
    "sphinx_prompt",
    "sphinx_toolbox.collapse",
]

autodoc_typehints = "signature"
typehints_use_signature = True
typehints_use_signature_return = True
always_document_param_types = True
typehints_defaults = "comma"


autodoc_show_sourcelink = True

extensions.append("sphinx.ext.intersphinx")
intersphinx_mapping = {
    "crypto": ("https://www.pycryptodome.org", None),
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
.. _PyNaCl: https://pynacl.readthedocs.io/en/latest/
.. _SageMath: https://www.sagemath.org
.. _primefac: https://pypi.org/project/primefac/
.. _bitarray: https://github.com/ilanschnell/bitarray
.. _pypkcs1: https://github.com/bdauvergne/python-pkcs1/
.. _pypi: https://pypi.org/
.. _sympy: https://www.sympy.org/
"""


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "pydata_sphinx_theme"
html_sidebars = {
    "**": [
        "sidebar-nav-bs.html",
    ],
    "why/index": [],
    "index": [],
    "bibliography": [],
}
html_theme_options: dict[str, object] = {
    "logo": {
        "text": f"ToyCrypto ({version})",
    },
    "icon_links": [
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/toycrypto/",
            "icon": "_static/pypi-logo-no-text.svg",
            "type": "local",
        },
        {
            # Label for this link
            "name": "GitHub",
            "url": f"https://github.com/{github_username}/{github_repository}",
            "icon": "fa-brands fa-github",
            "type": "fontawesome",
        },
    ],
    # page elements
    "navbar_start": ["navbar-logo"],
    "navbar_end": ["theme-switcher", "navbar-icon-links.html"],
    "footer_start": ["copyright", "sphinx-version"],
    "footer_end": ["theme-version"],
    "secondary_sidebar_items": ["page-toc", "edit-this-page", "sourcelink"],
    "header_links_before_dropdown": 4,
    "primary_sidebar_end": ["indices.html", "sidebar-ethical-ads.html"],
}

# Reorganization means some redirects.
# Sadly, I can't to 301s when hosting on github pages

redirects: dict[str, str] = {
    src: f"modules/{src}.html"
    for src in [
        "birthday", "bit_utils", "ec", "games", "nt", "rand",
        "rsa", "sieve", "types", "utils", "vigenere",
    ]
}  # fmt: skip

html_static_path = ["_static"]

# linkcheck configuration

linkcheck_ignore: list[str] = [
    # Taylor and Francis seem to forbid (403) robots
    r"^https://www.tandfonline.com/doi/abs/"
]

# If we hit a rate limit, just give it a pass after a few seconds
linkcheck_rate_limit_timeout = 5
linkcheck_report_timeouts_as_broken = False
