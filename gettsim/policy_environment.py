import copy
import datetime
import operator
from functools import reduce

import numpy as np
import pandas as pd
import yaml

from gettsim.config import INTERNAL_PARAM_GROUPS
from gettsim.config import ROOT_DIR
from gettsim.piecewise_functions import check_thresholds
from gettsim.piecewise_functions import get_piecewise_parameters
from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.taxes.eink_st import eink_st_tu_ab_1997
from gettsim.taxes.eink_st import eink_st_tu_bis_1996
from gettsim.taxes.zu_verst_eink.eink import sum_eink_mit_kapital
from gettsim.taxes.zu_verst_eink.eink import sum_eink_ohne_kapital
from gettsim.taxes.zu_verst_eink.freibetraege import eink_st_alleinerz_freib_tu_ab_2015
from gettsim.taxes.zu_verst_eink.freibetraege import eink_st_alleinerz_freib_tu_bis_2014
from gettsim.taxes.zu_verst_eink.freibetraege import eink_st_altersfreib_bis_2004
from gettsim.taxes.zu_verst_eink.freibetraege import eink_st_altersfreib_ab_2005
from gettsim.taxes.zu_verst_eink.freibetraege import eink_st_sonderausgaben_ab_2012
from gettsim.taxes.zu_verst_eink.freibetraege import eink_st_sonderausgaben_bis_2011
from gettsim.taxes.zu_verst_eink.vorsorgeaufw import vorsorgeaufw_ab_2005_bis_2009
from gettsim.taxes.zu_verst_eink.vorsorgeaufw import vorsorgeaufw_ab_2010_bis_2019
from gettsim.taxes.zu_verst_eink.vorsorgeaufw import vorsorgeaufw_ab_2020
from gettsim.taxes.zu_verst_eink.vorsorgeaufw import vorsorgeaufw_bis_2004
from gettsim.transfers.arbeitsl_geld_2.arbeitsl_geld_2 import (
    arbeitsl_geld_2_kindersatz_m_hh_ab_2011,
)
from gettsim.transfers.arbeitsl_geld_2.arbeitsl_geld_2 import (
    arbeitsl_geld_2_kindersatz_m_hh_bis_2010,
)
from gettsim.transfers.arbeitsl_geld_2.arbeitsl_geld_2 import (
    arbeitsl_geld_2_regelsatz_m_hh_ab_2011,
)
from gettsim.transfers.arbeitsl_geld_2.arbeitsl_geld_2 import (
    arbeitsl_geld_2_regelsatz_m_hh_bis_2010,
)
from gettsim.transfers.arbeitsl_geld_2.arbeitsl_geld_2_eink import (
    arbeitsl_geld_2_eink_anr_frei_m_ab_10_2005,
)
from gettsim.transfers.arbeitsl_geld_2.arbeitsl_geld_2_eink import (
    arbeitsl_geld_2_eink_anr_frei_m_bis_09_2005,
)
from gettsim.transfers.grunds_im_alter import grunds_im_alter_ges_rente_m_ab_2021
from gettsim.transfers.grunds_im_alter import grunds_im_alter_ges_rente_m_bis_2020
from gettsim.transfers.kindergeld import kindergeld_anspruch_nach_lohn
from gettsim.transfers.kindergeld import kindergeld_anspruch_nach_stunden
from gettsim.transfers.kindergeld import kindergeld_m_ab_1997
from gettsim.transfers.kindergeld import kindergeld_m_bis_1996
from gettsim.transfers.kinderzuschl.kinderzuschl import (
    _kinderzuschl_vor_vermög_check_m_hh_ab_07_2019,
)
from gettsim.transfers.kinderzuschl.kinderzuschl import (
    _kinderzuschl_vor_vermög_check_m_hh_bis_06_2019,
)
from gettsim.transfers.kinderzuschl.kinderzuschl_eink import (
    kinderzuschl_eink_regel_m_hh_ab_2011,
)
from gettsim.transfers.kinderzuschl.kinderzuschl_eink import (
    kinderzuschl_eink_regel_m_hh_bis_2010,
)
from gettsim.transfers.rente import ges_rente_nach_grundr_m
from gettsim.transfers.rente import ges_rente_vor_grundr_m
from gettsim.transfers.wohngeld import wohngeld_eink_abzüge_m_ab_2016
from gettsim.transfers.wohngeld import wohngeld_eink_abzüge_m_bis_2015
from gettsim.transfers.wohngeld import wohngeld_miete_m_ab_2009
from gettsim.transfers.wohngeld import wohngeld_miete_m_ab_2021
from gettsim.transfers.wohngeld import wohngeld_miete_m_bis_2008


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
        params_one_group = _load_parameter_group_from_yaml(date, group)

        # Align parameters for piecewise polynomial functions
        params[group] = _parse_piecewise_parameters(params_one_group)

    # extend dictionary with date-specific values which do not need an own function
    params = _parse_kinderzuschl_max(date, params)
    params = _parse_einführungsfaktor_vorsorgeaufw_alter_ab_2005(date, params)

    functions = load_reforms_for_date(date)

    return params, functions


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


