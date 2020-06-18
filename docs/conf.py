# Configuration file for the Sphinx documentation builder. This file only contains a
# selection of the most common options. For a full list see the documentation:
# http://www.sphinx-doc.org/en/master/config.
# -- Path setup --------------------------------------------------------------
# If extensions (or modules to document with autodoc) are in another directory, add
# these directories to sys.path here. If the directory is relative to the documentation
# root, use os.path.abspath to make it absolute, like shown here.
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------

project = "GETTSIM"
copyright = f"2019-{dt.datetime.now().year}, GETTSIM team"  # noqa: A001
author = "GETTSIM team"
release = "0.3.1"
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
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "sphinx_copybutton",
    "sphinx_rtd_theme",
]

# The master toctree document.
master_doc = "index"

# Add any paths that contain templates here, relative to this directory.
# templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and directories to
# ignore when looking for source files. This pattern also affects html_static_path and
# html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Extensions configuration ------------------------------------------------

add_module_names = False

autodoc_default_options = {
    "members": True,
    "private-members": True,
    "special-members": True,
    "undoc-members": True,
}
autodoc_mock_imports = [
    "bokeh",
    "networkx",
    "numpy",
    "pandas",
    "pygments",
    "pytest",
    "yaml",
]

extlinks = {
    "ghuser": ("https://github.com/%s", "@"),
    "gh": ("https://github.com/iza-institute-of-labor-economics/gettsim/pull/%s", "#"),
}

numpydoc_show_class_members = False

todo_include_todos = True
todo_emit_warnings = True

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for a list of
# builtin themes.
html_theme = "sphinx_rtd_theme"
html_logo = "_static/images/gettsim_logo.svg"

html_theme_options = {
    "logo_only": True,
    "display_version": False,
}

# Add any paths that contain custom static files (such as style sheets) here, relative
# to this directory. They are copied after the builtin static files, so a file named
# "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

html_css_files = ["css/custom.css"]
