from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models import Div
from bokeh.models import Panel
from bokeh.palettes import Category10
from bokeh.plotting import figure

from .plotstyle import plotstyle


def social_assistance(plot_dict, data):
    def setup_plot(src):
        p = figure(
            plot_width=750,
            plot_height=400,
            y_range=(0, 500),
            x_range=(2005, 2022),
            tooltips="$name: @$name €",
        )

        labels = list(src.data.keys())[1:]

        colors = Category10[len(labels)]

        for i in range(len(labels)):
            p.step(
                "index",
                labels[i],
                source=src,
                line_color=colors[i],
                line_width=2,
                legend_label=labels[i],
                alpha=0.8,
                muted_color=colors[i],
                muted_alpha=0.2,
                name=labels[i],
                mode="after",
            )
            p.circle(
                "index",
                labels[i],
                source=src,
                fill_color=colors[i],
                line_width=2,
                legend_label=labels[i],
                alpha=0.8,
                muted_color=colors[i],
                muted_alpha=0.2,
                line_color=colors[i],
                name=labels[i],
            )
        p.xaxis.bounds = (2004, max(src.data["index"]) + 1)
        p.xaxis.ticker.desired_num_ticks = 4

        plot = plotstyle(p, plot_dict)

        return plot

    data = data.rename(
        columns={
            "ein_erwachsener": "Single Adult",
            "zwei_erwachsene": "Adults in Couple",
            "weitere_erwachsene": "Adults not in Couple",
            "kinder_14_24": "Child 14 to 17 years",
            "kinder_7_13": "Child 6 to 13 years",
            "kinder_0_6": "Child < 6 years",
        }
    )
    src = ColumnDataSource(data)

    p = setup_plot(src)
    description = Div(text=plot_dict["description"], width=1000)

    layout = column(description, p)

    tab = Panel(child=layout, title="Social Assistance Rate")

    return tab
