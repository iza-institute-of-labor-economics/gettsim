"""This module contains the main namespace of gettsim."""
from __future__ import annotations

try:
    # Import the version from _version.py which is dynamically created by
    # setuptools-scm upon installing the project with pip.
    # Do not put it under version control!
    from _gettsim._version import version as __version__
except ImportError:
    __version__ = "unknown"


import itertools
import warnings

import pytest
from _gettsim_tests import TEST_DIR
from _gettsim.config import RESOURCE_DIR
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import set_up_policy_environment
from _gettsim.visualization import plot_dag

# ToDo: Remove. Legacy stuff, still in docs
from _gettsim import social_insurance_contributions
from _gettsim import synthetic
from _gettsim import taxes
from _gettsim import transfers


COUNTER_TEST_EXECUTIONS = itertools.count()


def test(*args):
    n_test_executions = next(COUNTER_TEST_EXECUTIONS)

    if n_test_executions == 0:
        pytest.main([str(TEST_DIR), *args])
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
    "RESOURCE_DIR",
    # ToDo: Remove remainder.
    "social_insurance_contributions",
    "synthetic",
    "taxes",
    "transfers",
]
