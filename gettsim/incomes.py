import numpy as np


def disposable_income(df):
    df["dpi_ind"] = df[
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
    df["dpi"] = round(
        np.maximum(0, sum(df["dpi_ind"]) + df["m_alg2"] + df["wohngeld"] + df["kiz"]), 2
    )
    return df


def gross_income(df):
    df["gross"] = round(
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
    return df
