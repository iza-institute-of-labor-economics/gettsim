"""Test namespace."""


def f(module2_params, g):  # noqa: ARG001
    return module2_params["a"] + module2_params["b"]


def g(module1__f, module2_params):
    return module1__f + module2_params["c"]


FUNCTIONS_MODULE2 = {
    "module2": {
        "f": f,
        "g": g,
    }
}
