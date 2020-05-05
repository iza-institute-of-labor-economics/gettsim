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
from gettsim.pre_processing.generic_functions import get_piecewise_parameters
from gettsim.pre_processing.piecewise_functions import piecewise_polynomial
from gettsim.taxes.eink_st import add_progressionsfaktor
from gettsim.taxes.kindergeld import kindergeld_anspruch_nach_lohn
from gettsim.taxes.kindergeld import kindergeld_anspruch_nach_stunden
from gettsim.taxes.zu_versteuerndes_eink import calc_hhfreib_from2015
from gettsim.taxes.zu_versteuerndes_eink import calc_hhfreib_until2014
from gettsim.taxes.zu_versteuerndes_eink import vorsorge_pre_2005
from gettsim.taxes.zu_versteuerndes_eink import vorsorge_since_2005
from gettsim.taxes.zu_versteuerndes_eink import vorsorge_since_2010


def get_policies_for_date(year, group, month=1, day=1, raw_group_data=None):
    if not raw_group_data:
        raw_group_data = yaml.safe_load(
            (ROOT_DIR / "data" / f"{group}.yaml").read_text(encoding="utf-8")
        )

    actual_date = datetime.date(year=year, month=month, day=day)
    tax_data = process_data(actual_date, group, raw_group_data=raw_group_data)

    return tax_data


def process_data(policy_date, group, raw_group_data=None, parameters=None):
    tax_data = load_data(
        policy_date, group, raw_group_data=raw_group_data, parameters=parameters
    )
    year = policy_date.year
    month = policy_date.month
    for param in tax_data:
        if type(tax_data[param]) == dict:
            if "type" in tax_data[param]:
                if tax_data[param]["type"].startswith("piecewise"):
                    if "progressionsfaktor" in tax_data[param]:
                        if tax_data[param]["progressionsfaktor"]:
                            tax_data[param] = add_progressionsfaktor(
                                tax_data[param], param
                            )
                    tax_data[param] = get_piecewise_parameters(
                        tax_data[param],
                        param,
                        piecewise_polynomial,
                        func_type=tax_data[param]["type"].split("_")[1],
                    )
            for key in ["type", "progressionsfaktor"]:
                tax_data[param].pop(key, None)

    if group == "arbeitsl_geld_2":
        if tax_data["jahr"] <= 2010:
            tax_data["calc_regelsatz"] = regelberechnung_until_2010
        else:
            tax_data["calc_regelsatz"] = regelberechnung_2011_and_beyond

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

    tax_data["jahr"] = year
    tax_data["datum"] = policy_date

    return tax_data


def load_data(policy_date, group, raw_group_data=None, parameters=None):
    if not raw_group_data:
        raw_group_data = yaml.safe_load(
            (ROOT_DIR / "data" / f"{group}.yaml").read_text(encoding="utf-8")
        )

    # Keys from the raw file which will not be transferred
    not_trans_keys = ["note", "reference", "deviation_from"]
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
                    tax_data[param] = load_data(
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
                # Keys which if given are transferred
                add_trans_keys = ["type", "progressionsfaktor"]
                for key in add_trans_keys:
                    if key in raw_group_data[param]:
                        tax_data[param][key] = raw_group_data[param][key]
                value_keys = (
                    key for key in policy_in_place.keys() if key not in not_trans_keys
                )
                if "deviation_from" in policy_in_place.keys():
                    if policy_in_place["deviation_from"] == "previous":
                        new_date = np.max(past_policies) - datetime.timedelta(days=1)
                        tax_data[param] = load_data(
                            new_date,
                            group,
                            raw_group_data=raw_group_data,
                            parameters=[param],
                        )[param]
                    elif "." in policy_in_place["deviation_from"]:
                        path_list = policy_in_place["deviation_from"].split(".")
                        tax_data[param] = load_data(
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
