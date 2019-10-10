import pandas as pd
from pandas_ods_reader import read_ods

from gettsim.config import ROOT_DIR


def load_test_data(year, file_name, columns, *pd_args, **pd_kwargs):
    """ Loads test data from Excel ('xls', 'xlsx') or Open Office Sheets ('ods').
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


def load_tb(year):
    df = pd.read_excel(ROOT_DIR / "data" / "param.xls").set_index("para")
    return df[f"y{year}"].to_dict()
