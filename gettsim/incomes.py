import numpy as np
import pandas as pd

from gettsim.func_out_columns import DPI
from gettsim.func_out_columns import GROSS


def disposable_income(df):
    disp_inc = pd.DataFrame(index=df.index, columns=DPI)
    disp_inc["dpi_ind"] = df[
        [
            "m_wage",
            "m_kapinc",
            "m_self",
            "m_vermiet",
            # "m_imputedrent", We need to discuss this!
            "m_pensions",
            "m_transfers",
            "kindergeld",
            "uhv",
        ]
    ].sum(axis=1) - df[
        ["incometax", "soli", "abgst", "gkvbeit", "rvbeit", "pvbeit", "avbeit"]
    ].sum(
        axis=1
    )

    # Disposible income on hh level
    disp_inc["dpi"] = round(
        np.maximum(
            0, sum(disp_inc["dpi_ind"]) + df["m_alg2"] + df["wohngeld"] + df["kiz"]
        ),
        2,
    )
    return disp_inc


def gross_income(df):
    gross_inc = pd.DataFrame(index=df.index, columns=GROSS)
    gross_inc["gross"] = round(
        df[
            [
                "m_wage",
                "m_kapinc",
                "m_self",
                "m_vermiet",
                "m_imputedrent",
                "m_pensions",
                "m_transfers",
                "kindergeld",
            ]
        ].sum(axis=1),
        2,
    )
    return gross_inc
