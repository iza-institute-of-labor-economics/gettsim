import glob

import pandas as pd
import yaml
from bokeh.io import save
from bokeh.layouts import gridplot
from bokeh.models.tools import HoverTool
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
    par = ColumnDataSource(par)
    return name, descr, par


def make_param_graphs(lang="de"):

    # get list of params
    param_files = glob.glob("*.yaml")

    for yaml_file in param_files:
        output_file(f"graphs/{yaml_file[:-5]}.html")

        # Read YAML
        with open(f"{yaml_file}") as f:
            params = yaml.safe_load(f)

        # Internal name of parameter
        all_keys = params.keys()
        plotlist = []
        for key in all_keys:
            # The DataFrame 'par' contains the data we want to plot
            name, descr, par = parse_yaml(params, key, lang)
            hover = HoverTool(
                tooltips=[
                    ("Date", "@date{%F}"),
                    ("Value", "$y{0.}"),
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
                tools=[hover],
                plot_height=400,
                plot_width=400,
            )

            # hover_tool.formatters = {"date": "datetime"}
            p.step("date", "value", color="navy", mode="after", source=par)
            p.circle("date", "value", color="navy", size=3, source=par)
            p = plotstyle(p)
            plotlist.append(p)
        grid = gridplot(plotlist, ncols=3)
        save(grid)


make_param_graphs()
