import copy
import datetime
import operator
from collections.abc import Callable
from functools import reduce

import numpy
import pandas as pd
import yaml

import _gettsim.functions  # Execute all decorators # noqa: F401
from _gettsim.config import INTERNAL_PARAMS_GROUPS, RESOURCE_DIR
from _gettsim.functions_loader import load_internal_functions
from _gettsim.piecewise_functions import (
    check_thresholds,
    get_piecewise_parameters,
    piecewise_polynomial,
)


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
        information see the documentation of the :ref:`params_files`.
    functions : dict
        Dictionary mapping column names to functions creating the respective
        data.

    """
    # Check policy date for correct format and transfer to datetime.date
    date = _parse_date(date)

    params = {}
    for group in INTERNAL_PARAMS_GROUPS:
        params_one_group = _load_parameter_group_from_yaml(date, group)

        # Align parameters for piecewise polynomial functions
        params[group] = _parse_piecewise_parameters(params_one_group)

    # extend dictionary with date-specific values which do not need an own function
    params = _parse_kinderzuschl_max(date, params)
    params = _parse_einführungsfaktor_vorsorgeaufw_alter_ab_2005(date, params)
    params = _parse_vorsorgepauschale_rentenv_anteil(date, params)
    functions = load_functions_for_date(date)

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
    """Prior to 2021, the maximum amount of the Kinderzuschlag was specified directly in
    the laws and directives.

    In 2021, 2022, and from 2024 on, this measure has been derived from
    subsistence levels. This function implements that calculation.

    For 2023 the amount is once again explicitly specified as a parameter.

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

    if 2023 > date.year >= 2021:
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
        out = piecewise_polynomial(
            pd.Series(jahr),
            thresholds=params["eink_st_abzuege"]["einführungsfaktor"]["thresholds"],
            rates=params["eink_st_abzuege"]["einführungsfaktor"]["rates"],
            intercepts_at_lower_thresholds=params["eink_st_abzuege"][
                "einführungsfaktor"
            ]["intercepts_at_lower_thresholds"],
        )
        params["eink_st_abzuege"]["einführungsfaktor_vorsorgeaufw_alter_ab_2005"] = (
            out.loc[0]
        )
    return params


def _parse_vorsorgepauschale_rentenv_anteil(date, params):
    """Calculate the share of pension contributions to be deducted for Lohnsteuer
    increases by year.

    Parameters
    ----------
    date: datetime.date
        The date for which the policy parameters are set up.
    params: dict
        A dictionary with parameters from the policy environment.

    Returns
    -------
    out: float

    """

    jahr = float(date.year)
    if jahr >= 2005:
        out = piecewise_polynomial(
            pd.Series(jahr),
            thresholds=params["eink_st_abzuege"]["vorsorgepauschale_rentenv_anteil"][
                "thresholds"
            ],
            rates=params["eink_st_abzuege"]["vorsorgepauschale_rentenv_anteil"][
                "rates"
            ],
            intercepts_at_lower_thresholds=params["eink_st_abzuege"][
                "vorsorgepauschale_rentenv_anteil"
            ]["intercepts_at_lower_thresholds"],
        )
        params["eink_st_abzuege"]["vorsorgepauschale_rentenv_anteil"] = out.loc[0]

    return params


def load_functions_for_date(date):
    """Load time-dependent policy reforms.

    Parameters
    ----------
    date : datetime.date
        The date for which the policy system is set up.

    Returns
    -------
    functions : dict
        Dictionary mapping column names to functions creating the respective
        data.

    """

    # Using TIME_DEPENDENT_FUNCTIONS here leads to failing tests.
    functions = {}
    for f in load_internal_functions().values():
        if not is_time_dependent(f) or is_active_at_date(f, date):
            info = f.__info__ if hasattr(f, "__info__") else {}
            name = info.get("dates_active_dag_key", f.__name__)
            functions[name] = f

    return functions


def is_time_dependent(f: Callable) -> bool:
    return hasattr(f, "__info__") and "dates_active_dag_key" in f.__info__


def is_active_at_date(f: Callable, date: datetime.date) -> bool:
    return f.__info__["start_date"] <= date <= f.__info__["end_date"]


