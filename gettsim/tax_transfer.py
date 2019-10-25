import numpy as np

from gettsim.benefits.alg2 import alg2
from gettsim.benefits.arbeitslosengeld import ui
from gettsim.benefits.benefit_checks import benefit_priority
from gettsim.benefits.kiz import kiz
from gettsim.benefits.unterhaltsvorschuss import uhv
from gettsim.benefits.wohngeld import wg
from gettsim.incomes import disposable_income
from gettsim.incomes import gross_income
from gettsim.pensions import pensions
from gettsim.social_insurance import soc_ins_contrib
from gettsim.taxes.calc_taxes import tax_sched
from gettsim.taxes.favorability_check import favorability_check
from gettsim.taxes.kindergeld import kindergeld
from gettsim.taxes.zve import zve


def tax_transfer(df, tb, tb_pens=None):
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

    # set default arguments
    tb_pens = [] if tb_pens is None else tb_pens
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
    df = _apply_tax_transfer_func(
        df,
        tax_func=soc_ins_contrib,
        level=person,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"tb": tb},
    )
    in_cols = [
        "m_wage_l1",
        "east",
        "child",
        "months_ue",
        "months_ue_l1",
        "months_ue_l2",
        "alg_soep",
        "m_pensions",
        "w_hours",
        "child_num_tu",
        "age",
    ]
    out_col = "m_alg1"
    df = _apply_tax_transfer_func(
        df,
        tax_func=ui,
        level=person,
        in_cols=in_cols,
        out_cols=[out_col],
        func_kwargs={"tb": tb},
    )
    in_cols = ["m_wage", "east", "age", "year", "byear", "exper", "EP"]
    out_col = "pensions_sim"
    df = _apply_tax_transfer_func(
        df,
        tax_func=pensions,
        level=person,
        in_cols=in_cols,
        out_cols=[out_col],
        func_kwargs={"tb": tb, "tb_pens": tb_pens},
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
    out_cols = [
        "zve_nokfb",
        "zve_abg_nokfb",
        "zve_kfb",
        "zve_abg_kfb",
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
    df = _apply_tax_transfer_func(
        df,
        tax_func=zve,
        level=tax_unit,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"tb": tb},
    )
    in_cols = [
        "child",
        "zve_nokfb",
        "zve_kfb",
        "zve_abg_kfb",
        "zve_abg_nokfb",
        "gross_e5",
        "zveranl",
        "gross_e5_tu",
    ]
    out_cols = (
        [f"tax_{inc}" for inc in tb["zve_list"]]
        + [f"tax_{inc}_tu" for inc in tb["zve_list"]]
        + ["abgst_tu", "abgst", "soli", "soli_tu"]
    )
    df = _apply_tax_transfer_func(
        df,
        tax_func=tax_sched,
        level=tax_unit,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"tb": tb},
    )
    in_cols = ["age", "w_hours", "ineducation", "m_wage"]
    out_cols = ["kindergeld_basis", "kindergeld_tu_basis"]
    df = _apply_tax_transfer_func(
        df,
        tax_func=kindergeld,
        level=tax_unit,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"tb": tb},
    )
    in_cols = [
        "zveranl",
        "child",
        "tax_nokfb_tu",
        "tax_kfb_tu",
        "abgst_tu",
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
    df = _apply_tax_transfer_func(
        df,
        tax_func=favorability_check,
        level=tax_unit,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"tb": tb},
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
    df = _apply_tax_transfer_func(
        df,
        tax_func=uhv,
        level=tax_unit,
        in_cols=in_cols,
        out_cols=[out_col],
        func_kwargs={"tb": tb},
    )
    in_cols = [
        "tu_id",
        "head_tu",
        "hh_korr",
        "hhsize",
        "child",
        "miete",
        "heizkost",
        "alleinerz",
        "child11_num_tu",
        "cnstyr",
        "mietstufe",
        "m_wage",
        "m_pensions",
        "ertragsanteil",
        "m_alg1",
        "m_transfers",
        "uhv",
        "gross_e1",
        "gross_e4",
        "gross_e5",
        "gross_e6",
        "incometax",
        "rvbeit",
        "gkvbeit",
        "handcap_degree",
        "divdy",
        "hhsize_tu",
    ]
    out_cols = ["wohngeld_basis", "wohngeld_basis_hh"]
    df = _apply_tax_transfer_func(
        df,
        tax_func=wg,
        level=household,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"tb": tb},
    )
    in_cols = [
        "hid",
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
    ]
    df = _apply_tax_transfer_func(
        df,
        tax_func=alg2,
        level=household,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"tb": tb},
    )
    in_cols = [
        "pid",
        "hid",
        "tu_id",
        "head",
        "hhtyp",
        "hh_korr",
        "hhsize",
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
    df = _apply_tax_transfer_func(
        df,
        tax_func=kiz,
        level=household,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"tb": tb},
    )
    in_cols = [
        "hh_korr",
        "hhsize",
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
    df = _apply_tax_transfer_func(
        df,
        tax_func=benefit_priority,
        level=household,
        in_cols=in_cols,
        out_cols=out_cols,
        func_kwargs={"tb": tb},
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
        "abgst",
        "gkvbeit",
        "rvbeit",
        "pvbeit",
        "avbeit",
        "kiz",
        "wohngeld",
        "m_alg2",
    ]
    out_cols = ["dpi_ind", "dpi"]
    df = _apply_tax_transfer_func(
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
    df = _apply_tax_transfer_func(
        df, tax_func=gross_income, level=household, in_cols=in_cols, out_cols=[out_col]
    )

    return df


def _apply_tax_transfer_func(
    df, tax_func, level, in_cols, out_cols, func_args=None, func_kwargs=None
):
    func_args = [] if func_args is None else func_args
    func_kwargs = {} if func_kwargs is None else func_kwargs
    for col in out_cols:
        df[col] = np.nan
    df.loc[:, in_cols + out_cols] = df.groupby(level)[in_cols + out_cols].apply(
        _apply_squeeze_function, tax_func, level, func_args, func_kwargs
    )
    return df


def _apply_squeeze_function(group, tax_func, level, func_args, func_kwargs):
    if level == ["hid", "tu_id", "pid"]:
        person = tax_func(group.squeeze(), *func_args, **func_kwargs)
        for var in person.index:
            group.loc[:, var] = person[var]
        return group
    else:
        return tax_func(group, *func_args, **func_kwargs)
