from datetime import date

from gettsim.benefits.arbeitsl_geld import ui
from gettsim.benefits.arbeitsl_geld_2 import alg2
from gettsim.benefits.benefit_checks import benefit_priority
from gettsim.benefits.elterngeld import elterngeld
from gettsim.benefits.unterhalt import uhv
from gettsim.benefits.wohngeld import wg
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.pre_processing.checks import check_boolean
from gettsim.pre_processing.exogene_renten_daten.lade_renten_daten import (
    lade_exogene_renten_daten,
)
from gettsim.pre_processing.policy_for_date import get_policies_for_date
from gettsim.renten_anspr import pensions
from gettsim.soz_vers import soc_ins_contrib
from gettsim.taxes.eink_st import eink_st
from gettsim.taxes.favorability_check import favorability_check
from gettsim.taxes.kindergeld import kindergeld
from gettsim.taxes.zu_versteuerndes_eink import zve
from gettsim.verfügb_eink import disposable_income


def tax_transfer(
    df,
    arbeitsl_geld_2_params,
    abgelt_st_params,
    arbeitsl_geld_params,
    soz_vers_beitr_params,
    eink_st_abzuege_params,
    elterngeld_params,
    unterhalt_params,
    wohngeld_params,
    kinderzuschlag_params,
    eink_st_params,
    soli_st_params,
    kindergeld_params,
    renten_daten,
):
    """ The German Tax-Transfer System.

    Arguments:

        *df* -- Input Data Frame
        *datayear* -- year of SOEP wave
        *taxyear* -- year of reform baseline
        *tb* -- dictionary with tax-benefit parameters
        *tb_pens* -- Parameters for pension calculations
        *mw* -- Mean earnings by year, for pension calculations.
        *hyporun* -- indicator for hypothetical household input
                     (default: False -> use real SOEP data)

    Returns:
        A dataframe containing the core elements of interest (tax payments,
        contributions, various benefits, disp. income, gross income)
    The 'sub' functions may take an argument 'ref', which might be used for small
     reforms that e.g. only differ in parameters or slightly change the calculation.
    """
    bool_variables = ["kind", "wohnort_ost"]
    check_boolean(df, bool_variables)
    # if hyporun is False:
    # df = uprate(df, datayear, settings['taxyear'], settings['MAIN_PATH'])

    # We initialize all output columns.
    # for column in OUT_PUT:
    # df[column] = 0.0
    household = ["hh_id"]
    tax_unit = ["hh_id", "tu_id"]
    person = ["hh_id", "tu_id", "p_id"]
    if df.groupby(person).ngroups != len(df):
        raise ValueError(
            "Household, tax unit and person identifier don't provide "
            "distinguishable individuals."
        )
    # We start with the top layer, which is household id. We treat this as the
    # "Bedarfsgemeinschaft" in German tax law.
    in_cols = [
        "bruttolohn_m",
        "wohnort_ost",
        "alter",
        "selbstständig",
        "hat_kinder",
        "eink_selbstst_m",
        "ges_rente_m",
        "prv_krankv_beit_m",
    ]
    out_cols = [
        "sozialv_beit_m",
        "rentenv_beit_m",
        "arbeitsl_v_beit_m",
        "ges_krankv_beit_m",
        "pflegev_beit_m",
    ]
    df = apply_tax_transfer_func(
        df,
        tax_func=soc_ins_contrib,
        level=person,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"params": soz_vers_beitr_params},
    )

    in_cols = [
        "bruttolohn_vorj_m",
        "wohnort_ost",
        "kind",
        "arbeitsl_lfdj_m",
        "arbeitsl_vorj_m",
        "arbeitsl_vor2j_m",
        "ges_rente_m",
        "arbeitsstunden_w",
        "anz_kinder_tu",
        "alter",
    ]
    out_col = "arbeitsl_geld_m"
    df = apply_tax_transfer_func(
        df,
        tax_func=ui,
        level=person,
        in_cols=in_cols,
        out_cols=[out_col],
        func_kwargs={
            "params": arbeitsl_geld_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "eink_st_abzuege_params": eink_st_abzuege_params,
            "eink_st_params": eink_st_params,
            "soli_st_params": soli_st_params,
        },
    )
    in_cols = [
        "bruttolohn_m",
        "wohnort_ost",
        "alter",
        "jahr",
        "geburtsjahr",
        "entgeltpunkte",
    ]
    out_col = "rente_anspr_m"
    df = apply_tax_transfer_func(
        df,
        tax_func=pensions,
        level=person,
        in_cols=in_cols,
        out_cols=[out_col],
        func_kwargs={
            "renten_daten": renten_daten,
            "soz_vers_beitr_params": soz_vers_beitr_params,
        },
    )
    in_cols = [
        "bruttolohn_m",
        "eink_selbstst_m",
        "kapital_eink_m",
        "vermiet_eink_m",
        "jahr_renteneintr",
        "ges_rente_m",
        "arbeitsstunden_w",
        "in_ausbildung",
        "gem_veranlagt",
        "kind",
        "betreuungskost_m",
        "prv_rente_beit_m",
        "behinderungsgrad",
        "rentenv_beit_m",
        "arbeitsl_v_beit_m",
        "pflegev_beit_m",
        "alleinerziehend",
        "alter",
        "anz_kinder_tu",
        "jahr",
        "wohnort_ost",
        "ges_krankv_beit_m",
    ]
    out_cols = [
        f"_zu_versteuerndes_eink_{inc}" for inc in eink_st_abzuege_params["eink_arten"]
    ] + [
        "kind_freib",
        "brutto_eink_1",
        "brutto_eink_4",
        "brutto_eink_5",
        "brutto_eink_6",
        "brutto_eink_7",
        "brutto_eink_1_tu",
        "brutto_eink_4_tu",
        "brutto_eink_5_tu",
        "brutto_eink_6_tu",
        "brutto_eink_7_tu",
        "_ertragsanteil",
        "sonder",
        "hh_freib",
        "altersfreib",
        "vorsorge",
    ]
    df = apply_tax_transfer_func(
        df,
        tax_func=zve,
        level=tax_unit,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={
            "eink_st_abzuege_params": eink_st_abzuege_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "kindergeld_params": kindergeld_params,
        },
    )
    in_cols = [
        f"_zu_versteuerndes_eink_{inc}" for inc in eink_st_abzuege_params["eink_arten"]
    ] + ["kind", "brutto_eink_5", "gem_veranlagt", "brutto_eink_5_tu"]
    out_cols = (
        [f"_st_{inc}" for inc in eink_st_abzuege_params["eink_arten"]]
        + [f"_st_{inc}_tu" for inc in eink_st_abzuege_params["eink_arten"]]
        + ["abgelt_st_m_tu", "abgelt_st_m", "soli_st_m", "soli_st_m_tu"]
    )
    df = apply_tax_transfer_func(
        df,
        tax_func=eink_st,
        level=tax_unit,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={
            "eink_st_params": eink_st_params,
            "eink_st_abzuege_params": eink_st_abzuege_params,
            "soli_st_params": soli_st_params,
            "abgelt_st_params": abgelt_st_params,
        },
    )

    in_cols = ["alter", "arbeitsstunden_w", "in_ausbildung", "bruttolohn_m"]
    out_cols = ["kindergeld_m_basis", "kindergeld_m_tu_basis"]
    df = apply_tax_transfer_func(
        df,
        tax_func=kindergeld,
        level=tax_unit,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"params": kindergeld_params},
    )
    in_cols = [f"_st_{inc}_tu" for inc in eink_st_abzuege_params["eink_arten"]] + [
        "gem_veranlagt",
        "kind",
        "abgelt_st_m_tu",
        "kindergeld_m_basis",
        "kindergeld_m_tu_basis",
    ]
    out_cols = [
        "eink_st_m_tu",
        "eink_st_m",
        "kindergeld_m",
        "kindergeld_m_hh",
        "kindergeld_m_tu",
        "kindergeld_anspruch",
    ]
    df = apply_tax_transfer_func(
        df,
        tax_func=favorability_check,
        level=tax_unit,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"params": eink_st_abzuege_params},
    )

    in_cols = [
        "hh_id",
        "tu_id",
        "p_id",
        "kind",
        "bruttolohn_m",
        "bruttolohn_vorj_m",
        "wohnort_ost",
        "eink_st_m",
        "soli_st_m",
        "sozialv_beit_m",
        "geburtsjahr",
        "geburtsmonat",
        "geburtstag",
        "m_elterngeld_mut",
        "m_elterngeld_vat",
        "m_elterngeld",
        "jahr",
    ]
    out_cols = ["elterngeld_m"]

    df = apply_tax_transfer_func(
        df,
        tax_func=elterngeld,
        level=["hh_id"],
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={
            "params": elterngeld_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "eink_st_abzuege_params": eink_st_abzuege_params,
            "eink_st_params": eink_st_params,
            "soli_st_params": soli_st_params,
        },
    )

    in_cols = [
        "alleinerziehend",
        "alter",
        "bruttolohn_m",
        "sonstig_eink_m",
        "kapital_eink_m",
        "vermiet_eink_m",
        "eink_selbstst_m",
        "arbeitsl_geld_m",
        "ges_rente_m",
        "gem_veranlagt",
    ]
    out_col = "unterhaltsvors_m"

    df = apply_tax_transfer_func(
        df,
        tax_func=uhv,
        level=tax_unit,
        in_cols=in_cols,
        out_cols=[out_col],
        func_kwargs={
            "params": unterhalt_params,
            "kindergeld_params": kindergeld_params,
        },
    )
    in_cols = [
        "tu_id",
        "tu_vorstand",
        "kind",
        "kaltmiete_m",
        "heizkost_m",
        "alleinerziehend",
        "alter",
        "kindergeld_anspruch",
        "immobilie_baujahr",
        "mietstufe",
        "bruttolohn_m",
        "ges_rente_m",
        "_ertragsanteil",
        "arbeitsl_geld_m",
        "sonstig_eink_m",
        "unterhaltsvors_m",
        "elterngeld_m",
        "brutto_eink_1",
        "brutto_eink_4",
        "brutto_eink_5",
        "brutto_eink_6",
        "eink_st_m",
        "rentenv_beit_m",
        "ges_krankv_beit_m",
        "behinderungsgrad",
    ]
    out_cols = ["wohngeld_basis", "wohngeld_basis_hh"]
    df = apply_tax_transfer_func(
        df,
        tax_func=wg,
        level=household,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"params": wohngeld_params},
    )
    in_cols = [
        "hh_id",
        "tu_id",
        "p_id",
        "tu_vorstand",
        "kind",
        "alter",
        "kaltmiete_m",
        "heizkost_m",
        "wohnfläche",
        "bewohnt_eigentum",
        "alleinerziehend",
        "bruttolohn_m",
        "ges_rente_m",
        "kapital_eink_m",
        "arbeitsl_geld_m",
        "sonstig_eink_m",
        "eink_selbstst_m",
        "vermiet_eink_m",
        "eink_st_m",
        "soli_st_m",
        "sozialv_beit_m",
        "kindergeld_m_hh",
        "unterhaltsvors_m",
        "elterngeld_m",
    ]
    out_cols = [
        "sum_basis_arbeitsl_geld_2_eink",
        "sum_arbeitsl_geld_2_eink_hh",
        "arbeitsl_geld_2_brutto_eink_hh",
        "alleinerziehenden_mehrbedarf",
        "regelbedarf_m",
        "regelsatz_m",
        "kost_unterk_m",
        "unterhaltsvors_m_hh",
        "eink_anrechn_frei",
        "sum_arbeitsl_geld_2_eink",
    ]
    df = apply_tax_transfer_func(
        df,
        tax_func=alg2,
        level=household,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"params": arbeitsl_geld_2_params},
    )
    in_cols = [
        "p_id",
        "hh_id",
        "tu_id",
        "kind",
        "rentner",
        "alter",
        "arbeitsstunden_w",
        "bruttolohn_m",
        "in_ausbildung",
        "kaltmiete_m",
        "kindergeld_anspruch",
        "heizkost_m",
        "alleinerziehend",
        "alleinerziehenden_mehrbedarf",
        "anz_erw_tu",
        "anz_kinder_tu",
        "arbeitsl_geld_2_brutto_eink_hh",
        "sum_arbeitsl_geld_2_eink_hh",
        "kindergeld_m_hh",
        "unterhaltsvors_m",
    ]
    out_cols = ["kinderzuschlag_temp", "kinderzuschlag_eink_spanne"]
    df = apply_tax_transfer_func(
        df,
        tax_func=kinderzuschlag_params["calc_kiz"],
        level=household,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={
            "params": kinderzuschlag_params,
            "arbeitsl_geld_2_params": arbeitsl_geld_2_params,
        },
    )
    in_cols = [
        "kind",
        "rentner",
        "alter",
        "vermögen_hh",
        "anz_erwachsene_hh",
        "anz_minderj_hh",
        "kinderzuschlag_temp",
        "wohngeld_basis_hh",
        "regelbedarf_m",
        "sum_basis_arbeitsl_geld_2_eink",
        "geburtsjahr",
    ]
    out_cols = ["kinderzuschlag_m", "wohngeld_m", "arbeitsl_geld_2_m"]
    df = apply_tax_transfer_func(
        df,
        tax_func=benefit_priority,
        level=household,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"params": arbeitsl_geld_2_params},
    )
    in_cols = [
        "bruttolohn_m",
        "kapital_eink_m",
        "eink_selbstst_m",
        "vermiet_eink_m",
        # "miete_unterstellt", We need to discuss this!
        "ges_rente_m",
        "sonstig_eink_m",
        "kindergeld_m",
        "unterhaltsvors_m",
        "eink_st_m",
        "soli_st_m",
        "abgelt_st_m",
        "ges_krankv_beit_m",
        "rentenv_beit_m",
        "pflegev_beit_m",
        "arbeitsl_v_beit_m",
        "kinderzuschlag_m",
        "wohngeld_m",
        "arbeitsl_geld_2_m",
    ]
    out_cols = ["verfügb_eink_m", "verfügb_eink_hh_m"]
    df = apply_tax_transfer_func(
        df,
        tax_func=disposable_income,
        level=household,
        in_cols=in_cols,
        out_cols=out_cols,
    )

    required_inputs = [
        "hh_id",
        "tu_id",
        "p_id",
        "tu_vorstand",
        "anz_erwachsene_hh",
        "anz_minderj_hh",
        "vermögen_hh",
        "bruttolohn_m",
        "alter",
        "selbstständig",
        "wohnort_ost",
        "hat_kinder",
        "eink_selbstst_m",
        "ges_rente_m",
        "prv_krankv_beit_m",
        "bruttolohn_vorj_m",
        "arbeitsl_lfdj_m",
        "arbeitsl_vorj_m",
        "arbeitsl_vor2j_m",
        "arbeitsstunden_w",
        "anz_kinder_tu",
        "anz_erw_tu",
        "geburtsjahr",
        "entgeltpunkte",
        "kind",
        "rentner",
        "betreuungskost_m",
        "miete_unterstellt",
        "kapital_eink_m",
        "vermiet_eink_m",
        "kaltmiete_m",
        "heizkost_m",
        "jahr_renteneintr",
        "behinderungsgrad",
        "wohnfläche",
        "gem_veranlagt",
        "in_ausbildung",
        "alleinerziehend",
        "bewohnt_eigentum",
        "immobilie_baujahr",
        "sonstig_eink_m",
    ]
    desired_outputs = [
        "rentenv_beit_m",
        "arbeitsl_v_beit_m",
        "ges_krankv_beit_m",
        "pflegev_beit_m",
        "arbeitsl_geld_m",
        "rente_anspr_m",
        "entgeltpunkte",
        "abgelt_st_m",
        "soli_st_m",
        "soli_st_m_tu",
        "kindergeld_m",
        "kindergeld_m_tu",
        "eink_st_m",
        "eink_st_m_tu",
        "unterhaltsvors_m",
        "regelsatz_m",
        "kost_unterk_m",
        "unterhaltsvors_m_hh",
        "kinderzuschlag_m",
        "wohngeld_m",
        "arbeitsl_geld_2_m",
        "verfügb_eink_m",
        "verfügb_eink_hh_m",
    ]
    return df[required_inputs + desired_outputs]


