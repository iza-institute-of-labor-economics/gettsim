import numpy as np


def kiz(household, params, arbeitsl_geld_2_params):
    """ Kinderzuschlag / Additional Child Benefit
        The purpose of Kinderzuschlag (Kiz) is to keep families out of ALG2. If they
        would be eligible to ALG2 due to the fact that their claim rises because of
        their children, they can claim Kiz.

        A couple of criteria need to be met.
        1. the household has to have some income
        2. net income minus housing benefit needs has to be lower than
           total ALG2 need plus additional child benefit.
        3. Over a certain income threshold (which depends on housing costs,
           and is therefore household-specific), parental income is deducted from
           child benefit claim.
    """

    """ In contrast to ALG2, Kiz considers only the rental costs that are attributed
        to the parents.
        This is done by some fixed share which is updated on annual basis
        ('jährlicher Existenzminimumsbericht')
    """
    # First, calculate the need similar to ALG2, but only for parents.
    household["kinderzuschlag_eink_regel"] = calc_kiz_ek(
        household, params, arbeitsl_geld_2_params
    )

    # Calculate share of tax unit wrt whole household
    # Add rents. First, correct rent for the case of several tax units within the HH
    tax_unit_share = household.groupby("tu_id")["tu_id"].transform("count") / len(
        household
    )
    household["kinderzuschlag_kaltmiete_m"] = household["kaltmiete_m"] * tax_unit_share
    household["kinderzuschlag_heizkost_m"] = household["heizkost_m"] * tax_unit_share
    # The actual living need is again broken down to the parents.
    wb = params["wohnbedarf_eltern_anteil"]
    household["wohnbedarf_eltern_anteil"] = 1.0
    for ad in [1, 2]:
        for ki in [1, 2, 3, 4]:
            household.loc[
                (household["anz_kinder_tu"] == ki) & (household["anz_erw_tu"] == ad),
                "wohnbedarf_eltern_anteil",
            ] = wb[ad][ki - 1]
        # if more than 4 children
        household.loc[
            (household["anz_kinder_tu"] >= 5) & (household["anz_erw_tu"] == ad),
            "wohnbedarf_eltern_anteil",
        ] = wb[ad][4]

    # apply this share to living costs
    # unlike ALG2, there is no check on whether living costs are "appropriate".
    household["kinderzuschlag_kosten_unterk_m"] = household[
        "wohnbedarf_eltern_anteil"
    ] * (
        household["kinderzuschlag_kaltmiete_m"] + household["kinderzuschlag_heizkost_m"]
    )
    household["kinderzuschlag_eink_relev"] = (
        household["kinderzuschlag_eink_regel"]
        + household["kinderzuschlag_kosten_unterk_m"]
    )

    # First, we need to count the number of children eligible to child benefit.
    # (§6a (1) Nr. 1 BKGG)kdu
    household["anz_kinder_anspruch"] = household["kindergeld_anspruch"].sum()
    # There is a maximum income threshold, depending on the need, plus the potential
    # kiz receipt (§6a (1) Nr. 3 BKGG)
    household["kinderzuschlag_eink_max"] = (
        household["kinderzuschlag_eink_relev"]
        + params["kinderzuschlag"] * household["anz_kinder_anspruch"]
    )
    # min income to be eligible for KIZ (different for singles and couples)
    # (§6a (1) Nr. 2 BKGG)
    household["kinderzuschlag_eink_min"] = calc_min_income_kiz(household, params)

    household["kinderzuschlag_eink_brutto"] = household[
        "arbeitsl_geld_2_brutto_eink_hh"
    ]
    household["kinderzuschlag_eink_netto"] = household["sum_arbeitsl_geld_2_eink_hh"]

    # 1st step: deduct children income for each eligible child (§6a (3) S.3 BKGG)
    household["kinderzuschlag_kindereink_abzug"] = household["kindergeld_anspruch"] * (
        np.maximum(
            0,
            params["kinderzuschlag"]
            - params["kinderzuschlag_transferentzug_kind"]
            * (household["bruttolohn_m"] + household["unterhaltsvors_m"]),
        )
    )

    # 2nd step: Calculate the parents income that needs to be subtracted
    # (§6a (6) S. 3 BKGG)
    household["kinderzuschlag_eink_anrechn"] = np.maximum(
        0,
        params["kinderzuschlag_transferentzug_eltern"]
        * (
            household["sum_arbeitsl_geld_2_eink_hh"]
            - household["kinderzuschlag_eink_relev"]
        ),
    )

    # Child income
    household = params["calc_kiz_amount"](household, params)
    # 'kiz_temp' is the theoretical kiz claim, before it is
    # checked against other benefits later on.
    household["kinderzuschlag_temp"] = household["kinderzuschlag"].max()

    return household


