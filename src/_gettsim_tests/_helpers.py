from datetime import datetime
from functools import lru_cache
from typing import Union

from _gettsim.policy_environment import set_up_policy_environment


@lru_cache(maxsize=100)
def cached_set_up_policy_environment(date: Union[int, str, datetime.date]) -> tuple[dict, dict]:
    return set_up_policy_environment(date)
