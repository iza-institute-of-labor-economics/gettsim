import copy
import datetime
import operator
from functools import reduce

import numpy as np
import pandas as pd
import yaml

from gettsim.config import INTERNAL_PARAM_GROUPS
from gettsim.config import ROOT_DIR
from gettsim.piecewise_functions import check_threholds
from gettsim.piecewise_functions import get_piecewise_parameters
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
from gettsim.transfers.arbeitsl_geld_2.arbeitsl_geld_2 import kindersatz_m_hh_ab_2011
from gettsim.transfers.arbeitsl_geld_2.arbeitsl_geld_2 import kindersatz_m_hh_bis_2010
from gettsim.transfers.arbeitsl_geld_2.arbeitsl_geld_2 import regelsatz_m_hh_ab_2011
from gettsim.transfers.arbeitsl_geld_2.arbeitsl_geld_2 import regelsatz_m_hh_bis_2010
from gettsim.transfers.arbeitsl_geld_2.eink_anr_frei import eink_anr_frei_ab_10_2005
from gettsim.transfers.arbeitsl_geld_2.eink_anr_frei import eink_anr_frei_bis_10_2005
from gettsim.transfers.kinderzuschlag.kinderzuschlag import (
    kinderzuschlag_ab_2005_bis_juni_2019,
)
from gettsim.transfers.kinderzuschlag.kinderzuschlag import kinderzuschlag_ab_juli_2019
from gettsim.transfers.kinderzuschlag.kinderzuschlag_eink import (
    kinderzuschlag_eink_regel_ab_2011,
)
from gettsim.transfers.kinderzuschlag.kinderzuschlag_eink import (
    kinderzuschlag_eink_regel_bis_2010,
)
from gettsim.transfers.wohngeld import wohngeld_eink_abzüge_ab_2016
from gettsim.transfers.wohngeld import wohngeld_eink_abzüge_bis_2015
from gettsim.transfers.wohngeld import wohngeld_max_miete_ab_2009
from gettsim.transfers.wohngeld import wohngeld_max_miete_bis_2008


def set_up_policy_environment(date):
    """Set up the policy environment for a particular date.

    Parameters
    ----------
    date : int, str, datetime.date
        The date for which the policy system is set up.


    Returns
    -------
    params : dict
        A dictionary with parameters from the policy environment. For more
        information see the documentation of the :ref:`param_files`.
    functions : dict
        Dictionary of time dependent policy reforms. Keys are the variable names they
        create.

    """
    # Check policy date for correct format and transfer to datetime.date
    date = _parse_date(date)

    params = {}
    for group in INTERNAL_PARAM_GROUPS:
        tax_data = _load_parameter_group_from_yaml(date, group)

        # Align paramters for e.g. piecewise polynomial functions
        params[group] = _parse_parameters(tax_data)

    functions = load_reforms_for_date(date)

    # extend dictionary with date-specific values which do not need an own function
    params = load_params_for_date(date, params)
    return params, functions


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


def _parse_date(date):
    """Check the policy date for different input formats.

    Parameters
    ----------
    date : datetime.date, str, int
        The date for which the policy system is set up.

    Returns
    -------
    date : datetime.date
        The date for which the policy system is set up.
    """
    if isinstance(date, str):
        date = pd.to_datetime(date).date()
    elif isinstance(date, int):
        date = datetime.date(year=date, month=1, day=1)
    return date


def load_reforms_for_date(date):
    """Load time dependet policy reforms.

    Parameters
    ----------
    date : datetime.date
        The date for which the policy system is set up.

    Returns
    -------
    functions : dict
        Dictionary of time dependent policy reforms. Keys are the variable names they
        create.

    """
    year = date.year
    functions = {}
    if year < 2009:
        functions["sum_brutto_eink"] = sum_brutto_eink_mit_kapital
    else:
        functions["sum_brutto_eink"] = sum_brutto_eink_ohne_kapital

    if year <= 2014:
        functions["alleinerziehend_freib_tu"] = alleinerziehend_freib_tu_bis_2014
    else:
        functions["alleinerziehend_freib_tu"] = alleinerziehend_freib_tu_ab_2015

    if year <= 1996:
        functions["eink_st_tu"] = eink_st_tu_bis_1996
        functions["kindergeld_m"] = kindergeld_m_bis_1996
    else:
        functions["eink_st_tu"] = eink_st_tu_ab_1997
        functions["kindergeld_m"] = kindergeld_m_ab_1997

    if year > 2011:
        functions["kindergeld_anspruch"] = kindergeld_anspruch_nach_stunden
    else:
        functions["kindergeld_anspruch"] = kindergeld_anspruch_nach_lohn

    if year > 2011:
        functions["sonderausgaben"] = sonderausgaben_ab_2012
    else:
        functions["sonderausgaben"] = sonderausgaben_bis_2011

    if year >= 2020:
        functions["vorsorge"] = vorsorge_ab_2020
    elif 2020 > year >= 2010:
        functions["vorsorge"] = vorsorge_ab_2010_bis_2019
    elif 2010 > year >= 2005:
        functions["vorsorge"] = vorsorge_ab_2005_bis_2009
    elif year <= 2004:
        functions["vorsorge"] = vorsorge_bis_2004

    if year <= 2015:
        functions["wohngeld_eink_abzüge"] = wohngeld_eink_abzüge_bis_2015
    else:
        functions["wohngeld_eink_abzüge"] = wohngeld_eink_abzüge_ab_2016

    if year <= 2008:
        functions["wohngeld_max_miete"] = wohngeld_max_miete_bis_2008
    else:
        functions["wohngeld_max_miete"] = wohngeld_max_miete_ab_2009

    if year <= 2010:
        functions["kinderzuschlag_eink_regel"] = kinderzuschlag_eink_regel_bis_2010
    else:
        functions["kinderzuschlag_eink_regel"] = kinderzuschlag_eink_regel_ab_2011

    if 2005 <= year <= 2019:
        functions["kinderzuschlag_m_vorläufig"] = kinderzuschlag_ab_2005_bis_juni_2019
    else:
        functions["kinderzuschlag_m_vorläufig"] = kinderzuschlag_ab_juli_2019

    if year <= 2010:
        functions["kindersatz_m_hh"] = kindersatz_m_hh_bis_2010
        functions["regelsatz_m_hh"] = regelsatz_m_hh_bis_2010
    else:
        functions["kindersatz_m_hh"] = kindersatz_m_hh_ab_2011
        functions["regelsatz_m_hh"] = regelsatz_m_hh_ab_2011

    if date <= datetime.date(year=2005, month=10, day=1):
        functions["eink_anr_frei"] = eink_anr_frei_bis_10_2005
    else:
        functions["eink_anr_frei"] = eink_anr_frei_ab_10_2005

    return functions


