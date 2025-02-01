import pytest

from _gettsim.functions.policy_function import PolicyFunction, policy_function


@policy_function()
def simple_policy_function(x):
    return x


@policy_function(leaf_name="simple_policy_function")
def policy_function_with_internal_name(x):
    return x


@pytest.mark.parametrize(
    "function",
    [
        simple_policy_function,
        policy_function_with_internal_name,
    ],
)
def test_function_type(function):
    assert isinstance(function, PolicyFunction)


@pytest.mark.parametrize(
    "function",
    [
        simple_policy_function,
        policy_function_with_internal_name,
    ],
)
def test_function_name(function):
    assert function.leaf_name == "simple_policy_function"


def test_set_qualified_name():
    function = simple_policy_function
    leaf_name = function.leaf_name
    function.set_qualified_name(f"module__{leaf_name}")
    assert function.qualified_name == f"module__{leaf_name}"
