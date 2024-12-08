"""Test namespace."""


def f(a, b):
    return a + b


def g(module1__f, c):
    return module1__f + c


FUNCTIONS_MODULE2 = {
    "module2": {
        "f": f,
        "g": g,
    }
}
