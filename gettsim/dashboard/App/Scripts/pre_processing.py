import pickle

import numpy as np
import pandas as pd
from gettsim import set_up_policy_environment
from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.taxes.eink_st import st_tarif
from gettsim.transfers.wohngeld import wohngeld_basis

# Each plot has one data preparation function as defined below


def deduction_data(start, end):
    """
    Data preparation for income tax deduction parameters. Return a dataframe.

    Parameters:
    start (Int): Defines the start of the simulated period
    end (Int):  Defines the end of the simulated period
    """

    # Period for simulation:
    years = range(start, end)
    eink_ab_df = pd.DataFrame()

    # Loop through years to get the policy parameters
    for i in years:
        policy_params, policy_functions = set_up_policy_environment(i)
        params = policy_params["eink_st_abzuege"]
        if i > 2001:
            params["grundfreibetrag"] = policy_params["eink_st"]["eink_st_tarif"][
                "thresholds"
            ][1]
        else:
            params["grundfreibetrag"] = 0
        eink_ab_df[i] = params.values()

    eink_ab_df.index = params.keys()
    deduction_df = eink_ab_df.transpose()
    # Adjust dictionairy entries into columns for kinderfreibetrag
    deduction_df = pd.concat(
        [
            deduction_df.drop(["kinderfreibetrag", "datum"], axis=1),
            deduction_df["kinderfreibetrag"].apply(pd.Series),
        ],
        axis=1,
    )
    deduction_df = deduction_df.drop(["behinderten_pauschbetrag", 0], axis=1)

    return deduction_df


# Prepare wohngeld data
def prepare_data(sel_year, hh_size):
    """
    For a given year and household_size this function creates the
    simulation dataframe later used for plotting.
    Parameters:
    sel_year (Int): The year for which the wohngeld will be simulated


    hh_size (Int): The size of the houshold for which wohngeld will be
                    simulated.
                    Values between 1 and 13.
                    More than 12 just adds a lump-sum on top

    Returns dataframe.
    """

    # Range of relevant income and rent combinations for the simulation
    einkommen = pd.Series(data=np.linspace(0, 1300, 50))
    miete = pd.Series(data=np.linspace(0, 1300, 50))

    # Todo replace this with sliders
    household_size = pd.Series(data=[hh_size] * len(einkommen))
    sel_year = sel_year

    # Create a dataframe for the simulated data
    wohngeld_df = pd.DataFrame(columns=einkommen)

    # Retrieve policy parameters for the selected year
    policy_params, policy_functions = set_up_policy_environment(sel_year)
    params = policy_params["wohngeld"]
    # To-do think about household["Mietstufe"]

    # Iterate through einkommen for all einkommen and miete combinations
    for i in range(len(einkommen)):
        this_column = wohngeld_df.columns[i]
        e = pd.Series(data=[einkommen[i]] * len(einkommen))
        wohngeld_df[this_column] = wohngeld_basis(
            haushaltsgröße=household_size,
            wohngeld_eink=e,
            wohngeld_miete=miete,
            wohngeld_params=params,
        )
    wohngeld_df.index = miete

    return wohngeld_df


def wohngeld_data():
    wg_dict = {}
    years = [1992, 2001, 2009, 2016, 2020, 2021]

    for i in years:
        wg_dict[i] = {j: prepare_data(i, j) for j in range(1, 13)}

    return wg_dict


def tax_rate_data(start, end):
    """
    For a given year span returns the policy parameters to plot income tax
    rate per income

    sel_year (Int): The year for which the data will be simulated. The range for
                    which parameters can be simulated is 2002-2020.

    returns dict
    """
    years = range(start, end)
    einkommen = pd.Series(data=np.linspace(0, 300000, 250))
    tax_rate_dict_full = {}
    for i in years:
        policy_params, policy_functions = set_up_policy_environment(i)
        eink_params = policy_params["eink_st"]
        soli_params = policy_params["soli_st"]["soli_st"]

        eink_tax = st_tarif(einkommen, eink_params)
        soli = piecewise_polynomial(
            eink_tax,
            thresholds=soli_params["thresholds"],
            rates=soli_params["rates"],
            intercepts_at_lower_thresholds=soli_params[
                "intercepts_at_lower_thresholds"
            ],
        )
        marginal_rate = np.gradient(eink_tax, einkommen)

        tax_rate_dict_full[i] = {
            "tax_rate": (eink_tax / einkommen),
            "overall_tax_rate": ((soli + eink_tax) / einkommen),
            "marginal_rate": pd.Series(marginal_rate),
            "income": einkommen,
        }

    return tax_rate_dict_full


def child_benefits_data(start, end):
    """
    Data preparation for kindergeld parameters. Returns a dataframe.
    Parameters:
    start (Int): Defines the start of the simulated period
    end (Int):  Defines the end of the simulated period
    """

    # Calculate simulation period
    years = range(start, end)

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
    """
    For a year range returns the policy parameters to plot the social security
    contributions

    start (Int): Defines the start of the simulated period
    end (Int):  Defines the end of the simulated period

    returns dataframe
    """
    years = range(start, end)

    soz_vers_dict = {}

    for i in years:
        policy_params, policy_functions = set_up_policy_environment(i)
        soz_vers_dict[i] = policy_params["soz_vers_beitr"]["soz_vers_beitr"]

    soz_vers_df = pd.DataFrame(data=soz_vers_dict).transpose()

    # Dictionairy entries into columns
    soz_vers_df = pd.concat(
        [
            soz_vers_df.drop(["ges_krankenv"], axis=1),
            soz_vers_df["ges_krankenv"].apply(pd.Series),
        ],
        axis=1,
    )
    soz_vers_df = pd.concat(
        [
            soz_vers_df.drop(["pflegev"], axis=1),
            soz_vers_df["pflegev"].apply(pd.Series),
        ],
        axis=1,
    )

    soz_vers_df.columns = [
        "unemployment insurance",
        "pension insurance",
        "health insurance employer",
        "health insurance employee",
        "care insurance",
        "additional care insurance no child",
    ]

    return soz_vers_df


# Call all data preparation functions into a single dictionairy


def generate_data():
    all_data = {
        "deductions": deduction_data(1975, 2021),
        "wohngeld": wohngeld_data(),
        "tax_rate": tax_rate_data(2002, 2022),
        "child_benefits": child_benefits_data(1975, 2022),
        "social_security": social_security_data(2002, 2022),
    }

    dbfile = open("all_data.pickle", "wb")

    # source, destination
    pickle.dump(all_data, dbfile)
    dbfile.close()


# This line needs to be run manually once after major changes i.e. new plots.
# generate_data()
