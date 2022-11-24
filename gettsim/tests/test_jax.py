import inspect

import jax.numpy
import numpy
import pytest
from numpy.testing import assert_array_equal

from gettsim.config import PATHS_TO_INTERNAL_FUNCTIONS
from gettsim.functions_loader import _load_functions
from gettsim.jax import make_vectorizable
from gettsim.jax import make_vectorizable_source
from gettsim.jax import TranslateToVectorizableError
from gettsim.transfers.elterngeld import elterngeld_geschw_bonus_m
from gettsim.transfers.grundrente import grundr_bew_zeiten_avg_entgeltp

# ======================================================================================
# Test functions (no error)
# ======================================================================================


def f1(x):
    if x < 0:
        return 0
    else:
        return 1


def f1_exp(x):
    return numpy.where(x < 0, 0, 1)


def f2(x):
    if x < 0:
        out = 0
    else:
        out = 1
    return out


def f2_exp(x):
    out = numpy.where(x < 0, 0, 1)
    return out


def f3(x):
    return 0 if x < 0 else 1


def f3_exp(x):
    return numpy.where(x < 0, 0, 1)


def f4(x):
    out = 1
    if x < 0:
        out = 0
    return out


def f4_exp(x):
    out = 1
    out = numpy.where(x < 0, 0, out)
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
    out = numpy.where(x < 0, -1, numpy.where(x > 0, 1, 0))
    return out


def f6(flag, another_flag):
    if flag and not another_flag:
        out = 1
    else:
        out = 0
    return out


def f6_exp(flag, another_flag):
    out = numpy.where(flag & ~another_flag, 1, 0)
    return out


def f7(x):
    out = 0 if x < 0 else 1
    return out


def f7_exp(x):
    out = numpy.where(x < 0, 0, 1)
    return out


def f8(x):
    return -1 if x < 0 else (1 if x > 0 else 0)


def f8_exp(x):
    return numpy.where(x < 0, -1, numpy.where(x > 0, 1, 0))


# expect no change since there is no if-clause and no [and|or] statement.
def f9(x):
    y = numpy.sum(x)
    z = numpy.prod(x)
    return y * z


def f10(x):
    flag = (x < 0) and (x > -1)
    another_flag = (x < 0) or (x > -1)
    return flag and not another_flag


def f10_exp(x):
    flag = (x < 0) & (x > -1)
    another_flag = (x < 0) | (x > -1)
    return flag & ~another_flag


def f11(x):
    if x < 0:
        out = -1
    else:
        out = 1 if x > 0 else 0
    return out


def f11_exp(x):
    out = numpy.where(x < 0, -1, numpy.where(x > 0, 1, 0))
    return out


def f12(x):
    out = 0
    if x < 1:
        out += 1
    return out


def f12_exp(x):
    out = 0
    out += numpy.where(x < 1, 1, out)
    return out


x = numpy.arange(-10, 10)
rng = numpy.random.default_rng(seed=0)
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
    (f7, f7_exp, (x,)),
    (f8, f8_exp, (x,)),
    (f9, f9, (x,)),
    (f10, f10_exp, (x,)),
    (f11, f11_exp, (x,)),
    (f12, f12_exp, (x,)),
]


# ======================================================================================
# Tests (no error)
# ======================================================================================


@pytest.mark.parametrize("func, expected, args", TEST_CASES)
def test_change_if_to_where_source(func, expected, args):  # noqa: U100
    exp = inspect.getsource(expected)
    exp = exp.replace("_exp", "")
    got = make_vectorizable_source(func, backend="numpy")
    assert exp == got


@pytest.mark.parametrize("func, expected, args", TEST_CASES)
def test_change_if_to_where_wrapper(func, expected, args):
    got_func = make_vectorizable(func, backend="numpy")
    got = got_func(*args)
    exp = expected(*args)
    assert_array_equal(got, exp)


# ======================================================================================
# Test correct error raising
# ======================================================================================


def g1(x):
    # function with multiple operations in the if-clause
    a = 0
    b = 1
    if x < 0:
        a = 1
        b = 0
    return a + b


def test_too_many_operations_error_source():
    with pytest.raises(TranslateToVectorizableError):
        make_vectorizable_source(g1, backend="numpy")


def test_too_many_operations_error_wrapper():
    with pytest.raises(TranslateToVectorizableError):
        make_vectorizable(g1, backend="numpy")


def test_notimplemented_error():
    with pytest.raises(NotImplementedError):
        make_vectorizable(f1, backend="dask")


