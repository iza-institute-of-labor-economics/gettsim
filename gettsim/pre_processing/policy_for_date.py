import copy
import datetime
import operator
from functools import reduce

import numpy as np
import pandas as pd
import yaml

from gettsim.benefits.arbeitsl_geld_2.arbeitsl_geld_2 import kindersatz_m_ab_2011
from gettsim.benefits.arbeitsl_geld_2.arbeitsl_geld_2 import kindersatz_m_bis_2010
from gettsim.benefits.arbeitsl_geld_2.arbeitsl_geld_2 import regelsatz_m_ab_2011
from gettsim.benefits.arbeitsl_geld_2.arbeitsl_geld_2 import regelsatz_m_bis_2010
from gettsim.benefits.arbeitsl_geld_2.eink_anr_frei import eink_anr_frei_ab_10_2005
from gettsim.benefits.arbeitsl_geld_2.eink_anr_frei import eink_anr_frei_bis_10_2005
from gettsim.benefits.kinderzuschlag.kinderzuschlag import (
    kinderzuschlag_ab_2005_bis_juni_2019,
)
from gettsim.benefits.kinderzuschlag.kinderzuschlag import kinderzuschlag_ab_juli_2019
from gettsim.benefits.kinderzuschlag.kinderzuschlag_eink import (
    kinderzuschlag_eink_regel_ab_2011,
)
from gettsim.benefits.kinderzuschlag.kinderzuschlag_eink import (
    kinderzuschlag_eink_regel_bis_2010,
)
from gettsim.benefits.wohngeld import wohngeld_eink_abzüge_ab_2016
from gettsim.benefits.wohngeld import wohngeld_eink_abzüge_bis_2015
from gettsim.benefits.wohngeld import wohngeld_max_miete_ab_2009
from gettsim.benefits.wohngeld import wohngeld_max_miete_bis_2008
from gettsim.config import INTERNAL_PARAM_GROUPS
from gettsim.config import ROOT_DIR
from gettsim.interface import create_linewise_printed_list
from gettsim.pre_processing.piecewise_functions import get_piecewise_parameters
from gettsim.pre_processing.policy_completion_funcs import add_progressionsfaktor
from gettsim.taxes.favorability_check import eink_st_tu_ab_1997
from gettsim.taxes.favorability_check import eink_st_tu_bis_1996
from gettsim.taxes.favorability_check import kindergeld_m_ab_1997
from gettsim.taxes.favorability_check import kindergeld_m_bis_1996
from gettsim.taxes.kindergeld import kindergeld_anspruch_nach_lohn
from gettsim.taxes.kindergeld import kindergeld_anspruch_nach_stunden
from gettsim.taxes.zu_verst_eink.eink import sum_brutto_eink_mit_kapital
from gettsim.taxes.zu_verst_eink.eink import sum_brutto_eink_ohne_kapital
from gettsim.taxes.zu_verst_eink.freibetraege import alleinerziehend_freib_tu_ab_2015
from gettsim.taxes.zu_verst_eink.freibetraege import alleinerziehend_freib_tu_bis_2014
from gettsim.taxes.zu_verst_eink.freibetraege import sonderausgaben_ab_2012
from gettsim.taxes.zu_verst_eink.freibetraege import sonderausgaben_bis_2011
from gettsim.taxes.zu_verst_eink.vorsorge import vorsorge_ab_2005_bis_2009
from gettsim.taxes.zu_verst_eink.vorsorge import vorsorge_ab_2010_bis_2019
from gettsim.taxes.zu_verst_eink.vorsorge import vorsorge_ab_2020
from gettsim.taxes.zu_verst_eink.vorsorge import vorsorge_bis_2004


def get_policies_for_date(policy_date, policy_groups="all"):
    """Get the state of the policy system for a particular date.

    The function returns time dependent policy reforms (functions) as well as the
    policy parameters for the current policy system.

    Parameters
    ----------
    policy_date : int, str, datetime.date
        The date for which the policy system is set up.
    policy_groups : list, str
        The group or a list of groups which parameters are loaded. If an invalid
        name is given, a list of all possible values is printed. Default is to load all
        parameter groups.

    Returns
    -------
    params_dict : dict
        Dictionary of parameters grouped in policy system compartments given in groups.
    policy_func_dict : dict
        Dictionary of time dependent policy reforms. Keys are the variable names they
        create.

    """
    # Check policy date for correct format and transfer to datetime.date
    policy_date = _parse_date(policy_date)

    # Check groups argument for correct format and transfer to list.
    group_list = _parse_parameter_groups(policy_groups)

    params_dict = {}

    for group in group_list:
        tax_data = _load_parameter_group_from_yaml(policy_date, group)

        # Align paramters for e.g. piecewise polynomial functions
        params_dict[group] = _parse_parameters(tax_data)

    policy_func_dict = load_reforms_for_date(policy_date)

    return params_dict, policy_func_dict


