import datetime

import numpy as np
import yaml

from gettsim.benefits.kiz import calc_kiz_amount_07_2019
from gettsim.benefits.kiz import calc_kiz_amount_2005
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


def get_policies_for_date(year, tax_data_raw=None, month=1, day=1):
    if not tax_data_raw:
        tax_data_raw = yaml.safe_load((ROOT_DIR / "data" / "param.yaml").read_text())
    tax_data = {}
    this_year = datetime.date(year=year, month=month, day=day)
    for key in tax_data_raw:
        if tax_data_raw[key]["values"] is not None:
            policy_dates = tax_data_raw[key]["values"]
            past_policies = [x for x in policy_dates if x <= this_year]
            if not past_policies:
                # TODO: Should there be missing values or should the key not exist?
                tax_data[key] = np.nan
            else:
                policy_in_place = max(past_policies)
                tax_data[key] = tax_data_raw[key]["values"][policy_in_place]["value"]
    tax_data["yr"] = year

    if year >= 2003:
        tax_data["calc_midi_contrib"] = calc_midi_contributions
    else:
        tax_data["calc_midi_contrib"] = no_midi
    if year > 2017:
        tax_data["calc_rentenwert"] = _rentenwert_from_2018
    else:
        tax_data["calc_rentenwert"] = _rentenwert_until_2017
    if year <= 2014:
        tax_data["calc_hhfreib"] = calc_hhfreib_until2014
    else:
        tax_data["calc_hhfreib"] = calc_hhfreib_from2015
    if year > 2011:
        tax_data["childben_elig_rule"] = kg_eligibility_hours
    else:
        tax_data["childben_elig_rule"] = kg_eligibility_wage
    if year < 2009:
        tax_data["calc_max_rent"] = calc_max_rent_until_2008
    else:
        tax_data["calc_max_rent"] = calc_max_rent_since_2009
    if year >= 2010:
        tax_data["vorsorge"] = vorsorge2010
    else:
        tax_data["vorsorge"] = vorsorge_dummy
    if (year >= 2020) or (year == 2019 and month >= 7):
        tax_data["calc_kiz_amount"] = calc_kiz_amount_07_2019
    else:
        tax_data["calc_kiz_amount"] = calc_kiz_amount_2005
    # TODO: We need to adapt favorability check for that. See
    #  https://github.com/iza-institute-of-labor-economics/gettsim/issues/81 for
    #  details.
    # if year >= 2009:
    #     tax_data["zve_list"] = ["nokfb", "kfb", "abg_nokfb", "abg_kfb"]
    # else:
    #     tax_data["zve_list"] = ["nokfb", "kfb"]
    tax_data["zve_list"] = ["nokfb", "kfb"]

    tax_data["tax_schedule"] = tarif
    return tax_data
