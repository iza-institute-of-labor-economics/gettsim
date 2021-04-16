from Scripts.plotstyle import plotstyle

from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models import Div
from bokeh.models import Panel
from bokeh.palettes import Category20
from bokeh.plotting import figure


def deductions(plot_dict, data):
    def setup_plot(src):
        """
        Create the deduction plot.

        Parameters

        src: ColumnDataSource returned by the data preparation function
        """

        selector_important = [
            "beitr_erz_ausb",
            "sächl_existenzmin",
            "sparerpauschbetrag",
            "werbungskostenpauschale",
            "alleinerziehenden_freibetrag",
            "grundfreibetrag",
        ]

        # Plot for the most important deductions
        p = figure(
            plot_height=400,
            plot_width=800,
            y_range=(0, 9500),
            x_range=(min(src.data["index"]), max(src.data["index"])),
            tooltips="$name: @$name €",
        )

        for count, i in enumerate(
            list(set(src.column_names) & set(selector_important))
        ):
            i = p.step(
                x="index",
                y=i,
                line_width=2,
                alpha=0.8,
                color=Category20[10][count],
                muted_color=Category20[10][count],
                legend_label=[
                    "Lump-sum deduction for employment income",
                    "Income Tax Allowance for children education",
                    "Basic Income Tax Allowance for children",
                    "Basic allowance",
                    "Income Tax Allowance for Single Parents",
                    "Allowance for Capital Gains",
                ][count],
                muted_alpha=0.2,
                source=src,
                name=i,
                mode="after",
            )

        for count, i in enumerate(
            list(set(src.column_names) & set(selector_important))
        ):
            i = p.circle(
                x="index",
                y=i,
                line_width=2,
                alpha=0.8,
                color=Category20[10][count],
                muted_color=Category20[10][count],
                legend_label=[
                    "Lump-sum deduction for employment income",
                    "Income Tax Allowance for children education",
                    "Basic Income Tax Allowance for children",
                    "Basic allowance",
                    "Income Tax Allowance for Single Parents",
                    "Allowance for Capital Gains",
                ][count],
                muted_alpha=0.2,
                source=src,
                name=i,
            )

        plot = plotstyle(p, plot_dict)

        return plot

    src = ColumnDataSource(data)

    p = setup_plot(src)
    description = Div(text=plot_dict["description"], width=1000,)

    layout = column(description, p)

    tab = Panel(child=layout, title="Income tax deductions")

    return tab
