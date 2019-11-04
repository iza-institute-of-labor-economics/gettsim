import pytest
from pandas.testing import assert_series_equal

from gettsim.benefits.arbeitslosengeld import ui
from gettsim.tax_transfer import _apply_tax_transfer_func
from gettsim.taxes.calc_taxes import tarif
from gettsim.tests.auxiliary_test_tax import get_policies_for_date
from gettsim.tests.auxiliary_test_tax import load_tax_benefit_data
from gettsim.tests.auxiliary_test_tax import load_test_data

input_cols = [
    "pid",
    "hid",
    "tu_id",
    "m_wage_l1",
    "east",
    "child",
    "months_ue",
    "months_ue_l1",
    "months_ue_l2",
    "alg_soep",
    "m_pensions",
    "w_hours",
    "child_num_tu",
    "age",
    "year",
]
OUT_COL = "m_alg1"
years = [2010, 2011, 2015, 2019]
tax_policy_data = load_tax_benefit_data()


@pytest.mark.parametrize("year", years)
def test_ui(year):
    file_name = "test_dfs_ui.ods"
    df = load_test_data(year, file_name, input_cols, pd_kwargs={"true_values": "TRUE"})
    tb = get_policies_for_date(tax_policy_data, year=year)
    tb["yr"] = year
    tb["tax_schedule"] = tarif
    expected = load_test_data(year, file_name, OUT_COL)
    df = _apply_tax_transfer_func(
        df,
        tax_func=ui,
        level=["hid", "tu_id", "pid"],
        in_cols=input_cols,
        out_cols=[OUT_COL],
        func_kwargs={"tb": tb},
    )
    # TODO: THis should be reviewed.
    assert_series_equal(df[OUT_COL], expected, check_less_precise=3)
