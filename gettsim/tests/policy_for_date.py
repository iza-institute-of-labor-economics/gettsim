import datetime

import numpy as np


def get_policies_for_date(tb_pre, year, month=1, day=1):
    tb = {}
    this_year = datetime.date(year=year, month=month, day=day)
    for key in tb_pre.keys():
        if tb_pre[key]["values"] is not None:
            policy_dates = list(tb_pre[key]["values"].keys())
            past_policies = [x for x in policy_dates if x <= this_year]
            if not past_policies:
                # TODO: Should there be missing values or should the key not exist?
                tb[key] = np.nan
            else:
                policy_in_place = max(past_policies)
                tb[key] = tb_pre[key]["values"][policy_in_place]["value"]
    return tb
