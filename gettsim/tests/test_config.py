import pytest

import gettsim


def test_default_backend():
    from gettsim.config import numpy_or_jax

    assert numpy_or_jax.__name__ == "numpy"


def test_set_backend(monkeypatch):
    # act like jax is installed so that tests run on windows
    monkeypatch.setattr(gettsim.config, "IS_JAX_INSTALLED", True)

    # expect default backend
    from gettsim.config import numpy_or_jax

    assert numpy_or_jax.__name__ == "numpy"

    # set jax backend
    gettsim.config.set_array_backend("jax")
    from gettsim.config import numpy_or_jax

    assert numpy_or_jax.__name__ == "jax.numpy"


@pytest.mark.parametrize("backend", ["dask", "jax.numpy"])
def test_wrong_backend(backend):
    with pytest.raises(ValueError):
        gettsim.config.set_array_backend(backend)
