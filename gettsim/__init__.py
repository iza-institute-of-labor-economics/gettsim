import pytest

from gettsim.config import ROOT_DIR


__version__ = "0.2.0"


def test():
    pytest.main([str(ROOT_DIR)])
