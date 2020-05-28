import numpy as np
import pandas as pd


def try_to_pandas(func):
    """Try to convert the output of the function to a :class:`pandas.Series`.

    This decorator can be used to wrap functions vectorized with :func:`numpy_vectorize`
    to ensure that the output is a :class:`pandas.Series` if the input was a series.

    It is assumed that the potential series or array is the first positional argument.

    """

    def wrapper(x, *args, **kwargs):
        index = x.index if isinstance(x, pd.Series) else None
        out = func(x, *args, **kwargs)
        out = pd.Series(index=index, data=out) if index is not None else out

        return out

    return wrapper


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
