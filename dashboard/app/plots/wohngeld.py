import itertools

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
from bokeh.models import Slider
from bokeh.palettes import Viridis256
from bokeh.plotting import figure
from bokeh.transform import transform

from .plotstyle import plotstyle


def wohngeld(plot_dict, data):
    def make_dataset(sel_year, hh_size, wg_dict):
        dataset = wg_dict[sel_year][hh_size]

        heatmap_source = pd.DataFrame(
            dataset.stack(), columns=["Wohngeld"]
        ).reset_index()
        heatmap_source.columns = ["Miete", "Einkommen", "Wohngeld"]

        return ColumnDataSource(heatmap_source)

    def update_plot(attr, old, new):  # noqa: U100
        sel_year = [1992, 2001, 2009, 2016, 2020, 2021][year_selection.active]
        hh_size = hh_size_selection.value
        new_src = make_dataset(sel_year, hh_size, wg_dict)

        src.data.update(new_src.data)

    def setup_plot(src):
        """Create the heatmap plot.

        src: ColumnDataSource

        """
        # Prepare a color pallete and color mapper
        mapper = LinearColorMapper(
            # force 0 to be mapped with white color
            palette=tuple(
                itertools.chain(["#FFFFFF"], tuple(reversed(Viridis256[1:])))
            ),
            low=0,
            high=1000,
        )

        # Actual figure setup
        p = figure(
            plot_width=800,
            plot_height=400,
            x_range=(src.data["Miete"].min(), src.data["Miete"].max()),
            y_range=(src.data["Einkommen"].min(), src.data["Einkommen"].max()),
            tools="hover",
            tooltips="Housing Benefit: @Wohngeld{0.0f}€",
        )

        p.rect(
            x="Miete",
            y="Einkommen",
            width=25,
            height=src.data["Einkommen"][1] - src.data["Einkommen"][0],
            source=src,
            line_color=transform("Wohngeld", mapper),
            fill_color=transform("Wohngeld", mapper),
        )

        color_bar = ColorBar(
            color_mapper=mapper,
            location=(0, 0),
            ticker=BasicTicker(desired_num_ticks=20),
            formatter=NumeralTickFormatter(format="0€"),
            label_standoff=12,
        )
        p.add_layout(color_bar, "right")

        plot = plotstyle(p, plot_dict)

        return plot

    wg_dict = data

    year_selection = RadioButtonGroup(
        labels=[str(i) for i in [1992, 2001, 2009, 2016, 2020, 2021]], active=5
    )
    year_selection.on_change("active", update_plot)

    hh_size_selection = Slider(start=1, end=12, value=4, step=1, title="Household Size")
    hh_size_selection.on_change("value", update_plot)

    src = make_dataset(2021, 4, wg_dict)

    p = setup_plot(src)

    description = Div(text=plot_dict["description"], width=1000)

    year_label = Div(text="Year")

    layout = column(description, year_label, year_selection, hh_size_selection, p)

    tab = Panel(child=layout, title="Housing benefits")

    return tab
