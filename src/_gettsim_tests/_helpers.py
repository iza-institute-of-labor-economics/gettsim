from datetime import datetime
from functools import lru_cache
from typing import Union

from _gettsim.policy_environment import set_up_policy_environment, _parse_date


def cached_set_up_policy_environment(date: Union[int, str, datetime.date]) -> tuple[dict, dict]:
    normalized_date = _parse_date(date)
    return _cached_set_up_policy_environment(normalized_date)


@lru_cache(maxsize=100)
def _cached_set_up_policy_environment(date: datetime.date) -> tuple[dict, dict]:
    return set_up_policy_environment(date)
