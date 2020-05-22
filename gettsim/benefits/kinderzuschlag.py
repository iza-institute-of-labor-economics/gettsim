import numpy as np


def kiz(household, params, arbeitsl_geld_2_params):
    """Kinderzuschlag / Additional Child Benefit

    The purpose of Kinderzuschlag (Kiz) is to keep families out of ALG2. If they would
    be eligible to ALG2 due to the fact that their claim rises because of their
    children, they can claim Kiz.

    A couple of criteria need to be met.

    1. the household has to have some income

    2. net income minus housing benefit needs has to be lower than total ALG2 need plus
       additional child benefit.

    3. Over a certain income threshold (which depends on housing costs, and is therefore
       household-specific), parental income is deducted from child benefit claim.

    In contrast to ALG2, Kiz considers only the rental costs that are attributed to the
    parents. This is done by some fixed share which is updated on annual basis
    ('jährlicher Existenzminimumsbericht')

    """
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
        household["arbeitsl_geld_2_brutto_eink_hh"]
        >= household["kinderzuschlag_eink_min"]
    ) & (
        household["sum_arbeitsl_geld_2_eink_hh"] <= household["kinderzuschlag_eink_max"]
    )
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
        household["arbeitsl_geld_2_brutto_eink_hh"]
        >= household["kinderzuschlag_eink_min"],
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


def kiz_dummy(household, params, arbeitsl_geld_2_params):
    """ Dummy function to return a bunch of zero values if called before 2005. """
    household["kinderzuschlag_temp"] = np.zeros((len(household), 1))
    household["kinderzuschlag_eink_spanne"] = np.zeros((len(household), 1))
    return household
