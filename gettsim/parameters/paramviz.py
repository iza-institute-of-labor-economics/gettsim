import datetime
import glob

import pandas as pd
import yaml
from bokeh.io import save
from bokeh.layouts import column
from bokeh.layouts import gridplot
from bokeh.models.tools import HoverTool
from bokeh.models.tools import ResetTool
from bokeh.models.widgets import DataTable
from bokeh.models.widgets import DateFormatter
from bokeh.models.widgets import TableColumn
from bokeh.plotting import ColumnDataSource
from bokeh.plotting import figure
from bokeh.plotting import output_file


def plotstyle(p):
    p.title.text_font_size = "10pt"
    p.xaxis.axis_label = "Year"
    p.toolbar.logo = None

    return p


def reshape_grouped_param():
    """ Reshape grouped dataframe by unpacking the value column"""

    #    for r in range(len(s)):
    pass


def parse_yaml(params, key, lang, grouped=False):
    # Legal name of parameter
    name = params[key]["name"][lang]
    descr = params[key]["description"][lang]
    par = pd.DataFrame(columns=["date", "value", "note"])
    if not grouped:
        # Ungrouped parameters
        for d in params[key]["values"].keys():
            row = {
                "date": d,
                "value": params[key]["values"][d]["value"],
                "note": params[key]["values"][d]["note"],
            }
            par = par.append(row, ignore_index=True)
    else:
        # Grouped Parameters
        all_dates = [key for key in params[key].keys() if type(key) == datetime.date]
        for d in all_dates:
            # is it a value or something more complicated?
            if "scalar" in params[key][d].keys():
                row = {
                    "date": d,
                    "value": params[key][d]["scalar"],
                    "note": params[key][d]["reference"],
                }
            else:
                row = {"date": d}
                if "reference" in params[key].keys():
                    row["note"] = params[key][d]["reference"]
                else:
                    row["note"] = None
                # value as dictionary. use the bit from policy_for_date.py

            par = par.append(row, ignore_index=True)

    # Some cleaning
    par["date"] = pd.to_datetime(par["date"], format="%Y-%m-%d")
    par.to_csv("~/test/par.csv", index=False)
    try:
        par["value"] = par["value"].astype(float)
    except TypeError:
        par["value"] = reshape_grouped_param(par["value"])

    par["note"] = par["note"].fillna("")
    if par["value"].max() < 1:
        unit = "share"
    else:
        unit = "amount"

    par = ColumnDataSource(par)
    return name, descr, par, unit


def make_param_graphs(lang="de"):

    # get list of params
    param_files = glob.glob("*.yaml")

    for yaml_file in param_files:
        # print(f"reading {yaml_file}...")
        file_name = yaml_file[:-5]
        output_file(f"graphs/{file_name}.html", title=file_name.title())
        grouped_params = ["wohngeld", "kinderzuschlag"]

        # Read YAML
        with open(f"{yaml_file}") as f:
            params = yaml.safe_load(f)
        # Internal name of parameter
        all_keys = params.keys()
        plotlist = []
        for key in all_keys:
            if yaml_file[:-5] in grouped_params:
                name, descr, par, unit = parse_yaml(params, key, lang, True)
            else:
                # The DataFrame 'par' contains the data we want to plot
                name, descr, par, unit = parse_yaml(params, key, lang)

            # How to format the values on mouse-over
            if unit == "share":
                format_str = "$y{0.3f}"
            else:
                format_str = "$y{0.}"

            hover = HoverTool(
                tooltips=[
                    ("Date", "@date{%F}"),
                    ("Value", format_str),
                    (
                        "Note",
                        """
                                  <div style="width:200px;">
                                  @note
                                  </div>
                                 """,
                    ),
                ],
                formatters={"date": "datetime"},
            )
            p = figure(
                title=f"{key}: {name}",
                x_axis_type="datetime",
                tools=[hover, ResetTool()],
                plot_height=400,
                plot_width=400,
            )

            # hover_tool.formatters = {"date": "datetime"}
            p.step("date", "value", color="navy", mode="after", source=par)
            p.circle("date", "value", color="navy", size=4, source=par)
            p = plotstyle(p)
            # add Data Table
            t = DataTable(
                source=par,
                width=400,
                columns=[
                    TableColumn(
                        field="date",
                        title="Datum",
                        formatter=DateFormatter(),
                        width=100,
                    ),
                    TableColumn(field="value", title="Wert", width=50),
                    TableColumn(field="note", title="Anmerkung", width=250),
                ],
            )
            plot_tab = column(p, t)
            plotlist.append(plot_tab)
        # Return grid in 3 columns
        grid = gridplot(plotlist, ncols=3)

        save(grid)
        # print(f"Parameter Visualization: File {file_name}.html created.")


make_param_graphs()