def _parse_piecewise_parameters(tax_data):
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


def _parse_kinderzuschl_max(date, params):
    """Prior to 2021, the maximum amount of the
    Kinderzuschlag was specified directly in the laws and directives.

    Since 2021, this measure has been derived from subsistence
    levels. This function implements that calculation.

    Parameters
    ----------
    date: datetime.date
        The date for which the policy parameters are set up.
    params: dict
        A dictionary with parameters from the policy environment.

    Returns
    -------
    params: dic
        updated dictionary

    """

    if date.year >= 2021:
        assert {"kinderzuschl", "kindergeld"} <= params.keys()
        params["kinderzuschl"]["maximum"] = (
            params["kinderzuschl"]["existenzminimum"]["regelsatz"]["kinder"]
            + params["kinderzuschl"]["existenzminimum"]["kosten_der_unterkunft"][
                "kinder"
            ]
            + params["kinderzuschl"]["existenzminimum"]["heizkosten"]["kinder"]
        ) / 12 - params["kindergeld"]["kindergeld"][1]

    return params


def _parse_einführungsfaktor_vorsorgeaufw_alter_ab_2005(date, params):
    """Calculate introductory factor for pension expense deductions which depends on the
    current year as follows:

    In the years 2005-2025 the share of deductible contributions increases by
    2 percentage points each year from 60% in 2005 to 100% in 2025.

    Reference: § 10 Abs. 1 Nr. 2 Buchst. a und b EStG

    Parameters
    ----------
    date: datetime.date
        The date for which the policy parameters are set up.
    params: dict
        A dictionary with parameters from the policy environment.

    Returns
    -------
    params: dic
        updated dictionary

    """
    jahr = float(date.year)
    if jahr >= 2005:

        # ToDo: remove conversion to Series after moving to scalar
        out = piecewise_polynomial(
            pd.Series(jahr),
            thresholds=params["eink_st_abzuege"]["einführungsfaktor"]["thresholds"],
            rates=params["eink_st_abzuege"]["einführungsfaktor"]["rates"],
            intercepts_at_lower_thresholds=params["eink_st_abzuege"][
                "einführungsfaktor"
            ]["intercepts_at_lower_thresholds"],
        )
        params["eink_st_abzuege"][
            "einführungsfaktor_vorsorgeaufw_alter_ab_2005"
        ] = out.loc[0]
    return params


