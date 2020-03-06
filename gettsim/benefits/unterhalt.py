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
    tax_unit["unterhalt_vors_m"] = 0
    # Amounts depend on age
    tax_unit.loc[
        (tax_unit["alter"] < 6) & tax_unit["alleinerziehend"], "unterhalt_vors_m"
    ] = (params["uhv6_amount"] - kindergeld_params["kgeld1"])
    tax_unit.loc[
        (tax_unit["alter"] >= 6)
        & (tax_unit["alter"] < 12)
        & tax_unit["alleinerziehend"],
        "unterhalt_vors_m",
    ] = (params["uhv12_amount"] - kindergeld_params["kgeld1"])
    # Older kids get it only if the parent has income > 600€
    uhv_inc_tu = (
        tax_unit[
            [
                "lohn_m",
                "sonstig_eink_m",
                "eink_selbstst_m",
                "vermiet_eink_m",
                "kapital_eink_m",
                "rente_m",
                "arbeitsl_geld_m",
            ]
        ]
        .sum()
        .sum()
    )
    tax_unit.loc[
        (tax_unit["alter"] >= 12)
        & (tax_unit["alter"] < 18)
        & (tax_unit["alleinerziehend"])
        & (uhv_inc_tu > params["uhv17_inc"]),
        "unterhalt_vors_m",
    ] = (params["uhv17_amount"] - kindergeld_params["kgeld1"])

    # round up
    tax_unit["unterhalt_vors_m"] = np.ceil(tax_unit["unterhalt_vors_m"]).astype(int)

    # TODO: Check against actual transfers
    return tax_unit


def uhv_pre_07_2017(tax_unit, params, kindergeld_params):
    """
    UHV before 07/2017. Not implemented yet, as it was only paid for 6 years.
    """
    tax_unit["unterhalt_vors_m"] = 0
    return tax_unit
