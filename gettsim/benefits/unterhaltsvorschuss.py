import numpy as np


def uhv(tax_unit, params, kindergeld_params, e_st_abz_params):
    """
    Since 2017, the receipt of this
    UHV has been extended substantially and needs to be taken into account, since it's
    dominant to other transfers, i.e. single parents 'have to' apply for it.

    returns:
    tax_unit: Updated DataFrame including uhv
    """
    if params["year"] >= 2017:
        return uhv_since_2017(tax_unit, params, kindergeld_params, e_st_abz_params)
    else:
        tax_unit["uhv"] = 0
        return tax_unit


def uhv_since_2017(tax_unit, params, kindergeld_params, e_st_abz_params):
    """ Advanced Alimony Payment / Unterhaltsvorschuss (UHV)

        In Germany, Single Parents get alimony payments for themselves and for their
        child from the ex partner. If the ex partner is not able to pay the child
        alimony, the government pays the child alimony to the mother (or the father, if
        he has the kids)


        returns:
            tax_unit: Updated DataFrame including uhv
        """
    # Benefit amount depends on the tax allowance for children ("sächliches Existenzminimum")
    # and the child benefit for the first child.
    print(params["uhv5"])
    print(e_st_abz_params["kifreib_s"])
    print(kindergeld_params["kgeld1"])
    tax_unit["uhv"] = 0
    # Amounts depend on age
    tax_unit.loc[tax_unit["age"].between(0, 5) & tax_unit["alleinerz"], "uhv"] = (
        params["uhv5"] * e_st_abz_params["kifreib_s"] / 12 - kindergeld_params["kgeld1"]
    )
    tax_unit.loc[tax_unit["age"].between(6, 11) & tax_unit["alleinerz"], "uhv"] = (
        params["uhv11"] * e_st_abz_params["kifreib_s"] / 12
        - kindergeld_params["kgeld1"]
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
        (tax_unit["age"].between(12, 17))
        & (tax_unit["alleinerz"])
        & (uhv_inc_tu > 600),
        "uhv",
    ] = (
        params["uhv17"] * e_st_abz_params["kifreib_s"] / 12
        - kindergeld_params["kgeld1"]
    )

    # round up
    tax_unit["uhv"] = np.ceil(tax_unit["uhv"]).astype(int)

    # TODO: Check against actual transfers
    return tax_unit
