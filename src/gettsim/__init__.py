"""This module contains the main namespace of gettsim."""
# Import the version from _version.py which is dynamically created by setuptools-scm
# when the project is installed with ``pip install -e .``. Do not put it into version
# control!
from __future__ import annotations

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"


import itertools
import warnings

import pytest
from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers  # noqa: F401
from gettsim.policy_environment import set_up_policy_environment  # noqa: F401
from gettsim.visualization import plot_dag  # noqa: F401


COUNTER_TEST_EXECUTIONS = itertools.count()


def test(*args):
    n_test_executions = next(COUNTER_TEST_EXECUTIONS)

    if n_test_executions == 0:
        pytest.main([str(ROOT_DIR), *args])
    else:
        warnings.warn(
            "Repeated execution of the test suite is not possible. Start a new Python "
            "session or restart the kernel in a Jupyter/IPython notebook to re-run the "
            "tests."
        )


__all__ = [
    "__version__",
    "compute_taxes_and_transfers",
    "set_up_policy_environment",
    "plot_dag",
]
