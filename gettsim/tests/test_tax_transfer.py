import itertools

import pandas as pd
import pytest

from gettsim.config import ROOT_DIR
from gettsim.pensions import _rentenwert_from_2018
from gettsim.pensions import _rentenwert_until_2017
from gettsim.social_insurance import calc_midi_contributions
from gettsim.social_insurance import no_midi
from gettsim.tax_transfer import tax_transfer
from gettsim.taxes.calc_taxes import tarif
from gettsim.tests.auxiliary_test_tax import load_tb


INPUT_COLUMNS = [
    "pid",
    "hid",
    "tu_id",
    "m_wage",
    "east",
    "age",
    "selfemployed",
    "haskids",
    "m_self",
    "m_pensions",
    "pkv",
    "year",
]


YEARS = [2002, 2010, 2018, 2019]
COLUMNS = ["svbeit", "rvbeit", "avbeit", "gkvbeit", "pvbeit"]


@pytest.mark.parametrize("year, column", itertools.product(YEARS, COLUMNS))
def test_soc_ins_contrib(year, column):
    df = pd.read_csv(ROOT_DIR / "tests" / "test_data" / "test_dfs_tax_transfer.csv")
    tb_pens = pd.read_excel(ROOT_DIR / "data" / "pensions.xlsx").set_index("var")
    tb = load_tb(year)
    tb["yr"] = year
    if year >= 2003:
        tb["calc_midi_contrib"] = calc_midi_contributions
    else:
        tb["calc_midi_contrib"] = no_midi
    if year > 2017:
        tb["calc_rentenwert"] = _rentenwert_from_2018
    else:
        tb["calc_rentenwert"] = _rentenwert_until_2017
    tb["tax_schedule"] = tarif
    tax_transfer(df, tb, tb_pens)
