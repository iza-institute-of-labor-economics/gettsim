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

from _gettsim import (
    aggregation,
    config,
    gettsim_typing,
    piecewise_functions,
    shared,
    taxes,
    transfers,
    visualization,
)
from _gettsim.functions.policy_function import PolicyFunction
from _gettsim.interface import (
    FunctionsAndColumnsOverlapWarning,
    compute_taxes_and_transfers,
)
from _gettsim.policy_environment import PolicyEnvironment, set_up_policy_environment
from _gettsim.synthetic import create_synthetic_data
from _gettsim.visualization import plot_dag
from _gettsim_tests import TEST_DIR

COUNTER_TEST_EXECUTIONS = itertools.count()


def test(*args):
    n_test_executions = next(COUNTER_TEST_EXECUTIONS)

    if n_test_executions == 0:
        pytest.main([str(TEST_DIR), "--noconftest", *args])
    else:
        warnings.warn(
            "Repeated execution of the test suite is not possible. Start a new Python "
            "session or restart the kernel in a Jupyter/IPython notebook to re-run the "
            "tests.",
            stacklevel=2,
        )


__all__ = [
    "__version__",
    "FunctionsAndColumnsOverlapWarning",
    "PolicyEnvironment",
    "PolicyFunction",
    "compute_taxes_and_transfers",
    "set_up_policy_environment",
    "plot_dag",
    # TODO (@hmgaudecker): See what can be changed/removed from remainder.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/378
    "aggregation",
    "config",
    "piecewise_functions",
    "policy_environment",
    "shared",
    "social_insurance_contributions",
    "create_synthetic_data",
    "taxes",
    "transfers",
    "gettsim_typing",
    "visualization",
]