def calc_kiz_amount_2005(household, params):
    """ Kinderzuschlag Amount from 2005 until 07/2019"
    """

    # Dummy variable whether household is in the relevant income range.
    household["kinderzuschlag_eink_spanne"] = (
        household["kinderzuschlag_eink_brutto"] >= household["kinderzuschlag_eink_min"]
    ) & (household["kinderzuschlag_eink_netto"] <= household["kinderzuschlag_eink_max"])
    household["kinderzuschlag"] = 0
    household.loc[
        household["kinderzuschlag_eink_spanne"], "kinderzuschlag"
    ] = np.maximum(
        0,
        household["kinderzuschlag_kindereink_abzug"].sum()
        - household["kinderzuschlag_eink_anrechn"],
    )

    return household


def calc_kiz_amount_07_2019(household, params):
    """ Kinderzuschlag Amount since 07/2019
        - no maximum income threshold anymore.
    """
    household["kinderzuschlag"] = 0
    household.loc[
        household["kinderzuschlag_eink_brutto"] >= household["kinderzuschlag_eink_min"],
        "kinderzuschlag",
    ] = np.maximum(
        0,
        household["kinderzuschlag_kindereink_abzug"].sum()
        - household["kinderzuschlag_eink_anrechn"],
    )

    return household


def calc_min_income_kiz(household, params):
    # Are there kids in the household
    if household["kind"].any() > 0:
        # Is it a single parent household
        if household["alleinerziehend"].all():
            return params["kinderzuschlag_min_eink_alleinerz"]
        else:
            return params["kinderzuschlag_min_eink_paare"]
    else:
        return 0


def calc_kiz_ek(household, params, arbeitsl_geld_2_params):
    if params["jahr"] <= 2010:
        calc_kiz_regel = _calc_kiz_regel_until_2010
    else:
        calc_kiz_regel = _calc_kiz_regel_since_2011

    kiz_regel = calc_kiz_regel(household, arbeitsl_geld_2_params)

    return np.select(
        [
            household["anz_erw_tu"] == 1,
            household["anz_erw_tu"] == 2,
            household["anz_erw_tu"] > 2,
        ],
        kiz_regel,
    )


def _calc_kiz_regel_until_2010(household, params):
    """"""
    return [
        params["regelsatz"] * (1 + household["alleinerziehenden_mehrbedarf"]),
        params["regelsatz"]
        * params["anteil_regelsatz"]["zwei_erwachsene"]
        * (2 + household["alleinerziehenden_mehrbedarf"]),
        params["regelsatz"]
        * params["anteil_regelsatz"]["weitere_erwachsene"]
        * household["anz_erw_tu"],
    ]


def _calc_kiz_regel_since_2011(household, params):
    return [
        params["regelsatz"][1] * (1 + household["alleinerziehenden_mehrbedarf"]),
        params["regelsatz"][2] * (2 + household["alleinerziehenden_mehrbedarf"]),
        params["regelsatz"][3] * household["anz_erw_tu"],
    ]


def kiz_dummy(household, params, arbeitsl_geld_2_params):
    """ Dummy function to return a bunch of zero values if called before 2005. """
    household["kinderzuschlag_temp"] = np.zeros((len(household), 1))
    household["kinderzuschlag_eink_spanne"] = np.zeros((len(household), 1))
    return household
