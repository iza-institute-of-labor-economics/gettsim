import importlib

from _gettsim.config import set_array_backend


def pytest_sessionstart(session):  # noqa: U100
    is_jax_installed = importlib.util.find_spec("jax") is not None
    backend = "jax" if is_jax_installed else "numpy"
    set_array_backend(backend)
