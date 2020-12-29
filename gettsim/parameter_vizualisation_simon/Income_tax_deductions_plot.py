# Import functions
# import gettsim
import pandas as pd
from bokeh.layouts import gridplot
from bokeh.palettes import Category20
from bokeh.plotting import figure
from bokeh.plotting import output_file
from bokeh.plotting import show

from gettsim import set_up_policy_environment

output_file("einkst_ab_plot.html")


# Data preparation income tax deductions
def prepare_data(start, end):
    """
    Data preparation for income tax deduction parameters. Return a dataframe.

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


def setup_plot(deduction_df):
    """
    Create the deduction plot.

    Parameters

    (pd.Dataframe): Returned by the data preparation function
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

    # Plot vorsorge parameters
    deductions_p = figure(
        title="Income tax deduction parameter vorsorge",
        plot_height=400,
        plot_width=850,
        y_range=(0, 3200),
        x_range=(start, end + 22),
        background_fill_color="#efefef",
    )

    for i in range(int(deduction_df[selector_vorsorge].shape[1])):
        i = deductions_p.line(
            deduction_df.index,
            deduction_df[selector_vorsorge].iloc[:, i],
            line_width=2,
            alpha=0.8,
            color=Category20[20][i],
            muted_color=Category20[20][i],
            legend_label=deduction_df[selector_vorsorge].columns[i],
            muted_alpha=0.2,
        )
    deductions_p.legend.location = "top_right"
    deductions_p.legend.click_policy = "hide"
    deductions_p.xaxis.axis_label = "Year"
    deductions_p.yaxis.axis_label = "Deductions in €"
    deductions_p.xaxis.bounds = (start, end)

    # Plot kinder parameters
    deductions_p2 = figure(
        title="Income tax deduction parents",
        plot_height=400,
        plot_width=850,
        y_range=(0, 3200),
        x_range=(start, end + 22),
        background_fill_color="#efefef",
    )

    for i in range(int(deduction_df[selector_kinder].shape[1])):
        i = deductions_p2.line(
            deduction_df.index,
            deduction_df[selector_kinder].iloc[:, i],
            line_width=2,
            alpha=0.8,
            color=Category20[20][i],
            muted_color=Category20[20][i],
            legend_label=deduction_df[selector_kinder].columns[i],
            muted_alpha=0.2,
        )
    deductions_p2.legend.location = "top_right"
    deductions_p2.legend.click_policy = "hide"
    deductions_p2.xaxis.axis_label = "Year"
    deductions_p2.yaxis.axis_label = "Deductions in €"
    deductions_p2.xaxis.bounds = (start, end)

    # Plot sparer params
    deductions_p3 = figure(
        title="Income tax deduction savings",
        plot_height=400,
        plot_width=850,
        y_range=(0, 3200),
        x_range=(start, end + 22),
        background_fill_color="#efefef",
    )

    for i in range(int(deduction_df[selector_sparer].shape[1])):
        i = deductions_p3.line(
            deduction_df.index,
            deduction_df[selector_sparer].iloc[:, i],
            line_width=2,
            alpha=0.8,
            color=Category20[20][i],
            muted_color=Category20[20][i],
            legend_label=deduction_df[selector_sparer].columns[i],
            muted_alpha=0.2,
        )
    deductions_p3.legend.location = "top_right"
    deductions_p3.legend.click_policy = "hide"
    deductions_p3.xaxis.axis_label = "Year"
    deductions_p3.yaxis.axis_label = "Deductions in €"
    deductions_p3.xaxis.bounds = (start, end)

    # Plot behinderten_pausch params
    deductions_p4 = figure(
        title="Income tax deduction disabled",
        plot_height=400,
        plot_width=850,
        y_range=(0, 3200),
        x_range=(start, end + 22),
        background_fill_color="#efefef",
    )

    for i in range(int(deduction_df[selector_behinderten].shape[1])):
        i = deductions_p4.line(
            deduction_df.index,
            deduction_df[selector_behinderten].iloc[:, i],
            line_width=2,
            alpha=0.8,
            color=Category20[20][i],
            muted_color=Category20[20][i],
            legend_label=deduction_df[selector_behinderten].columns[i],
            muted_alpha=0.2,
        )
    deductions_p4.legend.location = "top_right"
    deductions_p4.legend.click_policy = "hide"
    deductions_p4.xaxis.axis_label = "Year"
    deductions_p4.yaxis.axis_label = "Deductions in €"
    deductions_p4.xaxis.bounds = (start, end)

    return deductions_p, deductions_p2, deductions_p3, deductions_p4


# Example
start = 1975
end = 2020

processed_data = prepare_data(start, end)
plot1, plot2, plot3, plot4 = setup_plot(processed_data)
grid = gridplot([plot1, plot2, plot3, plot4], ncols=1)
show(grid)
