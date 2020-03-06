from gettsim.apply_tax_funcs import apply_tax_transfer_func
from gettsim.benefits.alg2 import alg2
from gettsim.benefits.arbeitslosengeld import ui
from gettsim.benefits.benefit_checks import benefit_priority
from gettsim.benefits.elterngeld import elterngeld
from gettsim.benefits.kiz import kiz
from gettsim.benefits.unterhaltsvorschuss import uhv
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
    bool_variables = ["child", "east"]
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
        "m_wage",
        "east",
        "age",
        "selfemployed",
        "haskids",
        "m_self",
        "m_pensions",
        "pkv",
    ]
    out_cols = ["svbeit", "rvbeit", "avbeit", "gkvbeit", "pvbeit"]
    df = apply_tax_transfer_func(
        df,
        tax_func=soc_ins_contrib,
        level=person,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"params": soz_vers_beitr_params},
    )

    in_cols = [
        "m_wage_l1",
        "east",
        "child",
        "months_ue",
        "months_ue_l1",
        "months_ue_l2",
        "m_pensions",
        "w_hours",
        "child_num_tu",
        "age",
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
    in_cols = ["m_wage", "east", "age", "year", "byear", "exper", "EP"]
    out_col = "pensions_sim"
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
        "m_wage",
        "m_self",
        "m_kapinc",
        "m_vermiet",
        "renteneintritt",
        "m_pensions",
        "w_hours",
        "ineducation",
        "zveranl",
        "child",
        "m_childcare",
        "priv_pens_contr",
        "handcap_degree",
        "rvbeit",
        "avbeit",
        "pvbeit",
        "alleinerz",
        "age",
        "child_num_tu",
        "year",
        "east",
        "gkvbeit",
    ]
    out_cols = [f"zve_{inc}" for inc in e_st_abzuege_params["zve_list"]] + [
        "kifreib",
        "gross_e1",
        "gross_e4",
        "gross_e5",
        "gross_e6",
        "gross_e7",
        "gross_e1_tu",
        "gross_e4_tu",
        "gross_e5_tu",
        "gross_e6_tu",
        "gross_e7_tu",
        "ertragsanteil",
        "sonder",
        "hhfreib",
        "altfreib",
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
    in_cols = [f"zve_{inc}" for inc in e_st_abzuege_params["zve_list"]] + [
        "child",
        "gross_e5",
        "zveranl",
        "gross_e5_tu",
    ]
    out_cols = (
        [f"tax_{inc}" for inc in e_st_abzuege_params["zve_list"]]
        + [f"tax_{inc}_tu" for inc in e_st_abzuege_params["zve_list"]]
        + ["abgelt_st_tu", "abgelt_st", "soli", "soli_tu"]
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

    in_cols = ["age", "w_hours", "ineducation", "m_wage"]
    out_cols = ["kindergeld_basis", "kindergeld_tu_basis"]
    df = apply_tax_transfer_func(
        df,
        tax_func=kindergeld,
        level=tax_unit,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"params": kindergeld_params},
    )
    in_cols = [f"tax_{inc}_tu" for inc in e_st_abzuege_params["zve_list"]] + [
        "zveranl",
        "child",
        "abgelt_st_tu",
        "kindergeld_basis",
        "kindergeld_tu_basis",
    ]
    out_cols = [
        "incometax_tu",
        "incometax",
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
        "child",
        "m_wage",
        "m_wage_l1",
        "east",
        "incometax",
        "soli",
        "svbeit",
        "byear",
        "bmonth",
        "bday",
        "elterngeld_mon_mut",
        "elterngeld_mon_vat",
        "elterngeld_mon",
        "year",
    ]
    out_cols = ["elterngeld", "geschw_bonus", "num_mehrlinge", "elternzeit_anspruch"]

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
        "alleinerz",
        "age",
        "m_wage",
        "m_transfers",
        "m_kapinc",
        "m_vermiet",
        "m_self",
        "m_alg1",
        "m_pensions",
        "zveranl",
    ]
    out_col = "uhv"
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
        "child",
        "miete",
        "heizkost",
        "alleinerz",
        "age",
        "cnstyr",
        "mietstufe",
        "m_wage",
        "m_pensions",
        "ertragsanteil",
        "m_alg1",
        "m_transfers",
        "uhv",
        "elterngeld",
        "gross_e1",
        "gross_e4",
        "gross_e5",
        "gross_e6",
        "incometax",
        "rvbeit",
        "gkvbeit",
        "handcap_degree",
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
        "child",
        "age",
        "miete",
        "heizkost",
        "wohnfl",
        "eigentum",
        "alleinerz",
        "m_wage",
        "m_pensions",
        "m_kapinc",
        "m_alg1",
        "m_transfers",
        "m_self",
        "m_vermiet",
        "incometax",
        "soli",
        "svbeit",
        "kindergeld_hh",
        "uhv",
        "elterngeld",
    ]
    out_cols = [
        "ar_base_alg2_ek",
        "ar_alg2_ek_hh",
        "alg2_grossek_hh",
        "mehrbed",
        "regelbedarf",
        "regelsatz",
        "alg2_kdu",
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
        "head",
        "child",
        "pensioner",
        "age",
        "w_hours",
        "m_wage",
        "ineducation",
        "miete",
        "heizkost",
        "alleinerz",
        "mehrbed",
        "adult_num_tu",
        "child_num_tu",
        "alg2_grossek_hh",
        "ar_alg2_ek_hh",
        "kindergeld_hh",
        "uhv",
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
        "child",
        "pensioner",
        "age",
        "hh_wealth",
        "adult_num",
        "child0_18_num",
        "kiz_temp",
        "wohngeld_basis_hh",
        "regelbedarf",
        "ar_base_alg2_ek",
        "byear",
    ]
    out_cols = ["kiz", "wohngeld", "m_alg2"]
    df = apply_tax_transfer_func(
        df,
        tax_func=benefit_priority,
        level=household,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"params": arbeitsl_geld_2_params},
    )
    in_cols = [
        "m_wage",
        "m_kapinc",
        "m_self",
        "m_vermiet",
        # "m_imputedrent", We need to discuss this!
        "m_pensions",
        "m_transfers",
        "kindergeld",
        "uhv",
        "incometax",
        "soli",
        "abgelt_st",
        "gkvbeit",
        "rvbeit",
        "pvbeit",
        "avbeit",
        "kiz",
        "wohngeld",
        "m_alg2",
    ]
    out_cols = ["dpi_ind", "dpi"]
    df = apply_tax_transfer_func(
        df,
        tax_func=disposable_income,
        level=household,
        in_cols=in_cols,
        out_cols=out_cols,
    )
    in_cols = [
        "m_wage",
        "m_kapinc",
        "m_self",
        "m_vermiet",
        "m_imputedrent",
        "m_pensions",
        "m_transfers",
        "kindergeld",
    ]
    out_col = "gross"
    df = apply_tax_transfer_func(
        df, tax_func=gross_income, level=household, in_cols=in_cols, out_cols=[out_col]
    )
    required_inputs = [
        "hid",
        "tu_id",
        "pid",
        "head_tu",
        "head",
        "adult_num",
        "child0_18_num",
        "hh_wealth",
        "m_wage",
        "age",
        "selfemployed",
        "east",
        "haskids",
        "m_self",
        "m_pensions",
        "pkv",
        "m_wage_l1",
        "months_ue",
        "months_ue_l1",
        "months_ue_l2",
        "w_hours",
        "child_num_tu",
        "adult_num_tu",
        "byear",
        "exper",
        "EP",
        "child",
        "pensioner",
        "m_childcare",
        "m_imputedrent",
        "m_kapinc",
        "m_vermiet",
        "miete",
        "heizkost",
        "renteneintritt",
        "handcap_degree",
        "wohnfl",
        "zveranl",
        "ineducation",
        "alleinerz",
        "eigentum",
        "cnstyr",
        "m_transfers",
    ]
    desired_outputs = [
        "svbeit",
        "rvbeit",
        "avbeit",
        "gkvbeit",
        "m_alg1",
        "pensions_sim",
        "gross_e1",
        "gross_e5",
        "gross_e6",
        "gross_e7",
        "gross_e1_tu",
        "gross_e4_tu",
        "gross_e5_tu",
        "gross_e6_tu",
        "gross_e7_tu",
        "abgelt_st_tu",
        "abgelt_st",
        "soli",
        "soli_tu",
        "kindergeld",
        "kindergeld_tu",
        "incometax",
        "incometax_tu",
        "uhv",
        "regelbedarf",
        "regelsatz",
        "alg2_kdu",
        "uhv_hh",
        "kiz",
        "wohngeld",
        "m_alg2",
        "dpi_ind",
        "dpi",
        "gross",
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
