import numpy as np


def zve(tax_unit, eink_st_abzuege_params, soz_vers_beitr_params, kindergeld_params):
    """Calculate taxable income (zve = zu versteuerndes Einkommen). The calculation
    of the 6 branches of income is according to
    https://de.wikipedia.org/wiki/Einkommensteuer_(Deutschland)#Rechenschema

        In fact, you need several taxable incomes because of
        - child allowance vs. child benefit
        - abgeltungssteuer vs. taxing capital income in the tariff
        It's always the most favorable for the taxpayer, but you know that only after
         applying the tax schedule
    """
    adult_married = ~tax_unit["kind"] & tax_unit["gem_veranlagt"]
    # married = [tax_unit['gem_veranlagt'], ~tax_unit['gem_veranlagt']]
    # create output dataframe and transter some important variables
    ####################################################
    # TAX DEDUCTIONS
    # 1. Allgemeine Sonderausgaben - Special Expenses
    # Sonderausgaben
    # 2. VORSORGEAUFWENDUNGEN (technically a special case of "Sonderausgaben")
    """
    Social insurance contributions can be partly deducted from taxable income
    This regulation has been changed often in recent years.
    """
    tax_unit.loc[:, "vorsorge"] = eink_st_abzuege_params["vorsorge"](
        tax_unit, eink_st_abzuege_params, soz_vers_beitr_params
    )

    # Taxable income (zve = zu versteuerndes Einkommen)
    # For married couples, household income is split between the two.
    # Without child allowance / Ohne Kinderfreibetrag (nokfb):
    tax_unit.loc[
        ~tax_unit["kind"], "_zu_versteuerndes_eink_kein_kind_freib"
    ] = zve_nokfb(tax_unit, eink_st_abzuege_params)
    # Calculate Child Tax Allowance
    tax_unit = kinderfreibetrag(tax_unit, eink_st_abzuege_params, kindergeld_params)

    # Subtract (corrected) Child allowance
    tax_unit.loc[~tax_unit["kind"], "_zu_versteuerndes_eink_kind_freib"] = np.maximum(
        tax_unit["_zu_versteuerndes_eink_kein_kind_freib"] - tax_unit["kind_freib"], 0
    )
    tax_unit.loc[
        ~tax_unit["kind"], "_zu_versteuerndes_eink_abgelt_st_m_kind_freib"
    ] = np.maximum(
        tax_unit["_zu_versteuerndes_eink_abgelt_st_m_kein_kind_freib"]
        - tax_unit["kind_freib"],
        0,
    )
    # Finally, modify married couples income according to Splitting rule,
    # i.e. each partner get assigned half of the total income
    for incdef in [
        "kein_kind_freib",
        "kind_freib",
    ]:
        tax_unit.loc[:, "_zu_versteuerndes_eink_" + incdef + "_tu"] = tax_unit.loc[
            adult_married, "_zu_versteuerndes_eink_" + incdef
        ].sum()
        tax_unit.loc[adult_married, "_zu_versteuerndes_eink_" + incdef] = (
            0.5 * tax_unit["_zu_versteuerndes_eink_" + incdef + "_tu"]
        )

    return tax_unit


