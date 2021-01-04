# Import functions
from Scripts.plotstyle import plotstyle

import pandas as pd
from bokeh.models import ColumnDataSource
from bokeh.models import Panel
from bokeh.palettes import Category20
from bokeh.plotting import figure

from gettsim import set_up_policy_environment


def deduction_tab(plot_dict):
    plot_dict = plot_dict["deductions"]

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

        return ColumnDataSource(deduction_df)

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
            plot_width=650,
            y_range=(0, 9500),
            x_range=(min(src.data["index"]), max(src.data["index"])),
            tooltips="$name: @$name €",
        )

        for count, i in enumerate(
            list(set(src.column_names) & set(selector_important))
        ):
            i = p.line(
                x="index",
                y=i,
                line_width=2,
                alpha=0.8,
                color=Category20[20][count],
                muted_color=Category20[20][count],
                legend_label=[
                    "Income Tax Allowance for children education",
                    "Basic Income Tax Allowance for children",
                    "Allowance for Capital Gains",
                    "Lump-sum deduction for employment income",
                    "Income Tax Allowance for Single Parents",
                    "Basic allowance",
                ][count],
                muted_alpha=0.2,
                source=src,
                name=i,
            )

        plot = plotstyle(p, plot_dict)

        return plot

    src = prepare_data(1975, 2020)

    p = setup_plot(src)

    layout = p

    tab = Panel(child=layout, title="Income tax deductions")

    return tab
