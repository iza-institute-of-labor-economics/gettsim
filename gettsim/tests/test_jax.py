import inspect

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from gettsim.jax import change_if_to_where_source
from gettsim.jax import change_if_to_where_wrapper
from gettsim.jax import TranslateToJaxError


# ======================================================================================
# Test functions (no error)
# ======================================================================================


def f1(x):
    if x < 0:
        return 0
    else:
        return 1


def f1_exp(x):
    return np.where(x < 0, 0, 1)


def f2(x):
    if x < 0:
        out = 0
    else:
        out = 1
    return out


def f2_exp(x):
    out = np.where(x < 0, 0, 1)
    return out


def f3(x):
    return 0 if x < 0 else 1


def f3_exp(x):
    return np.where(x < 0, 0, 1)


def f4(x):
    out = 1
    if x < 0:
        out = 0
    return out


def f4_exp(x):
    out = 1
    out = np.where(x < 0, 0, out)
    return out


def f5(x):
    if x < 0:
        out = -1
    elif x > 0:
        out = 1
    else:
        out = 0
    return out


def f5_exp(x):
    out = np.where(x < 0, -1, np.where(x > 0, 1, 0))
    return out


def f6(flag, another_flag):
    if flag and not another_flag:
        out = 1
    else:
        out = 0
    return out


def f6_exp(flag, another_flag):
    out = np.where(flag & ~another_flag, 1, 0)
    return out


x = np.arange(-10, 10)
rng = np.random.default_rng(seed=0)
flag = rng.binomial(1, 0.25, size=100)
another_flag = rng.binomial(1, 0.75, size=100)


TEST_CASES = [
    # (func, expected, args)
    (f1, f1_exp, (x,)),
    (f2, f2_exp, (x,)),
    (f3, f3_exp, (x,)),
    (f4, f4_exp, (x,)),
    (f5, f5_exp, (x,)),
    (f6, f6_exp, (flag, another_flag)),
]


# ======================================================================================
# Tests (no error)
# ======================================================================================


@pytest.mark.parametrize("func, expected, args", TEST_CASES)
def test_change_if_to_where_source(func, expected, args):  # noqa: U100
    exp = inspect.getsource(expected)
    exp = exp.replace("_exp", "")
    got = change_if_to_where_source(func, backend="np")
    assert exp == got


@pytest.mark.parametrize("func, expected, args", TEST_CASES)
def test_change_if_to_where_wrapper(func, expected, args):
    got_func = change_if_to_where_wrapper(func, backend="np")
    got = got_func(*args)
    exp = expected(*args)
    assert_array_equal(got, exp)


# ======================================================================================
# Test correct error raising
# ======================================================================================


def g1(x):
    a = 0
    b = 1
    if x < 0:
        a = 1
        b = 0
    return a + b


def test_multiline_error_source():
    with pytest.raises(TranslateToJaxError):
        change_if_to_where_source(g1)


def test_multiline_error_wrapper():
    with pytest.raises(TranslateToJaxError):
        change_if_to_where_wrapper(g1)
