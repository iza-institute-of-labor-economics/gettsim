from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models import Div
from bokeh.models import Panel
from bokeh.palettes import Category10
from bokeh.plotting import figure

from .plotstyle import plotstyle


def child_benefits(plot_dict, data):
    def setup_plot(kindergeld_df):
        """Create the kindergeld plot.

        Parameters
        (pd.Dataframe): Returned by the data preparation function

        """
        # Plot for kindergeld params

        source = ColumnDataSource(kindergeld_df)

        p = figure(
            title="Kindergeld per Child",
            plot_height=400,
            plot_width=800,
            y_range=(0, 270),
            x_range=(min(kindergeld_df.index), max(kindergeld_df.index) + 1),
            background_fill_color="#efefef",
            tooltips="$name: @$name €",
        )
        kig_params = list(kindergeld_df.columns)

        for i in kig_params:
            p.step(
                x="index",
                y=i,
                line_width=2,
                color=Category10[len(kig_params)][kig_params.index(i)],
                legend_label=i,
                alpha=0.8,
                muted_color=Category10[len(kig_params)][kig_params.index(i)],
                muted_alpha=0.2,
                source=source,
                name=i,
                mode="after",
            )

            p.circle(
                x="index",
                y=i,
                line_width=2,
                color=Category10[len(kig_params)][kig_params.index(i)],
                legend_label=i,
                alpha=0.8,
                muted_color=Category10[len(kig_params)][kig_params.index(i)],
                muted_alpha=0.2,
                source=source,
                name=i,
            )

        plot = plotstyle(p, plot_dict)

        return plot

    p = setup_plot(data)

    description = Div(text=plot_dict["description"], width=1000)

    layout = column(description, p)

    tab = Panel(child=layout, title="Child benefits")

    return tab
