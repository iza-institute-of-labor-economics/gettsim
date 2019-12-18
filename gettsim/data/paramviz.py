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


def parse_yaml(params, key, lang):
    # Legal name of parameter
    name = params[key]["name"][lang]
    descr = params[key]["description"][lang]

    par = pd.DataFrame(columns=["date", "value", "note"])
    for d in params[key]["values"].keys():
        date = d
        value = params[key]["values"][d]["value"]
        note = params[key]["values"][d]["note"]
        row = {"date": date, "value": value, "note": note}
        par = par.append(row, ignore_index=True)
    # Some cleaning
    par["date"] = pd.to_datetime(par["date"], format="%Y-%m-%d")
    par["value"] = par["value"].astype(float)
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
        file_name = yaml_file[:-5]
        output_file(f"graphs/{file_name}.html", title=file_name.title())

        # Read YAML
        with open(f"{yaml_file}") as f:
            params = yaml.safe_load(f)

        # Internal name of parameter
        all_keys = params.keys()
        plotlist = []
        for key in all_keys:
            # The DataFrame 'par' contains the data we want to plot
            name, descr, par, unit = parse_yaml(params, key, lang)
            # How to format the values on mouse-over
            if unit == "amount":
                format_str = "$y{0.}"
            if unit == "share":
                format_str = "$y{0.3f}"

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
            p.circle("date", "value", color="navy", size=3, source=par)
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
        grid = gridplot(plotlist, ncols=3)
        save(grid)
        print(f"File {file_name}.html created.")


make_param_graphs()
