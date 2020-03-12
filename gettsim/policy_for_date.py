import datetime

import numpy as np
import yaml

from gettsim.benefits.alg2 import e_anr_frei_2005_01
from gettsim.benefits.alg2 import e_anr_frei_2005_10
from gettsim.benefits.alg2 import regelberechnung_2011_and_beyond
from gettsim.benefits.alg2 import regelberechnung_until_2010
from gettsim.benefits.kiz import calc_kiz_amount_07_2019
from gettsim.benefits.kiz import calc_kiz_amount_2005
from gettsim.benefits.unterhaltsvorschuss import uhv_pre_07_2017
from gettsim.benefits.unterhaltsvorschuss import uhv_since_07_2017
from gettsim.benefits.wohngeld import calc_max_rent_since_2009
from gettsim.benefits.wohngeld import calc_max_rent_until_2008
from gettsim.config import ROOT_DIR
from gettsim.pensions import _rentenwert_from_2018
from gettsim.pensions import _rentenwert_until_2017
from gettsim.social_insurance import calc_midi_contributions
from gettsim.social_insurance import no_midi
from gettsim.taxes.calc_taxes import no_soli
from gettsim.taxes.calc_taxes import soli_formula_1991_92
from gettsim.taxes.calc_taxes import soli_formula_since_1995
from gettsim.taxes.calc_taxes import tarif
from gettsim.taxes.kindergeld import kg_eligibility_hours
from gettsim.taxes.kindergeld import kg_eligibility_wage
from gettsim.taxes.zve import calc_hhfreib_from2015
from gettsim.taxes.zve import calc_hhfreib_until2014
from gettsim.taxes.zve import vorsorge_pre_2005
from gettsim.taxes.zve import vorsorge_since_2005
from gettsim.taxes.zve import vorsorge_since_2010


def get_policies_for_date(year, group, month=1, day=1, raw_group_data=None):
    if not raw_group_data:
        raw_group_data = yaml.safe_load(
            (ROOT_DIR / "data" / f"{group}.yaml").read_text()
        )

    actual_date = datetime.date(year=year, month=month, day=day)
    if group == "ges_renten_vers":
        load_data = load_ges_renten_vers_params
    else:
        load_data = load_ordanary_data_group

    tax_data = load_data(raw_group_data, actual_date)
    tax_data["year"] = year
    tax_data["date"] = actual_date

    if group == "soz_vers_beitr":
        if year >= 2003:
            tax_data["calc_midi_contrib"] = calc_midi_contributions
        else:
            tax_data["calc_midi_contrib"] = no_midi

    elif group == "e_st_abzuege":
        if year <= 2014:
            tax_data["calc_hhfreib"] = calc_hhfreib_until2014
        else:
            tax_data["calc_hhfreib"] = calc_hhfreib_from2015
        if year >= 2010:
            tax_data["vorsorge"] = vorsorge_since_2010
        elif year >= 2005:
            tax_data["vorsorge"] = vorsorge_since_2005
        elif year <= 2004:
            tax_data["vorsorge"] = vorsorge_pre_2005

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

    elif group == "soli_st":
        if year in [1991, 1992]:
            tax_data["soli_formula"] = soli_formula_1991_92
        elif year >= 1995:
            tax_data["soli_formula"] = soli_formula_since_1995
        else:
            tax_data["soli_formula"] = no_soli

    elif group == "ges_renten_vers":
        if year > 2017:
            tax_data["calc_rentenwert"] = _rentenwert_from_2018
        else:
            tax_data["calc_rentenwert"] = _rentenwert_until_2017
    elif group == "kinderzuschlag":
        if (year >= 2020) or (year == 2019 and month >= 7):
            tax_data["calc_kiz_amount"] = calc_kiz_amount_07_2019
        else:
            tax_data["calc_kiz_amount"] = calc_kiz_amount_2005

    elif group == "arbeitsl_geld_2":
        if year <= 2010:
            tax_data["calc_regelsatz"] = regelberechnung_until_2010
        else:
            tax_data["calc_regelsatz"] = regelberechnung_2011_and_beyond

        if actual_date < datetime.date(year=2005, month=10, day=1):
            tax_data["calc_e_anr_frei"] = e_anr_frei_2005_01
        else:
            tax_data["calc_e_anr_frei"] = e_anr_frei_2005_10
    # Before 07/2017, UHV was only paid up to 6 years, which is why we model it only since then.
    elif group == "unterhalt":
        if year >= 2018 or (year == 2017 & month >= 7):
            tax_data["uhv_calc"] = uhv_since_07_2017
        else:
            tax_data["uhv_calc"] = uhv_pre_07_2017

    return tax_data


def load_ordanary_data_group(tax_data_raw, actual_date):
    tax_data = {}
    for key in tax_data_raw:
        policy_dates = tax_data_raw[key]["values"]
        past_policies = [x for x in policy_dates if x <= actual_date]
        if not past_policies:
            # TODO: Should there be missing values or should the key not exist?
            tax_data[key] = np.nan
        else:
            policy_in_place = np.max(past_policies)
            tax_data[key] = tax_data_raw[key]["values"][policy_in_place]["value"]
    return tax_data


def load_ges_renten_vers_params(raw_pension_data, actual_date):
    pension_data = {}
    # meanwages is only filled until 2016. The same is done in the pension function.
    min_year = min(actual_date.year, 2016)
    for key in raw_pension_data:
        data_years = list(raw_pension_data[key]["values"])
        # For calculating pensions we need demographic data up to three years in the
        # past.
        for year in range(min_year - 3, min_year + 1):
            past_data = [x for x in data_years if x.year <= year]
            if not past_data:
                # TODO: Should there be missing values or should the key not exist?
                pension_data[f"{key}_{year}"] = np.nan
            else:
                policy_year = np.max(past_data)
                pension_data[f"{key}_{year}"] = raw_pension_data[key]["values"][
                    policy_year
                ]["value"]
    return pension_data


def load_regrouped_wohngeld(policy_date):
    tax_data_raw = yaml.safe_load((ROOT_DIR / "data" / "wohngeld_neu.yaml").read_text())

    tax_data = {}
    for param in tax_data_raw:
        policy_dates = sorted(
            key for key in tax_data_raw[param].keys() if type(key) == datetime.date
        )
        past_policies = [x for x in policy_dates if x <= policy_date]
        if not past_policies:
            # TODO: Should there be missing values or should the key not exist?
            tax_data[param] = np.nan
        else:
            policy_in_place = tax_data_raw[param][np.max(past_policies)]
            if "scalar" in policy_in_place.keys():
                tax_data[param] = policy_in_place["scalar"]
            else:
                if "deviation_from" in policy_in_place.keys():
                    if policy_in_place["deviation_from"] == "previous":
                        new_date = np.max(past_policies) - datetime.timedelta(days=1)
                        tax_data[param] = load_regrouped_wohngeld(new_date)[param]
                        value_keys = sorted(
                            key for key in policy_in_place.keys() if type(key) == int
                        )

                        for key in value_keys:
                            if type(policy_in_place[key]) == dict:
                                nested_keys = policy_in_place.keys()
                                for nested_key in nested_keys:
                                    tax_data[param][key][nested_key] = policy_in_place[
                                        key
                                    ][nested_key]
                            else:
                                tax_data[param][key] = policy_in_place[key]

                else:
                    value_keys = sorted(
                        key for key in policy_in_place.keys() if type(key) == int
                    )
                    tax_data[param] = {}
                    for key in value_keys:
                        tax_data[param][key] = policy_in_place[key]
    tax_data["year"] = policy_date.year
    tax_data["date"] = policy_date
    return tax_data
