# Import functions
import pandas as pd
from bokeh.palettes import Category20
from bokeh.plotting import figure
from bokeh.plotting import output_file
from bokeh.plotting import show

from gettsim import set_up_policy_environment

output_file("einkst_ab_plot.html")


# Data preparation income tax deductions
def prepare_data(start, end):
    """
    Data preparation for income tax deduction parameters. Returns
    a dataframe.

    Parameters:
    start (Int): Defines the start of the simulated period
    end (Int):  Defines the end of the simulated period
    """
    # Period for simulation:
    years = range(start, end)
    eink_ab_df = pd.DataFrame()

    # Loop through years to get the policy parameters
    for i in years:
        policy_params, policy_functions = set_up_policy_environment(i)
        params = policy_params["eink_st_abzuege"]
        if i > 2001:
            params["grundfreibetrag"] = policy_params["eink_st"]["eink_st_tarif"][
                "thresholds"
            ][1]
        else:
            params["grundfreibetrag"] = 0
        eink_ab_df[i] = params.values()

    eink_ab_df.index = params.keys()
    deduction_df = eink_ab_df.transpose()
    # Adjust dictionairy entries into columns for kinderfreibetrag
    deduction_df = pd.concat(
        [
            deduction_df.drop(["kinderfreibetrag", "datum"], axis=1),
            deduction_df["kinderfreibetrag"].apply(pd.Series),
        ],
        axis=1,
    )
    # Adjust dictionairy entries into columns for behinderten_pauschbetrag
    deduction_df = pd.concat(
        [
            deduction_df.drop(["behinderten_pauschbetrag"], axis=1),
            deduction_df["behinderten_pauschbetrag"].apply(pd.Series),
        ],
        axis=1,
    )
    deduction_df = deduction_df.rename(
        columns={
            25: "behinderten_pauschbetrag25",
            35: "behinderten_pauschbetrag35",
            45: "behinderten_pauschbetrag45",
            55: "behinderten_pauschbetrag55",
            65: "behinderten_pauschbetrag65",
            75: "behinderten_pauschbetrag75",
            85: "behinderten_pauschbetrag85",
            95: "behinderten_pauschbetrag95",
        }
    )
    deduction_df = deduction_df.drop([0], axis=1)

    return deduction_df


def plotstyle(p, legend_location, x_axis_label, y_axis_label, lower_bound, upper_bound):
    p.legend.location = legend_location
    p.legend.click_policy = "mute"
    p.xaxis.axis_label = x_axis_label
    p.yaxis.axis_label = y_axis_label
    p.xaxis.bounds = (lower_bound, upper_bound)

    return p


