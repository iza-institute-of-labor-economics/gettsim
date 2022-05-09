from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models import Div
from bokeh.models import Panel
from bokeh.models import Slider
from bokeh.plotting import figure

from .plotstyle import plotstyle


def tax_rate(plot_dict, data):  # noqa: U100
    def make_dataset(sel_year, tax_rate_dict_full):
        dataset = tax_rate_dict_full[sel_year]

        return ColumnDataSource(dataset)

    def setup_plot(src):
        p = figure(plot_width=800, plot_height=400, y_range=(-0.01, 0.5))

        taxplot_dict = {
            "tax_rate": {"label": "Average Tax Rate", "color": "blue"},
            "overall_tax_rate": {
                "label": "Average Tax Rate incl. Soli",
                "color": "black",
            },
            "marginal_rate": {"label": "Marginal Tax Rate", "color": "red"},
            "overall_marginal_rate": {
                "label": "Marginal Tax Rate incl. Soli",
                "color": "green",
            },
        }

        for yvar in taxplot_dict.keys():
            p.line(
                x="income",
                y=yvar,
                source=src,
                line_width=2,
                line_color=taxplot_dict[yvar]["color"],
                legend_label=taxplot_dict[yvar]["label"],
            )

        plot = plotstyle(p, plot_dict)

        return plot

    def update_plot(attr, old, new):  # noqa: U100
        sel_year = year_selection.value
        new_src = make_dataset(sel_year, tax_rate_dict_full)

        src.data.update(new_src.data)

    tax_rate_dict_full = data

    year_selection = Slider(start=2002, end=2021, value=2021, step=1, title="Year")
    year_selection.on_change("value", update_plot)

    src = make_dataset(2021, tax_rate_dict_full)

    p = setup_plot(src)
    description = Div(text=plot_dict["description"], width=800)

    layout = column(description, year_selection, p)

    tab = Panel(child=layout, title="Tax rate per taxable income")

    return tab
