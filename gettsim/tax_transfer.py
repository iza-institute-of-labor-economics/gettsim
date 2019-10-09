import numpy as np

from gettsim.benefits.alg2 import alg2
from gettsim.benefits.arbeitslosengeld import ui
from gettsim.benefits.kiz import kiz
from gettsim.benefits.unterhaltsvorschuss import uhv
from gettsim.benefits.wohngeld import wg
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

    # We start with the top layer, which is household id. We treat this as the
    # "Bedarfsgemeinschaft" in the german tax law.
    for hid in df["hid"].unique():
        df_hh = df[df["hid"] == hid]
        for tu_id in df_hh["tu_id"].unique():
            df_tu = df_hh[df_hh["tu_id"] == tu_id]
            df_tu[
                "svbeit", "rvbeit", "avbeit", "gkvbeit", "pvbeit", "m_alg1", "pen_sim"
            ] = 0
            for i in df_tu.index:
                # Use Series instead of single row DataFrame
                df_row = df_tu.loc[i]

                ssc_contributions = ["svbeit", "rvbeit", "avbeit", "gkvbeit", "pvbeit"]
                df_tu.loc[i, ssc_contributions] = df_row.append(
                    soc_ins_contrib(df_row, tb)
                )

                # Unemployment benefits
                df_tu.loc[i, "m_alg1"] = ui(df_row, tb)

                # Pension benefits
                df_row.loc[i, "pen_sim"] = pensions(df_row, tb, tb_pens)

    # Income Tax
    taxvars = [
        "pid",
        "tu_id",
        "hid",
        "pweight",
        "female",
        "head_tu",
        "tu_id",
        "east",
        "m_wage",
        "selfemployed",
        "m_self",
        "m_pensions",
        "age",
        "pkv",
        "zveranl",
        "child",
        "child_num",
        "renteneintritt",
        "w_hours",
        "m_kapinc",
        "m_vermiet",
        "m_imputedrent",
        "marstat",
        "handcap_dummy",
        "handcap_degree",
        "rvbeit",
        "gkvbeit",
        "pvbeit",
        "avbeit",
        "adult_num_tu",
        "child_num_tu",
        "alleinerz",
        "ineducation",
    ]

    # 5.1 Calculate Taxable income (zve = zu versteuerndes Einkommen)
    # tu_id
    df = df.join(other=zve(df[taxvars], tb), how="inner")

    # 5.2 Apply Tax Schedule. returns incometax, capital income tax and soli
    # tu_id
    df = df.join(other=tax_sched(df, tb), how="inner")

    # 5.3 Child benefit (Kindergeld). Yes, this belongs to Income Tax
    # tu_id
    df = df.join(
        other=kindergeld(
            df[["hid", "tu_id", "age", "ineducation", "w_hours", "m_wage"]], tb
        ),
        how="inner",
    )

    # 5.4 Günstigerprüfung to obtain final income tax due.
    # different call here, because 'kindergeld' is overwritten by the function and
    # needs to be updated. not really elegant I must admit...
    # tu_id
    temp = favorability_check(df, tb)
    for var in [["incometax_tu", "kindergeld", "kindergeld_hh", "kindergeld_tu"]]:
        df[var] = temp[var]

    # 5.5 Solidarity Surcharge
    # df = df.join(other=soli(df, tb, taxyear), how="inner")

    # 6. SOCIAL TRANSFERS / BENEFITS
    # 6.0.1 Alimony Advance (Unterhaltsvorschuss)
    # tu_id
    df["uhv"] = uhv(df, tb)

    # 6.1. Wohngeld, Housing Benefit
    # hid
    df = df.join(other=wg(df, tb), how="inner")
    # 6.2 ALG2, Basic Unemployment Benefit
    # hid
    df = df.join(other=alg2(df, tb), how="inner")

    # 6.3. Kinderzuschlag, Additional Child Benefit
    # hid
    temp = kiz(df, tb)
    for var in [["m_alg2", "kiz", "wohngeld"]]:
        df[var] = temp[var]

    # 7. Drop unnecessary variables. not necessary anymore.s
    # df = dropstuff(df)

    # 8. Calculate disposable income
    # To be updated!
    df["dpi_ind"] = df[
        [
            "m_wage",
            "m_kapinc",
            "m_self",
            "m_vermiet",
            "m_imputedrent",
            "m_pensions",
            "m_transfers",
            "kindergeld",
            "uhv",
        ]
    ].sum(axis=1) - df[
        ["incometax", "soli", "abgst", "gkvbeit", "rvbeit", "pvbeit", "avbeit"]
    ].sum(
        axis=1
    )

    df["dpi_ind_temp"] = df.groupby(["hid"])["dpi_ind"].transform(sum)

    # Finally, add benefits that are defined on the household level
    df["dpi"] = round(
        np.maximum(0, df["dpi_ind_temp"] + df["m_alg2"] + df["wohngeld"] + df["kiz"]), 2
    )
    df["gross"] = round(
        df[
            [
                "m_wage",
                "m_kapinc",
                "m_self",
                "m_vermiet",
                "m_imputedrent",
                "m_pensions",
                "m_transfers",
                "kindergeld",
            ]
        ].sum(axis=1),
        2,
    )

    return df