def load_params_for_date(date, params):
    """Specify parameter values (not functions) which are subject to date.
    This is relevant if they depend on other parameters and/or if this changes over time

    Parameters
    ----------
    date: datetime.date
        The date for which the polocy system is set up
    params: dict
        A dictionary with parameters from the policy environment.

    Returns
    -------
    params: dic
        updated dictionary

    """

    if date.year <= 2020:
        params["kinderzuschlag"]["kinderzuschlag_max"] = params["kinderzuschlag"][
            "kinderzuschlag"
        ]
    else:
        """Since 2021, the maximum amount has been derived from subsistence levels
        published and updated regularly by the government
        """
        params["kinderzuschlag"]["kinderzuschlag_max"] = (
            params["kinderzuschlag"]["exmin"]["regelsatz"]["kinder"]
            + params["kinderzuschlag"]["exmin"]["kosten_der_unterkunft"]["kinder"]
            + params["kinderzuschlag"]["exmin"]["heizkosten"]["kinder"]
        ) / 12 - params["kindergeld"]["kindergeld"][1]
    return params


def _load_parameter_group_from_yaml(date, group, parameters=None):
    """Load data from raw yaml group file.

    Parameters
    ----------
    date : datetime.date
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
    raw_group_data = yaml.load(
        (ROOT_DIR / "parameters" / f"{group}.yaml").read_text(encoding="utf-8"),
        Loader=yaml.CLoader,
    )

    # Keys from the raw file which will not be transferred
    not_trans_keys = ["note", "reference", "deviation_from"]
    tax_data = {}
    if not parameters:
        parameters = raw_group_data.keys()
    for param in parameters:
        dates = sorted(
            key
            for key in raw_group_data[param].keys()
            if isinstance(key, datetime.date)
        )

        past_policies = [x for x in dates if x <= date]

        if not past_policies:
            # If no policy exists, then we check if the policy maybe agrees right now
            # with another one.
            if "deviation_from" in raw_group_data[param][np.min(dates)].keys():
                future_policy = raw_group_data[param][np.min(dates)]
                if "." in future_policy["deviation_from"]:
                    path_list = future_policy["deviation_from"].split(".")
                    tax_data[param] = _load_parameter_group_from_yaml(
                        date, path_list[0], parameters=[path_list[1]]
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
                            date, path_list[0], parameters=[path_list[1]]
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

    tax_data["datum"] = date

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


def add_progressionsfaktor(param_dict, parameter):
    """Quadratic factor of tax tariff function.

    The German tax tariff is defined on several income intervals with distinct
    marginal tax rates at the thresholds. To ensure an almost linear increase of
    the average tax rate, the German tax tariff is defined as a quadratic function,
    where the quadratic rate is the so called linear Progressionsfaktor. For its
    calculation one needs the lower (low_thres) and upper (upper_thres) thresholds of
    the interval as well as the marginal tax rate of the interval (rate_iv) and of the
    following interval (rate_fiv). The formula is then given by:

    (rate_fiv - rate_iv) / (2 * (upper_thres - low_thres))

    """
    out_dict = copy.deepcopy(param_dict)
    interval_keys = sorted(key for key in out_dict if isinstance(key, int))
    # Check and extract lower thresholds.
    lower_thresholds, upper_thresholds, thresholds = check_threholds(
        param_dict, parameter, interval_keys
    )
    for key in interval_keys:
        if "rate_quadratic" not in out_dict[key]:
            out_dict[key]["rate_quadratic"] = (
                out_dict[key + 1]["rate_linear"] - out_dict[key]["rate_linear"]
            ) / (2 * (upper_thresholds[key] - lower_thresholds[key]))
    return out_dict
