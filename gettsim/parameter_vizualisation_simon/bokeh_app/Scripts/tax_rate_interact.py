from Scripts.plotstyle import plotstyle

import numpy as np
import pandas as pd
from bokeh.layouts import column
from bokeh.models import ColumnDataSource
from bokeh.models import Panel
from bokeh.models import Slider
from bokeh.plotting import figure

from gettsim import set_up_policy_environment
from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.taxes.eink_st import st_tarif


def tax_rate_interact(plot_dict):
    plot_dict = plot_dict["tax_rate"]

    def prepare_data(start, end):
        """
        For a given year span returns the policy parameters to plot income tax
        rate per income

        sel_year (Int): The year for which the data will be simulated. The range for
                        which parameters can be simulated is 2002-2020.

        returns dict
        """
        years = range(start, end)
        einkommen = pd.Series(data=np.linspace(0, 300000, 250))
        tax_rate_dict_full = {}
        for i in years:
            policy_params, policy_functions = set_up_policy_environment(i)
            eink_params = policy_params["eink_st"]
            soli_params = policy_params["soli_st"]["soli_st"]

            eink_tax = st_tarif(einkommen, eink_params)
            soli = piecewise_polynomial(
                eink_tax,
                thresholds=soli_params["thresholds"],
                rates=soli_params["rates"],
                intercepts_at_lower_thresholds=soli_params[
                    "intercepts_at_lower_thresholds"
                ],
            )
            marginal_rate = np.gradient(eink_tax, einkommen)

            tax_rate_dict_full[i] = {
                "tax_rate": (eink_tax / einkommen),
                "overall_tax_rate": ((soli + eink_tax) / einkommen),
                "marginal_rate": pd.Series(marginal_rate),
                "income": einkommen,
            }

        return tax_rate_dict_full

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

        p = plotstyle(p, plot_dict)

        return p

    def update_plot(attr, old, new):
        sel_year = year_selection.value
        new_src = make_dataset(sel_year, tax_rate_dict_full)

        src.data.update(new_src.data)

    tax_rate_dict_full = prepare_data(2002, 2021)

    year_selection = Slider(start=2002, end=2020, value=2020, step=1, title="Year")
    year_selection.on_change("value", update_plot)

    src = make_dataset(2019, tax_rate_dict_full)

    p = setup_plot(src)

    layout = column(year_selection, p)

    tab = Panel(child=layout, title="Tax rate per taxable income")

    return tab
