import pytest
import yaml

from gettsim.config import ROOT_DIR


@pytest.fixture(scope="session")
def tax_policy_data():
    return yaml.safe_load(open(f"{ROOT_DIR}/data/param.yaml", "rb"))
