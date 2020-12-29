# Import functions
import pandas as pd
from bokeh.palettes import Category10
from bokeh.plotting import ColumnDataSource
from bokeh.plotting import figure
from bokeh.plotting import output_file
from bokeh.plotting import show

from gettsim import set_up_policy_environment

output_file("kindergeld_plot.html")


def prepare_data(start, end):
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


def setup_plot(kindergeld_df):
    """
    Create the kindergeld plot.

    Parameters

    (pd.Dataframe): Returned by the data preparation function
    """
    # Plot for kindergeld params

    source = ColumnDataSource(kindergeld_df)

    kindergeld_p = figure(
        title="Kindergeld per Child",
        plot_height=300,
        plot_width=600,
        y_range=(0, 270),
        x_range=(min(kindergeld_df.index), max(kindergeld_df.index)),
        background_fill_color="#efefef",
    )
    k = -1
    for i in kindergeld_df.columns:
        k = k + 1
        kindergeld_p.step(
            x="index",
            y=i,
            line_width=2,
            color=Category10[4][k],
            legend_label=kindergeld_df.columns[k],
            alpha=0.8,
            muted_color=Category10[4][k],
            muted_alpha=0.2,
            source=source,
            name=i,
        )

    kindergeld_p.legend.location = "top_left"
    kindergeld_p.legend.click_policy = "mute"

    kindergeld_p.xaxis.axis_label = "Year"
    kindergeld_p.yaxis.axis_label = "Kindergeld in €"

    return kindergeld_p


# Example
processed_data = prepare_data(start=1975, end=2020)
plot = setup_plot(processed_data)

show(plot)
