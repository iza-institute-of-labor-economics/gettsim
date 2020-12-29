# Import
import numpy as np
import pandas as pd
from bokeh.models import BasicTicker
from bokeh.models import ColorBar
from bokeh.models import ColumnDataSource
from bokeh.models import LinearColorMapper
from bokeh.models import NumeralTickFormatter
from bokeh.palettes import Magma256
from bokeh.plotting import figure
from bokeh.plotting import output_file
from bokeh.plotting import show
from bokeh.transform import transform

from gettsim import set_up_policy_environment
from gettsim.transfers.wohngeld import wohngeld_basis

output_file("wohngeld_plot.html")


# Prepare wohngeld data ALTERNATIVE
def prepare_data(sel_year, hh_size):
    """
    For a given year and household_size this function creates the simulation dataframe
    later used for plotting.
    Parameters:
    sel_year (Int): The year for which the wohngeld will be simulated, input
                    should come from a slider.
                    The range for which parameters can be simulated is 2002-2020

    hh_size (Int): The size of the houshold for which the wohngeld will be simulated.
                    Values between 1 and 13.
                    More than 12 just adds a lump-sum on top

    Returns dataframe.
    """

    # Range of relevant income and rent combinations for the simulation
    einkommen = pd.Series(data=np.linspace(0, 1300, 250))
    miete = pd.Series(data=np.linspace(0, 1300, 250))

    # Todo replace this with sliders
    household_size = pd.Series(data=[hh_size] * len(einkommen))
    sel_year = sel_year

    # Create a dataframe for the simulated data
    wohngeld_df = pd.DataFrame(columns=einkommen)

    # Retrieve policy parameters for the selected year
    policy_params, policy_functions = set_up_policy_environment(sel_year)
    params = policy_params["wohngeld"]
    # To-do think about household["Mietstufe"]

    # Iterate through einkommen to get wohngeld for all einkommen and miete combinations
    for i in range(len(einkommen)):
        this_column = wohngeld_df.columns[i]
        e = pd.Series(data=[einkommen[i]] * 250)
        wohngeld_df[this_column] = wohngeld_basis(
            haushaltsgröße=household_size,
            wohngeld_eink=e,
            wohngeld_max_miete=miete,
            wohngeld_params=params,
        )
    wohngeld_df.index = miete

    return wohngeld_df


def setup_plot(wohngeld_df):
    """
    Create the heatmap plot.

    parameters (pd.Dataframe): Returned by the data preparation function
    """

    # reshape to 1D array for heatmap
    heatmap_source = pd.DataFrame(
        wohngeld_df.stack(), columns=["Wohngeld"]
    ).reset_index()
    heatmap_source.columns = ["Miete", "Einkommen", "Wohngeld"]

    source = ColumnDataSource(heatmap_source)

    # Prepare a color pallete and color mapper
    colors = Magma256[128:256]
    colors = list(colors)
    colors.reverse()
    mapper = LinearColorMapper(
        palette=colors,
        low=heatmap_source.Wohngeld.min(),
        high=heatmap_source.Wohngeld.max(),
    )

    # Actual figure setup
    p = figure(
        plot_width=600,
        plot_height=400,
        title="Monthly wohngeld in € per income and rent",
        x_range=(0, 1300),
        y_range=(0, 1300),
        tools="",
    )

    p.rect(
        x="Miete",
        y="Einkommen",
        width=10,
        height=10,
        source=source,
        line_color=None,
        fill_color=transform("Wohngeld", mapper),
    )

    color_bar = ColorBar(
        color_mapper=mapper,
        location=(0, 0),
        ticker=BasicTicker(desired_num_ticks=20),
        formatter=NumeralTickFormatter(format="0€"),
        label_standoff=12,
        title="Wg in €",
    )

    p.xaxis.axis_label = "Monthly rent in €"
    p.xaxis[0].formatter = NumeralTickFormatter(format="0€")

    p.yaxis.axis_label = "Monthly income in €"
    p.yaxis[0].formatter = NumeralTickFormatter(format="0€")

    p.add_layout(color_bar, "right")
    return p


# Example simulation
processed_data = prepare_data(sel_year=2019, hh_size=1)
plot = setup_plot(processed_data)
show(plot)
