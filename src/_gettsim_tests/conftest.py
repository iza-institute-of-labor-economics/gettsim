from _gettsim.config import IS_JAX_INSTALLED
from _gettsim.config import set_array_backend


def pytest_sessionstart(session):  # noqa: U100
    backend = "jax" if IS_JAX_INSTALLED else "numpy"
    set_array_backend(backend)
