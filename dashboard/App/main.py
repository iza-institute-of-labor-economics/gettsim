# Bokeh basics
import pickle
from datetime import datetime

import pytz
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import Div
from bokeh.models.widgets import Tabs

tz = pytz.timezone("Europe/Berlin")

# Create a dictionairy to store all plot titles, axes etc.
plot_list = [
    "tax_rate",
    "wohngeld",
    "deductions",
    "social_security",
    "child_benefits",
]
plot_attributes = [
    "title",
    "x_axis_label",
    "y_axis_label",
    "x_axis_format",
    "y_axis_format",
    "legend_location",
    "description",
]
attribute_dict = {
    "tax_rate": [
        "Tax rate by taxable income",
        "Taxable income",
        "Tax rate",
        "0.00",
        "0%",
        "bottom_right",
        """Description text to be added.""",
    ],
    "deductions": [
        "Income tax deductions",
        "Year",
        "Deductions (in €)",
        "0€",
        "0€",
        "top_left",
        """Description text to be added.""",
    ],
    "wohngeld": [
        "Monthly housing benefits (in €) per income and rent",
        "Monthly rent in €",
        "Monthly income in €",
        "0€",
        "0€",
        "top_left",
        """Description text to be added.""",
    ],
    "child_benefits": [
        "Monthly child benefits per child",
        "Year",
        "Child benefits (in €)",
        "0",
        "0€",
        "top_left",
        """Description text to be added.""",
    ],
    "social_security": [
        "Social security contributions",
        "Year",
        "Social Security contributions",
        "0",
        "0%",
        "top_right",
        """Description text to be added.""",
    ],
}

print("{} INFO - Creating a plot dict".format(datetime.now(tz)))

plot_dict = {
    p: {a: attribute_dict[p][counter] for counter, a in enumerate(plot_attributes)}
    for p in plot_list
}


# Each tab is drawn by one script
from Scripts.heatmap import heatmap_tab
from Scripts.deductions import deductions
from Scripts.tax_rate import tax_rate
from Scripts.child_benefits import child_benefits
from Scripts.social_security import social_security


all_data = pickle.load(open("all_data.pickle", "rb"))

print("{} INFO - Server receives request".format(datetime.now(tz)))


# Call tab functions
tab1 = tax_rate(plot_dict["tax_rate"], all_data["tax_rate"])
tab2 = deductions(plot_dict["deductions"], all_data["deductions"])
tab3 = heatmap_tab(plot_dict["wohngeld"], all_data["wohngeld"])
tab4 = child_benefits(plot_dict["child_benefits"], all_data["child_benefits"])
tab5 = social_security(plot_dict["social_security"], all_data["social_security"])

tabs = Tabs(tabs=[tab1, tab2, tab3, tab4, tab5])

header = Div(
    text="""<h1>GETTSIM parameter visualisations</h1>""", width=900, height=80,
)

intro = Div(
    text="""This dashboard visualizes GETTSIM parameters. Further information can be
    found in the  <a href="https://gettsim.readthedocs.io/en/stable/">documention</a>.""",
    width=800,
    height=30,
)


print("{} INFO - Server completes processing request".format(datetime.now(tz)))

# Put everything together
curdoc().add_root(column(header, intro, tabs))
curdoc().title = "GETTSIM parameter visualizations"