def setup_plot(deduction_df):
    """
    Create the deduction plot.

    Parameters

    (pd.Dataframe): Returned by the data preparation
    function
    """
    # Selecotrs to split up plotting
    selector_vorsorge = [
        "vorsorge2004_vorwegabzug",
        "vorsorge_2004_grundhöchstbetrag",
        "altersentlastungsbetrag_max",
        "altersentlastung_quote",
        "vorsorge2004_kürzung_vorwegabzug",
        "vorsorge_sonstige_aufw_max",
        "vorsorge_altersaufw_max",
        "vorsorge_kranken_minderung",
    ]

    selector_kinder = [
        "alleinerziehenden_freibetrag",
        "alleinerziehenden_freibetrag_zusatz",
        "kinderbetreuungskosten_abz_anteil",
        "kinderbetreuungskosten_abz_maximum",
        "beitr_erz_ausb",
    ]

    selector_sparer = [
        "werbungskostenpauschale",
        "sonderausgabenpauschbetrag",
        "sparerpauschbetrag",
        "sparer_werbungskosten_pauschbetrag",
        "sächl_existenzmin",
    ]

    selector_behinderten = [
        "behinderten_pauschbetrag25",
        "behinderten_pauschbetrag35",
        "behinderten_pauschbetrag45",
        "behinderten_pauschbetrag55",
        "behinderten_pauschbetrag65",
        "behinderten_pauschbetrag75",
        "behinderten_pauschbetrag85",
        "behinderten_pauschbetrag95",
    ]

    selector_important = [
        "beitr_erz_ausb",
        "sächl_existenzmin",
        "sparerpauschbetrag",
        "werbungskostenpauschale",
        "alleinerziehenden_freibetrag",
        "grundfreibetrag",
    ]
    # Create nice parameter names - To do: find a better way to get names and include
    # into datapreparation

    deduction_df[selector_important].columns = [
        "Income Tax Allowance for children education",
        "Basic Income Tax Allowance for children",
        "Allowance for Capital Gains",
        "Lump-sum deduction for employment income",
        "Income Tax Allowance for Single Parents",
        "Basic allowance",
    ]

    # Plot for the most important deductions

    p = figure(
        title="Income tax deductions",
        plot_height=300,
        plot_width=600,
        y_range=(0, 9500),
        x_range=(start, end),
        background_fill_color="white",
    )

    for i in range(int(deduction_df[selector_important].shape[1])):
        i = p.line(
            deduction_df.index,
            deduction_df[selector_important].iloc[:, i],
            line_width=2,
            alpha=0.8,
            color=Category20[20][i],
            muted_color=Category20[20][i],
            legend_label=[
                "Income Tax Allowance for children education",
                "Basic Income Tax Allowance for children",
                "Allowance for Capital Gains",
                "Lump-sum deduction for employment income",
                "Income Tax Allowance for Single Parents",
                "Basic allowance",
            ][i],
            muted_alpha=0.2,
        )
    p.legend.background_fill_alpha = 0

    # Plot vorsorge parameters
    p1 = figure(
        title="Income tax deduction parameter vorsorge",
        plot_height=300,
        plot_width=850,
        y_range=(0, 3200),
        x_range=(start, end + 22),
        background_fill_color="#efefef",
    )

    for i in range(int(deduction_df[selector_vorsorge].shape[1])):
        i = p1.line(
            deduction_df.index,
            deduction_df[selector_vorsorge].iloc[:, i],
            line_width=2,
            alpha=0.8,
            color=Category20[20][i],
            muted_color=Category20[20][i],
            legend_label=deduction_df[selector_vorsorge].columns[i],
            muted_alpha=0.2,
        )

    # Plot kinder parameters
    p2 = figure(
        title="Income tax deduction parents",
        plot_height=300,
        plot_width=850,
        y_range=(0, 3200),
        x_range=(start, end + 22),
        background_fill_color="#efefef",
    )

    for i in range(int(deduction_df[selector_kinder].shape[1])):
        i = p2.line(
            deduction_df.index,
            deduction_df[selector_kinder].iloc[:, i],
            line_width=2,
            alpha=0.8,
            color=Category20[20][i],
            muted_color=Category20[20][i],
            legend_label=deduction_df[selector_kinder].columns[i],
            muted_alpha=0.2,
        )

    # Plot sparer params
    p3 = figure(
        title="Income tax deduction savings",
        plot_height=300,
        plot_width=850,
        y_range=(0, 3200),
        x_range=(start, end + 22),
        background_fill_color="#efefef",
    )

    for i in range(int(deduction_df[selector_sparer].shape[1])):
        i = p3.line(
            deduction_df.index,
            deduction_df[selector_sparer].iloc[:, i],
            line_width=2,
            alpha=0.8,
            color=Category20[20][i],
            muted_color=Category20[20][i],
            legend_label=deduction_df[selector_sparer].columns[i],
            muted_alpha=0.2,
        )

    # Plot behinderten_pausch params
    p4 = figure(
        title="Income tax deduction disabled",
        plot_height=300,
        plot_width=850,
        y_range=(0, 3200),
        x_range=(start, end + 22),
        background_fill_color="#efefef",
    )

    for i in range(int(deduction_df[selector_behinderten].shape[1])):
        i = p4.line(
            deduction_df.index,
            deduction_df[selector_behinderten].iloc[:, i],
            line_width=2,
            alpha=0.8,
            color=Category20[20][i],
            muted_color=Category20[20][i],
            legend_label=deduction_df[selector_behinderten].columns[i],
            muted_alpha=0.2,
        )
    p_list = [p, p1, p2, p3, p4]
    for p in p_list:
        p = plotstyle(
            p,
            "top_left",
            "year",
            "Deductions in €",
            min(deduction_df.index),
            max(deduction_df.index),
        )

    return p_list


# Example
start = 1975
end = 2020

processed_data = prepare_data(start, end)
plot, plot1, plot2, plot3, plot4 = setup_plot(processed_data)
# grid = gridplot([plot1, plot2, plot3, plot4], ncols=1)
show(plot)
