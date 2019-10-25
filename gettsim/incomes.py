import numpy as np


def disposable_income(household):
    household["dpi_ind"] = household[
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
    ].sum(axis=1) - household[
        ["incometax", "soli", "abgst", "gkvbeit", "rvbeit", "pvbeit", "avbeit"]
    ].sum(
        axis=1
    )

    # Disposible income on hh level
    household["dpi"] = round(
        np.maximum(
            0,
            sum(household["dpi_ind"])
            + household["m_alg2"]
            + household["wohngeld"]
            + household["kiz"],
        ),
        2,
    )
    return household


def gross_income(household):
    household["gross"] = round(
        household[
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
    return household
