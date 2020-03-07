from gettsim.apply_tax_funcs import apply_tax_transfer_func
from gettsim.benefits.arbeitsl_geld import ui
from gettsim.benefits.arbeitsl_geld_2 import alg2
from gettsim.benefits.benefit_checks import benefit_priority
from gettsim.benefits.elterngeld import elterngeld
from gettsim.benefits.kinderzuschlag import kiz
from gettsim.benefits.unterhalt import uhv
from gettsim.benefits.wohngeld import wg
from gettsim.checks import check_boolean
from gettsim.incomes import disposable_income
from gettsim.incomes import gross_income
from gettsim.pensions import pensions
from gettsim.policy_for_date import get_policies_for_date
from gettsim.social_insurance import soc_ins_contrib
from gettsim.taxes.e_st import e_st
from gettsim.taxes.favorability_check import favorability_check
from gettsim.taxes.kindergeld import kindergeld
from gettsim.taxes.zve import zve


def tax_transfer(
    df,
    arbeitsl_geld_2_params,
    abgelt_st_params,
    arbeitsl_geld_params,
    soz_vers_beitr_params,
    e_st_abzuege_params,
    elterngeld_params,
    unterhalt_params,
    wohngeld_params,
    kinderzuschlag_params,
    e_st_params,
    soli_st_params,
    kindergeld_params,
    ges_renten_vers_params,
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
    bool_variables = ["kind", "ostdeutsch"]
    check_boolean(df, bool_variables)
    # if hyporun is False:
    # df = uprate(df, datayear, settings['taxyear'], settings['MAIN_PATH'])

    # We initialize all output columns.
    # for column in OUT_PUT:
    # df[column] = 0.0
    household = ["hid"]
    tax_unit = ["hid", "tu_id"]
    person = ["hid", "tu_id", "pid"]
    if df.groupby(person).ngroups != len(df):
        raise ValueError(
            "Household, tax unit and person identifier don't provide "
            "distinguishable individuals."
        )
    # We start with the top layer, which is household id. We treat this as the
    # "Bedarfsgemeinschaft" in German tax law.
    in_cols = [
        "lohn_m",
        "ostdeutsch",
        "alter",
        "selbstständig",
        "hat_kinder",
        "eink_selbstst_m",
        "rente_m",
        "prv_krank_vers",
    ]
    out_cols = [
        "sozialv_beit_m",
        "rentenv_beit_m",
        "arbeitsl_beit_m",
        "krankv_beit_m",
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
        "m_arbeitsl",
        "ostdeutsch",
        "kind",
        "m_arbeitsl",
        "m_arbeitsl_vorj",
        "m_arbeitsl_vor2j",
        "rente_m",
        "arbeitsstund_w",
        "anz_kinder_tu",
        "alter",
    ]
    out_col = "m_alg1"
    df = apply_tax_transfer_func(
        df,
        tax_func=ui,
        level=person,
        in_cols=in_cols,
        out_cols=[out_col],
        func_kwargs={
            "params": arbeitsl_geld_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "e_st_abzuege_params": e_st_abzuege_params,
            "e_st_params": e_st_params,
            "soli_st_params": soli_st_params,
        },
    )
    in_cols = ["lohn_m", "ostdeutsch", "alter", "year", "geburtsjahr", "exper", "EP"]
    out_col = "rente_anspr_m"
    df = apply_tax_transfer_func(
        df,
        tax_func=pensions,
        level=person,
        in_cols=in_cols,
        out_cols=[out_col],
        func_kwargs={
            "params": ges_renten_vers_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
        },
    )
    in_cols = [
        "lohn_m",
        "eink_selbstst_m",
        "kapital_eink_m",
        "vermiet_eink_m",
        "rente_eint_jahr",
        "rente_m",
        "arbeitsstund_w",
        "in_ausbildung",
        "gem_veranlagt",
        "kind",
        "kind_betr_kost_m",
        "prv_rente_beit_m",
        "behinderungsgrad",
        "rentenv_beit_m",
        "arbeitsl_beit_m",
        "pflegev_beit_m",
        "alleinerziehend",
        "alter",
        "anz_kinder_tu",
        "year",
        "ostdeutsch",
        "krankv_beit_m",
    ]
    out_cols = [
        f"_zu_versteuerndes_eink_{inc}" for inc in e_st_abzuege_params["eink_arten"]
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
            "e_st_abzuege_params": e_st_abzuege_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "kindergeld_params": kindergeld_params,
        },
    )
    in_cols = [
        f"_zu_versteuerndes_eink_{inc}" for inc in e_st_abzuege_params["eink_arten"]
    ] + ["kind", "brutto_eink_5", "gem_veranlagt", "brutto_eink_5_tu"]
    out_cols = (
        [f"_st_{inc}" for inc in e_st_abzuege_params["eink_arten"]]
        + [f"_st_{inc}_tu" for inc in e_st_abzuege_params["eink_arten"]]
        + ["abgelt_st_tu", "abgelt_st", "soli_st", "soli_st_tu"]
    )
    df = apply_tax_transfer_func(
        df,
        tax_func=e_st,
        level=tax_unit,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={
            "e_st_params": e_st_params,
            "e_st_abzuege_params": e_st_abzuege_params,
            "soli_st_params": soli_st_params,
            "abgelt_st_params": abgelt_st_params,
        },
    )

    in_cols = ["alter", "arbeitsstund_w", "in_ausbildung", "lohn_m"]
    out_cols = ["kindergeld_basis", "kindergeld_tu_basis"]
    df = apply_tax_transfer_func(
        df,
        tax_func=kindergeld,
        level=tax_unit,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"params": kindergeld_params},
    )
    in_cols = [f"_st_{inc}_tu" for inc in e_st_abzuege_params["eink_arten"]] + [
        "gem_veranlagt",
        "kind",
        "abgelt_st_tu",
        "kindergeld_basis",
        "kindergeld_tu_basis",
    ]
    out_cols = [
        "eink_st_tu",
        "eink_st",
        "kindergeld",
        "kindergeld_hh",
        "kindergeld_tu",
    ]
    df = apply_tax_transfer_func(
        df,
        tax_func=favorability_check,
        level=tax_unit,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"params": e_st_abzuege_params},
    )

    in_cols = [
        "hid",
        "tu_id",
        "pid",
        "kind",
        "lohn_m",
        "dur_eink_vorj_m",
        "ostdeutsch",
        "eink_st",
        "soli_st",
        "sozialv_beit_m",
        "geburtsjahr",
        "geburtsmonat",
        "geburtstag",
        "elterngeld_mon_mut",
        "elterngeld_mon_vat",
        "elterngeld_mon",
        "year",
    ]
    out_cols = ["elterngeld", "geschw_bonus", "anz_mehrlinge", "elternzeit_anspruch"]

    df = apply_tax_transfer_func(
        df,
        tax_func=elterngeld,
        level=["hid"],
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={
            "params": elterngeld_params,
            "soz_vers_beitr_params": soz_vers_beitr_params,
            "e_st_abzuege_params": e_st_abzuege_params,
            "e_st_params": e_st_params,
            "soli_st_params": soli_st_params,
        },
    )

    in_cols = [
        "alleinerziehend",
        "alter",
        "lohn_m",
        "m_transfers",
        "kapital_eink_m",
        "vermiet_eink_m",
        "eink_selbstst_m",
        "arbeitsl_geld_m",
        "rente_m",
        "gem_veranlagt",
    ]
    out_col = "unterhalt_vors_m"
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
        "head_tu",
        "kind",
        "kaltmiete_m",
        "heizkost",
        "alleinerziehend",
        "alter",
        "baujahr",
        "mietstufe",
        "lohn_m",
        "rente_m",
        "_ertragsanteil",
        "arbeitsl_geld_m",
        "sonstig_eink_m",
        "unterhalt_vors_m",
        "elterngeld",
        "brutto_eink_1",
        "brutto_eink_4",
        "brutto_eink_5",
        "brutto_eink_6",
        "eink_st",
        "rentenv_beit_m",
        "krankv_beit_m",
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
        "hid",
        "pid",
        "head_tu",
        "kind",
        "alter",
        "kaltmiete_m",
        "heizkost",
        "wohnfläche",
        "wohneigentum",
        "alleinerziehend",
        "lohn_m",
        "rente_m",
        "kapital_eink_m",
        "arbeitsl_geld_m",
        "sonstig_eink_m",
        "eink_selbstst_m",
        "vermiet_eink_m",
        "eink_st",
        "soli_st",
        "sozialv_beit_m",
        "kindergeld_hh",
        "unterhalt_vors_m",
        "elterngeld",
    ]
    out_cols = [
        "ar_base_alg2_ek",
        "ar_alg2_ek_hh",
        "alg2_grossek_hh",
        "mehrbed",
        "regelbedarf_m",
        "regelsatz_m",
        "kost_unterk_m",
        "uhv_hh",
        "ekanrefrei",
        "ar_alg2_ek",
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
        "pid",
        "hid",
        "tu_id",
        "kind",
        "rentner",
        "alter",
        "arbeitsstund_w",
        "lohn_m",
        "in_ausbildung",
        "kaltmiete_m",
        "heizkost_m",
        "alleinerziehend",
        "mehrbed",
        "anz_erw_tu",
        "anz_kinder_tu",
        "alg2_grossek_hh",
        "ar_alg2_ek_hh",
        "kindergeld_hh",
        "unterhalt_vors_m",
    ]
    out_cols = ["kiz_temp", "kiz_incrange"]
    df = apply_tax_transfer_func(
        df,
        tax_func=kiz,
        level=household,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={
            "params": kinderzuschlag_params,
            "arbeitsl_geld_2_params": arbeitsl_geld_2_params,
            "kindergeld_params": kindergeld_params,
        },
    )
    in_cols = [
        "kind",
        "rentner",
        "alter",
        "hh_vermögen",
        "anz_erw_hh",
        "anz_minderj_hh",
        "kiz_temp",
        "wohngeld_basis_hh",
        "regelbedarf_m",
        "ar_base_alg2_ek",
        "geburtsjahr",
    ]
    out_cols = ["kinderzuschlag_m", "wohngeld", "arbeitsl_geld_2_m"]
    df = apply_tax_transfer_func(
        df,
        tax_func=benefit_priority,
        level=household,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"params": arbeitsl_geld_2_params},
    )
    in_cols = [
        "lohn_m",
        "kapital_eink_m",
        "eink_selbstst_m",
        "vermiet_eink_m",
        # "eigenheim_ersp_m", We need to discuss this!
        "rente_m",
        "sonstig_eink_m",
        "kindergeld",
        "unterhalt_vors_m",
        "eink_st",
        "soli_st",
        "abgelt_st",
        "krankv_beit_m",
        "rentenv_beit_m",
        "pflegev_beit_m",
        "arbeitsl_beit_m",
        "kinderzuschlag_m",
        "wohngeld_m",
        "arbeitsl_geld_2_m",
    ]
    out_cols = ["verfüg_eink_m", "verfüg_eink_hh_m"]
    df = apply_tax_transfer_func(
        df,
        tax_func=disposable_income,
        level=household,
        in_cols=in_cols,
        out_cols=out_cols,
    )
    in_cols = [
        "lohn_m",
        "kapital_eink_m",
        "eink_selbstst_m",
        "vermiet_eink_m",
        "eigenheim_ersp_m",
        "rente_m",
        "sonstig_eink_m",
        "kindergeld",
    ]
    out_col = "brutto_eink"
    df = apply_tax_transfer_func(
        df, tax_func=gross_income, level=household, in_cols=in_cols, out_cols=[out_col]
    )
    required_inputs = [
        "hid",
        "tu_id",
        "pid",
        "tu_vorstand",
        "anz_erw_hh",
        "anz_minderj_hh",
        "hh_vermögen",
        "lohn_m",
        "alter",
        "selbstständig",
        "ostdeutsch",
        "hat_kinder",
        "eink_selbstst_m",
        "rente_m",
        "prv_krank_vers",
        "dur_eink_vorj_m",
        "m_arbeitsl",
        "m_arbeitsl_vorj",
        "m_arbeitsl_vor2j",
        "arbeitsstund_w",
        "anz_kinder_tu",
        "anz_erw_tu",
        "geburtsjahr",
        "EP",
        "kind",
        "rentner",
        "kind_betr_kost_m",
        "eigenheim_ersp_m",
        "kapital_eink_m",
        "vermiet_eink_m",
        "kaltmiete_m",
        "heizkost_m",
        "rente_eint_jahr",
        "behinderungsgrad",
        "wohnfläche",
        "gem_veranlagt",
        "in_ausbildung",
        "alleinerziehend",
        "wohneigentum",
        "baujahr",
        "sonstig_eink_m",
    ]
    desired_outputs = [
        "sozialv_beit_m",
        "rentenv_beit_m",
        "arbeitsl_beit_m",
        "krankv_beit_m",
        "arbeitsl_geld_m",
        "rente_anspr_m",
        "brutto_eink_1",
        "brutto_eink_5",
        "brutto_eink_6",
        "brutto_eink_7",
        "brutto_eink_1_tu",
        "brutto_eink_4_tu",
        "brutto_eink_5_tu",
        "brutto_eink_6_tu",
        "brutto_eink_7_tu",
        "abgelt_st_tu",
        "abgelt_st",
        "soli_st",
        "soli_st_tu",
        "kindergeld",
        "kindergeld_tu",
        "eink_st",
        "eink_st_tu",
        "unterhalt_vors_m",
        "regelbedarf_m",
        "regelsatz_m",
        "kost_unterk_m",
        "uhv_hh",
        "kinderzuschlag_m",
        "wohngeld_m",
        "arbeitsl_geld_2_m",
        "verfüg_eink_m",
        "verfüg_eink_hh_m",
        "brutto_eink",
    ]
    return df[required_inputs + desired_outputs]


