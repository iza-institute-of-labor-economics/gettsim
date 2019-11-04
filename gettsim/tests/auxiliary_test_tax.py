import datetime

import numpy as np
import pandas as pd
import yaml

from gettsim.config import ROOT_DIR


def load_test_data(year, file_name, columns, *pd_args, **pd_kwargs):
    """ Loads test data from csv, Excel ('xls', 'xlsx') or Open Office Sheets ('ods').
        With OpenOffice Sheets, Boolean Variables are not correctly imported.
    """

    df = pd.read_csv(f"{ROOT_DIR}/tests/test_data/{file_name}")

    df_out = df.loc[df["year"].eq(year), columns]

    return df_out


def load_tax_benefit_data():
    return yaml.safe_load(open(f"{ROOT_DIR}/data/param.yaml", "rb"))


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
