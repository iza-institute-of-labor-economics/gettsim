# Bokeh basics
from Scripts.deductions_interact import deduction_tab
from Scripts.tax_rate_interact import tax_rate_interact
from Scripts.wohngeld_interact import wohngeld_tab

from bokeh.io import curdoc
from bokeh.models.widgets import Tabs

# Each tab is drawn by one script

# Create a dictionairy to store all plot titles, axes etc.
plot_list = ["wohngeld", "tax_rate", "deductions"]
plot_attributes = [
    "title",
    "x_axis_label",
    "y_axis_label",
    "x_axis_format",
    "y_axis_format",
    "legend_location",
]
attribute_dict = {
    "wohngeld": [
        "Monthly wohngeld in € per income and rent",
        "Monthly rent in €",
        "Monthly income in €",
        "0€",
        "0€",
        "None",
    ],
    "tax_rate": [
        "Tax rate per income",
        "Taxable income in €",
        "Tax rate",
        "0€",
        "0%",
        "bottom_right",
    ],
    "deductions": [
        "Income tax deductions",
        "Year",
        "Deductions in €",
        "0",
        "0€",
        "top_left",
    ],
}
plot_dict = {
    p: {a: attribute_dict[p][counter] for counter, a in enumerate(plot_attributes)}
    for p in plot_list
}


# Call tab functions
tab1 = tax_rate_interact(plot_dict)
tab2 = wohngeld_tab(plot_dict)
tab3 = deduction_tab(plot_dict)

tabs = Tabs(tabs=[tab1, tab2, tab3])

curdoc().add_root(tabs)
