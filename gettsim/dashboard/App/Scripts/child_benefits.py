from Scripts.plotstyle import plotstyle

from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models import Div
from bokeh.models import Panel
from bokeh.palettes import Category10
from bokeh.plotting import figure


def child_benefits(plot_dict, data):
    def setup_plot(kindergeld_df):
        """
        Create the kindergeld plot.
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
            x_range=(min(kindergeld_df.index), max(kindergeld_df.index)),
            background_fill_color="#efefef",
            tooltips="$name: @$name €",
        )
        k = -1
        for i in kindergeld_df.columns:
            k = k + 1
            p.step(
                x="index",
                y=i,
                line_width=2,
                color=Category10[4][k],
                legend_label=kindergeld_df.columns[k],
                alpha=0.8,
                muted_color=Category10[4][k],
                muted_alpha=0.2,
                source=source,
                name=i,
                mode="after",
            )
        k = -1
        for i in kindergeld_df.columns:
            k = k + 1
            p.circle(
                x="index",
                y=i,
                line_width=2,
                color=Category10[4][k],
                legend_label=kindergeld_df.columns[k],
                alpha=0.8,
                muted_color=Category10[4][k],
                muted_alpha=0.2,
                source=source,
                name=i,
            )

        plot = plotstyle(p, plot_dict)

        return plot

    p = setup_plot(data)

    description = Div(text=plot_dict["description"], width=1000,)

    layout = column(description, p)

    tab = Panel(child=layout, title="Child benefits")

    return tab
