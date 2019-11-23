import pandas as pd
import pytest

from gettsim.config import ROOT_DIR
from gettsim.policy_for_date import get_policies_for_date
from gettsim.tax_transfer import tax_transfer


YEARS = [2002, 2010, 2018, 2019]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_tax_transfer.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_tax_transfer(input_data, year):
    df = input_data[input_data["year"] == year].copy()
    pension_data = pd.read_excel(ROOT_DIR / "data" / "pensions.xlsx").set_index("var")
    e_st_abzuege_data = get_policies_for_date(year=year, group="e_st_abzuege")
    e_st_data = get_policies_for_date(year=year, group="e_st")
    soli_st_data = get_policies_for_date(year=year, group="soli_st")
    arbeitsl_geld_2_data = get_policies_for_date(year=year, group="arbeitsl_geld_2")
    arbeitsl_geld_data = get_policies_for_date(year=year, group="arbeitsl_geld")
    soz_vers_beitr_data = get_policies_for_date(year=year, group="soz_vers_beitr")
    unterhalt_data = get_policies_for_date(year=year, group="unterhalt")
    abgelt_st_data = get_policies_for_date(year=year, group="abgelt_st")
    wohngeld_data = get_policies_for_date(year=year, group="wohngeld")
    kinderzuschlag_data = get_policies_for_date(year=year, group="kinderzuschlag")
    kindergeld_data = get_policies_for_date(year=year, group="kindergeld")
    tax_transfer(
        df,
        arbeitsl_geld_2_data=arbeitsl_geld_2_data,
        abgelt_st_data=abgelt_st_data,
        arbeitsl_geld_data=arbeitsl_geld_data,
        soz_vers_beitr_data=soz_vers_beitr_data,
        e_st_abzuege_data=e_st_abzuege_data,
        unterhalt_data=unterhalt_data,
        wohngeld_data=wohngeld_data,
        kinderzuschlag_data=kinderzuschlag_data,
        e_st_data=e_st_data,
        soli_st_data=soli_st_data,
        kindergeld_data=kindergeld_data,
        pension_data=pension_data,
    )
