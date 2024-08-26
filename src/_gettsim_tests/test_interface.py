import warnings

import numpy
import pandas as pd
import pytest
from _gettsim.config import FOREIGN_KEYS
from _gettsim.gettsim_typing import convert_series_to_internal_type
from _gettsim.groupings import bg_id_numpy, wthh_id_numpy
from _gettsim.interface import (
    _convert_data_to_correct_types,
    _fail_if_foreign_keys_are_invalid,
    _fail_if_group_variables_not_constant_within_groups,
    _fail_if_pid_is_non_unique,
    _round_and_partial_parameters_to_functions,
    compute_taxes_and_transfers,
)
from _gettsim.policy_environment import PolicyEnvironment
from _gettsim.policy_function import PolicyFunction
from _gettsim.shared import policy_info
from gettsim import FunctionsAndColumnsOverlapWarning


@pytest.fixture(scope="module")
def minimal_input_data():
    n_individuals = 5
    out = pd.DataFrame(
        {
            "p_id": numpy.arange(n_individuals),
            "hh_id": numpy.arange(n_individuals),
        },
        index=numpy.arange(n_individuals),
    )
    return out


@pytest.fixture()
def input_data_aggregate_by_p_id():
    return pd.DataFrame(
        {
            "p_id": [1, 2, 3],
            "hh_id": [1, 1, 2],
        }
    )


# Create a partial function which is used by some tests below
def func_before_partial(arg_1, arbeitsl_geld_2_params):
    return arg_1 + arbeitsl_geld_2_params["test_param_1"]


func_after_partial = _round_and_partial_parameters_to_functions(
    {"test_func": func_before_partial},
    {"arbeitsl_geld_2": {"test_param_1": 1}},
    rounding=False,
)["test_func"]


def test_warn_if_functions_and_columns_overlap():
    environment = PolicyEnvironment([PolicyFunction(lambda x: x, function_name="dupl")])
    with pytest.warns(FunctionsAndColumnsOverlapWarning):
        compute_taxes_and_transfers(
            data=pd.DataFrame({"p_id": [0], "dupl": [1]}),
            environment=environment,
            targets=[],
        )


def test_dont_warn_if_functions_and_columns_dont_overlap():
    environment = PolicyEnvironment(
        [PolicyFunction(lambda x: x, function_name="some_func")]
    )
    with warnings.catch_warnings():
        warnings.filterwarnings("error", category=FunctionsAndColumnsOverlapWarning)
        compute_taxes_and_transfers(
            data=pd.DataFrame({"p_id": [0]}),
            environment=environment,
            targets=[],
        )


def test_recipe_to_ignore_warning_if_functions_and_columns_overlap():
    environment = PolicyEnvironment([PolicyFunction(lambda x: x, function_name="dupl")])
    with warnings.catch_warnings(
        category=FunctionsAndColumnsOverlapWarning, record=True
    ) as warning_list:
        warnings.filterwarnings("ignore", category=FunctionsAndColumnsOverlapWarning)
        compute_taxes_and_transfers(
            data=pd.DataFrame({"p_id": [0], "dupl": [1]}),
            environment=environment,
            targets=[],
        )

    assert len(warning_list) == 0


def test_fail_if_pid_does_not_exist():
    data = pd.Series(data=numpy.arange(8), name="hh_id").to_frame()

    with pytest.raises(ValueError):
        _fail_if_pid_is_non_unique(data)


def test_fail_if_pid_is_non_unique():
    data = pd.Series(data=numpy.arange(4).repeat(2), name="p_id").to_frame()

    with pytest.raises(ValueError):
        _fail_if_pid_is_non_unique(data)


@pytest.mark.parametrize("foreign_key", FOREIGN_KEYS)
def test_fail_if_foreign_key_points_to_non_existing_pid(foreign_key):
    data = pd.DataFrame(
        {
            "p_id": [1, 2, 3],
            foreign_key: [0, 1, 4],
        }
    )

    with pytest.raises(ValueError, match="not a valid p_id"):
        _fail_if_foreign_keys_are_invalid(data)


@pytest.mark.parametrize("foreign_key", FOREIGN_KEYS)
def test_allow_minus_one_as_foreign_key(foreign_key):
    data = pd.DataFrame(
        {
            "p_id": [1, 2, 3],
            foreign_key: [-1, 1, 2],
        }
    )

    _fail_if_foreign_keys_are_invalid(data)


