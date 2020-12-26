import pandas as pd
from bokeh.palettes import Category10
from bokeh.plotting import figure
from bokeh.plotting import output_file
from bokeh.plotting import show

from gettsim import set_up_policy_environment

output_file("ALG2_plot.html")


def prepare_data(start, end):

    """
    For a given year span returns the alg2 regelsatz parameters

    start (Int): The start year of the plotted year span. Paramters available after
                 introdcution in 2005.
    end (Int): The end year of the plotted year span.

    returns dataframe
    """
    years = range(start, end)

    regelsatz_dict = {}

    for i in years:
        policy_params, policy_functions = set_up_policy_environment(i)
        regelsatz_dict[i] = policy_params["arbeitsl_geld_2"]["regelsatz"]

    for i in range(2005, 2011):
        regelsatz_dict[i] = {1: regelsatz_dict[i]}

    regelsatz_df = pd.DataFrame(data=regelsatz_dict).transpose()

    return regelsatz_df


def setup_plot(regelsatz_df):

    color = Category10[6]

    p = figure(
        plot_width=600,
        plot_height=400,
        background_fill_color="white",
        title="Basic security standard rates (Regelsatz)",
    )

    for i in regelsatz_df.columns:
        p.line(
            regelsatz_df.index,
            regelsatz_df[i],
            line_width=2,
            line_color=color[i - 1],
            legend_label=("Subsistence level" + str(i)),
            alpha=0.8,
            muted_alpha=0.2,
            muted_color=color[i - 1],
        )

    p.legend.location = "bottom_left"

    p.yaxis.axis_label = "Monthly basic security payment in €"
    p.xaxis.axis_label = "Year"

    return p


# Example
processed_data = prepare_data(start=2005, end=2020)
plot = setup_plot(processed_data)
show(plot)