def calculate_tax_and_transfers(
    dataset, year,
):
    policy_date = date(year, 1, 1)
    renten_daten = lade_exogene_renten_daten()

    eink_st_abzuege_params = get_policies_for_date(
        policy_date=policy_date, group="eink_st_abzuege"
    )

    eink_st_params = get_policies_for_date(policy_date=policy_date, group="eink_st")

    soli_st_params = get_policies_for_date(policy_date=policy_date, group="soli_st")

    arbeitsl_geld_2_params = get_policies_for_date(
        policy_date=policy_date, group="arbeitsl_geld_2"
    )

    arbeitsl_geld_params = get_policies_for_date(
        policy_date=policy_date, group="arbeitsl_geld"
    )

    soz_vers_beitr_params = get_policies_for_date(
        policy_date=policy_date, group="soz_vers_beitr"
    )

    unterhalt_params = get_policies_for_date(policy_date=policy_date, group="unterhalt")

    abgelt_st_params = get_policies_for_date(policy_date=policy_date, group="abgelt_st")

    wohngeld_params = get_policies_for_date(policy_date=policy_date, group="wohngeld")

    kinderzuschlag_params = get_policies_for_date(
        policy_date=policy_date, group="kinderzuschlag"
    )

    kindergeld_params = get_policies_for_date(
        policy_date=policy_date, group="kindergeld"
    )

    elterngeld_params = get_policies_for_date(
        policy_date=policy_date, group="elterngeld"
    )

    return tax_transfer(
        dataset,
        arbeitsl_geld_2_params=arbeitsl_geld_2_params,
        abgelt_st_params=abgelt_st_params,
        arbeitsl_geld_params=arbeitsl_geld_params,
        soz_vers_beitr_params=soz_vers_beitr_params,
        eink_st_abzuege_params=eink_st_abzuege_params,
        elterngeld_params=elterngeld_params,
        unterhalt_params=unterhalt_params,
        wohngeld_params=wohngeld_params,
        kinderzuschlag_params=kinderzuschlag_params,
        eink_st_params=eink_st_params,
        soli_st_params=soli_st_params,
        kindergeld_params=kindergeld_params,
        renten_daten=renten_daten,
    )
