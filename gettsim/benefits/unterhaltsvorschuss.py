import numpy as np


def uhv(tax_unit, params, kindergeld_params):
    """
    Since 2017, the receipt of this
    UHV has been extended substantially and needs to be taken into account, since it's
    dominant to other transfers, i.e. single parents 'have to' apply for it.

    returns:
    tax_unit: Updated DataFrame including uhv
    """
    if params["year"] >= 2017:
        return uhv_since_2017(tax_unit, params, kindergeld_params)
    else:
        tax_unit["uhv"] = 0
        return tax_unit


def uhv_since_2017(tax_unit, params, kindergeld_params):
    """ Advanced Alimony Payment / Unterhaltsvorschuss (UHV)

        In Germany, Single Parents get alimony payments for themselves and for their
        child from the ex partner. If the ex partner is not able to pay the child
        alimony, the government pays the child alimony to the mother (or the father, if
        he has the kids)

        The amount is specified in §1612a BGB
        returns:
            tax_unit: Updated DataFrame including uhv
        """
    # Benefit amount depends on the tax allowance for children ("sächliches Existenzminimum")
    # and the child benefit for the first child.
    tax_unit["uhv"] = 0
    # Amounts depend on age
    tax_unit.loc[tax_unit["age"].between(0, 6) & tax_unit["alleinerz"], "uhv"] = (
        params["uhv6_amount"] - kindergeld_params["kgeld1"]
    )
    tax_unit.loc[tax_unit["age"].between(7, 12) & tax_unit["alleinerz"], "uhv"] = (
        params["uhv12_amount"] - kindergeld_params["kgeld1"]
    )

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
        (tax_unit["age"].between(13, 17))
        & (tax_unit["alleinerz"])
        & (uhv_inc_tu > 600),
        "uhv",
    ] = (params["uhv17_amount"] - kindergeld_params["kgeld1"])

    # round up
    tax_unit["uhv"] = np.ceil(tax_unit["uhv"]).astype(int)

    # TODO: Check against actual transfers
    return tax_unit
