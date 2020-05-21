import datetime

import numpy as np


def uhv(tax_unit, params, kindergeld_params):
    """
    Advance on Alimony Payment / Unterhaltsvorschuss (UHV)

    Single Parents get alimony payments for themselves and for their
    child from the ex partner. If the ex partner is not able to pay the child
    alimony, the government pays the child alimony to the mother (or the father, if
    he has the kids)

    The amount is specified in §1612a BGB and, ultimately, in
    Mindesunterhaltsverordnung.

    returns:
    tax_unit: Updated DataFrame including uhv
    """

    # UHV before 07/2017. Not implemented yet, as it was only paid for 6 years. So we
    # return nans
    if params["datum"] < datetime.date(2017, 7, 1):
        return tax_unit

    # Benefit amount depends on the tax allowance for children ("sächliches
    # Existenzminimum") and the child benefit for the first child.
    tax_unit["unterhaltsvors_m"] = 0
    # Amounts depend on age
    tax_unit.loc[
        (tax_unit["alter"] < 6) & tax_unit["alleinerziehend"], "unterhaltsvors_m"
    ] = (params["mindestunterhalt"][6] - kindergeld_params["kindergeld"][1])
    tax_unit.loc[
        (tax_unit["alter"] >= 6)
        & (tax_unit["alter"] < 12)
        & tax_unit["alleinerziehend"],
        "unterhaltsvors_m",
    ] = (params["mindestunterhalt"][12] - kindergeld_params["kindergeld"][1])
    # Older kids get it only if the parent has income > 600€
    uhv_inc_tu = (
        tax_unit[
            [
                "bruttolohn_m",
                "sonstig_eink_m",
                "eink_selbstst_m",
                "vermiet_eink_m",
                "kapital_eink_m",
                "ges_rente_m",
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
        & (uhv_inc_tu > params["unterhaltsvorschuss_mindesteinkommen"]),
        "unterhaltsvors_m",
    ] = (params["mindestunterhalt"][17] - kindergeld_params["kindergeld"][1])

    # round up
    tax_unit["unterhaltsvors_m"] = np.ceil(tax_unit["unterhaltsvors_m"]).astype(int)

    # TODO: Check against actual transfers
    return tax_unit
