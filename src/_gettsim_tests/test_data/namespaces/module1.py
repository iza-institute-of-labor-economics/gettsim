"""Test namespace."""

from _gettsim.functions.policy_function import policy_function


@policy_function()
def f(module1_params, h):  # noqa: ARG001
    return module1_params["a"] + module1_params["b"]


@policy_function()
def g(f, module1_params):
    return f + module1_params["c"]


@policy_function()
def h():
    return 1


FUNCTIONS_MODULE1 = {
    "module1": {
        "f": f,
        "g": g,
        "h": h,
    }
}
