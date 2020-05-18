import pytest

from gettsim.pre_processing.exogene_renten_daten.lade_renten_daten import (
    lade_exogene_renten_daten,
)


@pytest.fixture(scope="session")
def renten_daten():
    return lade_exogene_renten_daten()
