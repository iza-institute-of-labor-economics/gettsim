import copy
import datetime

import numpy as np

from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.pre_processing.piecewise_functions import piecewise_polynomial


def alg2(household, params):
    """ Basic Unemployment Benefit / Social Assistance
        Every household is assigend the sum of "needs" (Regelbedarf)
        These depend on the household composition (# of adults, kids in various age
        groups) and the rent. There are additional needs acknowledged for single
        parents. Income and wealth is tested for, the transfer withdrawal rate is
        non-constant.
    """
    if params["jahr"] < 2005:
        # warnings.warn("Arbeitslosengeld 2 existiert erst ab 2005 und wurde deshalb "
        #               "nicht berechnet.")
        return household

    household = params["calc_regelsatz"](household, params)

    # After introduction of Hartz IV until 2010, people becoming unemployed
    # received something on top to smooth the transition. not yet modelled...

    household = eink_anr_frei(household, params)

    return household


def regelberechnung_until_2010(household, params):
    num_adults = len(household) - household["kind"].sum()
    kinder_satz_m = 0
    for age_lims in [(0, 6), (7, 13), (14, 24)]:
        kinder_satz_m += (
            params["regelsatz"]
            * params["anteil_regelsatz"][f"kinder_{age_lims[0]}_{age_lims[1]}"]
            * (
                household["kind"] & household["alter"].between(age_lims[0], age_lims[1])
            ).sum()
        )

    if num_adults == 1:
        household["regelsatz_m"] = params["regelsatz"] * (
            1 + household["alleinerziehenden_mehrbedarf"]
        )
    elif num_adults > 1:
        household["regelsatz_m"] = params["regelsatz"] * (
            params["anteil_regelsatz"]["zwei_erwachsene"]
            * (2 + household["alleinerziehenden_mehrbedarf"])
            + (
                params["anteil_regelsatz"]["weitere_erwachsene"]
                * np.maximum((num_adults - 2), 0)
            )
        )
    household["regelsatz_m"] += kinder_satz_m

    return household


def regelberechnung_2011_and_beyond(household, params):

    num_adults = len(household) - household["kind"].sum()

    # Regelbedarsstufen 1 to 3 are for adults in different civil status.
    # Single adult has "Regelbedarfstufe" 1
    if num_adults == 1:
        household["regelsatz_m"] = params["regelsatz"][1] * (
            1 + household["alleinerziehenden_mehrbedarf"]
        )

    # Two adults are "Regelbedarstufe" 2. More are 3.
    elif num_adults > 1:
        household["regelsatz_m"] = params["regelsatz"][2] * (
            2 + household["alleinerziehenden_mehrbedarf"]
        ) + (params["regelsatz"][3] * np.maximum((num_adults - 2), 0))

    kinder_satz_m = 0
    # Regelbedarfsstufen 4 to 6 are for children in different age ranges.
    for i, age_lims in enumerate([(14, 25), (7, 13), (0, 6)]):
        kinder_satz_m += (
            params["regelsatz"][4 + i]
            * (
                household["kind"] & household["alter"].between(age_lims[0], age_lims[1])
            ).sum()
        )

    household["regelsatz_m"] += kinder_satz_m

    return household


def eink_anr_frei(household, params):
    """Calculate income not subject to transfer withdrawal for each person.

    """
    # If there live kids in the household, we select different parameters.
    if household["kind"].any():
        eink_anr_frei_params = copy.deepcopy(params["eink_anr_frei_kinder"])
    else:
        eink_anr_frei_params = copy.deepcopy(params["eink_anr_frei"])

    in_cols = [
        "bruttolohn_m",
        "eink_anrechn_frei",
        "eink_st_m",
        "soli_st_m",
        "sozialv_beit_m",
        "arbeitsl_geld_2_2005_netto_quote",
    ]
    # Everything was already initialized
    out_cols = []
    household = apply_tax_transfer_func(
        household,
        tax_func=eink_anr_frei_person,
        level=["hh_id", "tu_id", "p_id"],
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"eink_anr_frei_params": eink_anr_frei_params, "params": params},
    )
    return household


def eink_anr_frei_person(person, eink_anr_frei_params, params):
    # In the first version of alg2, the rates were multiplied by the nettoquote.
    rates_modified = False
    individual_params = copy.deepcopy(eink_anr_frei_params)

    if params["datum"] < datetime.date(year=2005, month=10, day=1):
        individual_params["rates"] *= person["arbeitsl_geld_2_2005_netto_quote"]
        rates_modified = True

    person["eink_anrechn_frei"] = piecewise_polynomial(
        x=person["bruttolohn_m"],
        lower_thresholds=individual_params["lower_thresholds"],
        upper_thresholds=individual_params["upper_thresholds"],
        rates=individual_params["rates"],
        intercepts_at_lower_thresholds=individual_params[
            "intercepts_at_lower_thresholds"
        ],
        rates_modified=rates_modified,
    )
    return person