@pytest.mark.parametrize("foreign_key", FOREIGN_KEYS)
def test_fail_if_foreign_key_points_to_pid_of_same_row(foreign_key):
    data = pd.DataFrame(
        {
            "p_id": [1, 2, 3],
            foreign_key: [1, 3, 3],
        }
    )

    with pytest.raises(ValueError, match="are equal to the p_id in the same row"):
        _fail_if_foreign_keys_are_invalid(data)


def test_fail_if_group_variables_not_constant_within_groups():
    data = pd.DataFrame(
        {
            "p_id": [1, 2, 3],
            "hh_id": [1, 1, 2],
            "arbeitsl_geld_2_m_hh": [100, 200, 300],
        }
    )

    with pytest.raises(ValueError):
        _fail_if_group_variables_not_constant_within_groups(data)


def test_missing_root_nodes_raises_error(minimal_input_data):
    def b(a):
        return a

    def c(b):
        return b

    environment = PolicyEnvironment([PolicyFunction(b), PolicyFunction(c)])

    with pytest.raises(
        ValueError,
        match="The following data columns are missing",
    ):
        compute_taxes_and_transfers(minimal_input_data, environment, targets="c")


def test_data_as_series():
    def c(p_id):
        return p_id

    data = pd.Series([1, 2, 3])
    data.name = "p_id"

    environment = PolicyEnvironment([c])
    compute_taxes_and_transfers(data, environment, targets="c")


def test_data_as_dict():
    def c(b):
        return b

    data = {
        "p_id": pd.Series([1, 2, 3]),
        "hh_id": pd.Series([1, 1, 2]),
        "b": pd.Series([100, 200, 300]),
    }

    environment = PolicyEnvironment([c])
    compute_taxes_and_transfers(data, environment, targets="c")


def test_wrong_data_type():
    def c(b):
        return b

    data = "not_a_data_object"
    with pytest.raises(
        NotImplementedError,
        match=(
            "'data' is not a pd.DataFrame or a "
            "pd.Series or a dictionary of pd.Series."
        ),
    ):
        compute_taxes_and_transfers(data, PolicyEnvironment([]), [c])


def test_check_minimal_spec_data():
    def c(b):
        return b

    data = pd.DataFrame(
        {
            "p_id": [1, 2, 3],
            "hh_id": [1, 1, 2],
            "a": [100, 200, 300],
            "b": [1, 2, 3],
        }
    )
    environment = PolicyEnvironment([c])
    with pytest.raises(
        ValueError,
        match="The following columns in 'data' are unused",
    ):
        compute_taxes_and_transfers(
            data, environment, targets="c", check_minimal_specification="raise"
        )


def test_check_minimal_spec_data_warn():
    def c(b):
        return b

    data = pd.DataFrame(
        {
            "p_id": [1, 2, 3],
            "hh_id": [1, 1, 2],
            "a": [100, 200, 300],
            "b": [1, 2, 3],
        }
    )
    environment = PolicyEnvironment([c])
    with pytest.warns(
        UserWarning,
        match="The following columns in 'data' are unused",
    ):
        compute_taxes_and_transfers(
            data, environment, targets="c", check_minimal_specification="warn"
        )


def test_check_minimal_spec_columns_overriding():
    def b(a):
        return a

    def c(a):
        return a

    data = pd.DataFrame(
        {
            "p_id": [1, 2, 3],
            "hh_id": [1, 1, 2],
            "a": [100, 200, 300],
            "b": [1, 2, 3],
        }
    )
    environment = PolicyEnvironment([b, c])
    with pytest.raises(
        ValueError,
        match="The following 'columns_overriding_functions' are unused",
    ):
        compute_taxes_and_transfers(
            data, environment, targets="c", check_minimal_specification="raise"
        )


def test_check_minimal_spec_columns_overriding_warn():
    def b(a):
        return a

    def c(a):
        return a

    data = pd.DataFrame(
        {
            "p_id": [1, 2, 3],
            "hh_id": [1, 1, 2],
            "a": [100, 200, 300],
            "b": [1, 2, 3],
        }
    )
    environment = PolicyEnvironment([b, c])
    with pytest.warns(
        UserWarning,
        match="The following 'columns_overriding_functions' are unused",
    ):
        compute_taxes_and_transfers(
            data, environment, targets="c", check_minimal_specification="warn"
        )


def test_function_without_data_dependency_is_not_mistaken_for_data(minimal_input_data):
    def a():
        return pd.Series(range(minimal_input_data.shape[0]))

    def b(a):
        return a

    environment = PolicyEnvironment([a, b])
    compute_taxes_and_transfers(minimal_input_data, environment, targets="b")


