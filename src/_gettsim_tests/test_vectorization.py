import datetime
import inspect
import string

import numpy
import pytest
from optree import tree_flatten

from _gettsim.config import USE_JAX

if USE_JAX:
    import jax.numpy
from numpy.testing import assert_array_equal

from _gettsim.functions.loader import load_functions_tree_for_date
from _gettsim.transfers.elterngeld import (
    elterngeld__grundsätzlich_anspruchsberechtigt,
)
from _gettsim.transfers.elterngeld.geschwisterbonus import (
    elterngeld__geschwisterbonus_m,
)
from _gettsim.transfers.grundrente import (
    rente__grundrente__durchschnittliche_entgeltpunkte,
)
from _gettsim.vectorization import (
    TranslateToVectorizableError,
    make_vectorizable,
    make_vectorizable_source,
)

# ======================================================================================
# Backend
# ======================================================================================

backends = ["jax", "numpy"] if USE_JAX else ["numpy"]

modules = {"numpy": numpy}
if USE_JAX:
    modules["jax"] = jax.numpy

# ======================================================================================
# String comparison
# ======================================================================================


def string_equal(s1, s2):
    remove = string.punctuation + string.whitespace
    mapping = {ord(c): None for c in remove}
    return s1.translate(mapping) == s2.translate(mapping)


def test_compare_str():
    assert string_equal("This ! is a     test.", "This is a test")
    assert not string_equal("This is a test", "This is not a test")


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
    out = numpy.where(numpy.logical_and(flag, numpy.logical_not(another_flag)), 1, 0)
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
    flag = numpy.logical_and(x < 0, x > -1)
    another_flag = numpy.logical_or(x < 0, x > -1)
    return numpy.logical_and(flag, numpy.logical_not(another_flag))


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


def f13(x):
    a = x < 0
    b = x > 0
    c = x != 0
    d = True
    return ((a and b) or c) and d


def f13_exp(x):
    a = x < 0
    b = x > 0
    c = x != 0
    d = True
    return numpy.logical_and(numpy.logical_or(numpy.logical_and(a, b), c), d)


def f14(x):
    a = x < 0
    b = x > 0
    c = x != 0
    d = True
    return a and b and c or d


def f14_exp(x):
    a = x < 0
    b = x > 0
    c = x != 0
    d = True
    return numpy.logical_or(numpy.logical_and(numpy.logical_and(a, b), c), d)


def f15(x):
    return min(x, 0)


def f15_exp(x):
    return numpy.minimum(x, 0)


def f16(x):
    n = int(sum(x))
    return max(n)


def f16_exp(x):
    n = int(numpy.sum(x))
    return numpy.max(n)


def f17(x):
    a = x < 0
    b = x // 2
    return any((a, b))


def f17_exp(x):
    a = x < 0
    b = x // 2
    return numpy.any((a, b))


def f18(x):
    n = int(any(x)) + 1
    return sum(n)


def f18_exp(x):
    n = int(numpy.any(x)) + 1
    return numpy.sum(n)


x = numpy.arange(-10, 10)
rng = numpy.random.default_rng(seed=0)
flag = rng.binomial(1, 0.25, size=100)
another_flag = rng.binomial(1, 0.75, size=100)


TEST_CASES = [
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
    (f13, f13_exp, (x,)),
    (f14, f14_exp, (x,)),
    (f15, f15_exp, (x,)),
    (f16, f16_exp, (x,)),
    (f17, f17_exp, (x,)),
    (f18, f18_exp, (x,)),
]


# ======================================================================================
# Tests (no error)
# ======================================================================================


@pytest.mark.parametrize("func, expected, args", TEST_CASES)
def test_change_if_to_where_source(func, expected, args):  # noqa: ARG001
    exp = inspect.getsource(expected)
    exp = exp.replace("_exp", "")
    got = make_vectorizable_source(func, backend="numpy")
    assert string_equal(exp, got)


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


def g4(x):
    # max with three arguments
    return max(x, 0, 1)


def test_notimplemented_error():
    with pytest.raises(NotImplementedError):
        make_vectorizable(f1, backend="dask")


@pytest.mark.parametrize("func", [g1, g2, g3, g4])
def test_unallowed_operation_source(func):
    with pytest.raises(TranslateToVectorizableError):
        make_vectorizable_source(func, backend="numpy")


@pytest.mark.parametrize("func", [g1, g2, g3, g4])
def test_unallowed_operation_wrapper(func):
    with pytest.raises(TranslateToVectorizableError):
        make_vectorizable(func, backend="numpy")


# ======================================================================================
# Test that functions defined in gettsim can be made vectorizable
# ======================================================================================


for year in range(1990, 2023):

    @pytest.mark.parametrize(
        "func",
        [
            pf.function
            for pf in tree_flatten(
                load_functions_tree_for_date(datetime.date(year=year, month=1, day=1))
            )[0]
        ],
    )
    @pytest.mark.parametrize("backend", backends)
    def test_convertible(func, backend):
        make_vectorizable(func, backend=backend)


# ======================================================================================
# Test that vectorized functions defined in gettsim can be called with array input
# ======================================================================================


