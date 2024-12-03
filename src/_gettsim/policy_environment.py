from __future__ import annotations

import copy
import datetime
from typing import Any

import numpy
import pandas as pd
import yaml
from optree import tree_flatten, tree_paths, tree_unflatten

from _gettsim.config import INTERNAL_PARAMS_GROUPS, RESOURCE_DIR
from _gettsim.functions.loader import (
    load_functions_tree_for_date,
    load_internal_aggregation_dict,
)
from _gettsim.functions.policy_function import PolicyFunction
from _gettsim.piecewise_functions import (
    check_thresholds,
    get_piecewise_parameters,
    piecewise_polynomial,
)
from _gettsim.shared import (
    get_by_path,
    merge_nested_dicts,
    set_by_path,
)


class PolicyEnvironment:
    """
    A container for policy functions and parameters.

    Almost always, instances are created with :PolicyEnvironment.for_date()`.

    Parameters
    ----------
    functions:
        A list of policy functions.
    params:
        A dictionary with policy parameters.
    aggregate_by_group_specs:
        A dictionary which contains specs for functions which aggregate variables on the
        aggregation levels specified in config.py. The syntax is the same as for
        aggregation specs in the code base and as specified in [GEP
        4](https://gettsim.readthedocs.io/en/stable/geps/gep-04.html).
    aggregate_by_p_id_specs:
        A dictionary which contains specs for linking aggregating taxes and by another
        individual (for example, a parent). The syntax is the same as for aggregation
        specs in the code base and as specified in [GEP
        4](https://gettsim.readthedocs.io/en/stable/geps/gep-04.html)
    """

    @staticmethod
    def for_date(date: datetime.date | str | int) -> PolicyEnvironment:
        """
        Set up the policy environment for a particular date.

        Parameters
        ----------
        date:
            The date for which the policy system is set up. An integer is
            interpreted as the year.

        Returns
        -------
        environment:
            The policy environment for the specified date.
        """
        # Check policy date for correct format and convert to datetime.date
        date = _parse_date(date)

        params = {}
        for group in INTERNAL_PARAMS_GROUPS:
            params_one_group = _load_parameter_group_from_yaml(date, group)

            # Align parameters for piecewise polynomial functions
            params[group] = _parse_piecewise_parameters(params_one_group)

        # Extend dictionary with date-specific values which do not need an own function
        params = _parse_kinderzuschl_max(date, params)
        params = _parse_einführungsfaktor_vorsorgeaufw_alter_ab_2005(date, params)
        params = _parse_vorsorgepauschale_rentenv_anteil(date, params)
        functions_tree = load_functions_tree_for_date(date)

        # Load aggregation specs
        aggregate_by_group_specs = load_internal_aggregation_dict("aggregate_by_group")
        aggregate_by_p_id_specs = load_internal_aggregation_dict("aggregate_by_p_id")

        return PolicyEnvironment(
            functions_tree, params, aggregate_by_group_specs, aggregate_by_p_id_specs
        )

    def __init__(
        self,
        functions_tree: dict[str, Any],
        params: dict[str, Any] | None = None,
        aggregate_by_group_specs: dict[str, Any] | None = None,
        aggregate_by_p_id_specs: dict[str, Any] | None = None,
    ):
        _fail_if_functions_tree_not_tree(functions_tree)
        flattened_functions_tree, tree_def = tree_flatten(functions_tree)
        functions_with_correct_types = [
            function
            if isinstance(function, PolicyFunction)
            else PolicyFunction(function)
            for function in flattened_functions_tree
        ]
        self._functions_tree = tree_unflatten(tree_def, functions_with_correct_types)

        self._params = params if params is not None else {}
        self._aggregate_by_group_specs = (
            aggregate_by_group_specs if aggregate_by_group_specs is not None else {}
        )
        self._aggregate_by_p_id_specs = (
            aggregate_by_p_id_specs if aggregate_by_p_id_specs is not None else {}
        )

    @property
    def functions_tree(self) -> dict[str, Any]:
        """The functions of the policy environment."""
        return self._functions_tree

    @property
    def params(self) -> dict[str, Any]:
        """The parameters of the policy environment."""
        return self._params

    @property
    def aggregate_by_group_specs(self) -> dict[str, Any]:
        """
        The specs for functions which aggregate variables on the aggregation levels
        specified in config.py.
        """
        return self._aggregate_by_group_specs

    @property
    def aggregate_by_p_id_specs(self) -> dict[str, Any]:
        """
        The specs for linking aggregating taxes and by another individual (for example,
        a parent).
        """
        return self._aggregate_by_p_id_specs

    def get_function_by_path(
        self, function_path: dict[str, Any] | list[str]
    ) -> PolicyFunction | None:
        """
        Return the function with a specific path in the function tree or `None` if no
        such function exists.

        Parameters
        ----------
        function_path:
            The path to the function in the function tree.
            Example 1: {"level_1": {"level_2": "function_name"}}
            Example 2: ["level_1", "level_2", "function_name"]

        Returns
        -------
        function:
            The functions with the specified tree path, if it exists.
        """
        if isinstance(function_path, dict):
            path_list = tree_paths(function_path)
            _fail_if_more_than_one_path(path_list)
            keys = path_list[0]
        elif isinstance(function_path, list):
            keys = function_path
        else:
            raise NotImplementedError(
                "The function_path must be a dictionary or a list."
            )

        try:
            out = get_by_path(self._functions_tree, keys)
        except KeyError:
            out = None

        return out

    def upsert_functions(
        self, functions_tree_update: dict[str, Any]
    ) -> PolicyEnvironment:
        """Upsert GETTSIM's function tree with (parts of) a new function tree.

        Adds to or overwrites functions of the policy environment. Note that this
        method does not modify the current policy environment but returns a new one.

        Parameters
        ----------
        functions_tree_update:
            The functions to add or overwrite.

        Returns
        -------
        new_environment:
            The policy environment with the new functions.
        """
        new_functions_tree = {**self._functions_tree}
        functions_to_upsert, tree_def = tree_flatten(functions_tree_update)
        functions_to_upsert = [
            function
            if isinstance(function, PolicyFunction)
            else PolicyFunction(function)
            for function in functions_to_upsert
        ]
        functions_tree_to_upsert = tree_unflatten(tree_def, functions_to_upsert)
        new_functions_tree = merge_nested_dicts(
            new_functions_tree, functions_tree_to_upsert
        )

        result = object.__new__(PolicyEnvironment)
        result._functions_tree = new_functions_tree  # noqa: SLF001
        result._params = self._params  # noqa: SLF001
        result._aggregate_by_group_specs = (  # noqa: SLF001
            self._aggregate_by_group_specs
        )
        result._aggregate_by_p_id_specs = self._aggregate_by_p_id_specs  # noqa: SLF001

        return result

    def replace_all_parameters(self, params: dict[str, Any]):
        """
        Replace all parameters of the policy environment. Note that this
        method does not modify the current policy environment but returns a new one.

        Parameters
        ----------
        params:
            The new parameters.

        Returns
        -------
        new_environment:
            The policy environment with the new parameters.
        """
        result = object.__new__(PolicyEnvironment)
        result._functions_tree = self._functions_tree  # noqa: SLF001
        result._params = params  # noqa: SLF001
        result._aggregate_by_group_specs = (  # noqa: SLF001
            self._aggregate_by_group_specs
        )
        result._aggregate_by_p_id_specs = self._aggregate_by_p_id_specs  # noqa: SLF001

        return result


def set_up_policy_environment(date: datetime.date | str | int) -> PolicyEnvironment:
    """
    Set up the policy environment for a particular date.

    Parameters
    ----------
    date:
        The date for which the policy system is set up. An integer is
        interpreted as the year.

    Returns
    -------
    environment:
        The policy environment for the specified date.
    """
    return PolicyEnvironment.for_date(date)


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
    params: dict
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
    params: dict
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
    out: dict

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


def _fail_if_more_than_one_path(path_list):
    """Raise error if more than one path is found."""
    if len(path_list) > 1:
        raise ValueError(
            "The functions_path must point to exactly one function in the functions "
            "tree."
        )


def _fail_if_functions_tree_not_tree(obj):
    """Raise error if functions are not passed as tree."""
    if not isinstance(obj, dict):
        raise TypeError("Functions must be passed as a tree.")


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
