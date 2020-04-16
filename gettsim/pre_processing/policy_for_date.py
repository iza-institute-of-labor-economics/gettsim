import copy
import datetime
import operator
from functools import reduce

import numpy as np
import yaml

from gettsim.benefits.arbeitsl_geld_2 import regelberechnung_2011_and_beyond
from gettsim.benefits.arbeitsl_geld_2 import regelberechnung_until_2010
from gettsim.benefits.kinderzuschlag import calc_kiz_amount_07_2019
from gettsim.benefits.kinderzuschlag import calc_kiz_amount_2005
from gettsim.benefits.kinderzuschlag import kiz
from gettsim.benefits.kinderzuschlag import kiz_dummy
from gettsim.benefits.unterhalt import uhv_pre_07_2017
from gettsim.benefits.unterhalt import uhv_since_07_2017
from gettsim.benefits.wohngeld import calc_max_rent_since_2009
from gettsim.benefits.wohngeld import calc_max_rent_until_2008
from gettsim.config import ROOT_DIR
from gettsim.pensions import _rentenwert_from_2018
from gettsim.pensions import _rentenwert_until_2017
from gettsim.pre_processing.generic_functions import get_piecewise_parameters
from gettsim.pre_processing.piecewise_functions import piecewise_polynominal
from gettsim.social_insurance import calc_midi_contributions
from gettsim.social_insurance import no_midi
from gettsim.taxes.eink_st import st_tarif
from gettsim.taxes.kindergeld import kindergeld_anspruch_nach_lohn
from gettsim.taxes.kindergeld import kindergeld_anspruch_nach_stunden
from gettsim.taxes.soli_st import keine_soli_st
from gettsim.taxes.soli_st import soli_st_formel_1991_92
from gettsim.taxes.soli_st import soli_st_formel_seit_1995
from gettsim.taxes.zve import calc_hhfreib_from2015
from gettsim.taxes.zve import calc_hhfreib_until2014
from gettsim.taxes.zve import vorsorge_pre_2005
from gettsim.taxes.zve import vorsorge_since_2005
from gettsim.taxes.zve import vorsorge_since_2010


def get_policies_for_date(year, group, month=1, day=1, raw_group_data=None):
    if not raw_group_data:
        raw_group_data = yaml.safe_load(
            (ROOT_DIR / "data" / f"{group}.yaml").read_text(encoding="utf-8")
        )

    actual_date = datetime.date(year=year, month=month, day=day)
    if group == "ges_renten_vers":
        tax_data = load_ges_renten_vers_params(raw_group_data, actual_date)
    elif group == "wohngeld":
        tax_data = load_regrouped_data(
            actual_date, group, raw_group_data=raw_group_data
        )
    elif group in ["arbeitsl_geld_2", "kindergeld", "eink_st_abzuege", "abgelt_st"]:
        tax_data = process_data(actual_date, group, raw_group_data=raw_group_data)
    else:
        tax_data = load_ordinary_data_group(raw_group_data, actual_date)

    tax_data["jahr"] = year
    tax_data["datum"] = actual_date

    if group == "soz_vers_beitr":
        if year >= 2003:
            tax_data["calc_midi_contrib"] = calc_midi_contributions
        else:
            tax_data["calc_midi_contrib"] = no_midi

    elif group == "eink_st_abzuege":
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
        tax_data["eink_arten"] = ["kein_kind_freib", "kind_freib"]

    elif group == "kindergeld":
        if year > 2011:
            tax_data["kindergeld_anspruch_regel"] = kindergeld_anspruch_nach_stunden
        else:
            tax_data["kindergeld_anspruch_regel"] = kindergeld_anspruch_nach_lohn

    elif group == "wohngeld":
        if year < 2009:
            tax_data["calc_max_rent"] = calc_max_rent_until_2008
        else:
            tax_data["calc_max_rent"] = calc_max_rent_since_2009

    elif group == "eink_st":
        tax_data["st_tarif"] = st_tarif

    elif group == "soli_st":
        if year in [1991, 1992]:
            tax_data["soli_formula"] = soli_st_formel_1991_92
        elif year >= 1995:
            tax_data["soli_formula"] = soli_st_formel_seit_1995
        else:
            tax_data["soli_formula"] = keine_soli_st

    elif group == "ges_renten_vers":
        if year > 2017:
            tax_data["calc_rentenwert"] = _rentenwert_from_2018
        else:
            tax_data["calc_rentenwert"] = _rentenwert_until_2017
    elif group == "kinderzuschlag":
        if year < 2004:
            tax_data["calc_kiz"] = kiz_dummy
        else:
            tax_data["calc_kiz"] = kiz
        if (year >= 2020) or (year == 2019 and month >= 7):
            tax_data["calc_kiz_amount"] = calc_kiz_amount_07_2019
        else:
            tax_data["calc_kiz_amount"] = calc_kiz_amount_2005

    # Before 07/2017, UHV was only paid up to 6 years, which is why we model it only since then.
    elif group == "unterhalt":
        if year >= 2018 or (year == 2017 & month >= 7):
            tax_data["uhv_calc"] = uhv_since_07_2017
        else:
            tax_data["uhv_calc"] = uhv_pre_07_2017

    return tax_data


