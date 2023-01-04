from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models import Div
from bokeh.models import Panel
from bokeh.palettes import Category10
from bokeh.plotting import figure

from .plotstyle import plotstyle


def social_security(plot_dict, data):
    def setup_plot(src):
        p = figure(
            plot_width=900,
            plot_height=400,
            x_range=(1984, 2022 + 8),
            tooltips="$name: @$name{0.00%}",
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
        p.xaxis.bounds = (1984, max(src.data["index"]) + 1)

        plot = plotstyle(p, plot_dict)

        return plot

    src = ColumnDataSource(data)

    p = setup_plot(src)
    description = Div(
        text=plot_dict["description"],
        width=1000,
    )

    layout = column(description, p)

    tab = Panel(child=layout, title="Social security contributions")

    return tab