@pytest.mark.parametrize("backend", backends)
def test_transfers__elterngeld__elterngeld__geschwisterbonus_m(backend):
    full = modules.get(backend).full

    # Test original gettsim function on scalar input
    # ==================================================================================
    elterngeld__basisbetrag_m = 3.0
    elterngeld__geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg = True
    elterngeld_params = {
        "geschwisterbonus_aufschlag": 1.0,
        "geschwisterbonus_minimum": 2.0,
    }

    exp = elterngeld__geschwisterbonus_m(
        elterngeld__basisbetrag_m=elterngeld__basisbetrag_m,
        elterngeld__geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg=elterngeld__geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg,
        elterngeld_params=elterngeld_params,
    )
    assert exp == 3.0

    # Create array inputs and assert that gettsim functions raises error
    # ==================================================================================
    shape = (10, 2)
    elterngeld__basisbetrag_m = full(shape, elterngeld__basisbetrag_m)
    elterngeld__geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg = full(
        shape, elterngeld__geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg
    )

    with pytest.raises(ValueError, match="truth value of an array with more than"):
        elterngeld__geschwisterbonus_m(
            elterngeld__basisbetrag_m=elterngeld__basisbetrag_m,
            elterngeld__geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg=elterngeld__geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg,
            elterngeld_params=elterngeld_params,
        )

    # Call converted function on array input and test result
    # ==================================================================================
    converted = make_vectorizable(elterngeld__geschwisterbonus_m, backend=backend)
    got = converted(
        elterngeld__basisbetrag_m=elterngeld__basisbetrag_m,
        elterngeld__geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg=elterngeld__geschwisterbonus_grundsätzlich_anspruchsberechtigt_fg,
        elterngeld_params=elterngeld_params,
    )
    assert_array_equal(got, full(shape, exp))


@pytest.mark.parametrize("backend", backends)
def test_transfers__grundrente__rente__grundrente__durchschnittliche_entgeltpunkte(
    backend,
):
    full = modules.get(backend).full

    # Test original gettsim function on scalar input
    # ==================================================================================
    grundr_entgeltp = 1.0
    grundr_bew_zeiten = 2

    exp = rente__grundrente__durchschnittliche_entgeltpunkte(
        grundr_entgeltp, grundr_bew_zeiten
    )
    assert exp == 0.5

    # Create array inputs and assert that gettsim functions raises error
    # ==================================================================================
    shape = (10, 2)
    grundr_entgeltp = full(shape, grundr_entgeltp)
    grundr_bew_zeiten = full(shape, grundr_bew_zeiten)

    with pytest.raises(ValueError, match="truth value of an array with more than"):
        rente__grundrente__durchschnittliche_entgeltpunkte(
            grundr_entgeltp, grundr_bew_zeiten
        )

    # Call converted function on array input and test result
    # ==================================================================================
    converted = make_vectorizable(
        rente__grundrente__durchschnittliche_entgeltpunkte, backend=backend
    )
    got = converted(grundr_entgeltp, grundr_bew_zeiten)
    assert_array_equal(got, full(shape, exp))


@pytest.mark.parametrize("backend", backends)
def test_transfers__elterngeld__grundsätzlich_anspruchsberechtigt(backend):
    full = modules.get(backend).full

    # Test original gettsim function on scalar input
    # ==================================================================================
    elterngeld_claimed = True
    arbeitsstunden_w = 20.0
    elterngeld__kind_grundsätzlich_anspruchsberechtigt_fg = True
    elterngeld__einkommen_vorjahr_unter_bezugsgrenze = True
    elterngeld__bezugsmonate_unter_grenze_fg = True
    elterngeld_params = {
        "max_arbeitsstunden_w": 31.0,
    }

    exp = elterngeld__grundsätzlich_anspruchsberechtigt(
        elterngeld_claimed=elterngeld_claimed,
        arbeitsstunden_w=arbeitsstunden_w,
        elterngeld__kind_grundsätzlich_anspruchsberechtigt_fg=elterngeld__kind_grundsätzlich_anspruchsberechtigt_fg,
        elterngeld__einkommen_vorjahr_unter_bezugsgrenze=elterngeld__einkommen_vorjahr_unter_bezugsgrenze,
        elterngeld__bezugsmonate_unter_grenze_fg=elterngeld__bezugsmonate_unter_grenze_fg,
        elterngeld_params=elterngeld_params,
    )

    assert exp is True

    # Create array inputs and assert that gettsim functions raises error
    # ==================================================================================
    shape = (10, 1)
    arbeitsstunden_w = full(shape, arbeitsstunden_w)

    with pytest.raises(ValueError, match="truth value of an array with more than"):
        exp = elterngeld__grundsätzlich_anspruchsberechtigt(
            arbeitsstunden_w=arbeitsstunden_w,
            elterngeld_claimed=elterngeld_claimed,
            elterngeld__kind_grundsätzlich_anspruchsberechtigt_fg=elterngeld__kind_grundsätzlich_anspruchsberechtigt_fg,
            elterngeld__einkommen_vorjahr_unter_bezugsgrenze=elterngeld__einkommen_vorjahr_unter_bezugsgrenze,
            elterngeld__bezugsmonate_unter_grenze_fg=elterngeld__bezugsmonate_unter_grenze_fg,
            elterngeld_params=elterngeld_params,
        )

    # Call converted function on array input and test result
    # ==================================================================================
    converted = make_vectorizable(
        elterngeld__grundsätzlich_anspruchsberechtigt, backend=backend
    )
    got = converted(
        elterngeld_claimed=elterngeld_claimed,
        arbeitsstunden_w=arbeitsstunden_w,
        elterngeld__kind_grundsätzlich_anspruchsberechtigt_fg=elterngeld__kind_grundsätzlich_anspruchsberechtigt_fg,
        elterngeld__einkommen_vorjahr_unter_bezugsgrenze=elterngeld__einkommen_vorjahr_unter_bezugsgrenze,
        elterngeld__bezugsmonate_unter_grenze_fg=elterngeld__bezugsmonate_unter_grenze_fg,
        elterngeld_params=elterngeld_params,
    )
    assert_array_equal(got, full(shape, exp))
