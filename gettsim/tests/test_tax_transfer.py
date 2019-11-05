import pandas as pd
import pytest

from gettsim.benefits.wohngeld import calc_max_rent_since_2009
from gettsim.benefits.wohngeld import calc_max_rent_until_2008
from gettsim.config import ROOT_DIR
from gettsim.pensions import _rentenwert_from_2018
from gettsim.pensions import _rentenwert_until_2017
from gettsim.social_insurance import calc_midi_contributions
from gettsim.social_insurance import no_midi
from gettsim.tax_transfer import tax_transfer
from gettsim.taxes.calc_taxes import tarif
from gettsim.taxes.kindergeld import kg_eligibility_hours
from gettsim.taxes.kindergeld import kg_eligibility_wage
from gettsim.taxes.zve import calc_hhfreib_from2015
from gettsim.taxes.zve import calc_hhfreib_until2014
from gettsim.taxes.zve import vorsorge2010
from gettsim.taxes.zve import vorsorge_dummy
from gettsim.tests.policy_for_date import get_policies_for_date


INPUT_COLS = [
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


@pytest.fixture
def input_data():
    file_name = "test_dfs_tax_transfer.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


@pytest.mark.parametrize("year", YEARS)
def test_soc_ins_contrib(input_data, tax_policy_data, year):
    df = input_data[input_data["year"] == year].copy()
    tb_pens = pd.read_excel(ROOT_DIR / "data" / "pensions.xlsx").set_index("var")
    tb = get_policies_for_date(tax_policy_data, year=year)
    tb["yr"] = year
    if year >= 2003:
        tb["calc_midi_contrib"] = calc_midi_contributions
    else:
        tb["calc_midi_contrib"] = no_midi
    if year > 2017:
        tb["calc_rentenwert"] = _rentenwert_from_2018
    else:
        tb["calc_rentenwert"] = _rentenwert_until_2017
    if year <= 2014:
        tb["calc_hhfreib"] = calc_hhfreib_until2014
    else:
        tb["calc_hhfreib"] = calc_hhfreib_from2015
    if year > 2011:
        tb["childben_elig_rule"] = kg_eligibility_hours
    else:
        tb["childben_elig_rule"] = kg_eligibility_wage
    if year < 2009:
        tb["calc_max_rent"] = calc_max_rent_until_2008
    else:
        tb["calc_max_rent"] = calc_max_rent_since_2009
    if year >= 2010:
        tb["vorsorge"] = vorsorge2010
    else:
        tb["vorsorge"] = vorsorge_dummy

    tb["tax_schedule"] = tarif
    tb["zve_list"] = ["nokfb", "kfb"]
    tax_transfer(df, tb, tb_pens)
