import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.benefits.kiz import kiz
from gettsim.config import ROOT_DIR
from gettsim.taxes.kindergeld import kg_eligibility_hours
from gettsim.taxes.kindergeld import kg_eligibility_wage
from gettsim.tests.auxiliary_test_tax import get_policies_for_date
from gettsim.tests.auxiliary_test_tax import load_tax_benefit_data


input_cols = [
    "pid",
    "hid",
    "tu_id",
    "head",
    "hhtyp",
    "hh_korr",
    "hhsize",
    "child",
    "pensioner",
    "age",
    "w_hours",
    "m_wage",
    "ineducation",
    "miete",
    "heizkost",
    "alleinerz",
    "mehrbed",
    "adult_num_tu",
    "child_num_tu",
    "alg2_grossek_hh",
    "ar_alg2_ek_hh",
    "kindergeld_hh",
    "uhv",
    "year",
]
out_cols = ["kiz_temp", "kiz_incrange"]
years = [2006, 2009, 2011, 2013, 2016, 2019]
tax_policy_data = load_tax_benefit_data()


@pytest.fixture
def input_data():
    file_name = "test_dfs_kiz.csv"
    out = pd.read_csv(f"{ROOT_DIR}/tests/test_data/{file_name}")
    return out


@pytest.mark.parametrize("year", years)
def test_kiz(input_data, year):
    columns = ["kiz_temp"]
    year_data = input_data[input_data["year"] == year]
    df = year_data[input_cols].copy()
    tb = get_policies_for_date(tax_policy_data, year=year)
    tb["yr"] = year
    if year > 2011:
        tb["childben_elig_rule"] = kg_eligibility_hours
    else:
        tb["childben_elig_rule"] = kg_eligibility_wage
    for col in out_cols:
        df[col] = np.nan
    df = df.groupby("hid").apply(kiz, tb=tb)
    assert_frame_equal(df[columns], year_data[columns], check_less_precise=True)