def load_ordinary_data_group(tax_data_raw, actual_date):
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


def process_data(policy_date, group, raw_group_data=None, parameters=None):
    tax_data = load_regrouped_data(
        policy_date, group, raw_group_data=raw_group_data, parameters=parameters
    )
    if group == "arbeitsl_geld_2":
        if tax_data["jahr"] >= 2005:
            for param in ["e_anr_frei_kinder", "e_anr_frei"]:
                tax_data[param] = get_piecewise_parameters(
                    tax_data[param], param, piecewise_polynominal
                )
        if tax_data["jahr"] <= 2010:
            tax_data["calc_regelsatz"] = regelberechnung_until_2010
        else:
            tax_data["calc_regelsatz"] = regelberechnung_2011_and_beyond

    return tax_data


def load_regrouped_data(policy_date, group, raw_group_data=None, parameters=None):
    if not raw_group_data:
        raw_group_data = yaml.safe_load(
            (ROOT_DIR / "data" / f"{group}.yaml").read_text(encoding="utf-8")
        )
    additional_keys = ["note", "reference", "deviation_from"]
    tax_data = {}
    if not parameters:
        parameters = raw_group_data.keys()
    for param in parameters:
        policy_dates = sorted(
            key for key in raw_group_data[param].keys() if type(key) == datetime.date
        )

        past_policies = [x for x in policy_dates if x <= policy_date]

        if not past_policies:
            # If no policy exists, then we check if the policy maybe agrees right now
            # with another one.
            if "deviation_from" in raw_group_data[param][np.min(policy_dates)].keys():
                future_policy = raw_group_data[param][np.min(policy_dates)]
                if "." in future_policy["deviation_from"]:
                    path_list = future_policy["deviation_from"].split(".")
                    tax_data[param] = load_regrouped_data(
                        policy_date,
                        path_list[0],
                        raw_group_data=raw_group_data,
                        parameters=[path_list[1]],
                    )[path_list[1]]
            else:
                # TODO: Should there be missing values or should the key not exist?
                tax_data[param] = np.nan
        else:
            policy_in_place = raw_group_data[param][np.max(past_policies)]
            if "scalar" in policy_in_place.keys():
                tax_data[param] = policy_in_place["scalar"]
            else:
                tax_data[param] = {}
                value_keys = (
                    key for key in policy_in_place.keys() if key not in additional_keys
                )
                if "deviation_from" in policy_in_place.keys():
                    if policy_in_place["deviation_from"] == "previous":
                        new_date = np.max(past_policies) - datetime.timedelta(days=1)
                        tax_data[param] = load_regrouped_data(
                            new_date,
                            "arbeitsl_geld_2_neu",
                            raw_group_data=raw_group_data,
                            parameters=[param],
                        )[param]
                    elif "." in policy_in_place["deviation_from"]:
                        path_list = policy_in_place["deviation_from"].split(".")
                        tax_data[param] = load_regrouped_data(
                            policy_date,
                            path_list[0],
                            raw_group_data=raw_group_data,
                            parameters=[path_list[1]],
                        )[path_list[1]]
                    for key in value_keys:
                        key_list = []
                        tax_data[param][key] = transfer_dictionary(
                            policy_in_place[key],
                            copy.deepcopy(tax_data[param][key]),
                            key_list,
                        )
                else:
                    for key in value_keys:
                        tax_data[param][key] = policy_in_place[key]

    tax_data["jahr"] = policy_date.year
    tax_data["datum"] = policy_date

    return tax_data


def transfer_dictionary(remaining_dict, new_dict, key_list):
    # To call recursive, always check if object is a dict
    if type(remaining_dict) == dict:
        for key in remaining_dict.keys():
            key_list_updated = key_list + [key]
            new_dict = transfer_dictionary(
                remaining_dict[key], new_dict, key_list_updated
            )
    elif len(key_list) == 0:
        return remaining_dict
    else:
        # Now remaining dict is just a scalar
        set_by_path(new_dict, key_list, remaining_dict)
    return new_dict


def get_by_path(data_dict, key_list):
    """Access a nested object in root by item sequence."""
    return reduce(operator.getitem, key_list, data_dict)


def set_by_path(data_dict, key_list, value):
    """Set a value in a nested object in root by item sequence."""
    get_by_path(data_dict, key_list[:-1])[key_list[-1]] = value
