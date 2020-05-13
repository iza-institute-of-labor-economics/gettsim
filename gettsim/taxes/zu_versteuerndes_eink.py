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
    # Income components on annual basis
    # Income from Self-Employment
    tax_unit.loc[:, "brutto_eink_1"] = 12 * tax_unit["eink_selbstst_m"]
    # Earnings
    tax_unit = calc_gross_e4(tax_unit, eink_st_abzuege_params, soz_vers_beitr_params)
    # Capital Income
    tax_unit.loc[:, "brutto_eink_5"] = np.maximum((12 * tax_unit["kapital_eink_m"]), 0)
    # Income from rents
    tax_unit.loc[:, "brutto_eink_6"] = 12 * tax_unit["vermiet_eink_m"]
    # Others (Pensions)
    tax_unit = calc_gross_e7(tax_unit, eink_st_abzuege_params)

    # Sum of incomes
    tax_unit.loc[:, "sum_brutto_eink"] = calc_gde(tax_unit, eink_st_abzuege_params)

    # # Gross (market) income <> sum of incomes...
    # tax_unit.loc[:, "m_brutto"] = tax_unit[
    #     ["m_self", "m_wage", "m_kapinc", "m_vermiet", "m_pensions"]
    # ].sum(axis=1)

    tax_unit.loc[:, "behinderungsgrad_pauschalbetrag"] = calc_handicap_lump_sum(
        tax_unit, eink_st_abzuege_params
    )

    # Aggregate several incomes on the taxpayer couple
    for inc in [
        "brutto_eink_1",
        "brutto_eink_4",
        "brutto_eink_5",
        "brutto_eink_6",
        "brutto_eink_7",
    ]:
        tax_unit.loc[adult_married, inc + "_tu"] = tax_unit.loc[
            adult_married, inc
        ].sum()

    # TAX DEDUCTIONS
    # 1. Allgemeine Sonderausgaben - Special Expenses
    # Sonderausgaben
    tax_unit = deductible_child_care_costs(tax_unit, eink_st_abzuege_params)
    # 2. VORSORGEAUFWENDUNGEN (technically a special case of "Sonderausgaben")
    """
    Social insurance contributions can be partly deducted from taxable income
    This regulation has been changed often in recent years.
    """
    tax_unit.loc[:, "vorsorge"] = eink_st_abzuege_params["vorsorge"](
        tax_unit, eink_st_abzuege_params, soz_vers_beitr_params
    )

    # 3. Tax Deduction for elderly ("Altersentlastungsbetrag")
    # does not affect pensions.
    tax_unit = calc_altfreibetrag(tax_unit, eink_st_abzuege_params)
    # 4.. Entlastungsbetrag für Alleinerziehende: Tax Deduction for Single Parents.
    tax_unit = eink_st_abzuege_params["calc_hhfreib"](tax_unit, eink_st_abzuege_params)

    # Taxable income (zve = zu versteuerndes Einkommen)
    # For married couples, household income is split between the two.
    # Without child allowance / Ohne Kinderfreibetrag (nokfb):
    tax_unit.loc[
        ~tax_unit["kind"], "_zu_versteuerndes_eink_kein_kind_freib"
    ] = zve_nokfb(tax_unit, eink_st_abzuege_params)
    # Tax base including capital income
    tax_unit = zve_abg_nokfb(tax_unit, eink_st_abzuege_params)
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
        "abgelt_st_m_kein_kind_freib",
        "kind_freib",
        "abgelt_st_m_kind_freib",
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
    kigeld_kinder = kindergeld_params["kindergeld_anspruch_regel"](
        tax_unit, kindergeld_params
    ).sum()

    # Find out who has the lower zve among partners
    nokfb_lower = tax_unit["_zu_versteuerndes_eink_kein_kind_freib"].min()

    # Add both components of Child Allowance for ease of notation.
    if params["jahr"] >= 2000:
        kifreib_total = (
            params["kinderfreibetrag_sächl_exmin"]
            + params["kinderfreibetrag_betr_erz_ausb"]
        )
    # 'kifreib_bezt_erz_ausb' does not exist before 2000.
    else:
        kifreib_total = params["kinderfreibetrag_sächl_exmin"]

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
        - tax_unit["sonder"]
        - tax_unit["behinderungsgrad_pauschalbetrag"]
        - tax_unit["hh_freib"]
        - tax_unit["altersfreib"],
    )