def test_fail_if_targets_are_not_in_functions_or_in_columns_overriding_functions(
    minimal_input_data,
):
    environment = PolicyEnvironment([])

    with pytest.raises(
        ValueError,
        match="The following targets have no corresponding function",
    ):
        compute_taxes_and_transfers(
            minimal_input_data, environment, targets="unknown_target"
        )


def test_fail_if_missing_pid(minimal_input_data):
    data = minimal_input_data.drop("p_id", axis=1).copy()
    with pytest.raises(
        ValueError,
        match="The input data must contain the column p_id",
    ):
        compute_taxes_and_transfers(data, PolicyEnvironment([]), targets=[])


def test_fail_if_non_unique_pid(minimal_input_data):
    data = minimal_input_data.copy()
    data["p_id"] = 1

    with pytest.raises(
        ValueError,
        match="The following p_ids are non-unique",
    ):
        compute_taxes_and_transfers(data, PolicyEnvironment([]), targets=[])


def test_fail_if_non_unique_cols(minimal_input_data):
    data = minimal_input_data.copy()
    data["temp"] = data["hh_id"]
    data = data.rename(columns={"temp": "hh_id"})
    with pytest.raises(
        ValueError,
        match="The following columns are non-unique",
    ):
        compute_taxes_and_transfers(data, PolicyEnvironment([]), targets=[])


def test_consecutive_internal_test_runs():
    from gettsim import test

    test("--collect-only")

    with pytest.warns(UserWarning, match="Repeated execution of the test suite"):
        test("--collect-only")


def test_partial_parameters_to_functions():
    # Partial function produces correct result
    assert func_after_partial(2) == 3


def test_partial_parameters_to_functions_removes_argument():
    # Fails if params is added to partial function
    with pytest.raises(
        TypeError,
        match=("got multiple values for argument "),
    ):
        func_after_partial(2, {"test_param_1": 1})

    # No error for original function
    func_before_partial(2, {"test_param_1": 1})


def test_partial_parameters_to_functions_keep_decorator():
    """Make sure that rounding decorator is kept for partial function."""

    @policy_info(params_key_for_rounding="params_key_test")
    def test_func(arg_1, arbeitsl_geld_2_params):
        return arg_1 + arbeitsl_geld_2_params["test_param_1"]

    partial_func = _round_and_partial_parameters_to_functions(
        {"test_func": test_func},
        {"arbeitsl_geld_2": {"test_param_1": 1}},
        rounding=False,
    )["test_func"]

    assert partial_func.__info__["params_key_for_rounding"] == "params_key_test"


def test_user_provided_aggregate_by_group_specs():
    data = pd.DataFrame(
        {
            "p_id": [1, 2, 3],
            "hh_id": [1, 1, 2],
            "arbeitsl_geld_2_m": [100, 100, 100],
        }
    )
    aggregate_by_group_specs = {
        "arbeitsl_geld_2_m_hh": {
            "source_col": "arbeitsl_geld_2_m",
            "aggr": "sum",
        }
    }
    expected_res = pd.Series([200, 200, 100])

    out = compute_taxes_and_transfers(
        data,
        PolicyEnvironment([]),
        aggregate_by_group_specs=aggregate_by_group_specs,
        targets="arbeitsl_geld_2_m_hh",
    )

    numpy.testing.assert_array_almost_equal(out["arbeitsl_geld_2_m_hh"], expected_res)


def test_user_provided_aggregate_by_group_specs_function():
    data = pd.DataFrame(
        {
            "p_id": [1, 2, 3],
            "hh_id": [1, 1, 2],
            "arbeitsl_geld_2_m": [200, 100, 100],
        }
    )
    aggregate_by_group_specs = {
        "arbeitsl_geld_2_double_m_hh": {
            "source_col": "arbeitsl_geld_2_m_double",
            "aggr": "max",
        }
    }
    expected_res = pd.Series([400, 400, 200])

    def arbeitsl_geld_2_m_double(arbeitsl_geld_2_m):
        return 2 * arbeitsl_geld_2_m

    environment = PolicyEnvironment([arbeitsl_geld_2_m_double])

    out = compute_taxes_and_transfers(
        data,
        environment,
        aggregate_by_group_specs=aggregate_by_group_specs,
        targets="arbeitsl_geld_2_double_m_hh",
    )

    numpy.testing.assert_array_almost_equal(
        out["arbeitsl_geld_2_double_m_hh"], expected_res
    )


