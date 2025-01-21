import pytest

import _gettsim


def test_conftest_set_array_backend_updates_use_jax(request):
    expected = request.config.option.USE_JAX
    from _gettsim.config import USE_JAX

    assert expected == USE_JAX


def test_conftest_set_array_backend_updates_backend(request):
    use_jax = request.config.option.USE_JAX
    expected = "jax.numpy" if use_jax else "numpy"
    from _gettsim.config import numpy_or_jax

    got = numpy_or_jax.__name__
    assert expected == got


@pytest.mark.parametrize("backend", ["dask", "jax.numpy"])
def test_wrong_backend(backend):
    with pytest.raises(ValueError):
        _gettsim.config.set_array_backend(backend)
