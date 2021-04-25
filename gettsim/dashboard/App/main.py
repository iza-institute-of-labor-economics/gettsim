import pickle

import pytz
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import Div
from bokeh.models.widgets import Tabs
from Scripts.child_benefits import child_benefits
from Scripts.deductions import deductions
from Scripts.heatmap import heatmap_tab
from Scripts.social_assistance import social_assistance
from Scripts.social_security import social_security
from Scripts.tax_rate import tax_rate

tz = pytz.timezone("Europe/Berlin")

# Create a dictionary to store all plot titles, axes etc.
plot_list = [
    "tax_rate",
    "wohngeld",
    "deductions",
    "social_security",
    "child_benefits",
    "social_assistance",
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
        "Statutory Income Tax rate by taxable income",
        "Taxable income",
        "Tax rate",
        "€0",
        "0%",
        "bottom_right",
        """This graph demonstrates the statutory income tax rate with and without
        Solidarity Surcharge.""",
    ],
    "deductions": [
        "Income tax deductions",
        "Year",
        "Annual Deductions (in €)",
        "0€",
        "0€",
        "top_left",
        """This graph shows the evolution of the main lump-sum tax deductions
        creating a wedge between market and taxable income.""",
    ],
    "wohngeld": [
        "Monthly housing benefits (in €) per income and rent",
        "Monthly rent in €",
        "Monthly income in €",
        "0€",
        "0€",
        "top_left",
        """This Graph depicts the monthly housing benefit, depending on household size and
        year. We assume Mietstufe 3, which corresponds to a municipality with average
        rental cost.""",
    ],
    "child_benefits": [
        "Monthly child benefits per child",
        "Year",
        "Child benefits (in €)",
        "0",
        "0€",
        "top_left",
        """Monthly child benefit by order of child within the household.""",
    ],
    "social_security": [
        "Social security contribution rates",
        "Year",
        "Social Security contribution rate",
        "0",
        "0%",
        "top_right",
        """This graph depicts contribution rates to the four main branches of
        social security. With the exception of health insurance, contributions
        are shared between employer and employee. The graph shows only the
        employees share for those branches.""",
    ],
    "social_assistance": [
        "Social Assistance rate",
        "Year",
        "Monthly Social Assistance Rate (€)",
        "0",
        "0€",
        "top_left",
        """This graph depicts personal social assistance payments
        ('Regelsatz Arbeitslosengeld II') by household member.""",
    ],
}

# print("{} INFO - Creating a plot dict".format(datetime.now(tz)))

plot_dict = {
    p: {a: attribute_dict[p][counter] for counter, a in enumerate(plot_attributes)}
    for p in plot_list
}

all_data = pickle.load(open("all_data.pickle", "rb"))

# print("{} INFO - Server receives request".format(datetime.now(tz)))

# Call tab functions)
tab1 = tax_rate(plot_dict["tax_rate"], all_data["tax_rate"])
tab2 = deductions(plot_dict["deductions"], all_data["deductions"])
tab3 = heatmap_tab(plot_dict["wohngeld"], all_data["wohngeld"])
tab4 = child_benefits(plot_dict["child_benefits"], all_data["child_benefits"])
tab5 = social_security(plot_dict["social_security"], all_data["social_security"])
tab6 = social_assistance(plot_dict["social_assistance"], all_data["social_assistance"])

tabs = Tabs(tabs=[tab1, tab2, tab3, tab4, tab5, tab6])

header = Div(text="""<h1>GETTSIM parameter visualisations</h1>""", width=900, height=80)

intro = Div(
    text="""<h4>This dashboard visualizes GETTSIM parameters. Further information can be
    found in the
    <a href="https://gettsim.readthedocs.io/en/stable/">documentation</a>.</h4>
    """,
    width=800,
    height=70,
)


# print("{} INFO - Server completes processing request".format(datetime.now(tz)))

# Put everything together
curdoc().add_root(column(header, intro, tabs))
curdoc().title = "GETTSIM parameter visualizations"
