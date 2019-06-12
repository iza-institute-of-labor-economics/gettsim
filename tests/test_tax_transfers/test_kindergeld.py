import pandas as pd
import pytest
from pandas.testing import assert_series_equal
from tests.auxiliary_test import load_tb
from src.analysis.tax_transfer_funcs.taxes import (
    kindergeld,
    kg_eligibility_wage,
    kg_eligibility_hours,
)


def child_benefit_standard_df():
    cols = ["tu_id", "age", "w_hours", "ineducation", "m_wage"]
    data = [
        [1, 45, 40, False, 3000],
        [1, 40, 0, False, 0],
        [1, 24, 30, True, 700],
        [1, 18, 0, True, 200],
        [1, 17, 2, True, 0],
        [1, 15, 0, True, 0],
    ]

    df = pd.DataFrame(columns=cols, data=data)
    return df


def child_benefit_many_children_df():
    df = pd.DataFrame()
    df["tu_id"] = [5] * 6
    df["age"] = [1, 2, 3, 4, 5, 6]
    df["ineducation"] = [True] * 6
    df["w_hours"] = [0] * 6
    df["m_wage"] = [0] * 6
    return df


def child_benefit_eligibility_conditions():
    cols = ["tu_id", "age", "w_hours", "ineducation", "m_wage"]
    data = [
        [0, 50, 40, False, 0],
        [0, 12, 0, False, 0],
        [0, 14, 25, True, 800],
        [0, 15, 0, True, 300],
    ]
    df = pd.DataFrame(columns=cols, data=data)
    return df


to_test = [
    (child_benefit_standard_df(), 2019, 588),
    (child_benefit_standard_df(), 2002, 462),
    (child_benefit_many_children_df(), 2011, 1203),
    (child_benefit_many_children_df(), 2001, 966),
    (child_benefit_eligibility_conditions(), 2013, 558),
    (child_benefit_eligibility_conditions(), 2000, 429),
]


@pytest.mark.parametrize("df, yr, res", to_test)
def test_kindergeld(df, yr, res):
    tb = load_tb(yr)
    if yr > 2011:
        tb["childben_elig_rule"] = kg_eligibility_hours
    else:
        tb["childben_elig_rule"] = kg_eligibility_wage

    actual = pd.DataFrame(index=df["tu_id"], columns=["kindergeld_tu_basis"])
    for tu_id in df["tu_id"].unique():
        actual_tu = kindergeld(df[df["tu_id"] == tu_id], tb)
        actual.loc[tu_id, "kindergeld_tu_basis"] = actual_tu["kindergeld_tu_basis"]
    expected = pd.Series(data=res, index=actual.index, name="kindergeld_tu_basis")

    print(actual, "\n\n")
    print(expected, "\n\n")

    assert_series_equal(actual["kindergeld_tu_basis"], expected)
