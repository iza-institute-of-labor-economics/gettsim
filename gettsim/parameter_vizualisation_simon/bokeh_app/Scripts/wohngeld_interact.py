# Import
from Scripts.plotstyle import plotstyle

import numpy as np
import pandas as pd
from bokeh.layouts import column
from bokeh.models import BasicTicker
from bokeh.models import ColorBar
from bokeh.models import ColumnDataSource
from bokeh.models import LinearColorMapper
from bokeh.models import NumeralTickFormatter
from bokeh.models import Panel
from bokeh.models import Slider
from bokeh.palettes import Magma256
from bokeh.plotting import figure
from bokeh.transform import transform

from gettsim import set_up_policy_environment
from gettsim.transfers.wohngeld import wohngeld_basis


def wohngeld_tab(plot_dict):
    plot_dict = plot_dict["wohngeld"]

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
                wohngeld_max_miete=miete,
                wohngeld_params=params,
            )
        wohngeld_df.index = miete

        return wohngeld_df

    def loop(start, end):
        wg_dict = {}
        years = range(start, end)
        # hh_size_range = To do implement loop over hh_size-> issue too slow
        for i in years:
            wg_dict[i] = prepare_data(i, 1)

        return wg_dict

    def make_dataset(sel_year, wg_dict):
        dataset = wg_dict[sel_year]

        heatmap_source = pd.DataFrame(
            dataset.stack(), columns=["Wohngeld"]
        ).reset_index()
        heatmap_source.columns = ["Miete", "Einkommen", "Wohngeld"]

        return ColumnDataSource(heatmap_source)

    def update_plot(attr, old, new):
        sel_year = year_selection.value
        new_src = make_dataset(sel_year, wg_dict)

        src.data.update(new_src.data)

    def setup_plot(src):
        """
        Create the heatmap plot.

        parameters (pd.Dataframe): Returned by the data preparation function
        """

        # Prepare a color pallete and color mapper
        colors = Magma256[128:256]
        colors = list(colors)
        colors.reverse()
        mapper = LinearColorMapper(
            palette=colors,
            low=min(src.data["Wohngeld"]),
            high=max(src.data["Wohngeld"]),
        )

        # Actual figure setup
        p = figure(
            plot_width=600,
            plot_height=400,
            x_range=(0, 1300),
            y_range=(0, 1300),
            tools="",
        )

        p.rect(
            x="Miete",
            y="Einkommen",
            width=30,
            height=30,
            source=src,
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
        p.add_layout(color_bar, "right")

        plot = plotstyle(p, plot_dict)

        return plot

    wg_dict = loop(2002, 2021)

    year_selection = Slider(start=2002, end=2020, value=2020, step=1, title="Year")
    year_selection.on_change("value", update_plot)

    src = make_dataset(2020, wg_dict)

    p = setup_plot(src)

    layout = column(year_selection, p)

    tab = Panel(child=layout, title="Wohngeld heatmap")

    return tab