def kinderfreibetrag(tax_unit, params, kindergeld_params):
    """Calculate zve with Child Allowance (Kinderfreibetrag)"""
    tax_unit["kifreib"] = 0.0
    #
    # Married couples may share deductions if one partner does not need it.
    # For non-married, just deduct half the amount for each child.
    # TODO: Check whether this is correct for non-married couples

    # Count number of children eligible for Child Benefit.
    # Child allowance is only received for these kids.
    kigeld_kinder = tax_unit["_kindergeld_anspruch"].sum()

    # Find out who has the lower zve among partners
    nokfb_lower = tax_unit["_zu_versteuerndes_eink_kein_kind_freib"].min()

    kifreib_total = sum(params["kinderfreibetrag"].values())

    diff_kifreib = nokfb_lower - (kifreib_total * kigeld_kinder)
    # If the couple is married and one partner does not earn enough
    # to split the kinderfeibetrag, things get a bit more complicated.
    if diff_kifreib < 0 & tax_unit[~tax_unit["kind"]]["gem_veranlagt"].all():

        # The high earner gets half of the total kinderfreibetrag plus the amount the
        # lower earner can't claim.
        kifreib_higher = (kifreib_total * kigeld_kinder) + abs(diff_kifreib)
        # The second earner subtracts the remaining amount
        kifreib_lower = kifreib_total * kigeld_kinder - abs(diff_kifreib)
        # Then we assign each adult the amount and return the series
        tax_unit.loc[
            ~tax_unit["kind"] & tax_unit["_zu_versteuerndes_eink_kein_kind_freib"]
            != nokfb_lower,
            "kind_freib",
        ] = kifreib_higher
        tax_unit.loc[
            ~tax_unit["kind"] & tax_unit["_zu_versteuerndes_eink_kein_kind_freib"]
            == nokfb_lower,
            "kind_freib",
        ] = kifreib_lower
        return tax_unit

    # For non married couples or couples where both earn enough this are a lot easier.
    # Just split the kinderfreibetrag 50/50.
    else:
        tax_unit.loc[~tax_unit["kind"], "kind_freib"] = kifreib_total * kigeld_kinder
        return tax_unit


def zve_nokfb(tax_unit, params):
    """Calculate zve with no 'kinderfreibetrag'."""
    return np.maximum(
        0,
        tax_unit["sum_brutto_eink"]
        - tax_unit["vorsorge"]
        - tax_unit["sonderausgaben"]
        - tax_unit["behinderungsgrad_pauschalbetrag"]
        - tax_unit["hh_freib"]
        - tax_unit["altersfreib"],
    )


def _vorsorge_since_2010(tax_unit, params, soz_vers_beitr_params):
    """ Vorsorgeaufwendungen 2010 regime
        § 10 (3) EStG
        The share of deductable pension contributions increases each year by 2 pp.
        ('nachgelagerte Besteuerung'). In 2018, it's 86%. Add other contributions;
        4% from health contributions are not deductable.
        only deduct pension contributions up to the ceiling. multiply by 2
        because it's both employee and employer contributions.

        Contributions to other security branches can also be deducted.

        This ruling differs to vorsorge2005() only in the treatment of other contributions.
        """

    # calculate x% of relevant employer and employee contributions and private contributions
    # then subtract employer contributions
    altersvors = tax_unit["_altervorsorge_aufwend"]
    # also subtract health + care + unemployment insurance contributions
    # 'Basisvorsorge': Health and old-age care contributions are deducted anyway.
    sonstige_vors = 12 * (
        tax_unit["pflegev_beit_m"]
        + (1 - params["vorsorge_kranken_minderung"]) * tax_unit["ges_krankenv_beit_m"]
    )
    # maybe add avbeit, but do not exceed 1900€.
    sonstige_vors = np.maximum(
        sonstige_vors,
        np.minimum(
            sonstige_vors + 12 * tax_unit["arbeitsl_v_beit_m"],
            params["vorsorge_sonstige_aufw_max"],
        ),
    )
    return altersvors.astype(int) + sonstige_vors.astype(int)


def _vorsorge_since_2005(tax_unit, params, soz_vers_beitr_params):
    """ Vorsorgeaufwendungen 2005 to 2010
    Pension contributions are accounted for up to €20k.
    From this, a certain share can actually be deducted,
    starting with 60% in 2005.
    Other deductions are simply added up, up to a ceiling of 1500 p.a. for standard employees.
    """

    altersvors = tax_unit["_altervorsorge_aufwend"]

    sonstige_vors = ~tax_unit["kind"] * np.minimum(
        params["vorsorge_sonstige_aufw_max"],
        12
        * (
            tax_unit["ges_krankenv_beit_m"]
            + tax_unit["arbeitsl_v_beit_m"]
            + tax_unit["pflegev_beit_m"]
        ),
    ).astype(int)

    return (altersvors + sonstige_vors).astype(int)


