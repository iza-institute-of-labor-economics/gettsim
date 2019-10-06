import pandas as pd


def uhv(df, tb):
    """
    Since 2017, the receipt of this
    UHV has been extended substantially and needs to be taken into account, since it's
    dominant to other transfers, i.e. single parents 'have to' apply for it.
    """
    if tb["yr"] >= 2017:
        return uhv_since_2017(df, tb)
    else:
        return 0


def uhv_since_2017(df, tb):
    """ Advanced Alimony Payment / Unterhaltsvorschuss (UHV)

        In Germany, Single Parents get alimony payments for themselves and for their
        child from the ex partner. If the ex partner is not able to pay the child
        alimony, the government pays the child alimony to the mother (or the father, if
        he has the kids)

        returns:
            uhv (pd.Series): Alimony Payment on individual level
        """
    # Benefit amount depends on parameters M (rent) and Y (income) (§19 WoGG)
    # Calculate them on the level of the tax unit
    uhv_df = pd.DataFrame(index=df.index.copy())

    uhv_df["uhv"] = 0
    # Amounts depend on age
    uhv_df.loc[df["age"].between(0, 5) & df["alleinerz"], "uhv"] = tb["uhv5"]
    uhv_df.loc[df["age"].between(6, 11) & df["alleinerz"], "uhv"] = tb["uhv11"]
    # Older kids get it only if the parent has income > 600€
    uhv_df["uhv_inc_tu"] = (
        df[
            [
                "m_wage",
                "m_transfers",
                "m_self",
                "m_vermiet",
                "m_kapinc",
                "m_pensions",
                "m_alg1",
            ]
        ]
        .sum()
        .sum()
    )
    uhv_df.loc[
        (df["age"].between(12, 17)) & (df["alleinerz"]) & (uhv_df["uhv_inc_tu"] > 600),
        "uhv",
    ] = tb["uhv17"]
    # TODO: Check against actual transfers
    return uhv_df["uhv"]
