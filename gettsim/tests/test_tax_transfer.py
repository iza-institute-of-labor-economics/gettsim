from datetime import date

import pandas as pd
import pytest

from gettsim.config import ROOT_DIR
from gettsim.pre_processing.policy_for_date import get_policies_for_date
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
    eink_st_abzuege_raw_data,
    renten_daten,
    eink_st_raw_data,
    soli_st_raw_data,
    arbeitsl_geld_2_raw_data,
    arbeitsl_geld_raw_data,
    soz_vers_beitr_raw_data,
    unterhalt_raw_data,
    abgelt_st_raw_data,
    wohngeld_raw_data,
    kinderzuschlag_raw_data,
    kindergeld_raw_data,
    elterngeld_raw_data,
):
    df = input_data[input_data["jahr"] == year].copy()
    policy_date = date(year, 1, 1)
    eink_st_abzuege_params = get_policies_for_date(
        policy_date=policy_date,
        group="eink_st_abzuege",
        raw_group_data=eink_st_abzuege_raw_data,
    )
    eink_st_params = get_policies_for_date(
        policy_date=policy_date, group="eink_st", raw_group_data=eink_st_raw_data
    )
    soli_st_params = get_policies_for_date(
        policy_date=policy_date, group="soli_st", raw_group_data=soli_st_raw_data
    )
    arbeitsl_geld_2_params = get_policies_for_date(
        policy_date=policy_date,
        group="arbeitsl_geld_2",
        raw_group_data=arbeitsl_geld_2_raw_data,
    )
    arbeitsl_geld_params = get_policies_for_date(
        policy_date=policy_date,
        group="arbeitsl_geld",
        raw_group_data=arbeitsl_geld_raw_data,
    )
    soz_vers_beitr_params = get_policies_for_date(
        policy_date=policy_date,
        group="soz_vers_beitr",
        raw_group_data=soz_vers_beitr_raw_data,
    )
    unterhalt_params = get_policies_for_date(
        policy_date=policy_date, group="unterhalt", raw_group_data=unterhalt_raw_data
    )
    abgelt_st_params = get_policies_for_date(
        policy_date=policy_date, group="abgelt_st", raw_group_data=abgelt_st_raw_data
    )
    wohngeld_params = get_policies_for_date(
        policy_date=policy_date, group="wohngeld", raw_group_data=wohngeld_raw_data
    )
    kinderzuschlag_params = get_policies_for_date(
        policy_date=policy_date,
        group="kinderzuschlag",
        raw_group_data=kinderzuschlag_raw_data,
    )
    kindergeld_params = get_policies_for_date(
        policy_date=policy_date, group="kindergeld", raw_group_data=kindergeld_raw_data
    )

    elterngeld_params = get_policies_for_date(
        policy_date=policy_date, group="elterngeld", raw_group_data=elterngeld_raw_data
    )

    tax_transfer(
        df,
        arbeitsl_geld_2_params=arbeitsl_geld_2_params,
        abgelt_st_params=abgelt_st_params,
        arbeitsl_geld_params=arbeitsl_geld_params,
        soz_vers_beitr_params=soz_vers_beitr_params,
        eink_st_abzuege_params=eink_st_abzuege_params,
        elterngeld_params=elterngeld_params,
        unterhalt_params=unterhalt_params,
        wohngeld_params=wohngeld_params,
        kinderzuschlag_params=kinderzuschlag_params,
        eink_st_params=eink_st_params,
        soli_st_params=soli_st_params,
        kindergeld_params=kindergeld_params,
        renten_daten=renten_daten,
    )
