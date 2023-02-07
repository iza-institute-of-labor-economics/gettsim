"""This module puts together the data needed for the dashboards based on the specified
GETTSIM parameters.

It has to be run manually after any parameter is changed.

"""
import pickle
from datetime import date

import pandas as pd
from _gettsim.config import numpy_or_jax as np
from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.policy_environment import set_up_policy_environment
from _gettsim.taxes.eink_st import _eink_st_tarif
from _gettsim.transfers.wohngeld import wohngeld_miete_m_hh_ab_2009
from _gettsim.transfers.wohngeld import wohngeld_miete_m_hh_bis_2008
from _gettsim.transfers.wohngeld import wohngeld_min_miete_m_hh
from _gettsim.transfers.wohngeld import wohngeld_vor_vermög_check_m_hh


wohngeld_miete_m_hh_ab_2009 = np.vectorize(wohngeld_miete_m_hh_ab_2009)
wohngeld_miete_m_hh_bis_2008 = np.vectorize(wohngeld_miete_m_hh_bis_2008)
wohngeld_min_miete_m_hh = np.vectorize(wohngeld_min_miete_m_hh)
wohngeld_vor_vermög_check_m_hh = np.vectorize(wohngeld_vor_vermög_check_m_hh)
_eink_st_tarif = np.vectorize(_eink_st_tarif)


# Each plot has one data preparation function as defined below


def deduction_data(start, end):
    """Data preparation for income tax deduction parameters. Return a dataframe.

    Parameters:
    start (Int): Defines the start of the simulated period
    end (Int):  Defines the end of the simulated period

    """

    # Period for simulation:
    years = range(start, end + 1)
    eink_ab_df = {}
    # input older grundfreibetrag values by hand
    grundfreibetrag = {
        2001: 14093 / 1.95583,
        2000: 13499 / 1.95583,
        1999: 13067 / 1.95583,
        1998: 12365 / 1.95583,
        1997: 12095 / 1.95583,
        1996: 12095 / 1.95583,
        1995: 5616 / 1.95583,
        1994: 5616 / 1.95583,
        1993: 5616 / 1.95583,
        1992: 5616 / 1.95583,
        1991: 5616 / 1.95583,
        1990: 5616 / 1.95583,
        1989: 4752 / 1.95583,
        1988: 4752 / 1.95583,
        1987: 4536 / 1.95583,
        1986: 4536 / 1.95583,
        1985: 4212 / 1.95583,
        1984: 4212 / 1.95583,
        1983: 4212 / 1.95583,
        1982: 4212 / 1.95583,
        1981: 4212 / 1.95583,
        1980: 3690 / 1.95583,
        1979: 3690 / 1.95583,
        1978: 3329 / 1.95583,
        1977: 3029 / 1.95583,
        1976: 3029 / 1.95583,
        1975: 3029 / 1.95583,
    }
    # Loop through years to get the policy parameters
    for i in years:
        policy_params, policy_functions = set_up_policy_environment(i)
        params = policy_params["eink_st_abzuege"]
        if i < 2002:
            params["grundfreibetrag"] = round(grundfreibetrag[i])
        if i >= 2002:
            params["grundfreibetrag"] = policy_params["eink_st"]["eink_st_tarif"][
                "thresholds"
            ][1]
        eink_ab_df[i] = params

    eink_ab_df = pd.DataFrame(eink_ab_df)

    deduction_df = eink_ab_df.transpose()
    # Adjust dictionary entries into columns for kinderfreibetrag
    deduction_df = pd.concat(
        [
            deduction_df.drop(["kinderfreibetrag", "datum"], axis=1),
            deduction_df["kinderfreibetrag"].apply(pd.Series),
        ],
        axis=1,
    )
    deduction_df = deduction_df.drop(["behinderten_pauschbetrag", 0], axis=1)
    return deduction_df


