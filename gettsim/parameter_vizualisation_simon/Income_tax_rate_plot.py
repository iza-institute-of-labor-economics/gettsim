import numpy as np
import pandas as pd
from bokeh.models import LinearAxis
from bokeh.models import NumeralTickFormatter
from bokeh.models import Range1d
from bokeh.plotting import figure
from bokeh.plotting import output_file
from bokeh.plotting import show

from gettsim import set_up_policy_environment
from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.taxes.eink_st import st_tarif

output_file("income_tax_rate_plot.html")


def prepare_data(sel_year):
    """
    For a given year returns the policy parameters to plot income tax rate per income

    sel_year (Int): The year for which the data will be simulated. The range for
                    which parameters can be simulated is 2002-2020.

    returns dict
    """

    einkommen = pd.Series(data=np.linspace(0, 300000, 250))
    policy_params, policy_functions = set_up_policy_environment(sel_year)
    eink_params = policy_params["eink_st"]
    soli_params = policy_params["soli_st"]["soli_st"]

    eink_tax = st_tarif(einkommen, eink_params)
    soli = piecewise_polynomial(
        eink_tax,
        thresholds=soli_params["thresholds"],
        rates=soli_params["rates"],
        intercepts_at_lower_thresholds=soli_params["intercepts_at_lower_thresholds"],
    )
    marginal_rate = np.gradient(eink_tax, einkommen)

    tax_rate_dict = {}
    tax_rate_dict["tax_rate"] = eink_tax / einkommen
    tax_rate_dict["overall_tax_rate"] = (soli + eink_tax) / einkommen
    tax_rate_dict["marginal_rate"] = marginal_rate
    tax_rate_dict["income"] = einkommen
    tax_rate_dict["params"] = policy_params
    tax_rate_dict["year"] = sel_year

    return tax_rate_dict


def setup_plot(tax_rate_dict):

    p = figure(
        plot_width=400,
        plot_height=400,
        background_fill_color="white",
        title="Tax rate per income in " + str(tax_rate_dict["year"]),
    )
    p.line(
        tax_rate_dict["income"],
        tax_rate_dict["tax_rate"],
        line_width=2,
        legend_label="Income tax rate",
    )
    p.line(
        tax_rate_dict["income"],
        tax_rate_dict["overall_tax_rate"],
        line_width=2,
        line_color="black",
        legend_label="Income tax rate + soli",
    )
    p.line(
        tax_rate_dict["income"],
        tax_rate_dict["marginal_rate"],
        line_width=2,
        line_color="red",
        legend_label="Marginal tax rate",
    )

    p.xaxis.ticker = tax_rate_dict["params"]["eink_st"]["eink_st_tarif"]["thresholds"][
        1:5
    ]
    p.xaxis[0].formatter = NumeralTickFormatter(format="0")
    p.xaxis.major_label_orientation = (22 / 7) / 4  # 22/7 ~ pi
    p.xaxis.major_label_text_alpha = 0

    p.xgrid.band_hatch_pattern = "/"
    p.xgrid.band_hatch_alpha = 0.6
    p.xgrid.band_hatch_color = "lightgrey"
    p.xgrid.band_hatch_weight = 0.5
    p.xgrid.band_hatch_scale = 10

    p.extra_x_ranges = {"einkommen": Range1d(start=0, end=300000)}
    p.add_layout(LinearAxis(x_range_name="einkommen"), "below")
    p.xaxis[1].formatter = NumeralTickFormatter(format="0")
    p.xaxis[1].axis_label = "Taxable income in €"

    p.yaxis.axis_label = "Tax rate"
    p.yaxis[0].formatter = NumeralTickFormatter(format="0%")

    p.legend.location = "bottom_right"

    p.xaxis[0].fixed_location = 0.5

    return p


# Example year

processed_data = prepare_data(sel_year=2019)
plot = setup_plot(processed_data)

show(plot)
