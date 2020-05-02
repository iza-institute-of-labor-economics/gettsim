import pytest
import yaml

from gettsim.config import ROOT_DIR
from gettsim.pre_processing.exogene_renten_daten.lade_renten_daten import (
    lade_exogene_renten_daten,
)


@pytest.fixture(scope="session")
def eink_st_raw_data():
    return yaml.safe_load(
        (ROOT_DIR / "data" / "eink_st.yaml").read_text(encoding="utf-8")
    )


@pytest.fixture(scope="session")
def renten_daten():
    return lade_exogene_renten_daten()


@pytest.fixture(scope="session")
def eink_st_abzuege_raw_data():
    return yaml.safe_load(
        (ROOT_DIR / "data" / "eink_st_abzuege.yaml").read_text(encoding="utf-8")
    )


@pytest.fixture(scope="session")
def soli_st_raw_data():
    return yaml.safe_load(
        (ROOT_DIR / "data" / "soli_st.yaml").read_text(encoding="utf-8")
    )


@pytest.fixture(scope="session")
def arbeitsl_geld_2_raw_data():
    return yaml.safe_load(
        (ROOT_DIR / "data" / "arbeitsl_geld_2.yaml").read_text(encoding="utf-8")
    )


@pytest.fixture(scope="session")
def arbeitsl_geld_raw_data():
    return yaml.safe_load(
        (ROOT_DIR / "data" / "arbeitsl_geld.yaml").read_text(encoding="utf-8")
    )


@pytest.fixture(scope="session")
def unterhalt_raw_data():
    return yaml.safe_load(
        (ROOT_DIR / "data" / "unterhalt.yaml").read_text(encoding="utf-8")
    )


@pytest.fixture(scope="session")
def abgelt_st_raw_data():
    return yaml.safe_load(
        (ROOT_DIR / "data" / "abgelt_st.yaml").read_text(encoding="utf-8")
    )


@pytest.fixture(scope="session")
def wohngeld_raw_data():
    return yaml.safe_load(
        (ROOT_DIR / "data" / "wohngeld.yaml").read_text(encoding="utf-8")
    )


@pytest.fixture(scope="session")
def kinderzuschlag_raw_data():
    return yaml.safe_load(
        (ROOT_DIR / "data" / "kinderzuschlag.yaml").read_text(encoding="utf-8")
    )


@pytest.fixture(scope="session")
def kindergeld_raw_data():
    return yaml.safe_load(
        (ROOT_DIR / "data" / "kindergeld.yaml").read_text(encoding="utf-8")
    )


@pytest.fixture(scope="session")
def soz_vers_beitr_raw_data():
    return yaml.safe_load(
        (ROOT_DIR / "data" / "soz_vers_beitr.yaml").read_text(encoding="utf-8")
    )


@pytest.fixture(scope="session")
def elterngeld_raw_data():
    return yaml.safe_load(
        (ROOT_DIR / "data" / "elterngeld.yaml").read_text(encoding="utf-8")
    )
