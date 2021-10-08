from bokeh.models import NumeralTickFormatter


# Define central functions used by all plots
def plotstyle(p, plot_dict):
    p.title.text = plot_dict["title"]
    p.xaxis.axis_label = plot_dict["x_axis_label"]
    p.yaxis.axis_label = plot_dict["y_axis_label"]
    p.xaxis[0].formatter = NumeralTickFormatter(format=plot_dict["x_axis_format"])
    p.yaxis[0].formatter = NumeralTickFormatter(format=plot_dict["y_axis_format"])
    p.background_fill_color = "white"

    if p.legend != []:
        p.legend.location = plot_dict["legend_location"]
        p.legend.click_policy = "mute"
        p.legend.background_fill_alpha = 0.5

    return p
