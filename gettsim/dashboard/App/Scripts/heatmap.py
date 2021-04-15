from Scripts.plotstyle import plotstyle

import pandas as pd
from bokeh.layouts import column
from bokeh.models import BasicTicker
from bokeh.models import ColorBar
from bokeh.models import ColumnDataSource
from bokeh.models import Div
from bokeh.models import LinearColorMapper
from bokeh.models import NumeralTickFormatter
from bokeh.models import Panel
from bokeh.models import RadioButtonGroup
from bokeh.palettes import Turbo256
from bokeh.plotting import figure
from bokeh.transform import transform


def heatmap_tab(plot_dict, data):
    def make_dataset(sel_year, hh_size, wg_dict):
        dataset = wg_dict[sel_year][hh_size]

        heatmap_source = pd.DataFrame(
            dataset.stack(), columns=["Wohngeld"]
        ).reset_index()
        heatmap_source.columns = ["Miete", "Einkommen", "Wohngeld"]

        return ColumnDataSource(heatmap_source)

    def update_plot(attr, old, new):
        sel_year = [1992, 2001, 2009, 2016, 2020, 2021][year_selection.active]
        hh_size = hh_size_selection.active + 1
        new_src = make_dataset(sel_year, hh_size, wg_dict)

        src.data.update(new_src.data)

    def setup_plot(src):
        """
        Create the heatmap plot.

        parameters (pd.Dataframe): Returned by the data preparation function
        """

        # Prepare a color pallete and color mapper
        colors = Turbo256[145:256]
        colors = list(colors)
        # colors.reverse()
        mapper = LinearColorMapper(
            palette=colors,
            low=min(src.data["Wohngeld"]),
            high=max(src.data["Wohngeld"]),
        )

        # Actual figure setup
        p = figure(
            plot_width=800,
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
            title="Housing benefits (in €)",
        )
        p.add_layout(color_bar, "right")

        plot = plotstyle(p, plot_dict)

        return plot

    wg_dict = data

    year_selection = RadioButtonGroup(
        labels=[str(i) for i in [1992, 2001, 2009, 2016, 2020, 2021]], active=5
    )
    year_selection.on_change("active", update_plot)

    hh_size_selection = RadioButtonGroup(
        labels=[str(i) for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]], active=0
    )
    hh_size_selection.on_change("active", update_plot)

    src = make_dataset(2020, 1, wg_dict)

    p = setup_plot(src)

    description = Div(text=plot_dict["description"], width=1000,)

    year_label = Div(text="Year")
    hh_size_label = Div(text="Household size")

    layout = column(
        description, year_label, year_selection, hh_size_label, hh_size_selection, p
    )

    tab = Panel(child=layout, title="Housing benefits heatmap")

    return tab
