import pytest
import yaml

from gettsim.config import ROOT_DIR


@pytest.fixture(scope="session")
def raw_tax_policy_data():
    return yaml.safe_load((ROOT_DIR / "data" / "param.yaml").read_text())


@pytest.fixture(scope="session")
def raw_pension_data():
    return yaml.safe_load((ROOT_DIR / "data" / "pension_data.yaml").read_text())