def prepare_wg_data(sel_year, hh_size):
    """
    For a given year and household_size this function creates the
    simulation dataframe later used for plotting.
    Parameters:
    sel_year: Int
        The year for which the wohngeld will be simulated

    hh_size: Int
        The size of the houshold for which wohngeld will be simulated.
        Values between 1 and 13. More than 12 just adds a lump-sum on top

    Returns dataframe.
    """
    # Retrieve policy parameters for the selected year
    policy_params, policy_functions = set_up_policy_environment(sel_year)
    params = policy_params["wohngeld"]

    # Range of relevant income and rent combinations for the simulation
    einkommen = pd.Series(data=np.linspace(0, 4000, 81))
    miete = pd.Series(data=np.linspace(0, 2000, 81))
    household_size = pd.Series(data=[hh_size] * len(einkommen))

    # Miete needs to be corrected acc. to mietstufe and hh size
    if sel_year <= 2008:
        wohngeld_miete_m_hh = wohngeld_miete_m_hh_bis_2008(
            pd.Series([3] * len(miete)),
            pd.Series([1980] * len(miete)),
            household_size,
            miete,
            pd.Series([1] * len(miete)),
            wohngeld_min_miete_m_hh(household_size, params),
            params,
        )
    if 2009 <= sel_year:
        wohngeld_miete_m_hh = wohngeld_miete_m_hh_ab_2009(
            pd.Series([3] * len(miete)),
            household_size,
            miete,
            pd.Series([1] * len(miete)),
            wohngeld_min_miete_m_hh(household_size, params),
            params,
        )

    # Create a dataframe for the simulated data
    wohngeld_df = pd.DataFrame(columns=einkommen)

    # To-do think about household["Mietstufe"]

    # Iterate through einkommen for all einkommen and miete combinations
    for i in range(len(einkommen)):
        this_column = wohngeld_df.columns[i]
        e = pd.Series(data=[einkommen[i]] * len(einkommen))
        wohngeld_df[this_column] = wohngeld_vor_vermög_check_m_hh(
            haushaltsgröße_hh=household_size,
            # Account for minimum income
            wohngeld_eink_m=np.maximum(e, params["min_eink"][hh_size]),
            wohngeld_miete_m_hh=wohngeld_miete_m_hh,
            wohngeld_params=params,
        )
    wohngeld_df.index = miete

    return wohngeld_df


def wohngeld_data():
    wg_dict = {}
    years = [1992, 2001, 2009, 2016, 2020, 2021]

    for i in years:
        wg_dict[i] = {j: prepare_wg_data(i, j) for j in range(1, 13)}

    return wg_dict


def tax_rate_data(start, end):
    """For a given year span returns the policy parameters to plot income tax rate per
    income.

    sel_year (Int): The year for which the data will be simulated. The range for
                    which parameters can be simulated is 2002-2020.

    returns dict

    """
    years = range(start, end + 1)
    einkommen = pd.Series(data=np.linspace(0, 300000, 601))
    tax_rate_dict_full = {}
    for i in years:
        policy_params, policy_functions = set_up_policy_environment(i)
        eink_params = policy_params["eink_st"]
        soli_params = policy_params["soli_st"]["soli_st"]

        eink_tax = _eink_st_tarif(einkommen, eink_params)

        soli = np.array(
            [
                piecewise_polynomial(
                    x,
                    thresholds=soli_params["thresholds"],
                    rates=soli_params["rates"],
                    intercepts_at_lower_thresholds=soli_params[
                        "intercepts_at_lower_thresholds"
                    ],
                )
                for x in eink_tax
            ]
        )
        marginal_rate = np.gradient(eink_tax, einkommen)
        overall_marginal_rate = np.gradient(eink_tax + soli, einkommen)
        tax_rate_dict_full[i] = {
            "tax_rate": (eink_tax / einkommen),
            "overall_tax_rate": ((soli + eink_tax) / einkommen),
            "marginal_rate": pd.Series(marginal_rate),
            "overall_marginal_rate": pd.Series(overall_marginal_rate),
            "income": einkommen,
        }

    return tax_rate_dict_full


