import pandas as pd
from gettsim.config import ROOT_DIR


def load_input(year, file_name, columns, *pd_args, **pd_kwargs):
    df = pd.read_excel(
        ROOT_DIR / "tests" / "test_data" / file_name, *pd_args, **pd_kwargs
    )
    df = df[df["year"] == year]
    df = df[columns]
    return df


def load_tb(year):
    df = pd.read_excel(ROOT_DIR / "original_data" / "param.xls").set_index("para")
    return df[f"y{year}"].to_dict()


def load_output(year, file_name, column):
    df = pd.read_excel(ROOT_DIR / "tests" / "test_data" / file_name)
    df = df[df["year"] == year]
    return df[column]
