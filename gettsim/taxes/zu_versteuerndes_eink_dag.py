import pandas as pd

from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.taxes.zu_versteuerndes_eink import zve
from gettsim.tests.test_zu_versteuerndes_eink import INPUT_COLS
from gettsim.tests.test_zu_versteuerndes_eink import OUT_COLS


def _zu_versteuerndes_eink_kein_kind_freib(
    p_id,
    hh_id,
    tu_id,
    bruttolohn_m,
    betreuungskost_m,
    eink_selbstst_m,
    kapital_eink_m,
    vermiet_eink_m,
    jahr_renteneintr,
    ges_rente_m,
    arbeitsstunden_w,
    in_ausbildung,
    gem_veranlagt,
    kind,
    behinderungsgrad,
    rentenv_beit_m,
    prv_rente_beit_m,
    arbeitsl_v_beit_m,
    pflegev_beit_m,
    alleinerziehend,
    alter,
    anz_kinder_tu,
    jahr,
    wohnort_ost,
    ges_krankenv_beit_m,
    params,
):

    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            bruttolohn_m,
            betreuungskost_m,
            eink_selbstst_m,
            kapital_eink_m,
            vermiet_eink_m,
            jahr_renteneintr,
            ges_rente_m,
            arbeitsstunden_w,
            in_ausbildung,
            gem_veranlagt,
            kind,
            behinderungsgrad,
            rentenv_beit_m,
            prv_rente_beit_m,
            arbeitsl_v_beit_m,
            pflegev_beit_m,
            alleinerziehend,
            alter,
            anz_kinder_tu,
            jahr,
            wohnort_ost,
            ges_krankenv_beit_m,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=zve,
        level=["hh_id", "tu_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={
            "eink_st_abzuege_params": params["eink_st_abzuege_params"],
            "soz_vers_beitr_params": params["soz_vers_beitr_params"],
            "kindergeld_params": params["kindergeld_params"],
        },
    )

    return df["_zu_versteuerndes_eink_kein_kind_freib"]


def altersfreib(
    p_id,
    hh_id,
    tu_id,
    bruttolohn_m,
    betreuungskost_m,
    eink_selbstst_m,
    kapital_eink_m,
    vermiet_eink_m,
    jahr_renteneintr,
    ges_rente_m,
    arbeitsstunden_w,
    in_ausbildung,
    gem_veranlagt,
    kind,
    behinderungsgrad,
    rentenv_beit_m,
    prv_rente_beit_m,
    arbeitsl_v_beit_m,
    pflegev_beit_m,
    alleinerziehend,
    alter,
    anz_kinder_tu,
    jahr,
    wohnort_ost,
    ges_krankenv_beit_m,
    params,
):

    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            bruttolohn_m,
            betreuungskost_m,
            eink_selbstst_m,
            kapital_eink_m,
            vermiet_eink_m,
            jahr_renteneintr,
            ges_rente_m,
            arbeitsstunden_w,
            in_ausbildung,
            gem_veranlagt,
            kind,
            behinderungsgrad,
            rentenv_beit_m,
            prv_rente_beit_m,
            arbeitsl_v_beit_m,
            pflegev_beit_m,
            alleinerziehend,
            alter,
            anz_kinder_tu,
            jahr,
            wohnort_ost,
            ges_krankenv_beit_m,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=zve,
        level=["hh_id", "tu_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={
            "eink_st_abzuege_params": params["eink_st_abzuege_params"],
            "soz_vers_beitr_params": params["soz_vers_beitr_params"],
            "kindergeld_params": params["kindergeld_params"],
        },
    )

    return df["altersfreib"]


def _zu_versteuerndes_eink_kind_freib(
    p_id,
    hh_id,
    tu_id,
    bruttolohn_m,
    betreuungskost_m,
    eink_selbstst_m,
    kapital_eink_m,
    vermiet_eink_m,
    jahr_renteneintr,
    ges_rente_m,
    arbeitsstunden_w,
    in_ausbildung,
    gem_veranlagt,
    kind,
    behinderungsgrad,
    rentenv_beit_m,
    prv_rente_beit_m,
    arbeitsl_v_beit_m,
    pflegev_beit_m,
    alleinerziehend,
    alter,
    anz_kinder_tu,
    jahr,
    wohnort_ost,
    ges_krankenv_beit_m,
    params,
):

    df = pd.concat(
        [
            p_id,
            hh_id,
            tu_id,
            bruttolohn_m,
            betreuungskost_m,
            eink_selbstst_m,
            kapital_eink_m,
            vermiet_eink_m,
            jahr_renteneintr,
            ges_rente_m,
            arbeitsstunden_w,
            in_ausbildung,
            gem_veranlagt,
            kind,
            behinderungsgrad,
            rentenv_beit_m,
            prv_rente_beit_m,
            arbeitsl_v_beit_m,
            pflegev_beit_m,
            alleinerziehend,
            alter,
            anz_kinder_tu,
            jahr,
            wohnort_ost,
            ges_krankenv_beit_m,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=zve,
        level=["hh_id", "tu_id"],
        in_cols=INPUT_COLS,
        out_cols=OUT_COLS,
        func_kwargs={
            "eink_st_abzuege_params": params["eink_st_abzuege_params"],
            "soz_vers_beitr_params": params["soz_vers_beitr_params"],
            "kindergeld_params": params["kindergeld_params"],
        },
    )

    return df["_zu_versteuerndes_eink_kind_freib"]
