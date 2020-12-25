import pandas as pd
from bokeh.models import NumeralTickFormatter
from bokeh.palettes import Category20
from bokeh.plotting import figure
from bokeh.plotting import output_file
from bokeh.plotting import show

from gettsim import set_up_policy_environment

output_file("soz_vers_plot.html")


def prepare_data(start, end):
    """
    For a year range returns the policy parameters to plot the social security
    contributions

    start (Int): Defines the start of the simulated period
    end (Int):  Defines the end of the simulated period

    returns dataframe
    """
    years = range(start, end)

    soz_vers_dict = {}

    for i in years:
        policy_params, policy_functions = set_up_policy_environment(i)
        soz_vers_dict[i] = policy_params["soz_vers_beitr"]["soz_vers_beitr"]

    soz_vers_df = pd.DataFrame(data=soz_vers_dict).transpose()

    # Dictionairy entries into columns
    soz_vers_df = pd.concat(
        [
            soz_vers_df.drop(["ges_krankenv"], axis=1),
            soz_vers_df["ges_krankenv"].apply(pd.Series),
        ],
        axis=1,
    )
    soz_vers_df = pd.concat(
        [
            soz_vers_df.drop(["pflegev"], axis=1),
            soz_vers_df["pflegev"].apply(pd.Series),
        ],
        axis=1,
    )
    return soz_vers_df


def setup_plot(soz_vers_df):
    color = Category20[6]

    p = figure(
        plot_width=600,
        plot_height=400,
        background_fill_color="white",
        title="Social Security contributions",
        x_range=(min(soz_vers_df.index), max(soz_vers_df.index) + 6),
    )
    k = -1
    for i in soz_vers_df.columns:
        k = k + 1
        p.line(
            soz_vers_df.index,
            soz_vers_df[i],
            line_width=2,
            line_color=color[k],
            legend_label=i,
            alpha=0.8,
            muted_alpha=0.2,
            muted_color=color[k],
        )

    p.legend.location = "top_right"
    p.xaxis.bounds = (min(soz_vers_df.index), max(soz_vers_df.index))

    p.legend.click_policy = "mute"

    p.yaxis.axis_label = "Social security contributions"
    p.xaxis.axis_label = "Year"

    p.yaxis[0].formatter = NumeralTickFormatter(format="0%")

    return p


# Example

processed_data = prepare_data(start=2002, end=2019)
plot = setup_plot(processed_data)
show(plot)