def vorsorge_pre_2005(tax_unit, params, soz_vers_beitr_params):
    """ Vorsorgeaufwendungen up until 2004.
        - only pension and health contributions.
    """

    # Distinguish between married and singles
    # Single Taxpayer
    if not tax_unit["gem_veranlagt"].max():
        if params["jahr"] <= 2019:
            # Amount 1: Basic deduction, based on earnings. Usually zero.
            item_1 = np.maximum(
                params["vorsorge2004_vorwegabzug"]
                - params["vorsorge2004_kürzung_vorwegabzug"]
                * 12
                * tax_unit["bruttolohn_m"],
                0,
            )
        else:
            # No "vorwegabzug" anymore after 2019.
            item_1 = 0
        # calcuate the remaining amount.
        vorsorg_rest = np.maximum(
            12 * (tax_unit["rentenv_beit_m"] + tax_unit["ges_krankenv_beit_m"])
            - item_1,
            0,
        )
        # Deduct a 'Grundhöchstbetrag' (1334€ in 2004),
        # or the actual expenses if lower (which is unlikely)
        item_2 = np.minimum(params["vorsorge_2004_grundhöchstbetrag"], vorsorg_rest)
        # From what is left from vorsorg_rest, you may deduct 50%.
        # (up until 50% of 'Grundhöchstbetrag')
        item_3 = np.minimum(
            0.5 * (vorsorg_rest - item_2),
            0.5 * params["vorsorge_2004_grundhöchstbetrag"],
        )
    # For the married couple, the same stuff, but with tu totals.
    if tax_unit["gem_veranlagt"].max():
        for var in ["bruttolohn_m", "rentenv_beit_m", "ges_krankenv_beit_m"]:
            # TODO: Shouldnt here be summe over the variables?
            tax_unit[f"{var}_tu"] = tax_unit.loc[
                ~tax_unit["kind"], "bruttolohn_m"
            ].sum()
        if params["jahr"] <= 2019:
            item_1 = 0.5 * np.maximum(
                2 * params["vorsorge2004_vorwegabzug"]
                - params["vorsorge2004_kürzung_vorwegabzug"]
                * 12
                * tax_unit["bruttolohn_m_tu"],
                0,
            )
        else:
            item_1 = 0

        vorsorg_rest = 0.5 * np.maximum(
            12 * (tax_unit["rentenv_beit_m_tu"] + tax_unit["ges_krankenv_beit_m_tu"])
            - item_1,
            0,
        )
        item_2 = 0.5 * np.minimum(
            params["vorsorge_2004_grundhöchstbetrag"], vorsorg_rest
        )
        item_3 = 0.5 * np.minimum(
            (vorsorg_rest - item_2), 2 * params["vorsorge_2004_grundhöchstbetrag"]
        )

    # Finally, add up all three amounts and assign it to the adults.
    vorsorge = ~tax_unit["kind"] * (item_1 + item_2 + item_3).astype(int)
    return vorsorge


def vorsorge_since_2005(tax_unit, params, soz_vers_beitr_params):
    """ With the 2005 reform, no taxpayer was supposed to be affected negatively.
        Therefore, one needs to compute amounts
        (2004 and 2005 regime) and take the higher one.
    """
    vors_2004 = vorsorge_pre_2005(tax_unit, params, soz_vers_beitr_params)
    vors_2005 = _vorsorge_since_2005(tax_unit, params, soz_vers_beitr_params)

    return np.maximum(vors_2004, vors_2005)


def vorsorge_since_2010(tax_unit, params, soz_vers_beitr_params):
    """ After a supreme court ruling, the 2005 rule had to be changed in 2010.
        Therefore, one needs to compute amounts
        (2004 and 2010 regime) and take the higher one. (§10 (3a) EStG).
        Sidenote: The 2010 ruling is by construction
        *always* more or equally beneficial than the 2005 one,
        so no need for a separate check there.
    """
    vors_2004 = vorsorge_pre_2005(tax_unit, params, soz_vers_beitr_params)
    vors_2010 = _vorsorge_since_2010(tax_unit, params, soz_vers_beitr_params)

    return np.maximum(vors_2004, vors_2010)
