import datetime

import numpy as np
import yaml

from gettsim.benefits.wohngeld import calc_max_rent_since_2009
from gettsim.benefits.wohngeld import calc_max_rent_until_2008
from gettsim.config import ROOT_DIR
from gettsim.pensions import _rentenwert_from_2018
from gettsim.pensions import _rentenwert_until_2017
from gettsim.social_insurance import calc_midi_contributions
from gettsim.social_insurance import no_midi
from gettsim.taxes.calc_taxes import tarif
from gettsim.taxes.kindergeld import kg_eligibility_hours
from gettsim.taxes.kindergeld import kg_eligibility_wage
from gettsim.taxes.zve import calc_hhfreib_from2015
from gettsim.taxes.zve import calc_hhfreib_until2014
from gettsim.taxes.zve import vorsorge2010
from gettsim.taxes.zve import vorsorge_dummy


def get_policies_for_date(tb_pre, year, month=1, day=1):
    tb = {}
    this_year = datetime.date(year=year, month=month, day=day)
    for key in tb_pre:
        if tb_pre[key]["values"] is not None:
            policy_dates = tb_pre[key]["values"]
            past_policies = [x for x in policy_dates if x <= this_year]
            if not past_policies:
                # TODO: Should there be missing values or should the key not exist?
                tb[key] = np.nan
            else:
                policy_in_place = max(past_policies)
                tb[key] = tb_pre[key]["values"][policy_in_place]["value"]
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
    return tb


def standard_policy_data():
    return yaml.safe_load((ROOT_DIR / "data" / "param.yaml").read_text())