def zve_abg_nokfb(tax_unit, params):
    """Calculates the zve with capital income in the tax base."""
    if tax_unit[~tax_unit["kind"]]["gem_veranlagt"].all():
        tax_unit.loc[
            ~tax_unit["kind"], "_zu_versteuerndes_eink_abgelt_st_m_kein_kind_freib"
        ] = np.maximum(
            0,
            tax_unit["sum_brutto_eink"]
            + np.maximum(
                0,
                tax_unit["brutto_eink_5"]
                - 2 * params["sparerpauschbetrag"]
                - 2 * params["sparer_werbungskosten_pauschbetrag"],
            )
            - tax_unit["vorsorge"]
            - tax_unit["sonder"]
            - tax_unit["behinderungsgrad_pauschalbetrag"]
            - tax_unit["hh_freib"]
            - tax_unit["altersfreib"],
        )
    else:
        tax_unit.loc[
            ~tax_unit["kind"], "_zu_versteuerndes_eink_abgelt_st_m_kein_kind_freib"
        ] = np.maximum(
            0,
            tax_unit["sum_brutto_eink"]
            + np.maximum(
                0,
                tax_unit["brutto_eink_5"]
                - params["sparerpauschbetrag"]
                - params["sparer_werbungskosten_pauschbetrag"],
            )
            - tax_unit["vorsorge"]
            - tax_unit["sonder"]
            - tax_unit["behinderungsgrad_pauschalbetrag"]
            - tax_unit["hh_freib"]
            - tax_unit["altersfreib"],
        )
    return tax_unit


def calc_altfreibetrag(tax_unit, params):
    """Calculates the deductions for elderly. Not tested yet!!!"""
    tax_unit["altersfreib"] = 0.0
    tax_unit.loc[tax_unit["alter"] > 64, "altersfreib"] = np.minimum(
        params["altersentlastung_quote"]
        * 12
        * (
            tax_unit["bruttolohn_m"]
            + np.maximum(
                0,
                tax_unit[["kapital_eink_m", "eink_selbstst_m", "vermiet_eink_m"]].sum(
                    axis=1
                ),
            )
        ),
        params["altersentlastungsbetrag_max"],
    )
    return tax_unit


def calc_handicap_lump_sum(tax_unit, params):
    """Calculate the different deductions for different handicap degrees."""
    # Behinderten-Pauschbeträge
    # Pick the correct one based on handicap degree
    hc_degrees = [
        tax_unit["behinderungsgrad"].between(25, 30),
        tax_unit["behinderungsgrad"].between(35, 40),
        tax_unit["behinderungsgrad"].between(45, 50),
        tax_unit["behinderungsgrad"].between(55, 60),
        tax_unit["behinderungsgrad"].between(65, 70),
        tax_unit["behinderungsgrad"].between(75, 80),
        tax_unit["behinderungsgrad"].between(85, 90),
        tax_unit["behinderungsgrad"].between(95, 100),
    ]

    return np.nan_to_num(
        np.select(hc_degrees, params["behinderten_pausch_betrag"].values())
    )


def calc_gde(tax_unit, params):
    """Calculates sum of the taxable income. It depends on the year if capital
    income, counts into the sum."""
    gross_gde = tax_unit[
        ["brutto_eink_1", "brutto_eink_4", "brutto_eink_6", "brutto_eink_7"]
    ].sum(axis=1)

    # Add UBI to taxable income
    # if ref == "UBI":
    #    zve.loc[:, "gross_gde"] = zve["gross_gde"] + (tax_unit["ubi"] * 12)

    # Kapitaleinkommen im Tarif versteuern oder nicht?
    # If capital income tax with tarif, add capital income to tax base but account
    # for exemptions
    if params["jahr"] < 2009:
        gross_gde += np.maximum(
            tax_unit["brutto_eink_5"]
            - params["sparerpauschbetrag"]
            - params["sparer_werbungskosten_pauschbetrag"],
            0,
        )
    return gross_gde


def calc_gross_e4(tax_unit, params, soz_vers_beitr_params):
    """Calculates the gross incomes of non selfemployed work. The wage is reducted by a
    lump sum payment for 'Werbungskosten'"""

    tax_unit.loc[:, "brutto_eink_4"] = 12 * tax_unit["bruttolohn_m"]
    # Every adult with some wage, gets a lump sum payment for Werbungskosten
    tax_unit.loc[
        (~tax_unit["kind"]) & (tax_unit["bruttolohn_m"] > 0), "brutto_eink_4"
    ] -= params["werbungskostenpauschale"]

    # If they earn less the mini job limit, then their relevant gross income is 0
    if tax_unit["wohnort_ost"].iloc[0]:
        mini = soz_vers_beitr_params["geringfügige_eink_grenzen"]["mini_job"]["ost"]
    else:
        mini = soz_vers_beitr_params["geringfügige_eink_grenzen"]["mini_job"]["west"]

    tax_unit.loc[tax_unit["bruttolohn_m"] <= mini, "brutto_eink_4"] = 0
    return tax_unit


