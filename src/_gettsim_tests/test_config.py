import importlib

import pytest

import _gettsim


def test_default_backend():
    from _gettsim.config import numpy_or_jax

    assert numpy_or_jax.__name__ == "numpy"


def test_set_backend():
    is_jax_installed = importlib.util.find_spec("jax") is not None

    # expect default backend
    from _gettsim.config import numpy_or_jax

    assert numpy_or_jax.__name__ == "numpy"

    if is_jax_installed:
        # set jax backend
        _gettsim.config.set_array_backend("jax")
        from _gettsim.config import numpy_or_jax

        assert numpy_or_jax.__name__ == "jax.numpy"

        from _gettsim.config import USE_JAX

        assert USE_JAX
    else:
        with pytest.raises(AssertionError):
            _gettsim.config.set_array_backend("jax")


@pytest.mark.parametrize("backend", ["dask", "jax.numpy"])
def test_wrong_backend(backend):
    with pytest.raises(ValueError):
        _gettsim.config.set_array_backend(backend)
