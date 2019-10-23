import numpy as np

from gettsim.benefits.alg2 import alg2
from gettsim.benefits.arbeitslosengeld import ui
from gettsim.benefits.benefit_checks import benefit_priority
from gettsim.benefits.kiz import kiz
from gettsim.benefits.unterhaltsvorschuss import uhv
from gettsim.benefits.wohngeld import wg
from gettsim.func_out_columns import ALG2
from gettsim.func_out_columns import BP
from gettsim.func_out_columns import DPI
from gettsim.func_out_columns import FC
from gettsim.func_out_columns import GROSS
from gettsim.func_out_columns import KIZ
from gettsim.func_out_columns import UHV
from gettsim.func_out_columns import WG
from gettsim.incomes import disposable_income
from gettsim.incomes import gross_income
from gettsim.pensions import pensions
from gettsim.social_insurance import soc_ins_contrib
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
    # household = ["hid"]
    tax_unit = ["hid", "tu_id"]
    person = ["hid", "tu_id", "pid"]
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
    for col in out_cols:
        df[col] = np.nan
    df = df.groupby(person)[in_cols + out_cols].apply(soc_ins_contrib, tb=tb)
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
    df[out_col] = np.nan
    df = df.groupby(person)[in_cols + [out_col]].apply(ui, tb=tb)
    in_cols = ["m_wage", "east", "age", "year", "byear", "exper", "EP"]
    out_col = "pensions_sim"
    df[out_col] = np.nan
    df = df.groupby(person)[in_cols + [out_col]].apply(pensions, tb=tb)
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
    df = df.groupby(tax_unit)[in_cols + out_cols].apply(zve, tb=tb)
    in_cols = ["age", "w_hours", "ineducation", "m_wage"]
    out_cols = ["kindergeld_basis", "kindergeld_tu_basis"]
    for col in out_cols:
        df[col] = np.nan
    df = df.groupby(tax_unit)[in_cols + out_cols].apply(kindergeld, tb=tb)

    for hid in df["hid"].unique():
        hh_indices = df[df["hid"] == hid].index
        for tu_id in df.loc[hh_indices, "tu_id"].unique():
            tu_indices = df[df["tu_id"] == tu_id].index

            # 5.4 Günstigerprüfung to obtain final income tax due.
            # different call here, because 'kindergeld' is overwritten by the
            # function and needs to be updated. not really elegant I must admit...
            df.loc[tu_indices, FC] = favorability_check(df.loc[tu_indices, :], tb)

            # 6. SOCIAL TRANSFERS / BENEFITS
            # 6.0.1 Alimony Advance (Unterhaltsvorschuss)
            df.loc[tu_indices, UHV] = uhv(df.loc[tu_indices, :], tb)

        # 6.1. Wohngeld, Housing Benefit
        df.loc[hh_indices, WG] = wg(df.loc[hh_indices, :], tb)

        # 6.2 ALG2, Basic Unemployment Benefit
        df.loc[hh_indices, ALG2] = alg2(df.loc[hh_indices, :], tb)

        # 6.3. Kinderzuschlag, Additional Child Benefit
        df.loc[hh_indices, KIZ] = kiz(df.loc[hh_indices, :], tb)

        df.loc[hh_indices, BP] = benefit_priority(df.loc[hh_indices, :], tb)

        # 8. Calculate disposable income
        df.loc[hh_indices, DPI] = disposable_income(df.loc[hh_indices, :])

    df[GROSS] = gross_income(df)

    return df
