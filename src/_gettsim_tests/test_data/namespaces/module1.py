"""Test namespace."""


def f(module1_params, h):  # noqa: ARG001
    return module1_params["a"] + module1_params["b"]


def g(f, module1_params):
    return f + module1_params["c"]


def h():
    return 1


FUNCTIONS_MODULE1 = {
    "module1": {
        "f": f,
        "g": g,
        "h": h,
    }
}