def test_aggregate_by_group_specs_missing_group_sufix():
    data = pd.DataFrame(
        {
            "p_id": [1, 2, 3],
            "hh_id": [1, 1, 2],
            "arbeitsl_geld_2_m": [100, 100, 100],
        }
    )
    aggregate_by_group_specs = {
        "arbeitsl_geld_2_agg_m": {
            "source_col": "arbeitsl_geld_2_m",
            "aggr": "sum",
        }
    }
    with pytest.raises(
        ValueError,
        match="Name of aggregated column needs to have a suffix",
    ):
        compute_taxes_and_transfers(
            data,
            PolicyEnvironment([]),
            aggregate_by_group_specs=aggregate_by_group_specs,
            targets="arbeitsl_geld_2_agg_m",
        )


def test_aggregate_by_group_specs_agg_not_impl():
    data = pd.DataFrame(
        {
            "p_id": [1, 2, 3],
            "hh_id": [1, 1, 2],
            "arbeitsl_geld_2_m": [100, 100, 100],
        }
    )
    aggregate_by_group_specs = {
        "arbeitsl_geld_2_m_hh": {
            "source_col": "arbeitsl_geld_2_m",
            "aggr": "aggr_not_implemented",
        }
    }
    with pytest.raises(
        ValueError,
        match="Aggr aggr_not_implemented is not implemented.",
    ):
        compute_taxes_and_transfers(
            data,
            PolicyEnvironment([]),
            aggregate_by_group_specs=aggregate_by_group_specs,
            targets="arbeitsl_geld_2_m_hh",
        )


@pytest.mark.parametrize(
    ("df, aggregate_by_p_id_spec, target, expected"),
    [
        (
            "input_data_aggregate_by_p_id",
            {
                "target_func": {
                    "p_id_to_aggregate_by": "hh_id",
                    "source_col": "source_func",
                    "aggr": "sum",
                    "func_return": 100,
                }
            },
            "target_func",
            pd.Series([200, 100, 0]),
        ),
        (
            "input_data_aggregate_by_p_id",
            {
                "target_func_m": {
                    "p_id_to_aggregate_by": "hh_id",
                    "source_col": "source_func_m",
                    "aggr": "sum",
                    "func_return": 100,
                }
            },
            "target_func_y",
            pd.Series([2400, 1200, 0]),
        ),
        (
            "input_data_aggregate_by_p_id",
            {
                "target_func_m": {
                    "p_id_to_aggregate_by": "hh_id",
                    "source_col": "source_func_m",
                    "aggr": "sum",
                    "func_return": 100,
                }
            },
            "target_func_y_hh",
            pd.Series([3600, 3600, 0]),
        ),
    ],
)
def test_user_provided_aggregate_by_p_id_specs(
    df, aggregate_by_p_id_spec, target, expected, request
):
    df = request.getfixturevalue(df)

    target_aggregate_by_p_id_spec = next(iter(aggregate_by_p_id_spec.keys()))

    def source_func():
        return numpy.array(
            [aggregate_by_p_id_spec[target_aggregate_by_p_id_spec]["func_return"]]
            * len(df)
        )

    environment = PolicyEnvironment(
        [
            PolicyFunction(
                source_func,
                function_name=aggregate_by_p_id_spec[target_aggregate_by_p_id_spec][
                    "source_col"
                ],
            )
        ]
    )
    out = compute_taxes_and_transfers(
        df,
        environment,
        aggregate_by_p_id_specs=aggregate_by_p_id_spec,
        targets=target,
    )

    numpy.testing.assert_array_almost_equal(out[target], expected)


@pytest.mark.parametrize(
    "input_data, expected_type, expected_output_data",
    [
        (pd.Series([0, 1, 0]), bool, pd.Series([False, True, False])),
        (pd.Series([1.0, 0.0, 1]), bool, pd.Series([True, False, True])),
        (pd.Series([200, 550, 237]), float, pd.Series([200.0, 550.0, 237.0])),
        (pd.Series([1.0, 4.0, 10.0]), int, pd.Series([1, 4, 10])),
        (pd.Series([200.0, 567.0]), int, pd.Series([200, 567])),
        (pd.Series([1.0, 0.0]), bool, pd.Series([True, False])),
    ],
)
def test_convert_series_to_internal_types(
    input_data, expected_type, expected_output_data
):
    adjusted_input = convert_series_to_internal_type(input_data, expected_type)
    pd.testing.assert_series_equal(adjusted_input, expected_output_data)


