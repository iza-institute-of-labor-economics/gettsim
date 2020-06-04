import pytest

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers  # noqa: F401
from gettsim.pre_processing.policy_for_date import get_policies_for_date  # noqa: F401
from gettsim.visualization import plot_dag  # noqa: F401


__version__ = "0.3.0"


def test():
    pytest.main([str(ROOT_DIR)])