def _parse_parameters(tax_data):
    """Check if parameters are stored in implicit structures and align to general
    structure.

    Parameters
    ----------
    tax_data : dict
        Loaded raw tax data.

    Returns
    -------
    tax_data : dict
        Parsed parameters ready to use in gettsim.

    """
    for param in tax_data:
        if isinstance(tax_data[param], dict):
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
                        func_type=tax_data[param]["type"].split("_")[1],
                    )
            for key in ["type", "progressionsfaktor"]:
                tax_data[param].pop(key, None)

    return tax_data


def _parse_parameter_groups(policy_groups):
    """Check group argument for correct format and transfer to list.

    Parameters
    ----------
    policy_groups : list, str
        The group or a list of groups which parameters are loaded. Default is
        all parameters

    Returns
    -------
        List of groups to be loaded.

    """
    if isinstance(policy_groups, list):
        misspelled = [
            group for group in policy_groups if group not in INTERNAL_PARAM_GROUPS
        ]
        if not misspelled:
            out = policy_groups
        else:
            part_1 = "The groups"
            list_1 = create_linewise_printed_list(misspelled)
            part_2 = "are not in the internal yaml files."
            part_3 = "Possible group names are:"
            list_formatted_internal_groups = create_linewise_printed_list(
                INTERNAL_PARAM_GROUPS
            )

            raise ValueError(
                "\n".join(
                    [part_1, list_1, part_2, part_3, list_formatted_internal_groups]
                )
            )
    elif isinstance(policy_groups, str):
        if policy_groups == "all":
            out = INTERNAL_PARAM_GROUPS
        elif policy_groups in INTERNAL_PARAM_GROUPS:
            out = [policy_groups]
        else:
            part_1 = f"{policy_groups} is not a valid group name."
            part_2 = "Possible group names are:"
            list_formatted_internal_groups = create_linewise_printed_list(
                INTERNAL_PARAM_GROUPS
            )
            raise ValueError(
                "\n".join([part_1, part_2, list_formatted_internal_groups])
            )
    else:
        raise ValueError(f"{policy_groups} is not a string or list.")

    return out


def _parse_date(policy_date):
    """Check the policy date for different input formats.

    Parameters
    ----------
    policy_date : datetime.date, str, int
        The date for which the policy system is set up.

    Returns
    -------
    policy_date : datetime.date
        The date for which the policy system is set up.
    """
    if isinstance(policy_date, str):
        policy_date = pd.to_datetime(policy_date).date()
    elif isinstance(policy_date, int):
        policy_date = datetime.date(year=policy_date, month=1, day=1)
    return policy_date


