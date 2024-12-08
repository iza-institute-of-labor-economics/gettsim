"""Test namespace."""


def f(a, b):
    return a + b


def g(f, c):
    return f + c


FUNCTIONS_MODULE1 = {
    "module1": {
        "f": f,
        "g": g,
    }
}