def load_reforms_for_date(date):
    """Load time-dependent policy reforms.

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
        functions["sum_eink"] = sum_eink_mit_kapital
    else:
        functions["sum_eink"] = sum_eink_ohne_kapital

    if year <= 2014:
        functions["alleinerz_freib_tu"] = eink_st_alleinerz_freib_tu_bis_2014
    else:
        functions["alleinerz_freib_tu"] = eink_st_alleinerz_freib_tu_ab_2015

    if year <= 2004:
        functions["eink_st_altersfreib"] = eink_st_altersfreib_bis_2004
    else:
        functions["eink_st_altersfreib"] = eink_st_altersfreib_ab_2005

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
        functions["sonderausgaben"] = eink_st_sonderausgaben_ab_2012
    else:
        functions["sonderausgaben"] = eink_st_sonderausgaben_bis_2011

    if year >= 2020:
        functions["vorsorge"] = vorsorgeaufw_ab_2020
    elif 2020 > year >= 2010:
        functions["vorsorge"] = vorsorgeaufw_ab_2010_bis_2019
    elif 2010 > year >= 2005:
        functions["vorsorge"] = vorsorgeaufw_ab_2005_bis_2009
    elif year <= 2004:
        functions["vorsorge"] = vorsorgeaufw_bis_2004

    if year <= 2015:
        functions["wohngeld_eink_abzüge_m"] = wohngeld_eink_abzüge_m_bis_2015
    else:
        functions["wohngeld_eink_abzüge_m"] = wohngeld_eink_abzüge_m_ab_2016

    if year <= 2008:
        functions["wohngeld_miete_m"] = wohngeld_miete_m_bis_2008
    elif 2009 <= year <= 2020:
        functions["wohngeld_miete_m"] = wohngeld_miete_m_ab_2009
    else:
        functions["wohngeld_miete_m"] = wohngeld_miete_m_ab_2021

    if year <= 2010:
        functions[
            "kinderzuschl_eink_regel_m_hh"
        ] = kinderzuschl_eink_regel_m_hh_bis_2010
    else:
        functions["kinderzuschl_eink_regel_m_hh"] = kinderzuschl_eink_regel_m_hh_ab_2011

    if date < datetime.date(year=2019, month=7, day=1):
        functions[
            "_kinderzuschl_vor_vermög_check_m_hh"
        ] = _kinderzuschl_vor_vermög_check_m_hh_bis_06_2019
    else:
        functions[
            "_kinderzuschl_vor_vermög_check_m_hh"
        ] = _kinderzuschl_vor_vermög_check_m_hh_ab_07_2019

    if year <= 2010:
        functions[
            "arbeitsl_geld_2_kindersatz_m_hh"
        ] = arbeitsl_geld_2_kindersatz_m_hh_bis_2010
        functions[
            "arbeitsl_geld_2_regelsatz_m_hh"
        ] = arbeitsl_geld_2_regelsatz_m_hh_bis_2010
    else:
        functions[
            "arbeitsl_geld_2_kindersatz_m_hh"
        ] = arbeitsl_geld_2_kindersatz_m_hh_ab_2011
        functions[
            "arbeitsl_geld_2_regelsatz_m_hh"
        ] = arbeitsl_geld_2_regelsatz_m_hh_ab_2011

    if date < datetime.date(year=2005, month=10, day=1):
        functions[
            "arbeitsl_geld_2_eink_anr_frei_m"
        ] = arbeitsl_geld_2_eink_anr_frei_m_bis_09_2005
    else:
        functions[
            "arbeitsl_geld_2_eink_anr_frei_m"
        ] = arbeitsl_geld_2_eink_anr_frei_m_ab_10_2005

    # Introduction of Grundrente
    if year < 2021:
        functions["ges_rente_m"] = ges_rente_vor_grundr_m
        functions["grunds_im_alter_ges_rente_m"] = grunds_im_alter_ges_rente_m_bis_2020
    else:
        functions["ges_rente_m"] = ges_rente_nach_grundr_m
        functions["grunds_im_alter_ges_rente_m"] = grunds_im_alter_ges_rente_m_ab_2021

    return functions


def _load_parameter_group_from_yaml(
    date, group, parameters=None, yaml_path=ROOT_DIR / "parameters"
):
    """Load data from raw yaml group file.

    Parameters
    ----------
    date : datetime.date
        The date for which the policy system is set up.
    group : string
        Policy system compartment.
    parameters : list
        List of parameters to be loaded. Only relevant for in function calls.
    yaml_path : path
        Path to directory of yaml_file. (Used for testing of this function).

    Returns
    -------
    tax_data : dict
        Dictionary of parameters loaded from raw yaml file and striped of
        unnecessary keys.

    """

    def subtract_years_from_date(dt, years):
        """Subtract one or more years from a date object"""
        try:
            dt = dt.replace(year=dt.year - years)

        # Take care of leap years
        except ValueError:
            dt = dt.replace(year=dt.year - years, day=dt.day - 1)
        return dt

    raw_group_data = yaml.load(
        (yaml_path / f"{group}.yaml").read_text(encoding="utf-8"),
        Loader=yaml.CLoader,
    )

    # Load parameters (exclude 'rounding' parameters which are handled at the
    # end of this function)
    not_trans_keys = ["note", "reference", "deviation_from", "access_different_date"]
    tax_data = {}
    if not parameters:
        parameters = [k for k in raw_group_data if k != "rounding"]

    # Load values of all parameters at the specified date
    for param in parameters:
        policy_dates = sorted(
            key
            for key in raw_group_data[param].keys()
            if isinstance(key, datetime.date)
        )

        past_policies = [d for d in policy_dates if d <= date]

        if not past_policies:
            # If no policy exists, then we check if the policy maybe agrees right now
            # with another one.
            if "deviation_from" in raw_group_data[param][np.min(policy_dates)].keys():
                future_policy = raw_group_data[param][np.min(policy_dates)]
                if "." in future_policy["deviation_from"]:
                    path_list = future_policy["deviation_from"].split(".")
                    tax_data[param] = _load_parameter_group_from_yaml(
                        date,
                        path_list[0],
                        parameters=[path_list[1]],
                        yaml_path=yaml_path,
                    )[path_list[1]]
            else:
                # TODO: Should there be missing values or should the key not exist?
                tax_data[param] = np.nan
        else:
            policy_in_place = raw_group_data[param][np.max(past_policies)]
            if "scalar" in policy_in_place.keys():
                if policy_in_place["scalar"] == "inf":
                    tax_data[param] = np.inf
                else:
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
                            new_date, group, parameters=[param], yaml_path=yaml_path
                        )[param]
                    elif "." in policy_in_place["deviation_from"]:
                        path_list = policy_in_place["deviation_from"].split(".")
                        tax_data[param] = _load_parameter_group_from_yaml(
                            date,
                            path_list[0],
                            parameters=[path_list[1]],
                            yaml_path=yaml_path,
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

            # Also load earlier parameter values if this is specified in yaml
            if "access_different_date" in raw_group_data[param]:
                if raw_group_data[param]["access_different_date"] == "vorjahr":
                    date_last_year = subtract_years_from_date(date, years=1)
                    tax_data[f"{param}_vorjahr"] = _load_parameter_group_from_yaml(
                        date_last_year, group, parameters=[param], yaml_path=yaml_path
                    )[param]
                else:
                    raise ValueError(
                        "Currently, access_different_date is only implemented for "
                        "'vorjahr' (last year). "
                        f"For parameter {param} a different string is specified."
                    )

    tax_data["datum"] = np.datetime64(date)

    # Load rounding parameters if they exist
    if "rounding" in raw_group_data:
        tax_data["rounding"] = _load_rounding_parameters(
            date, raw_group_data["rounding"]
        )
    return tax_data


def _load_rounding_parameters(date, rounding_spec):
    """Load rounding parameters for a specific date from a dictionary.

    Parameters
    ----------
    date : datetime.date
        The date for which the policy system is set up.
    rounding_spec : dictionary
          - Keys: Functions to be rounded.
          - Values: Rounding parameters for all dates

    Returns:
        dictionary:
          - Keys: Functions to be rounded.
          - Values: Rounding parameters for the specified date
    """
    out = {}
    rounding_parameters = ["direction", "base"]

    # Load values of all parameters at the specified date.
    for function_name, rounding_spec_func in rounding_spec.items():

        # Find all specified policy dates before date.
        policy_dates_before_date = sorted(
            key
            for key in rounding_spec_func.keys()
            if isinstance(key, datetime.date) and key <= date
        )

        # If any rounding specs are defined for a date before the specified
        # date, copy them to params dictionary.
        # If no appropriate rounding specs are found for the requested date,
        # the function will not appear in the returned dictionary.
        # Note this will raise an error later unless the user adds an
        # appropriate rounding specification to the parameters dictionary.
        if policy_dates_before_date:
            policy_date_in_place = np.max(policy_dates_before_date)
            policy_in_place = rounding_spec_func[policy_date_in_place]
            out[function_name] = {}
            for key in [k for k in policy_in_place if k in rounding_parameters]:
                out[function_name][key] = policy_in_place[key]
    return out


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
    lower_thresholds, upper_thresholds, thresholds = check_thresholds(
        param_dict, parameter, interval_keys
    )
    for key in interval_keys:
        if "rate_quadratic" not in out_dict[key]:
            out_dict[key]["rate_quadratic"] = (
                out_dict[key + 1]["rate_linear"] - out_dict[key]["rate_linear"]
            ) / (2 * (upper_thresholds[key] - lower_thresholds[key]))
    return out_dict