def load_reforms_for_date(policy_date):
    """Load time dependet policy reforms.

    Parameters
    ----------
    policy_date : datetime.date
        The date for which the policy system is set up.

    Returns
    -------
    policy_func_dict : dict
        Dictionary of time dependent policy reforms. Keys are the variable names they
        create.

    """
    year = policy_date.year
    policy_func_dict = {}
    if year < 2009:
        policy_func_dict["sum_brutto_eink"] = sum_brutto_eink_mit_kapital
    else:
        policy_func_dict["sum_brutto_eink"] = sum_brutto_eink_ohne_kapital

    if year <= 2014:
        policy_func_dict["alleinerziehend_freib_tu"] = alleinerziehend_freib_tu_bis_2014
    else:
        policy_func_dict["alleinerziehend_freib_tu"] = alleinerziehend_freib_tu_ab_2015

    if year <= 1996:
        policy_func_dict["eink_st_tu"] = eink_st_tu_bis_1996
        policy_func_dict["kindergeld_m"] = kindergeld_m_bis_1996
    else:
        policy_func_dict["eink_st_tu"] = eink_st_tu_ab_1997
        policy_func_dict["kindergeld_m"] = kindergeld_m_ab_1997

    if year > 2011:
        policy_func_dict["kindergeld_anspruch"] = kindergeld_anspruch_nach_stunden
    else:
        policy_func_dict["kindergeld_anspruch"] = kindergeld_anspruch_nach_lohn

    if year > 2011:
        policy_func_dict["sonderausgaben"] = sonderausgaben_ab_2012
    else:
        policy_func_dict["sonderausgaben"] = sonderausgaben_bis_2011

    if year >= 2020:
        policy_func_dict["vorsorge"] = vorsorge_ab_2020
    elif 2020 > year >= 2010:
        policy_func_dict["vorsorge"] = vorsorge_ab_2010_bis_2019
    elif 2010 > year >= 2005:
        policy_func_dict["vorsorge"] = vorsorge_ab_2005_bis_2009
    elif year <= 2004:
        policy_func_dict["vorsorge"] = vorsorge_bis_2004

    if year <= 2015:
        policy_func_dict["wohngeld_eink_abzüge"] = wohngeld_eink_abzüge_bis_2015
    else:
        policy_func_dict["wohngeld_eink_abzüge"] = wohngeld_eink_abzüge_ab_2016

    if year <= 2008:
        policy_func_dict["wohngeld_max_miete"] = wohngeld_max_miete_bis_2008
    else:
        policy_func_dict["wohngeld_max_miete"] = wohngeld_max_miete_ab_2009

    if year <= 2010:
        policy_func_dict[
            "kinderzuschlag_eink_regel"
        ] = kinderzuschlag_eink_regel_bis_2010
    else:
        policy_func_dict[
            "kinderzuschlag_eink_regel"
        ] = kinderzuschlag_eink_regel_ab_2011

    if 2005 <= year <= 2019:
        policy_func_dict[
            "_kinderzuschlag_m_vorläufig"
        ] = kinderzuschlag_ab_2005_bis_juni_2019
    else:
        policy_func_dict["_kinderzuschlag_m_vorläufig"] = kinderzuschlag_ab_juli_2019

    if year <= 2010:
        policy_func_dict["kindersatz_m"] = kindersatz_m_bis_2010
        policy_func_dict["regelsatz_m"] = regelsatz_m_bis_2010
    else:
        policy_func_dict["kindersatz_m"] = kindersatz_m_ab_2011
        policy_func_dict["regelsatz_m"] = regelsatz_m_ab_2011

    if policy_date <= datetime.date(year=2005, month=10, day=1):
        policy_func_dict["eink_anr_frei"] = eink_anr_frei_bis_10_2005
    else:
        policy_func_dict["eink_anr_frei"] = eink_anr_frei_ab_10_2005

    return policy_func_dict


def _load_parameter_group_from_yaml(policy_date, group, parameters=None):
    """Load data from raw yaml group file.

    Parameters
    ----------
    policy_date : datetime.date
        The date for which the policy system is set up.
    group : string
        Policy system compartment.
    parameters : list
        List of parameters to be loaded. Only relevant for in function calls.

    Returns
    -------
    tax_data : dict
        Dictionary of parameters loaded from raw yaml file and striped of
        unnecessary keys.

    """
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
            key
            for key in raw_group_data[param].keys()
            if isinstance(key, datetime.date)
        )

        past_policies = [x for x in policy_dates if x <= policy_date]

        if not past_policies:
            # If no policy exists, then we check if the policy maybe agrees right now
            # with another one.
            if "deviation_from" in raw_group_data[param][np.min(policy_dates)].keys():
                future_policy = raw_group_data[param][np.min(policy_dates)]
                if "." in future_policy["deviation_from"]:
                    path_list = future_policy["deviation_from"].split(".")
                    tax_data[param] = _load_parameter_group_from_yaml(
                        policy_date, path_list[0], parameters=[path_list[1]]
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
                        tax_data[param] = _load_parameter_group_from_yaml(
                            new_date, group, parameters=[param]
                        )[param]
                    elif "." in policy_in_place["deviation_from"]:
                        path_list = policy_in_place["deviation_from"].split(".")
                        tax_data[param] = _load_parameter_group_from_yaml(
                            policy_date, path_list[0], parameters=[path_list[1]]
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

    tax_data["datum"] = policy_date

    return tax_data


def transfer_dictionary(remaining_dict, new_dict, key_list):
    # To call recursive, always check if object is a dict
    if isinstance(remaining_dict, dict):
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
