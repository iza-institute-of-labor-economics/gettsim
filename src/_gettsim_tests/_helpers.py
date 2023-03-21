from __future__ import annotations

from functools import lru_cache
from typing import TYPE_CHECKING

from _gettsim.policy_environment import _parse_date, set_up_policy_environment

if TYPE_CHECKING:
    import datetime


def cached_set_up_policy_environment(
    date: int | str | datetime.date
) -> tuple[dict, dict]:
    normalized_date = _parse_date(date)
    return _cached_set_up_policy_environment(normalized_date)


@lru_cache(maxsize=100)
def _cached_set_up_policy_environment(date: datetime.date) -> tuple[dict, dict]:
    return set_up_policy_environment(date)
