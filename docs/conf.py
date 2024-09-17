# Configuration file for the Sphinx documentation builder. This file only contains a
# selection of the most common options. For a full list see the documentation:
# http://www.sphinx-doc.org/en/master/config.
# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory, add
# these directories to sys.path here. If the directory is relative to the documentation
# root, use os.path.abspath to make it absolute, like shown here.
import datetime as dt
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path("../src").resolve()))

# -- Project information -----------------------------------------------------

project = "GETTSIM"
copyright = f"2019-{dt.datetime.today().year}, GETTSIM team"  # noqa: A001
author = "GETTSIM team"
release = "0.5.1"
version = ".".join(release.split(".")[:2])

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be extensions coming
# with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    "nbsphinx",
    "sphinx_automodapi.automodapi",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "myst_parser",
    "autodoc2",
]

# The master toctree document.
master_doc = "index"

# Add any paths that contain templates here, relative to this directory.

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "restructuredtext",
    ".md": "markdown",
}

# List of patterns, relative to source directory, that match files and directories to
# ignore when looking for source files. This pattern also affects html_static_path and
# html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Extensions configuration ------------------------------------------------

myst_enable_extensions = ["fieldlist"]

add_module_names = False

autodoc2_packages = [
    {
        "path": "../src/_gettsim/social_insurance_contributions",
    },
    {
        "path": "../src/_gettsim/taxes",
    },
    {
        "path": "../src/_gettsim/transfers",
    },
]

autodoc2_render_plugin = "myst"

autodoc2_output_dir = "gettsim_objects/apidocs"

autodoc2_index_template = """Policy functions in GETTSIM
===============================

This section documents the internal functions provided by GETTSIM to model the tax and
transfer system [#f1]_.

.. toctree::
   :titlesonly:
   :glob:
{% for package in top_level %}
   {{ package }}
{%- endfor %}

.. [#f1] Created with `sphinx-autodoc2
    <https://github.com/chrisjsewell/sphinx-autodoc2>`_'"""

autodoc_default_options = {
    "members": True,
    "private-members": True,
    "special-members": True,
    "undoc-members": True,
}
autodoc_mock_imports = [
    "networkx",
    "numpy",
    "numpy_groupies",
    "numba",
    "weave",
    "pandas",
    "pygments",
    "pytest",
    "yaml",
]

extlinks = {
    "ghuser": ("https://github.com/%s", "@%s"),
    "gh": (
        "https://github.com/iza-institute-of-labor-economics/gettsim/pull/%s",
        "#%s",
    ),
}

intersphinx_mapping = {
    "numpy": ("https://docs.scipy.org/doc/numpy", None),
    "pandas": ("https://pandas.pydata.org/pandas-docs/stable", None),
    "python": ("https://docs.python.org/", None),
}

myst_heading_anchors = 3

numpydoc_show_class_members = False

todo_include_todos = True
todo_emit_warnings = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for a list of
# builtin themes.
html_theme = "pydata_sphinx_theme"
html_logo = "_static/images/gettsim_logo.svg"

html_theme_options = {
    "github_url": "https://github.com/iza-institute-of-labor-economics/gettsim",
}

# Add any paths that contain custom static files (such as style sheets) here, relative
# to this directory. They are copied after the builtin static files, so a file named
# "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = ["css/custom.css"]

html_sidebars = {
    "**": [
        "relations.html",  # needs 'show_related': True theme option to display
        "searchbox.html",
    ]
}

# Napoleon settings
napoleon_use_rtype = False