def child_benefits_data(start, end):
    """Data preparation for kindergeld parameters.

    Returns a dataframe.
    Parameters:
    start (Int): Defines the start of the simulated period
    end (Int):  Defines the end of the simulated period

    """

    # Calculate simulation period
    years = range(start, end + 1)

    # Data preparation for Kindergeld params
    kindergeld_df = pd.DataFrame()

    for i in years:
        policy_params, policy_functions = set_up_policy_environment(i)
        kindergeld_df[i] = policy_params["kindergeld"]["kindergeld"].values()

    kindergeld_df = kindergeld_df.transpose()

    kindergeld_labels = ["First child", "Second child", "Third child", "Fourth child"]
    kindergeld_df.columns = kindergeld_labels

    return kindergeld_df


def social_security_data(start, end):
    """For a year range returns the policy parameters to plot the social insurance
    contributions.

    start (Int): Defines the start of the simulated period
    end (Int):  Defines the end of the simulated period

    returns dataframe

    """
    years = range(start, end + 1)

    soz_vers_dict = {}

    for i in years:
        policy_params, policy_functions = set_up_policy_environment(i)
        soz_vers_dict[i] = policy_params["soz_vers_beitr"]["beitr_satz"]

    soz_vers_df = pd.DataFrame(data=soz_vers_dict).transpose()
    # Dictionary entries into columns
    ges_krankenv = soz_vers_df["ges_krankenv"].apply(pd.Series)
    ges_pflegev = soz_vers_df["ges_pflegev"].apply(pd.Series)

    soz_vers_out = pd.concat(
        [
            soz_vers_df[["arbeitsl_v", "ges_rentenv"]],
            ges_krankenv[["mean_allgemein", "allgemein", "mean_zusatzbeitrag"]],
            ges_pflegev,
        ],
        axis=1,
    )
    soz_vers_out.columns = [
        "unemployment insurance",
        "pension insurance",
        "health insurance average",
        "health insurance general",
        "health insurance top-up",
        "care insurance",
        "additional care insurance no child",
    ]
    # We don't need the top-up for childless persons
    soz_vers_out = soz_vers_out.drop(columns=["additional care insurance no child"])

    return soz_vers_out


def social_assistance_data(start, end):
    """For a year range returns the policy parameters to plot the social insurance
    contributions.

    start (Int):
        Defines the start of the simulated period
    end (Int):
        Defines the end of the simulated period

    returns:
        soz_ass_out: pd.DataFrame

    """

    years = range(start, end + 1)

    soz_ass_dict = {}

    for i in years:
        policy_params, policy_functions = set_up_policy_environment(i)
        if i <= 2010:
            anteil_regelsatz = policy_params["arbeitsl_geld_2"]["anteil_regelsatz"]
            anteil_regelsatz["ein_erwachsener"] = 1
            regelsätze = (
                np.array(list(anteil_regelsatz.values()))
                * policy_params["arbeitsl_geld_2"]["regelsatz"]
            )
            soz_ass_dict[i] = dict(zip(anteil_regelsatz.keys(), regelsätze))
        else:
            soz_ass_dict[i] = dict(
                zip(
                    [
                        "ein_erwachsener",
                        "zwei_erwachsene",
                        "weitere_erwachsene",
                        "kinder_14_24",
                        "kinder_7_13",
                        "kinder_0_6",
                    ],
                    policy_params["arbeitsl_geld_2"]["regelsatz"].values(),
                )
            )

    soz_ass_df = pd.DataFrame.from_dict(soz_ass_dict, orient="index")
    soz_ass_out = soz_ass_df[
        [
            "ein_erwachsener",
            "zwei_erwachsene",
            "weitere_erwachsene",
            "kinder_14_24",
            "kinder_7_13",
            "kinder_0_6",
        ]
    ]
    return soz_ass_out


# Call all data preparation functions into a single dictionary
def generate_data():
    current_year = date.today().year
    all_data = {
        "deductions": deduction_data(1975, current_year),
        "wohngeld": wohngeld_data(),
        "tax_rate": tax_rate_data(2002, current_year),
        "child_benefits": child_benefits_data(1975, current_year),
        "social_security": social_security_data(1984, current_year),
        "social_assistance": social_assistance_data(2005, current_year),
    }
    dbfile = open("params_dashboard_data.pickle", "wb")

    # source, destination
    pickle.dump(all_data, dbfile)
    dbfile.close()


if __name__ == "__main__":
    # Run manually once after major changes i.e. new plots.
    generate_data()
