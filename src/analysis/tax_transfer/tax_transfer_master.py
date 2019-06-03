# -*- coding: utf-8 -*-
"""
TAX TRANSFER SIMULATION

Eric Sommer, 2018
"""

import numpy as np
import pandas as pd


from src.analysis.tax_transfer.taxes import soli, zve, tax_sched
from src.analysis.tax_transfer.unemployment_benefits import ui, wg, alg2
from src.analysis.tax_transfer.child_benefits import kindergeld, uhv
from src.analysis.tax_transfer.child_benefits import favorability_check, kiz
from src.analysis.tax_transfer.social_insurance import soc_ins_contrib
from src.analysis.tax_transfer.pensions import pensions
from src.model_code.imports import get_params
from bld.project_paths import project_paths_join as ppj


def tax_transfer(df, datayear, taxyear, tb, tb_pens=None, mw=None, hyporun=False):
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
    mw = [] if mw is None else mw
    # if hyporun is False:
    # df = uprate(df, datayear, settings['taxyear'], settings['MAIN_PATH'])

    # Social Insurance Contributions
    df = df.join(
        other=soc_ins_contrib(
            df[
                [
                    "pid",
                    "hid",
                    "east",
                    "m_wage",
                    "selfemployed",
                    "m_self",
                    "m_pensions",
                    "age",
                    "haskids",
                    "pkv",
                ]
            ],
            tb,
            taxyear,
        ),
        how="inner",
    )

    # Unemployment benefits
    df["m_alg1"] = ui(df, tb, taxyear)

    # Pension benefits
    df["pen_sim"] = pensions(df, tb, tb_pens, mw, taxyear, hyporun)

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
    df = df.join(other=zve(df[taxvars], tb, taxyear, hyporun), how="inner")

    # print(df[['typ_bud', 'y_wage', 'zve_nokfb']][df['y_wage'].between(64000, 70000)])
    # 5.2 Apply Tax Schedule
    df = df.join(other=tax_sched(df, tb, taxyear, hyporun), how="inner")

    # 5.3 Child benefit (Kindergeld). Yes, this belongs to Income Tax
    df = df.join(
        other=kindergeld(
            df[["hid", "tu_id", "age", "ineducation", "w_hours", "m_wage"]], tb, taxyear
        ),
        how="inner",
    )

    # 5.4 Günstigerprüfung to obtain final income tax due.
    # different call here, because 'kindergeld' is overwritten by the function and
    # needs to be updated. not really elegant I must admit...
    temp = favorability_check(df, tb, taxyear)
    for var in [["incometax_tu", "kindergeld", "kindergeld_hh", "kindergeld_tu"]]:
        df[var] = temp[var]

    # 5.5 Solidarity Surcharge
    df = df.join(other=soli(df, tb, taxyear), how="inner")

    # 6. SOCIAL TRANSFERS / BENEFITS
    # 6.0.1 Alimony Advance (Unterhaltsvorschuss)
    if taxyear >= 2017:
        df["uhv"] = uhv(df, tb, taxyear)
    else:
        df["uhv"] = 0

    # 6.1. Wohngeld, Housing Benefit
    # TODO: rename wohngeld ('wohngeld_basis') until final check.
    df = df.join(other=wg(df, tb, taxyear, hyporun), how="inner")
    # 6.2 ALG2, Basic Unemployment Benefit
    df = df.join(other=alg2(df, tb, taxyear), how="inner")

    # 6.3. Kinderzuschlag, Additional Child Benefit
    temp = kiz(df, tb, taxyear, hyporun)
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


if __name__ == "__main__":
    settings = pd.read_json(ppj("IN_MODEL_SPECS", "settings.json"))
    tb = get_params(ppj("IN_DATA"))["y" + str(settings["taxyear"][0])]
    tb_pens = pd.read_excel(
        ppj("IN_DATA", "pensions.xlsx"), index_col="var"
    ).transpose()
    mw = pd.read_json(ppj("IN_DATA", "mw_pensions.json"))
    df = pd.read_pickle(ppj("SOEP_PATH", "2_taxben_input.dta"))
    # reduce dataset to last available SOEP year
    df = df[df["syear"] == df["syear"].max()]
    tt_out = tax_transfer(
        df, df["syear"].max(), settings["taxyear"][0], tb, tb_pens, mw, False
    )
    tt_out.to_json(
        ppj("OUT_DATA", "taxben_results_{}.json".format(settings["Reforms"][0]))
    )
