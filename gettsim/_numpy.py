import numpy as np


def numpy_vectorize(
    func=None, *, otypes=None, doc=None, excluded=None, cache=False, signature=None
):
    """Vectorize a function with :func:`numpy.vectorize`.
    This decorator exposes :func:`numpy.vectorize` completely with all keyword arguments
    which is not possible with the generic function.
    """

    def decorator_numpy_vectorize(func):
        def wrapper_numpy_vectorize(*args, **kwargs):
            return np.vectorize(
                func,
                otypes=otypes,
                doc=doc,
                excluded=excluded,
                cache=cache,
                signature=signature,
            )(*args, **kwargs)

        return wrapper_numpy_vectorize

    if callable(func):
        out = decorator_numpy_vectorize(func)
    else:
        out = decorator_numpy_vectorize

    return out
