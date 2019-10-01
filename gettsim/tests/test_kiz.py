import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from gettsim.benefits.kiz import kiz
from gettsim.taxes.kindergeld import kg_eligibility_hours
from gettsim.taxes.kindergeld import kg_eligibility_wage
from gettsim.tests.auxiliary_test_tax import load_tb
from gettsim.tests.auxiliary_test_tax import load_test_data


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

years = [2006, 2009, 2011, 2013, 2016, 2019]


@pytest.mark.parametrize("year", years)
def test_kiz(year):
    file_name = "test_dfs_kiz.xlsx"
    columns = ["kiz_temp"]
    df = load_test_data(year, file_name, input_cols)
    tb = load_tb(year)
    tb["yr"] = year
    if year > 2011:
        tb["childben_elig_rule"] = kg_eligibility_hours
    else:
        tb["childben_elig_rule"] = kg_eligibility_wage
    calculated = pd.DataFrame(columns=columns)
    for hid in df["hid"].unique():
        calculated = calculated.append(kiz(df[df["hid"] == hid], tb)[columns])
    expected = load_test_data(year, file_name, columns)
    assert_frame_equal(calculated, expected, check_dtype=False)
