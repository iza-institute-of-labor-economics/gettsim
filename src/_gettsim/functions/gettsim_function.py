from __future__ import annotations

from abc import ABC
from typing import Callable


class GettsimFunction(Callable, ABC):
    """
    An abstract base class for all callables in the Gettsim framework.
    """