def _load_parameter_group_from_yaml(
    date, group, parameters=None, yaml_path=RESOURCE_DIR / "parameters"
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
    out_params : dict
        Dictionary of parameters loaded from raw yaml file and striped of
        unnecessary keys.

    """

    def subtract_years_from_date(dt, years):
        """Subtract one or more years from a date object."""
        try:
            dt = dt.replace(year=dt.year - years)

        # Take care of leap years
        except ValueError:
            dt = dt.replace(year=dt.year - years, day=dt.day - 1)
        return dt

    def set_date_to_beginning_of_year(dt):
        """Set date to the beginning of the year."""

        dt = dt.replace(month=1, day=1)

        return dt

    raw_group_data = yaml.load(
        (yaml_path / f"{group}.yaml").read_text(encoding="utf-8"),
        Loader=yaml.CLoader,
    )

    # Load parameters (exclude 'rounding' parameters which are handled at the
    # end of this function)
    not_trans_keys = ["note", "reference", "deviation_from", "access_different_date"]
    out_params = {}
    if not parameters:
        parameters = [k for k in raw_group_data if k != "rounding"]

    # Load values of all parameters at the specified date
    for param in parameters:
        policy_dates = sorted(
            key for key in raw_group_data[param] if isinstance(key, datetime.date)
        )

        past_policies = [d for d in policy_dates if d <= date]

        if not past_policies:
            # If no policy exists, then we check if the policy maybe agrees right now
            # with another one.
            # Otherwise, do not create an entry for this parameter.
            if "deviation_from" in raw_group_data[param][numpy.min(policy_dates)]:
                future_policy = raw_group_data[param][numpy.min(policy_dates)]
                if "." in future_policy["deviation_from"]:
                    path_list = future_policy["deviation_from"].split(".")
                    params_temp = _load_parameter_group_from_yaml(
                        date,
                        path_list[0],
                        parameters=[path_list[1]],
                        yaml_path=yaml_path,
                    )
                    if path_list[1] in params_temp:
                        out_params[param] = params_temp[path_list[1]]

        else:
            policy_in_place = raw_group_data[param][numpy.max(past_policies)]
            if "scalar" in policy_in_place:
                if policy_in_place["scalar"] == "inf":
                    out_params[param] = numpy.inf
                else:
                    out_params[param] = policy_in_place["scalar"]
            else:
                out_params[param] = {}
                # Keys which if given are transferred
                add_trans_keys = ["type", "progressionsfaktor"]
                for key in add_trans_keys:
                    if key in raw_group_data[param]:
                        out_params[param][key] = raw_group_data[param][key]
                value_keys = (
                    key for key in policy_in_place if key not in not_trans_keys
                )
                if "deviation_from" in policy_in_place:
                    if policy_in_place["deviation_from"] == "previous":
                        new_date = numpy.max(past_policies) - datetime.timedelta(days=1)
                        out_params[param] = _load_parameter_group_from_yaml(
                            new_date, group, parameters=[param], yaml_path=yaml_path
                        )[param]
                    elif "." in policy_in_place["deviation_from"]:
                        path_list = policy_in_place["deviation_from"].split(".")
                        out_params[param] = _load_parameter_group_from_yaml(
                            date,
                            path_list[0],
                            parameters=[path_list[1]],
                            yaml_path=yaml_path,
                        )[path_list[1]]
                    for key in value_keys:
                        key_list = []
                        out_params[param][key] = transfer_dictionary(
                            policy_in_place[key],
                            copy.deepcopy(out_params[param][key]),
                            key_list,
                        )
                else:
                    for key in value_keys:
                        out_params[param][key] = policy_in_place[key]

            # Also load earlier parameter values if this is specified in yaml
            if "access_different_date" in raw_group_data[param]:
                if raw_group_data[param]["access_different_date"] == "vorjahr":
                    date_last_year = subtract_years_from_date(date, years=1)
                    params_last_year = _load_parameter_group_from_yaml(
                        date_last_year, group, parameters=[param], yaml_path=yaml_path
                    )
                    if param in params_last_year:
                        out_params[f"{param}_vorjahr"] = params_last_year[param]
                elif raw_group_data[param]["access_different_date"] == "jahresanfang":
                    date_beginning_of_year = set_date_to_beginning_of_year(date)
                    if date_beginning_of_year == date:
                        out_params[f"{param}_jahresanfang"] = out_params[param]
                    else:
                        params_beginning_of_year = _load_parameter_group_from_yaml(
                            date_beginning_of_year,
                            group,
                            parameters=[param],
                            yaml_path=yaml_path,
                        )
                        if param in params_beginning_of_year:
                            out_params[f"{param}_jahresanfang"] = (
                                params_beginning_of_year[param]
                            )
                else:
                    raise ValueError(
                        "Currently, access_different_date is only implemented for "
                        "'vorjahr' (last year) and "
                        "'jahresanfang' (beginning of the year). "
                        f"For parameter {param} a different string is specified."
                    )

    out_params["datum"] = numpy.datetime64(date)

    # Load rounding parameters if they exist
    if "rounding" in raw_group_data:
        out_params["rounding"] = _load_rounding_parameters(
            date, raw_group_data["rounding"]
        )
    return out_params


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
            for key in rounding_spec_func
            if isinstance(key, datetime.date) and key <= date
        )

        # If any rounding specs are defined for a date before the specified
        # date, copy them to params dictionary.
        # If no appropriate rounding specs are found for the requested date,
        # the function will not appear in the returned dictionary.
        # Note this will raise an error later unless the user adds an
        # appropriate rounding specification to the parameters dictionary.
        if policy_dates_before_date:
            policy_date_in_place = numpy.max(policy_dates_before_date)
            policy_in_place = rounding_spec_func[policy_date_in_place]
            out[function_name] = {}
            for key in [k for k in policy_in_place if k in rounding_parameters]:
                out[function_name][key] = policy_in_place[key]
    return out


def transfer_dictionary(remaining_dict, new_dict, key_list):
    # To call recursive, always check if object is a dict
    if isinstance(remaining_dict, dict):
        for key in remaining_dict:
            key_list_updated = [*key_list, key]
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


def add_progressionsfaktor(params_dict, parameter):
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
    out_dict = copy.deepcopy(params_dict)
    interval_keys = sorted(key for key in out_dict if isinstance(key, int))
    # Check and extract lower thresholds.
    lower_thresholds, upper_thresholds, thresholds = check_thresholds(
        params_dict, parameter, interval_keys
    )
    for key in interval_keys:
        if "rate_quadratic" not in out_dict[key]:
            out_dict[key]["rate_quadratic"] = (
                out_dict[key + 1]["rate_linear"] - out_dict[key]["rate_linear"]
            ) / (2 * (upper_thresholds[key] - lower_thresholds[key]))
    return out_dict
