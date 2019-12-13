import numpy as np


def uhv(tax_unit, params, kindergeld_params):
    """
    Advance on Alimony Payment / Unterhaltsvorschuss (UHV)

    Single Parents get alimony payments for themselves and for their
    child from the ex partner. If the ex partner is not able to pay the child
    alimony, the government pays the child alimony to the mother (or the father, if
    he has the kids)

    The amount is specified in §1612a BGB and, ultimately, in Mindesunterhaltsverordnung.

    returns:
    tax_unit: Updated DataFrame including uhv
    """

    return params["uhv_calc"](tax_unit, params, kindergeld_params)


def uhv_since_07_2017(tax_unit, params, kindergeld_params):
    """ UHV ruling since 07/2017. Before 2017, basically the same, but
        eligibility was more restrictive.

        returns:
            tax_unit: Updated DataFrame including uhv
        """
    # Benefit amount depends on the tax allowance for children ("sächliches Existenzminimum")
    # and the child benefit for the first child.
    tax_unit["uhv"] = 0
    # Amounts depend on age
    tax_unit.loc[(tax_unit["age"] <= 6) & tax_unit["alleinerz"], "uhv"] = (
        params["uhv6_amount"] - kindergeld_params["kgeld1"]
    )
    tax_unit.loc[
        (tax_unit["age"] >= 7) & (tax_unit["age"] <= 12) & tax_unit["alleinerz"], "uhv"
    ] = (params["uhv12_amount"] - kindergeld_params["kgeld1"])
    # Older kids get it only if the parent has income > 600€
    uhv_inc_tu = (
        tax_unit[
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
    tax_unit.loc[
        (tax_unit["age"] >= 13)
        & (tax_unit["age"] <= 17)
        & (tax_unit["alleinerz"])
        & (uhv_inc_tu > params["uhv17_inc"]),
        "uhv",
    ] = (params["uhv17_amount"] - kindergeld_params["kgeld1"])

    # round up
    tax_unit["uhv"] = np.ceil(tax_unit["uhv"]).astype(int)

    # TODO: Check against actual transfers
    return tax_unit


def uhv_pre_07_2017(tax_unit, params, kindergeld_params):
    """
    UHV before 07/2017. Not implemented yet, as it was only paid for 6 years.
    """
    tax_unit["uhv"] = 0
    return tax_unit
