import pandas as pd

from gettsim.config import ROOT_DIR


def load_test_data(year, file_name, columns, *pd_args, **pd_kwargs):
    if file_name.split(".")[1][:3] == "xls":
        df = pd.read_excel(
            ROOT_DIR / "tests" / "test_data" / file_name, *pd_args, **pd_kwargs
        )
    if file_name.split(".")[1] == "csv":
        df = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    df = df.loc[df["year"].eq(year), columns].copy()

    return df


def load_tb(year):
    df = pd.read_excel(ROOT_DIR / "data" / "param.xls").set_index("para")
    return df[f"y{year}"].to_dict()
