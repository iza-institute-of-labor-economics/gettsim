import pandas as pd
from bld.project_paths import project_paths_join as ppj


def load_input(year, file_name, columns, *pd_args, **pd_kwargs):
    df = pd.read_excel(ppj("TESTS_TAX_TRANSFERS", file_name), *pd_args, **pd_kwargs)
    df = df[df["year"] == year]
    df = df[columns]
    return df


def load_tb(year):
    df = pd.read_excel(ppj("IN_DATA", "param.xls")).set_index("para")
    return df["y{}".format(year)].to_dict()


def load_output(year, file_name, column):
    df = pd.read_excel(ppj("TESTS_TAX_TRANSFERS", file_name))
    df = df[df["year"] == year]
    return df[column]
