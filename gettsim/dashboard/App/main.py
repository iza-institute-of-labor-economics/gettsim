# Bokeh basics
import pickle
from datetime import datetime

import pytz
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.layouts import row
from bokeh.models import Button
from bokeh.models import Div
from bokeh.models import TextInput
from bokeh.models.widgets import Tabs

tz = pytz.timezone("Europe/Berlin")

# Create a dictionairy to store all plot titles, axes etc.
plot_list = [
    "tax_rate",
    "wohngeld",
    "deductions",
    "behavioral_response",
    "revenue_bevavior",
    "child_benefits",
    "parameter_heatmap",
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
        "Monthly wohngeld in € per income and rent",
        "Monthly rent in €",
        "Monthly income in €",
        "0€",
        "0€",
        "top_left",
        """Description text to be added.""",
    ],
    "tax_revenue": [
        "Aggregate mechanical tax revenue effects of reform",
        "Agr. change to tax revenue (in Million €)",
        "Deciles",
        "0€",
        "",
        "",
        """Simulation of tax revenue changes of the considered reform in 2017. Shown are the
        aggregate (not average) changes in tax revenue per decile in Million Euro. The table
        also shows the corresponding changes to effective tax rate (ΔETR).""",
    ],
    "behavioral_response": [
        "Average change to reported tax base per decile",
        "",
        "Avg. changes to reported tax base (in €)",
        "",
        "0€",
        "top_left",
        """Based on the changes to the effective tax rate (ΔETR) by decile, this figure
        illustrates the average change in reported total tax base due to behavioral
        responses for different elasticity levels. Bottom three deciles are omitted (as ΔETR=0).
        The recovered portion can be used to simulate offsetting externalities like
        evaded taxes recovered in tax audits or income shifted to other tax bases or
        periods.""",
    ],
    "revenue_bevavior": [
        "Aggregate tax revenue change after behavioral responses per decile",
        "Agr. change to tax revenue (in Million €)",
        "Deciles",
        "0€",
        "",
        "",
        """""",
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
    "parameter_heatmap": [
        "Heatmap: Reform effect on tax revenue by behavioral response parameter values",
        "Recovered portion (Offsetting externalities to behavioral reactions)",
        "Elasticity of capital income",
        "0.0",
        "0.0",
        "",
        """Parameter heatmap for the elasticity of capital income and recovered portion.
        Displays how combinations of the parameters affect the total revenue effect of
        the simulated reform. The black dots indicate for which combination the reform
        would have an aggregate effect of approximately 0. For most deciles the changes
        are small.""",
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
from Scripts.pre_processing import generate_data
from Scripts.child_benefits import child_benefits


all_data = pickle.load(open("all_data.pickle", "rb"))

print("{} INFO - Server receives request".format(datetime.now(tz)))


# Call tab functions
tab1 = tax_rate(plot_dict["tax_rate"], all_data["tax_rate"])
tab2 = deductions(plot_dict["deductions"], all_data["deductions"])
tab3 = heatmap_tab(plot_dict["wohngeld"], all_data["wohngeld"])
tab4 = child_benefits(plot_dict["child_benefits"], all_data["child_benefits"])


tabs = Tabs(tabs=[tab1, tab2, tab3, tab4])

header = Div(
    text="""<h1>GETTSIM parameter visualisations</h1>""", width=900, height=80,
)

intro = Div(
    text="""This dashboard visualizes GETTSIM parameters. Further information can be
    found in the  <a href="https://gettsim.readthedocs.io/en/stable/">documention</a>.""",
    width=800,
    height=30,
)

spacer = Div(text="""""", height=20)

# Functions for regenerating data


def finished_text():
    update_text.value = "Status: Completed"


def update_function():
    update_text.value = "Status: In progress"
    curdoc().add_next_tick_callback(generate_data)
    curdoc().add_next_tick_callback(finished_text)


update_text = TextInput(value="Status: Not started", disabled=True, width=140)

button = Button(
    label="Regenerate data", button_type="success", width=140, background="#c1c1c1"
)
button.on_click(update_function)


print("{} INFO - Server completes processing request".format(datetime.now(tz)))

# Put everything together
curdoc().add_root(column(header, intro, row(button, update_text), spacer, tabs))
curdoc().title = "GETTSIM parameter visualizations"