def calculate_tax_and_transfers(
    dataset, year,
):
    ges_renten_vers_params = get_policies_for_date(year=year, group="ges_renten_vers")

    e_st_abzuege_params = get_policies_for_date(year=year, group="e_st_abzuege")

    e_st_params = get_policies_for_date(year=year, group="e_st")

    soli_st_params = get_policies_for_date(year=year, group="soli_st")

    arbeitsl_geld_2_params = get_policies_for_date(year=year, group="arbeitsl_geld_2")

    arbeitsl_geld_params = get_policies_for_date(year=year, group="arbeitsl_geld")

    soz_vers_beitr_params = get_policies_for_date(year=year, group="soz_vers_beitr")

    unterhalt_params = get_policies_for_date(year=year, group="unterhalt")

    abgelt_st_params = get_policies_for_date(year=year, group="abgelt_st")

    wohngeld_params = get_policies_for_date(year=year, group="wohngeld")

    kinderzuschlag_params = get_policies_for_date(year=year, group="kinderzuschlag")

    kindergeld_params = get_policies_for_date(year=year, group="kindergeld")

    elterngeld_params = get_policies_for_date(year=year, group="elterngeld")

    return tax_transfer(
        dataset,
        arbeitsl_geld_2_params=arbeitsl_geld_2_params,
        abgelt_st_params=abgelt_st_params,
        arbeitsl_geld_params=arbeitsl_geld_params,
        soz_vers_beitr_params=soz_vers_beitr_params,
        e_st_abzuege_params=e_st_abzuege_params,
        elterngeld_params=elterngeld_params,
        unterhalt_params=unterhalt_params,
        wohngeld_params=wohngeld_params,
        kinderzuschlag_params=kinderzuschlag_params,
        e_st_params=e_st_params,
        soli_st_params=soli_st_params,
        kindergeld_params=kindergeld_params,
        ges_renten_vers_params=ges_renten_vers_params,
    )
