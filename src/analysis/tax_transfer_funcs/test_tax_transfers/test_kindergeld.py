import pandas as pd
import pytest
from pandas.testing import assert_series_equal
from src.analysis.tax_transfer_funcs.test_tax_transfers.auxiliary_test_tax import (
    load_tb,
)
from src.analysis.tax_transfer_funcs.test_tax_transfers.auxiliary_test_tax import (
    load_output,
)
from src.analysis.tax_transfer_funcs.test_tax_transfers.auxiliary_test_tax import (
    load_input,
)
from src.analysis.tax_transfer_funcs.taxes import (
    kindergeld,
    kg_eligibility_wage,
    kg_eligibility_hours,
)


input_cols = ["tu_id", "age", "w_hours", "ineducation", "m_wage"]

years = [2000, 2002, 2010, 2011, 2013, 2019]


@pytest.mark.parametrize("yr", years)
def test_kindergeld(yr):
    filename = "test_dfs_kindergeld.xlsx"
    df = load_input(yr, filename, input_cols)
    tb = load_tb(yr)
    if yr > 2011:
        tb["childben_elig_rule"] = kg_eligibility_hours
    else:
        tb["childben_elig_rule"] = kg_eligibility_wage

    calculated = pd.DataFrame(columns=["kindergeld_tu_basis"])
    for tu_id in df["tu_id"].unique():
        calculated = calculated.append(
            kindergeld(df[df["tu_id"] == tu_id], tb), sort=True
        )

    expected = load_output(yr, filename, "kindergeld_tu_basis")

    print(calculated, "\n\n")
    print(expected, "\n\n")

    assert_series_equal(calculated["kindergeld_tu_basis"].astype("int64"), expected)
