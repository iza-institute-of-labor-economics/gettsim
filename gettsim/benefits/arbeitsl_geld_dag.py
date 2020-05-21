import pandas as pd

from gettsim.benefits.arbeitsl_geld import ui
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.pre_processing.piecewise_functions import piecewise_polynomial
from gettsim.taxes.eink_st import st_tarif


def arbeitsl_geld_m(
    p_id,
    hh_id,
    tu_id,
    bruttolohn_vorj_m,
    wohnort_ost,
    kind,
    arbeitsl_lfdj_m,
    arbeitsl_vorj_m,
    arbeitsl_vor2j_m,
    ges_rente_m,
    arbeitsstunden_w,
    anz_kinder_tu,
    alter,
    jahr,
    berechtigt_für_arbeitsl_geld,
    proxy_eink_vorj,
    arbeitsl_geld_params,
    soz_vers_beitr_params,
    eink_st_abzuege_params,
    eink_st_params,
    soli_st_params,
):
    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            bruttolohn_vorj_m,
            wohnort_ost,
            kind,
            arbeitsl_lfdj_m,
            arbeitsl_vorj_m,
            arbeitsl_vor2j_m,
            ges_rente_m,
            arbeitsstunden_w,
            anz_kinder_tu,
            alter,
            jahr,
            berechtigt_für_arbeitsl_geld,
            proxy_eink_vorj,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=ui,
        level=["hh_id", "tu_id", "p_id"],
        in_cols=df.columns.tolist(),
        out_cols=["arbeitsl_geld_m"],
        func_kwargs={
            "params": arbeitsl_geld_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "eink_st_abzuege_params": eink_st_abzuege_params,
            "eink_st_params": eink_st_params,
            "soli_st_params": soli_st_params,
        },
    )

    return df["arbeitsl_geld_m"]


def monate_arbeitsl(arbeitsl_lfdj_m, arbeitsl_vorj_m, arbeitsl_vor2j_m):
    return arbeitsl_lfdj_m + arbeitsl_vorj_m + arbeitsl_vor2j_m


def berechtigt_für_arbeitsl_geld(
    monate_arbeitsl, alter, ges_rente_m, arbeitsstunden_w, arbeitsl_geld_params
):
    """Check eligibility for unemployment benefits.

    Different rates for parent and non-parents. Take into account actual wages. There
    are different replacement rates depending on presence of children

    """
    return (
        (1 <= monate_arbeitsl)
        & (monate_arbeitsl <= 12)
        & (alter < 65)
        & (ges_rente_m == 0)
        & (arbeitsstunden_w < arbeitsl_geld_params["arbeitsl_geld_stundengrenze"])
    )


def proxy_eink_vorj(
    beitr_bemess_grenze_rentenv,
    wohnort_ost,
    bruttolohn_vorj_m,
    arbeitsl_geld_params,
    eink_st_params,
    eink_st_abzuege_params,
    soli_st_params,
    soz_vers_beitr_params,
):
    """ Calculating the claim for benefits depending on previous wage.

    - Arbeitslosengeld
    - Elterngeld

    """
    # Relevant wage is capped at the contribution thresholds
    max_wage = bruttolohn_vorj_m.clip(lower=None, upper=beitr_bemess_grenze_rentenv)

    # We need to deduct lump-sum amounts for contributions, taxes and soli
    prox_ssc = arbeitsl_geld_params["soz_vers_pausch_arbeitsl_geld"] * max_wage

    # Fictive taxes (Lohnsteuer) are approximated by applying the wage to the tax tariff
    prox_tax = st_tarif(
        12 * max_wage - eink_st_abzuege_params["werbungskostenpauschale"],
        eink_st_params,
    )

    prox_soli = piecewise_polynomial(
        prox_tax,
        lower_thresholds=soli_st_params["soli_st"]["lower_thresholds"],
        upper_thresholds=soli_st_params["soli_st"]["upper_thresholds"],
        rates=soli_st_params["soli_st"]["rates"],
        intercepts_at_lower_thresholds=soli_st_params["soli_st"][
            "intercepts_at_lower_thresholds"
        ],
    )

    return (max_wage - prox_ssc - prox_tax / 12 - prox_soli / 12).clip(lower=0)


def beitr_bemess_grenze_rentenv(wohnort_ost, soz_vers_beitr_params):
    return wohnort_ost.replace(
        {
            True: soz_vers_beitr_params["beitr_bemess_grenze"]["rentenv"]["ost"],
            False: soz_vers_beitr_params["beitr_bemess_grenze"]["rentenv"]["west"],
        }
    )
