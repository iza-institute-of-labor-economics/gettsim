from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models import Div
from bokeh.models import Panel
from bokeh.palettes import Category10
from bokeh.plotting import figure

from .plotstyle import plotstyle


def deductions(plot_dict, data):
    def setup_plot(src):
        """Create the deduction plot.

        Parameters

        src: ColumnDataSource returned by the data preparation function

        """
        # Plot for the most important deductions
        p = figure(
            plot_height=400,
            plot_width=800,
            y_range=(0, 10500),
            x_range=(min(src.data["index"]), max(src.data["index"]) + 1),
            tooltips="$name: $y{0} €",
        )
        deduct_labels = {
            "beitr_erz_ausb": "Income Tax Allowance for children education",
            "sächl_existenzmin": "Basic Income Tax Allowance for children",
            "sparerpauschbetrag": "Allowance for Capital Gains",
            "werbungskostenpauschale": "Lump-sum deduction for employment income",
            "alleinerz_freibetrag": "Income Tax Allowance for Single Parents",
            "grundfreibetrag": "Basic allowance",
        }

        for count, i in enumerate(
            list(set(src.column_names) & set(deduct_labels.keys()))
        ):
            color = Category10[len(deduct_labels.keys())][count]
            p.step(
                x="index",
                y=i,
                line_width=2,
                alpha=0.8,
                color=color,
                legend_label=deduct_labels[i],
                muted_color=color,
                muted_alpha=0.2,
                source=src,
                name=deduct_labels[i],
                mode="after",
            )

            p.circle(
                x="index",
                y=i,
                line_width=2,
                alpha=0.8,
                color=color,
                legend_label=deduct_labels[i],
                muted_color=color,
                muted_alpha=0.2,
                source=src,
                name=deduct_labels[i],
            )

        plot = plotstyle(p, plot_dict)

        return plot

    src = ColumnDataSource(data)

    p = setup_plot(src)
    description = Div(text=plot_dict["description"], width=1000)

    layout = column(description, p)

    tab = Panel(child=layout, title="Income tax deductions")

    return tab