@pytest.mark.parametrize(
    "input_data, expected_type, error_match",
    [
        (
            pd.Series(["Hallo", 200, 325]),
            float,
            "Conversion from input type object to float failed.",
        ),
        (
            pd.Series([True, False]),
            float,
            "Conversion from input type bool to float failed.",
        ),
        (
            pd.Series(["a", "b", "c"]).astype("category"),
            float,
            "Conversion from input type category to float failed.",
        ),
        (
            pd.Series(["2.0", "3.0"]),
            int,
            "Conversion from input type object to int failed.",
        ),
        (
            pd.Series([1.5, 1.0, 2.9]),
            int,
            "Conversion from input type float64 to int failed.",
        ),
        (
            pd.Series(["a", "b", "c"]).astype("category"),
            int,
            "Conversion from input type category to int failed.",
        ),
        (
            pd.Series([5, 2, 3]),
            bool,
            "Conversion from input type int64 to bool failed.",
        ),
        (
            pd.Series([1.5, 1.0, 35.0]),
            bool,
            "Conversion from input type float64 to bool failed.",
        ),
        (
            pd.Series(["a", "b", "c"]).astype("category"),
            bool,
            "Conversion from input type category to bool failed.",
        ),
        (
            pd.Series(["richtig"]),
            bool,
            "Conversion from input type object to bool failed.",
        ),
        (
            pd.Series(["True", "False", ""]),
            bool,
            "Conversion from input type object to bool failed.",
        ),
        (
            pd.Series(["true"]),
            bool,
            "Conversion from input type object to bool failed.",
        ),
        (
            pd.Series(["zweitausendzwanzig"]),
            numpy.datetime64,
            "Conversion from input type object to datetime64 failed.",
        ),
        (
            pd.Series([True, True]),
            numpy.datetime64,
            "Conversion from input type bool to datetime64 failed.",
        ),
        (
            pd.Series([2020]),
            str,
            "The internal type <class 'str'> is not yet supported.",
        ),
    ],
)
def test_fail_if_cannot_be_converted_to_internal_type(
    input_data, expected_type, error_match
):
    with pytest.raises(ValueError, match=error_match):
        convert_series_to_internal_type(input_data, expected_type)


@pytest.mark.parametrize(
    "data, functions_overridden",
    [
        (
            pd.DataFrame({"bg_id": [1, 2, 3]}),
            {"bg_id": bg_id_numpy},
        ),
        (
            pd.DataFrame({"wthh_id": [1, 2, 3]}),
            {"wthh_id": wthh_id_numpy},
        ),
    ],
)
def test_provide_endogenous_groupings(data, functions_overridden):
    """Test whether GETTSIM handles user-provided grouping IDs, which would otherwise be
    set endogenously."""
    _convert_data_to_correct_types(data, functions_overridden)


@pytest.mark.parametrize(
    "data, functions_overridden, error_match",
    [
        (
            pd.DataFrame({"hh_id": [1, 1.1, 2]}),
            {},
            "The data types of the following columns are invalid: \n"
            "\n - hh_id: Conversion from input type float64 to int failed."
            " This conversion is only supported if all decimal places of input"
            " data are equal to 0.",
        ),
        (
            pd.DataFrame({"wohnort_ost": [1.1, 0.0, 1.0]}),
            {},
            "The data types of the following columns are invalid: \n"
            "\n - wohnort_ost: Conversion from input type float64 to bool failed."
            " This conversion is only supported if input data exclusively contains"
            " the values 1.0 and 0.0.",
        ),
        (
            pd.DataFrame({"wohnort_ost": [2, 0, 1], "hh_id": [1.0, 2.0, 3.0]}),
            {},
            "The data types of the following columns are invalid: \n"
            "\n - wohnort_ost: Conversion from input type int64 to bool failed."
            " This conversion is only supported if input data exclusively contains"
            " the values 1 and 0.",
        ),
        (
            pd.DataFrame({"wohnort_ost": ["True", "False"]}),
            {},
            "The data types of the following columns are invalid: \n"
            "\n - wohnort_ost: Conversion from input type object to bool failed."
            " Object type is not supported as input.",
        ),
        (
            pd.DataFrame({"hh_id": [1, "1", 2], "bruttolohn_m": ["2000", 3000, 4000]}),
            {},
            "The data types of the following columns are invalid: \n"
            "\n - hh_id: Conversion from input type object to int failed. "
            "Object type is not supported as input."
            "\n - bruttolohn_m: Conversion from input type object to float failed."
            " Object type is not supported as input.",
        ),
    ],
)
def test_fail_if_cannot_be_converted_to_correct_type(
    data, functions_overridden, error_match
):
    with pytest.raises(ValueError, match=error_match):
        _convert_data_to_correct_types(data, functions_overridden)
