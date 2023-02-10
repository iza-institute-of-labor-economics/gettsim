import pickle
import warnings

import pytz
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import Div
from bokeh.models.widgets import Tabs

from .plots.child_benefits import child_benefits
from .plots.deductions import deductions
from .plots.social_assistance import social_assistance
from .plots.social_security import social_security
from .plots.tax_rate import tax_rate
from .plots.wohngeld import wohngeld

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
# Github-Link to Parameters
params_url = """https://github.com/iza-institute-of-labor-economics/
gettsim/blob/main/gettsim/parameters"""
attribute_dict = {
    "tax_rate": [
        "Statutory Income Tax rate by taxable income",
        "Taxable income",
        "Tax rate",
        "€0",
        "0%",
        "bottom_right",
        f"""This graph demonstrates the statutory income tax rate with and without
        Solidarity Surcharge. <a href="{params_url}/eink_st.yaml">
        <em>Details and legal references.</em></a>
        """,
    ],
    "deductions": [
        "Income tax deductions",
        "Year",
        "Annual Deductions (in €)",
        "0€",
        "0€",
        "top_left",
        f"""This graph shows the evolution of the main lump-sum tax deductions
        creating a wedge between market and taxable income.
        <a href="{params_url}/eink_st_abzuege.yaml">
        <em>Details and legal references.</em></a>""",
    ],
    "wohngeld": [
        "Monthly housing benefits (in €) per income and rent",
        "Monthly rent in €",
        "Monthly income in €",
        "0€",
        "0€",
        "top_left",
        f"""This Graph depicts the monthly housing benefit, depending on household size
        and year, for a given combination of rent and income. We assume 'Mietstufe' 3,
        which corresponds to a municipality with average rental cost.
        <a href="{params_url}/wohngeld.yaml">
        <em>Details and legal references.</em></a>""",
    ],
    "child_benefits": [
        "Monthly child benefits per child",
        "Year",
        "Child benefits (in €)",
        "0",
        "0€",
        "top_left",
        f"""Monthly child benefit by order of child within the household.
        <a href="{params_url}/kindergeld.yaml">
        <em>Details and legal references.</em></a>""",
    ],
    "social_security": [
        "Social security contribution rates",
        "Year",
        "Social Security contribution rate",
        "0",
        "0%",
        "center_right",
        f"""This graph depicts contribution rates to the four main branches of
        social insurance. With the exception of health insurance from 2006 to
        2018, contributions are shared equally between employer and employee.
        The additional health care contribution rate for employees used to
        vary across health insurance funds; we assume the national average.
        In the period 1993-2007, competition between sickness funds meant
        there was not one contribution rate. GETTSIM provides an average.
        <a href="{params_url}/soz_vers_beitr.yaml">
        <em>Details and legal references.</em></a>""",
    ],
    "social_assistance": [
        "Social Assistance rate",
        "Year",
        "Monthly Social Assistance Rate (€)",
        "0",
        "0€",
        "bottom_right",
        f"""This graph depicts monthly personal social assistance payments
         ('Regelsatz Arbeitslosengeld II') by household member.
        <a href="{params_url}/arbeitsl_geld_2.yaml">
        <em>Details and legal references.</em></a>""",
    ],
}


def create_dashboard():
    # print("{} INFO - Creating a plot dict".format(datetime.now(tz)))

    plot_dict = {
        p: {a: attribute_dict[p][counter] for counter, a in enumerate(plot_attributes)}
        for p in plot_list
    }
    # Makes a difference whether we launch the Dashboard app or start tests.
    all_data = None
    try:
        all_data = pickle.load(open("dashboard/params_dashboard_data.pickle", "rb"))
    except FileNotFoundError:
        try:
            all_data = pickle.load(open("params_dashboard_data.pickle", "rb"))
        except FileNotFoundError:
            warnings.warn(
                "No dashboard data found. Please run 'pre_processing_data.py' first."
            )

    # Start dashboard only if data was found
    if all_data:
        # Call tab functions)
        tab1 = tax_rate(plot_dict["tax_rate"], all_data["tax_rate"])
        tab2 = deductions(plot_dict["deductions"], all_data["deductions"])
        tab3 = wohngeld(plot_dict["wohngeld"], all_data["wohngeld"])
        tab4 = child_benefits(plot_dict["child_benefits"], all_data["child_benefits"])
        tab5 = social_security(
            plot_dict["social_security"], all_data["social_security"]
        )
        tab6 = social_assistance(
            plot_dict["social_assistance"], all_data["social_assistance"]
        )

        tabs = Tabs(tabs=[tab1, tab2, tab3, tab4, tab5, tab6])

        header = Div(
            text="""<h1>GETTSIM parameter visualisations</h1>""", width=900, height=80
        )

        intro = Div(
            text="""<h4>This dashboard visualizes GETTSIM parameters. Further
            information can be found in the
            <a href="https://gettsim.readthedocs.io/en/stable/">documentation</a>.</h4>
            """,
            width=800,
            height=70,
        )

        # Put everything together
        curdoc().add_root(column(header, intro, tabs))
        curdoc().title = "GETTSIM parameter visualizations"


create_dashboard()
