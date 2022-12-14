import itertools

import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from gettsim import compute_taxes_and_transfers
from gettsim import set_up_policy_environment
from gettsim.config import ROOT_DIR


INPUT_COLS = [
    "hh_id",
    "tu_id",
    "p_id",
    "eink_st_kinderfreib_tu",
    "wohnort_ost",
    "steuerklasse",
    "bruttolohn_m",
    "alter",
    "hat_kinder",
    "arbeitsstunden_w",
    "in_ausbildung",
]

OUT_COLS = ["lohn_st_m", "lohn_st_soli_m", "lohn_st_eink", "vorsorgepauschale"]


YEARS = [2022]


@pytest.fixture(scope="module")
def input_data():

    # Loading BMF test data
    lst_data = pd.read_excel(
        ROOT_DIR / "tests" / "test_data" / "lohnsteuer_testfälle_bmf_2022.xlsx",
        header=9,
    )

    # Drop test cases not covered by GETTSIM

    lst_data.columns = lst_data.columns.str.lower()

    lst_data = lst_data[
        (lst_data["af"] == 0)
        & (lst_data["ajahr"] == 0)
        & (lst_data["alter1"] != 1)
        & (lst_data["entsch"] == 0)
        & (lst_data["jfreib"] == 0)
        & (lst_data["jhinzu"] == 0)
        & (lst_data["jre4"] == 0)
        & (lst_data["jre4ent"] == 0)
        & (lst_data["jvbez"] == 0)
        & (lst_data["lzzfreib"] == 0)
        & (lst_data["lzzhinzu"] == 0)
        & (lst_data["krv"] != 2)
        & (lst_data["pkpv"] == 0)
        & (lst_data["pkv"] == 0)
        & (lst_data["pvs"] == 0)
        & (lst_data["sonstb"] == 0)
        & (lst_data["sonstent"] == 0)
        & (lst_data["sterbe"] == 0)
        & (lst_data["vbez"] == 0)
        & (lst_data["vbezm"] == 0)
        & (lst_data["vbezs"] == 0)
        & (lst_data["vbs"] == 0)
        & (lst_data["vkapa"] == 0)
        & (lst_data["vmt"] == 0)
        & (lst_data["zmvb"] == 0)
    ].copy()

    lst_data.head()

    # Only keep relevant variables and rename then to GETTSIM convention
    # lst_data.columns
    var_names = {
        "lfd. nr.": "p_id",
        "stkl": "steuerklasse",
        "zkf": "anz_kinder_mit_kindergeld_tu",
        "krv": "wohnort_ost",
        "re4": "lst_wage",  # in cents
        "lzz": "period_of_obtained_wage",
        "lstlzz": "lohn_st",
        "solzlzz": "lohn_st_soli",
    }
    test_data = lst_data[[*var_names]].rename(columns=var_names).copy()

    # Create IDs
    test_data["tu_id"] = test_data["p_id"]
    test_data["hh_id"] = test_data["p_id"]

    # Create variables needed for GETTSIM (not sure why GETTSIM requires them)
    test_data["alter"] = 25
    test_data.loc[test_data["wohnort_ost"] == 0, "wohnort_ost"] = False
    test_data.loc[test_data["wohnort_ost"] == 1, "wohnort_ost"] = True
    test_data["wohnort_ost"] = test_data["wohnort_ost"].astype(bool)
    test_data.loc[test_data["anz_kinder_mit_kindergeld_tu"] == 0, "hat_kinder"] = False
    test_data.loc[test_data["anz_kinder_mit_kindergeld_tu"] > 0, "hat_kinder"] = True
    test_data["hat_kinder"] = test_data["hat_kinder"].astype(bool)
    test_data["arbeitsstunden_w"] = 40
    test_data["in_ausbildung"] = False

    # Transform cent values to full Euros
    test_data["lst_wage"] = test_data["lst_wage"] / 100
    test_data["lohn_st"] = test_data["lohn_st"] / 100
    test_data["lohn_st_soli"] = test_data["lohn_st_soli"] / 100

    # Take into account period of obtained wage (Lohnzahlungszeitraum, LZZ)
    test_data.loc[test_data["period_of_obtained_wage"] == 4, "bruttolohn_m"] = (
        test_data["lst_wage"] * 360 / 12
    )
    test_data.loc[test_data["period_of_obtained_wage"] == 3, "bruttolohn_m"] = (
        test_data["lst_wage"] / 7 * 360 / 12
    )
    test_data.loc[
        test_data["period_of_obtained_wage"] == 2, "bruttolohn_m"
    ] = test_data["lst_wage"]
    test_data.loc[test_data["period_of_obtained_wage"] == 1, "bruttolohn_m"] = (
        test_data["lst_wage"] / 12
    )

    test_data["lohn_st_m"] = test_data["lohn_st"]
    test_data["lohn_st_soli_m"] = test_data["lohn_st_soli"]

    for outvar in ["lohn_st_m", "lohn_st_soli_m"]:

        test_data.loc[test_data["period_of_obtained_wage"] == 4, outvar] = (
            test_data[outvar] * 360 / 12
        )
        test_data.loc[test_data["period_of_obtained_wage"] == 3, outvar] = (
            test_data[outvar] / 7 * 360 / 12
        )
        test_data.loc[test_data["period_of_obtained_wage"] == 2, outvar] = test_data[
            outvar
        ]
        test_data.loc[test_data["period_of_obtained_wage"] == 1, outvar] = (
            test_data[outvar] / 12
        )

    # Provisionally, calculate amount of claimed Kinderfreibeträge outside of Gettsim
    test_data["eink_st_kinderfreib_tu"] = (
        test_data["anz_kinder_mit_kindergeld_tu"] * (2730 + 1464) * 2
    )

    # Conditions to simplify testing
    test_data["lohn_st_eink"] = 0
    test_data["vorsorgepauschale"] = 0

    test_data = test_data[test_data["steuerklasse"].isin([5])]
    test_data = test_data[test_data["p_id"] == 1305]

    return test_data


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_lohnsteuer_2(input_data, year, column):
    input_data = input_data.reset_index(drop=True)
    df = input_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
        columns_overriding_functions=["eink_st_kinderfreib_tu"],
    )
    assert_series_equal(result[column], input_data[column], check_dtype=False)
