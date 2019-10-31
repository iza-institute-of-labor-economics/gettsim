import datetime

import pandas as pd
import yaml
from pandas_ods_reader import read_ods

from gettsim.config import ROOT_DIR


def load_test_data(year, file_name, columns, *pd_args, **pd_kwargs):
    """ Loads test data from csv, Excel ('xls', 'xlsx') or Open Office Sheets ('ods').
        With OpenOffice Sheets, Boolean Variables are not correctly imported.
    """
    bool_cols = [
        "child",
        "zveranl",
        "ineducation",
        "head",
        "head_tu",
        "eigentum",
        "alleinerz",
        "east",
        "pensioner",
        "selfemployed",
        "haskids",
        "pkv",
    ]
    if file_name.endswith("csv"):
        df = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    if file_name.endswith("xls") or file_name.endswith("xlsx"):
        df = pd.read_excel(
            ROOT_DIR / "tests" / "test_data" / file_name, *pd_args, **pd_kwargs
        )
    if file_name.endswith("ods"):
        # always load the first sheet
        df = read_ods(ROOT_DIR / "tests" / "test_data" / file_name, 1)
        for col in bool_cols:
            if col in df.columns:
                df[col] = df[col].astype(bool)

    df = df.loc[df["year"].eq(year), columns].copy()

    return df


def load_tb(year, month=1, day=1):
    tb_pre = yaml.safe_load(open(f"{ROOT_DIR}/data/param.yaml", "rb"))
    tb = {}
    this_year = datetime.date(year=year, month=month, day=day)
    for key in tb_pre.keys():
        if tb_pre[key]["values"] is not None:
            policy_dates = list(tb_pre[key]["values"].keys())
            past_policies = [x for x in policy_dates if x <= this_year]
            if not past_policies:
                pass
            else:
                policy_in_place = max(past_policies)
                tb[key] = tb_pre[key]["values"][policy_in_place]["value"]
    return tb
