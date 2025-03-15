"""Test namespace."""

from _gettsim.function_types import policy_function


@policy_function()
def f(h: int, module1_params: dict[str, int]) -> int:  # noqa: ARG001
    return module1_params["a"] + module1_params["b"]


@policy_function()
def g(f: int, module1_params: dict[str, int]) -> int:
    return f + module1_params["c"]


@policy_function()
def h() -> int:
    return 1


@policy_function()
def some_unused_function(some_unused_param: int) -> int:
    return some_unused_param


FUNCTIONS_MODULE1 = {
    "module1": {
        "f": f,
        "g": g,
        "h": h,
        "some_unused_function": some_unused_function,
    }
}
