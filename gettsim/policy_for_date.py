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


def get_policies_for_date(year, group, month=1, day=1):
    tax_data_raw = yaml.safe_load((ROOT_DIR / "data" / f"{group}.yaml").read_text())
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
                policy_in_place = np.max(past_policies)
                tax_data[key] = tax_data_raw[key]["values"][policy_in_place]["value"]
    tax_data["year"] = year

    if group == "soz_vers_beitr":
        if year >= 2003:
            tax_data["calc_midi_contrib"] = calc_midi_contributions
        else:
            tax_data["calc_midi_contrib"] = no_midi
        if year > 2017:
            tax_data["calc_rentenwert"] = _rentenwert_from_2018
        else:
            tax_data["calc_rentenwert"] = _rentenwert_until_2017

    elif group == "e_st_abzuege":
        if year <= 2014:
            tax_data["calc_hhfreib"] = calc_hhfreib_until2014
        else:
            tax_data["calc_hhfreib"] = calc_hhfreib_from2015
        if year >= 2010:
            tax_data["vorsorge"] = vorsorge2010
        else:
            tax_data["vorsorge"] = vorsorge_dummy

        # TODO: We need to adapt favorability check for that. See
        #  https://github.com/iza-institute-of-labor-economics/gettsim/issues/81 for
        #  details.
        # if year >= 2009:
        #     tax_data["zve_list"] = ["nokfb", "kfb", "abg_nokfb", "abg_kfb"]
        # else:
        #     tax_data["zve_list"] = ["nokfb", "kfb"]
        tax_data["zve_list"] = ["nokfb", "kfb"]

    elif group == "kindergeld":
        if year > 2011:
            tax_data["childben_elig_rule"] = kg_eligibility_hours
        else:
            tax_data["childben_elig_rule"] = kg_eligibility_wage

    elif group == "wohngeld":
        if year < 2009:
            tax_data["calc_max_rent"] = calc_max_rent_until_2008
        else:
            tax_data["calc_max_rent"] = calc_max_rent_since_2009

    elif group == "e_st":
        tax_data["tax_schedule"] = tarif

    return tax_data


def get_pension_data_for_year(raw_year, raw_pension_data=None):
    if not raw_pension_data:
        raw_pension_data = yaml.safe_load(
            (ROOT_DIR / "data" / "pension_data.yaml").read_text()
        )
    pension_data = {}

    # meanwages is only filled until 2016. The same is done in the pension function.
    min_year = min(raw_year, 2016)

    for key in raw_pension_data:
        data_years = list(raw_pension_data[key]["values"].keys())
        # For calculating pensions we need demographic data up to three years in the
        # past.
        for year in range(min_year - 3, min_year + 1):
            past_data = [x for x in data_years if x <= year]
            if not past_data:
                # TODO: Should there be missing values or should the key not exist?
                pension_data[f"{key}_{year}"] = np.nan
            else:
                policy_year = np.max(past_data)
                pension_data[f"{key}_{year}"] = raw_pension_data[key]["values"][
                    policy_year
                ]["value"]

    return pension_data
