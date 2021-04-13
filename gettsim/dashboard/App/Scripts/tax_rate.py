from Scripts.plotstyle import plotstyle

from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models import Div
from bokeh.models import Panel
from bokeh.models import Slider
from bokeh.plotting import figure


def tax_rate(plot_dict, data):
    def make_dataset(sel_year, tax_rate_dict_full):
        dataset = tax_rate_dict_full[sel_year]

        return ColumnDataSource(dataset)

    def setup_plot(src):

        p = figure(plot_width=800, plot_height=400, y_range=(-0.01, 0.5),)
        p.line(
            x="income",
            y="tax_rate",
            source=src,
            line_width=2,
            legend_label="Income tax rate",
        )
        p.line(
            x="income",
            y="overall_tax_rate",
            source=src,
            line_width=2,
            line_color="black",
            legend_label="Income tax rate + soli",
        )
        p.line(
            x="income",
            y="marginal_rate",
            source=src,
            line_width=2,
            line_color="red",
            legend_label="Marginal tax rate",
        )

        plot = plotstyle(p, plot_dict)

        return plot

    def update_plot(attr, old, new):
        sel_year = year_selection.value
        new_src = make_dataset(sel_year, tax_rate_dict_full)

        src.data.update(new_src.data)

    tax_rate_dict_full = data

    year_selection = Slider(start=2002, end=2021, value=2021, step=1, title="Year")
    year_selection.on_change("value", update_plot)

    src = make_dataset(2019, tax_rate_dict_full)

    p = setup_plot(src)
    description = Div(text=plot_dict["description"], width=1000,)

    layout = column(description, year_selection, p)

    tab = Panel(child=layout, title="Tax rate per taxable income")

    return tab
