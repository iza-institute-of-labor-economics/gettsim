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
def test_tax_transfer(
    input_data,
    year,
    e_st_abzuege_raw_data,
    ges_renten_vers_raw_data,
    e_st_raw_data,
    soli_st_raw_data,
    arbeitsl_geld_2_raw_data,
    arbeitsl_geld_raw_data,
    soz_vers_beitr_raw_data,
    unterhalt_raw_data,
    abgelt_st_raw_data,
    wohngeld_raw_data,
    kinderzuschlag_raw_data,
    kindergeld_raw_data,
):
    df = input_data[input_data["year"] == year].copy()
    ges_renten_vers_data = get_policies_for_date(
        year=year, group="ges_renten_vers", raw_group_data=ges_renten_vers_raw_data
    )
    e_st_abzuege_data = get_policies_for_date(
        year=year, group="e_st_abzuege", raw_group_data=e_st_abzuege_raw_data
    )
    e_st_data = get_policies_for_date(
        year=year, group="e_st", raw_group_data=e_st_raw_data
    )
    soli_st_data = get_policies_for_date(
        year=year, group="soli_st", raw_group_data=soli_st_raw_data
    )
    arbeitsl_geld_2_data = get_policies_for_date(
        year=year, group="arbeitsl_geld_2", raw_group_data=arbeitsl_geld_2_raw_data
    )
    arbeitsl_geld_data = get_policies_for_date(
        year=year, group="arbeitsl_geld", raw_group_data=arbeitsl_geld_raw_data
    )
    soz_vers_beitr_data = get_policies_for_date(
        year=year, group="soz_vers_beitr", raw_group_data=soz_vers_beitr_raw_data
    )
    unterhalt_data = get_policies_for_date(
        year=year, group="unterhalt", raw_group_data=unterhalt_raw_data
    )
    abgelt_st_data = get_policies_for_date(
        year=year, group="abgelt_st", raw_group_data=abgelt_st_raw_data
    )
    wohngeld_data = get_policies_for_date(
        year=year, group="wohngeld", raw_group_data=wohngeld_raw_data
    )
    kinderzuschlag_data = get_policies_for_date(
        year=year, group="kinderzuschlag", raw_group_data=kinderzuschlag_raw_data
    )
    kindergeld_data = get_policies_for_date(
        year=year, group="kindergeld", raw_group_data=kindergeld_raw_data
    )
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
        ges_renten_vers_data=ges_renten_vers_data,
    )
