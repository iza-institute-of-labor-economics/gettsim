import pandas as pd


def uprate(df, dy, ty, path):
    """Uprating monetary values to account for difference between
    data year and simulation year.

    not sure whether we need this

    """

    # define all monetary variables
    # get uprate matrix ,as np.array
    upr = pd.read_excel(path + "/data/params/uprate_cpi.xls", index_col="ausgang")
    factor = upr.loc[dy]["y" + str(ty)]
    print(
        "Uprating monetary variables from year "
        + str(dy)
        + " to "
        + str(ty)
        + " with factor "
        + str(factor)
    )
    money_vars = [
        "k_inco",
        "m_pensions",
        "m_transfers",
        "childinc",
        "m_kapinc",
        "m_vermiet",
        "m_imputedrent",
        "versbez",
        "m_wage",
        "othwage_ly",
        "h_wage",
        "kaltmiete",
        "heizkost",
        "kapdienst",
        "miete",
    ]

    for v in money_vars:
        df[v] = factor * df[v]

    return df
