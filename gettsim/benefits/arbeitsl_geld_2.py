import copy
import datetime

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

    # After introduction of Hartz IV until 2010, people becoming unemployed
    # received something on top to smooth the transition. not yet modelled...

    household = eink_anr_frei(household, params)

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
