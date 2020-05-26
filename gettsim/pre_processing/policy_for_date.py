import copy
import datetime
import operator
from functools import reduce

import numpy as np
import yaml

from gettsim.benefits.arbeitsl_geld_2 import regelberechnung_2011_and_beyond
from gettsim.benefits.arbeitsl_geld_2 import regelberechnung_until_2010
from gettsim.benefits.benefit_checks_dag import kinderzuschlag_temp_vorläufig_ab_2005
from gettsim.benefits.benefit_checks_dag import kinderzuschlag_temp_vorläufig_bis_2004
from gettsim.benefits.benefit_checks_dag import regelbedarf_m_vorläufig_ab_2005
from gettsim.benefits.benefit_checks_dag import regelbedarf_m_vorläufig_bis_2004
from gettsim.benefits.benefit_checks_dag import wohngeld_basis_hh_vorläufig_ab_2005
from gettsim.benefits.benefit_checks_dag import wohngeld_basis_hh_vorläufig_bis_2004
from gettsim.config import ROOT_DIR
from gettsim.pre_processing.generic_functions import get_piecewise_parameters
from gettsim.pre_processing.piecewise_functions import piecewise_polynomial
from gettsim.pre_processing.policy_completion_funcs import add_progressionsfaktor
from gettsim.taxes.favorability_check import _eink_st_m_tu_ab_1997
from gettsim.taxes.favorability_check import _eink_st_m_tu_bis_1996
from gettsim.taxes.favorability_check import _kindergeld_m_ab_1997
from gettsim.taxes.favorability_check import _kindergeld_m_bis_1996
from gettsim.taxes.kindergeld import _kindergeld_anspruch_nach_lohn
from gettsim.taxes.kindergeld import _kindergeld_anspruch_nach_stunden
from gettsim.taxes.zu_verst_eink.eink import _sum_brutto_eink_mit_kapital
from gettsim.taxes.zu_verst_eink.eink import _sum_brutto_eink_ohne_kapital
from gettsim.taxes.zu_verst_eink.freibeträge import _hh_freib_bis_2014
from gettsim.taxes.zu_verst_eink.freibeträge import _hh_freib_seit_2015
from gettsim.taxes.zu_verst_eink.freibeträge import _sonderausgaben_ab_2012
from gettsim.taxes.zu_verst_eink.freibeträge import _sonderausgaben_bis_2011
from gettsim.taxes.zu_verst_eink.vorsorge import _vorsorge_2005_vs_pre_2005
from gettsim.taxes.zu_verst_eink.vorsorge import _vorsorge_2010_vs_pre_2005
from gettsim.taxes.zu_verst_eink.vorsorge import _vorsorge_ab_2010
from gettsim.taxes.zu_verst_eink.vorsorge import _vorsorge_bis_2004


def get_policies_for_date(policy_date, groups="all"):
    all_params_groups = [
        "eink_st",
        "eink_st_abzuege",
        "soli_st",
        "arbeitsl_geld_2",
        "arbeitsl_geld",
        "soz_vers_beitr",
        "unterhalt",
        "abgelt_st",
        "wohngeld",
        "kinderzuschlag",
        "kindergeld",
        "elterngeld",
    ]
    if type(groups) == list:
        group_list = groups
    elif type(groups) == str:
        if groups == "all":
            group_list = all_params_groups
        elif groups in all_params_groups:
            group_list = [groups]
        else:
            raise ValueError(f"{groups} is not a category for groups.")
    else:
        raise ValueError(f"{groups} is not a string or list.")

    params_dict = {}
    year = policy_date.year

    for group in group_list:
        tax_data = load_data(policy_date, group)

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

            tax_data["eink_arten"] = ["kein_kind_freib", "kind_freib"]

        tax_data["jahr"] = year
        tax_data["datum"] = policy_date
        params_dict[group] = tax_data

    policy_func_dict = {}
    if year < 2009:
        policy_func_dict["sum_brutto_eink"] = _sum_brutto_eink_mit_kapital
    else:
        policy_func_dict["sum_brutto_eink"] = _sum_brutto_eink_ohne_kapital

    if year <= 2014:
        policy_func_dict["hh_freib"] = _hh_freib_bis_2014
    else:
        policy_func_dict["hh_freib"] = _hh_freib_seit_2015

    if year <= 1996:
        policy_func_dict["eink_st_m_tu"] = _eink_st_m_tu_bis_1996
        policy_func_dict["kindergeld_m"] = _kindergeld_m_bis_1996
    else:
        policy_func_dict["eink_st_m_tu"] = _eink_st_m_tu_ab_1997
        policy_func_dict["kindergeld_m"] = _kindergeld_m_ab_1997

    if year > 2011:
        policy_func_dict["_kindergeld_anspruch"] = _kindergeld_anspruch_nach_stunden
    else:
        policy_func_dict["_kindergeld_anspruch"] = _kindergeld_anspruch_nach_lohn

    if year > 2011:
        policy_func_dict["sonderausgaben"] = _sonderausgaben_ab_2012
    else:
        policy_func_dict["sonderausgaben"] = _sonderausgaben_bis_2011

    if year >= 2020:
        policy_func_dict["vorsorge"] = _vorsorge_ab_2010
    elif 2020 > year >= 2010:
        policy_func_dict["vorsorge"] = _vorsorge_2010_vs_pre_2005
    elif 2010 > year >= 2005:
        policy_func_dict["vorsorge"] = _vorsorge_2005_vs_pre_2005
    elif year <= 2004:
        policy_func_dict["vorsorge"] = _vorsorge_bis_2004

    if year < 2005:
        policy_func_dict[
            "kinderzuschlag_temp_vorläufig"
        ] = kinderzuschlag_temp_vorläufig_bis_2004
        policy_func_dict["regelbedarf_m_vorläufig"] = regelbedarf_m_vorläufig_bis_2004
        policy_func_dict[
            "wohngeld_basis_hh_vorläufig"
        ] = wohngeld_basis_hh_vorläufig_bis_2004
    else:
        policy_func_dict[
            "kinderzuschlag_temp_vorläufig"
        ] = kinderzuschlag_temp_vorläufig_ab_2005
        policy_func_dict["regelbedarf_m_vorläufig"] = regelbedarf_m_vorläufig_ab_2005
        policy_func_dict[
            "wohngeld_basis_hh_vorläufig"
        ] = wohngeld_basis_hh_vorläufig_ab_2005

    return params_dict, policy_func_dict


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
