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
from gettsim.func_out_columns import KG
from gettsim.func_out_columns import KIZ
from gettsim.func_out_columns import PENS
from gettsim.func_out_columns import SOC_SEC
from gettsim.func_out_columns import TAX_SCHED
from gettsim.func_out_columns import UHV
from gettsim.func_out_columns import UI
from gettsim.func_out_columns import WG
from gettsim.func_out_columns import ZVE
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
    # household = ["hid"]
    # tax_unit = ["hid", "tu_id"]
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
    df.groupby(person)[in_cols + out_cols].apply(soc_ins_contrib, tb=tb, axis=1)

    for hid in df["hid"].unique():
        hh_indices = df[df["hid"] == hid].index
        for tu_id in df.loc[hh_indices, "tu_id"].unique():
            tu_indices = df[df["tu_id"] == tu_id].index
            for i in tu_indices:

                df.loc[i, SOC_SEC] = soc_ins_contrib(df.loc[i], tb)
                # Unemployment benefits
                df.loc[i, UI] = ui(df.loc[i], tb)
                # Pension benefits
                df.loc[i, PENS] = pensions(df.loc[i], tb, tb_pens)

            # Tax unit based calculations
            # 5.1 Calculate Taxable income (zve = zu versteuerndes Einkommen)
            df.loc[tu_indices, ZVE] = zve(df.loc[tu_indices, :], tb)

            # 5.2 Apply Tax Schedule. returns incometax, capital income tax and soli
            df.loc[tu_indices, TAX_SCHED] = tax_sched(df.loc[tu_indices, :], tb)

            # 5.3 Child benefit (Kindergeld). Yes, this belongs to Income Tax
            df.loc[tu_indices, KG] = kindergeld(df.loc[tu_indices, :], tb)

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
