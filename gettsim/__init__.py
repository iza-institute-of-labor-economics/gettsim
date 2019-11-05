import os

import pytest

from gettsim.config import ROOT_DIR


__version__ = "0.2.0"


def test():
    cwd = os.getcwd()
    os.chdir(ROOT_DIR)
    pytest.main()
    os.chdir(cwd)
