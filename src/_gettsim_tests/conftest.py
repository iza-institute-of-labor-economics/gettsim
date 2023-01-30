from _gettsim.config import set_array_backend


def pytest_addoption(parser):  # type: ignore[no-untyped-def]
    parser.addoption(
        "--use-jax",
        action="store_true",
        default=False,
        dest="USE_JAX",
        help="Use JAX backend for tests.",
    )


def pytest_sessionstart(session):  # type: ignore[no-untyped-def]
    use_jax = session.config.option.USE_JAX
    backend = "jax" if use_jax else "numpy"
    set_array_backend(backend)
