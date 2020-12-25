import numpy as np
import pandas as pd
from bokeh.models import NumeralTickFormatter
from bokeh.palettes import Category20
from bokeh.plotting import figure
from bokeh.plotting import output_file
from bokeh.plotting import show

from gettsim import set_up_policy_environment
from gettsim.social_insurance.beitr_bemess_grenzen import rentenv_beitr_bemess_grenze
from gettsim.transfers.arbeitsl_geld import proxy_eink_vorj_arbeitsl_geld

output_file("unemployment_plot.html")


def prepare_data(sel_year):

    """
    For a given year returns the policy parameters to plot the unemployment benefits

    sel_year (Int): The year for which the data will be simulated. The range for which
                    parameters can be simulated is 2002-2020.

    returns dict
    """

    einkommen_lastyear_m = pd.Series(data=np.linspace(0, 10000, 250))
    policy_params, policy_functions = set_up_policy_environment(sel_year)

    alg_params_kind = policy_params["arbeitsl_geld"]["arbeitsl_geld_satz_mit_kindern"]
    alg_params = policy_params["arbeitsl_geld"]["arbeitsl_geld_satz_ohne_kinder"]
    wohnort_ost_false = pd.Series(data=[False] * 250)
    wohnort_ost_true = pd.Series(data=[True] * 250)

    # Relevant einkommen for ALG West
    relevant_einkommen_west_m = proxy_eink_vorj_arbeitsl_geld(
        rentenv_beitr_bemess_grenze(wohnort_ost_false, policy_params["soz_vers_beitr"]),
        einkommen_lastyear_m,
        policy_params["arbeitsl_geld"],
        policy_params["eink_st"],
        policy_params["eink_st_abzuege"],
        policy_params["soli_st"],
    )

    # Relevant einkommen for ALG East
    relevant_einkommen_east_m = proxy_eink_vorj_arbeitsl_geld(
        rentenv_beitr_bemess_grenze(wohnort_ost_true, policy_params["soz_vers_beitr"]),
        einkommen_lastyear_m,
        policy_params["arbeitsl_geld"],
        policy_params["eink_st"],
        policy_params["eink_st_abzuege"],
        policy_params["soli_st"],
    )

    unemployment_dict = {}
    unemployment_dict["einkommen_lastyear_m"] = einkommen_lastyear_m
    unemployment_dict["unemployment_west_kind"] = (
        relevant_einkommen_west_m * alg_params_kind
    )
    unemployment_dict["unemployment_west"] = relevant_einkommen_west_m * alg_params
    unemployment_dict["unemployment_east_kind"] = (
        relevant_einkommen_east_m * alg_params_kind
    )
    unemployment_dict["unemployment_east"] = relevant_einkommen_east_m * alg_params
    unemployment_dict["year"] = sel_year

    return unemployment_dict


def setup_plot(unemployment_dict):

    color = Category20[4]

    p = figure(
        plot_width=400,
        plot_height=400,
        background_fill_color="white",
        title="Unemployment benefit per prior income in "
        + str(unemployment_dict["year"]),
    )
    # West
    p.line(
        unemployment_dict["einkommen_lastyear_m"],
        unemployment_dict["unemployment_west"],
        line_width=2,
        line_color=color[0],
        legend_label="ALG without children / West",
        alpha=0.8,
        muted_alpha=0.2,
        muted_color=color[0],
    )
    p.line(
        unemployment_dict["einkommen_lastyear_m"],
        unemployment_dict["unemployment_west_kind"],
        line_width=2,
        line_color=color[1],
        legend_label="ALG with children / West",
        alpha=0.8,
        muted_alpha=0.2,
        muted_color=color[1],
    )

    # East
    p.line(
        unemployment_dict["einkommen_lastyear_m"],
        unemployment_dict["unemployment_east"],
        line_width=2,
        line_color=color[2],
        legend_label="ALG without children / East",
        alpha=0.8,
        muted_alpha=0.2,
        muted_color=color[2],
    )
    p.line(
        unemployment_dict["einkommen_lastyear_m"],
        unemployment_dict["unemployment_east_kind"],
        line_width=2,
        line_color=color[3],
        legend_label="ALG with children / East",
        alpha=0.8,
        muted_alpha=0.2,
        muted_color=color[3],
    )

    p.xaxis[0].formatter = NumeralTickFormatter(format="0")
    p.yaxis[0].formatter = NumeralTickFormatter(format="0")

    p.legend.location = "bottom_right"
    p.legend.click_policy = "mute"

    p.yaxis.axis_label = "Monthly unemployment benefit in €"
    p.xaxis.axis_label = "Monthly gross income prior year in €"

    return p


# Example

processed_data = prepare_data(sel_year=2019)
plot = setup_plot(processed_data)
show(plot)