def g2(x):
    # function with illegal operations in the if-clause
    if x < 0:
        print(x)  # noqa: T201
    else:
        print(not x)  # noqa: T201


def g3(x):
    # return statement in if-body but no else clause
    if x < 0:
        return 0
    return 1


@pytest.mark.parametrize("func", [g2, g3])
def test_unallowed_operation_source(func):
    with pytest.raises(TranslateToVectorizableError):
        make_vectorizable_source(func, backend="numpy")


@pytest.mark.parametrize("func", [g2, g3])
def test_unallowed_operation_wrapper(func):
    with pytest.raises(TranslateToVectorizableError):
        make_vectorizable(func, backend="numpy")


# ======================================================================================
# Test that functions defined in gettsim can be made vectorizable
# ======================================================================================


gettsim_functions = _load_functions(sources=PATHS_TO_INTERNAL_FUNCTIONS)


@pytest.mark.parametrize("func", gettsim_functions.values())
def test_convertable(func):
    make_vectorizable(func, backend="numpy")


# ======================================================================================
# Test that vectorized functions defined in gettsim can be called with array input
# ======================================================================================


@pytest.mark.xfail(reason="max operator is not vectorized.")
@pytest.mark.parametrize("backend", ["numpy", "jax"])
def test_transfers__elterngeld__elterngeld_geschw_bonus_m(backend):

    full = {"numpy": numpy.full, "jax": jax.numpy.full}[backend]

    # Test original gettsim function on scalar input
    # ==================================================================================
    elterngeld_eink_erlass_m = 3.0
    elterngeld_geschw_bonus_anspruch = True
    elterngeld_params = {"geschw_bonus_aufschlag": 1.0, "geschw_bonus_minimum": 2.0}

    exp = elterngeld_geschw_bonus_m(
        elterngeld_eink_erlass_m=elterngeld_eink_erlass_m,
        elterngeld_geschw_bonus_anspruch=elterngeld_geschw_bonus_anspruch,
        elterngeld_params=elterngeld_params,
    )
    assert exp == 3.0

    # Create array inputs and assert that gettsim functions raises error
    # ==================================================================================
    shape = (10, 2)
    elterngeld_eink_erlass_m = full(shape, elterngeld_eink_erlass_m)
    elterngeld_geschw_bonus_anspruch = full(shape, elterngeld_geschw_bonus_anspruch)

    with pytest.raises(ValueError, match="truth value of an array with more than"):
        elterngeld_geschw_bonus_m(
            elterngeld_eink_erlass_m=elterngeld_eink_erlass_m,
            elterngeld_geschw_bonus_anspruch=elterngeld_geschw_bonus_anspruch,
            elterngeld_params=elterngeld_params,
        )

    # Call converted function on array input and test result
    # ==================================================================================
    converted = make_vectorizable(elterngeld_geschw_bonus_m, backend=backend)
    got = converted(
        elterngeld_eink_erlass_m=elterngeld_eink_erlass_m,
        elterngeld_geschw_bonus_anspruch=elterngeld_geschw_bonus_anspruch,
        elterngeld_params=elterngeld_params,
    )
    assert_array_equal(got, full(shape, exp))


@pytest.mark.parametrize("backend", ["numpy", "jax"])
def test_transfers__grundrente__grundr_bew_zeiten_avg_entgeltp(backend):

    full = {"numpy": numpy.full, "jax": jax.numpy.full}[backend]

    # Test original gettsim function on scalar input
    # ==================================================================================
    grundr_entgeltp = 1.0
    grundr_bew_zeiten = 2

    exp = grundr_bew_zeiten_avg_entgeltp(grundr_entgeltp, grundr_bew_zeiten)
    assert exp == 0.5

    # Create array inputs and assert that gettsim functions raises error
    # ==================================================================================
    shape = (10, 2)
    grundr_entgeltp = full(shape, grundr_entgeltp)
    grundr_bew_zeiten = full(shape, grundr_bew_zeiten)

    with pytest.raises(ValueError, match="truth value of an array with more than"):
        grundr_bew_zeiten_avg_entgeltp(grundr_entgeltp, grundr_bew_zeiten)

    # Call converted function on array input and test result
    # ==================================================================================
    converted = make_vectorizable(grundr_bew_zeiten_avg_entgeltp, backend=backend)
    got = converted(grundr_entgeltp, grundr_bew_zeiten)
    assert_array_equal(got, full(shape, exp))