def deductible_child_care_costs(tax_unit, params):
    """Calculating sonderausgaben for childcare. We follow 10 Abs.1 Nr. 5 EStG. You can
    details here https://www.buzer.de/s1.htm?a=10&g=estg."""
    # So far we only implement the current regulation, which has been in place since 2012.
    if params["jahr"] < 2012:
        # For earlier years we only use the pausch value
        tax_unit.loc[~tax_unit["kind"], "sonder"] = params["sonderausgabenpauschbetrag"]
        return tax_unit
    else:
        adult_num = len(tax_unit[~tax_unit["kind"]])
        # The maximal amount to claim is 4000 per child. We only count the claim for
        # children under 14. By law the parents are also to allow to claim for disabled
        # children til the age of 25.
        eligible = tax_unit["alter"] <= 14

        deductible_costs = (
            eligible
            * np.minimum(
                params["kinderbetreuungskosten_abz_maximum"],
                12 * tax_unit["betreuungskost_m"],
            )
            * params["kinderbetreuungskosten_abz_anteil"]
            / adult_num
        )
        # If parents can't claim anything, they get a pausch value.
        tax_unit.loc[~tax_unit["kind"], "sonder"] = max(
            np.sum(deductible_costs), params["sonderausgabenpauschbetrag"]
        )
        return tax_unit


def calc_gross_e7(tax_unit, params):
    """ Calculates the gross income of 'Sonsitge Einkünfte'. In our case that's only
    pensions."""
    # The share of pensions subject to income taxation
    tax_unit.loc[tax_unit["jahr_renteneintr"] <= 2004, "_ertragsanteil"] = 0.27
    tax_unit.loc[
        tax_unit["jahr_renteneintr"].between(2005, 2020), "_ertragsanteil"
    ] = 0.5 + 0.02 * (tax_unit["jahr_renteneintr"] - 2005)
    tax_unit.loc[
        tax_unit["jahr_renteneintr"].between(2021, 2040), "_ertragsanteil"
    ] = 0.8 + 0.01 * (tax_unit["jahr_renteneintr"] - 2020)
    tax_unit.loc[tax_unit["jahr_renteneintr"] >= 2041, "_ertragsanteil"] = 1
    tax_unit.loc[:, "brutto_eink_7"] = np.maximum(
        12 * (tax_unit["_ertragsanteil"] * tax_unit["ges_rente_m"]), 0,
    )
    return tax_unit


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
    altersvors = calc_altersvors_aufwend(tax_unit, params)
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

    altersvors = calc_altersvors_aufwend(tax_unit, params)

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


def calc_altersvors_aufwend(tax_unit, params):
    """Return the amount of contributions to retirement savings that is deductible from
    taxable income. **This function becomes relevant in 2005, do not use it for prior
    year**.

    The share of deductible contributions increases each year from 60% in 2005 to 100%
    in 2025.
    """

    einführungsfaktor = 0.6 + 0.02 * (min(params["jahr"], 2025) - 2005)

    altersvors = ~tax_unit["kind"] * (
        einführungsfaktor
        * (12 * 2 * tax_unit["rentenv_beit_m"] + (12 * tax_unit["prv_rente_beit_m"]))
        - (12 * tax_unit["rentenv_beit_m"])
    ).astype(int)

    return np.minimum(params["vorsorge_altersaufw_max"], altersvors)


def calc_hhfreib_until2014(tax_unit, params):
    """Calculates tax reduction for single parents. Used to be called
    'Haushaltsfreibetrag'"""
    tax_unit["hh_freib"] = 0.0
    tax_unit.loc[tax_unit["alleinerziehend"], "hh_freib"] = params[
        "alleinerziehenden_freibetrag"
    ]
    return tax_unit


def calc_hhfreib_from2015(tax_unit, params):
    """Calculates tax reduction for single parents. Since 2015, it increases with
    number of children. Used to be called 'Haushaltsfreibetrag'"""
    tax_unit["hh_freib"] = 0.0
    tax_unit.loc[tax_unit["alleinerziehend"], "hh_freib"] = params[
        "alleinerziehenden_freibetrag"
    ] + ((tax_unit["kind"].sum() - 1) * params["alleinerziehenden_freibetrag_zusatz"])
    return tax_unit
