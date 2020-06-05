import itertools
import warnings

import pytest

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers  # noqa: F401
from gettsim.pre_processing.policy_for_date import get_policies_for_date  # noqa: F401

__version__ = "0.3.1"

COUNTER_TEST_EXECUTIONS = itertools.count()


def test():
    n_test_executions = next(COUNTER_TEST_EXECUTIONS)

    if n_test_executions == 0:
        pytest.main([str(ROOT_DIR)])
    else:
        warnings.warn(
            "Repeated execution of the test suite is not possible. Start a new Python"
            "session or restart the kernel in a Jupyter/IPython notebook to re-run the"
            "tests."
        )
