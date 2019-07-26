# -*- coding: utf-8 -*-
"""
TAX TRANSFER SYSTEM FOR UBI
Eric Sommer, 2018
"""
import pandas as pd

from bld.project_paths import project_paths_join as ppj
from src.analysis.tax_transfer_funcs.benefits.benefit_checks import uhv
from src.analysis.tax_transfer_funcs.pensions import pensions
from src.analysis.tax_transfer_funcs.social_insurance import soc_ins_contrib
from src.analysis.tax_transfer_funcs.taxes import favorability_check
from src.analysis.tax_transfer_funcs.taxes import soli
from src.analysis.tax_transfer_funcs.taxes import tax_sched
from src.analysis.tax_transfer_funcs.zve import zve
from src.model_code.imports import aggr
from src.model_code.imports import get_params

# from numba import jit


def ubi_settings(tb):
    """ Set alternative tax benefit parameters for UBI
    """
    tb_ubi = tb.copy()

    # UBI amount for adults
    tb_ubi["ubi_adult"] = 1000
    tb_ubi["ubi_child"] = 0.5 * tb_ubi["ubi_adult"]

    # Minijobgrenze
    tb_ubi["mini_grenzew"] = 0
    tb_ubi["mini_grenzeo"] = tb_ubi["mini_grenzew"]

    # Midijobgrenze
    tb_ubi["midi_grenze"] = 0

    # UBI Flat Rate
    tb_ubi["flatrate"] = 0.81
    # change basic allowance?
    tb_ubi["G"] = tb["G"]

    # Kindergeld
    for i in range(1, 5):
        tb_ubi["kgeld" + str(i)] = 0

    # Tax Tariff

    return tb_ubi


def tax_transfer_ubi(df, datayear, taxyear, tb, tb_pens=None, mw=None, hyporun=False):
    """Counterfactual with Unconditional Basic income

    Either uses the functions from the baseline system (tax_transfer_funcs.py)
    or redefines the respective element

    - Basic guidelines:
        1. UBI replaces ALG2, Social assistance, Kindergeld, Wohngeld, Kinderzuschlag
        2. UBI is a flat rate, possibly lower for kids below a certain age.
        3. UBI is not means-tested and does not depend on family composition
        4. UBI is fully taxable
        5. Mini and Midi job rules are not touched


    Arguments:

        - *df*: Input Data Frame
        - *datayear*: year of SOEP wave
        - *taxyear*: year of reform baseline
        - *tb*: dictionary with tax-benefit parameters
        - *tb_pens*: Parameters for pension calculations
        - *mw*: Mean earnings by year, for pension calculations.
        - *hyporun*: indicator for hypothetical household input (defult: use real SOEP
                     data)


    """
    # set default arguments
    tb_pens = [] if tb_pens is None else tb_pens
    mw = [] if mw is None else mw
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
    df["m_alg1"] = 0

    # Pension benefits
    df["pen_sim"] = pensions(df, tb, tb_pens, mw, taxyear, hyporun)

    # UBI
    df["ubi"] = ubi(df, tb)
    # aggregate it on hh level
    df["ubi_hh"] = aggr(df, "ubi", "all_hh")
    df["ubi_tu"] = aggr(df, "ubi", "all_tu")
    # Income Tax
    taxvars = [
        "pid",
        "hid",
        "female",
        "pweight",
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
        "ubi",
        "ubi_tu",
    ]

    # 5.1 Calculate Taxable income (zve = zu versteuerndes Einkommen)
    df = df.join(other=zve(df[taxvars], tb, taxyear, hyporun, ref="UBI"), how="inner")

    # 5.2 Apply Tax Schedule
    df = df.join(other=tax_sched(df, tb, 2018, ref="UBI"), how="inner")

    # 5.3 Child benefit (Kindergeld). Yes, this belongs to Income Tax
    df["kindergeld_basis"] = 0
    df["kindergeld_tu_basis"] = 0

    # 5.4 Günstigerprüfung to obtain final income tax due.
    # different call here, because 'kindergeld' is overwritten by the function and
    # needs to be updated. not really elegant I must admit...
    temp = favorability_check(df, tb, taxyear)
    for var in [["incometax_tu", "kindergeld", "kindergeld_hh", "kindergeld_tu"]]:
        df[var] = temp[var]
    df["tu_id"].describe()
    # 5.5 Solidarity Surcharge
    df = df.join(other=soli(df, tb, taxyear), how="inner")

    # 6. SOCIAL TRANSFERS / BENEFITS
    # 6.0.1 Alimony Advance (Unterhaltsvorschuss)
    df["uhv"] = uhv(df, tb, taxyear)
    df["uhv_hh"] = aggr(df, "uhv", "all_hh")

    # 6.1. Wohngeld, Housing Benefit
    df["wohngeld"] = 0
    # 6.2 ALG2, Basic Unemployment Benefit
    df["m_alg2"] = 0

    # 6.3. Kinderzuschlag, Additional Child Benefit
    df["kiz"] = 0

    # 7. Drop unnecessary variables. not necessary anymore.s
    # df = dropstuff(df)

    # 8. Finally, calculate disposable income
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
            "ubi",
            "uhv",
        ]
    ].sum(axis=1) - df[
        ["incometax", "soli", "abgst", "gkvbeit", "rvbeit", "pvbeit", "avbeit"]
    ].sum(
        axis=1
    )

    df["dpi_ind_temp"] = df.groupby(["hid"])["dpi_ind"].transform(sum)

    # There are no benefits at the household level
    df["dpi"] = df["dpi_ind_temp"]

    return df


def ubi(df, tb):
    ubi = pd.DataFrame(index=df.index.copy())
    # ubi["hid"] = df["hid"]
    ubi["ubi"] = 0
    ubi.loc[df["age"] >= 18, "ubi"] = tb["ubi_adult"]
    ubi.loc[df["age"] < 18, "ubi"] = tb["ubi_child"]

    # ubi['ubi_hh'] = aggr(ubi, 'ubi', True)

    return ubi["ubi"]


if __name__ == "__main__":
    settings = pd.read_json(ppj("IN_MODEL_SPECS", "settings.json"))
    tb = get_params(ppj("IN_DATA"))["y" + str(settings["taxyear"][0])]
    tb_pens = pd.read_excel(
        ppj("IN_DATA", "pensions.xlsx"), index_col="var"
    ).transpose()
    tb_ubi = ubi_settings(tb)
    mw = pd.read_json(ppj("IN_DATA", "mw_pensions.json"))
    df = pd.read_pickle(ppj("SOEP_PATH", "2_taxben_input.dta"))
    # reduce dataset
    df = df[df["syear"] == df["syear"].max()]
    tt_out = tax_transfer_ubi(
        df, df["syear"].max(), settings["taxyear"][0], tb_ubi, tb_pens, mw, False
    )
    tt_out.to_json(ppj("OUT_DATA", "taxben_results_{}.json".format("UBI")))
