# -*- coding: utf-8 -*-
"""
IZAMOD SETTINGS

get_settings: Global simulation settings
ubi_settings: set alternative tax benefit parameters for UBI
hypo_graph_settings: settings for hypothetical graphs
"""
import os
import socket


def get_settings():
    """ Initialize Global Settings
    """
    # Base year
    taxyear = 2019

    # The baseline scenario is always called RS`taxyear' (RS = Rechtsstand)
    reforms = ["RS" + str(taxyear), "UBI"]

    # DATA CREATION
    # load raw SOEP data and merge them into one data set
    load_data = 0
    # Minimum year to collect data from.
    minyear = 2005
    # prepare tax-ben input
    prepare_data = 0

    # prepare descriptive statistics
    show_descr = 0

    # TAX TRANSFER CALCULATION
    taxtrans = 1
    # Produce Output
    output = 1

    # Run Hypo file for debugging
    run_hypo = 0

    # PATH SETTINGS
    MAIN_PATH = os.getcwd() + "/"
    # SOEP_PATH: Where is the SOEP data stored?
    # Find out whether we are on the GPU.
    if socket.gethostname() == "gpu1":
        SOEP_PATH = "/data/shares/dynamod/data/raw/soep/"
    else:
        SOEP_PATH = "V:/soep/datasets/2016/v33.1/long/"
    # The Path for self produced data
    DATA_PATH = MAIN_PATH + "data/"
    GRAPH_PATH = MAIN_PATH + "graphs/"

    return {
        "Reforms": reforms,
        "load_data": load_data,
        "minyear": minyear,
        "prepare_data": prepare_data,
        "show_descr": show_descr,
        "taxtrans": taxtrans,
        "taxyear": taxyear,
        "output": output,
        "run_hypo": run_hypo,
        "MAIN_PATH": MAIN_PATH,
        "SOEP_PATH": SOEP_PATH,
        "DATA_PATH": DATA_PATH,
        "GRAPH_PATH": GRAPH_PATH,
    }


def ubi_settings(tb):
    """ Set alternative tax benefit parameters for UBI
    """

    tb_ubi = tb.copy()
    # UBI amount for adults
    tb_ubi["ubi_adult"] = 800
    tb_ubi["ubi_child"] = 0.5 * tb_ubi["ubi_adult"]

    # Minijobgrenze
    tb_ubi["mini_grenzew"] = 0
    tb_ubi["mini_grenzeo"] = tb_ubi["mini_grenzew"]

    # Midijobgrenze
    tb_ubi["midi_grenze"] = 0

    # UBI Flat Rate
    tb_ubi["flatrate"] = 0.4

    # Kindergeld
    for i in range(1, 5):
        tb_ubi["kgeld" + str(i)] = 0

    # Tax Tariff

    return tb_ubi

def get_ref_text(refname):
    """ defines a bit of tex code which briefly sums up what each reform is doing.
    """

    if refname == "UBI":
        tb = ubi_settings({})

        ref_text = """Adult rate: \EUR{{{}}}, Kid rate: \EUR{{{}}},
                Abolition of Marginal Jobs, Abolition of 'Gleitzone'.
                Abolition of Unemployment Benefit, Housing Benefit, Additional Child Benefit,
                Child Allowance. UBI is fully subject to income taxation. Income Tax:
                Flat Rate of {}%.
                """.format(int(tb["ubi_adult"]), int(tb["ubi_child"]), tb['flatrate']*100)
    else:
        ref_text = ""

    return ref_text


def hypo_graph_settings(lang, t):
    """ Set various settings for Hypo Graphs
        args:
            lang: ["en", "de"]
            t: hypo household type
    """
    # Create labels for each graph type
    if lang == "en":
        if t <= 33:
            xlabels = {
                "lego": "Gross monthly household income (€)",
                "emtr": "Gross monthly household income (€)",
                "bruttonetto": "Gross monthly household income (€)",
            }
        else:
            xlabels = {
                "lego": "Gross monthly income of secondary earner (€)",
                "emtr": "Gross monthly income of secondary earner (€)",
                "bruttonetto": "Gross monthly income of secondary earner (€)",
                    }

        ylabels = {
            "lego": "Disp. monthly household income (€)",
            "emtr": "Effective Marginal Tax Rate",
            "bruttonetto": "Disp. monthly household income (€)",
        }
    if lang == "de":
        if t <= 33:
            xlabels = {
                "lego": "Brutto-Haushaltseinkommen (€ / Monat)",
                "emtr": "Brutto-Haushaltseinkommen (€ / Monat)",
                "bruttonetto": "Brutto-Haushaltseinkommen (€ / Monat)",
            }
        else:
            xlabels = {
                "lego": "Bruttoeinkommen des Zweitverdienenden (€ / Monat)",
                "emtr": "Bruttoeinkommen des Zweitverdienenden (€ / Monat)",
                "bruttonetto": "Bruttoeinkommen des Zweitverdienenden (€ / Monat)",
            }
        ylabels = {
            "lego": "Verf. Einkommen (€ / Monat)",
            "emtr": "Effektive Grenzbelastung",
            "bruttonetto": "Verf. Einkommen (€ / Monat)",
        }
    # depending on the plottype, which reform-specific variables to plot?
    yvars = {"emtr": "emtr", "bruttonetto": "dpi"}

    # max yearly income to plot. can also vary by t
    maxinc = 80000

    return xlabels, ylabels, yvars, maxinc

def get_reform_names(lang):
    """ returns a language-specific proper name for every reform
    """
    refnames = {"de": {
            "RS2017": "Rechtsstand 2017",
            "RS2018": "Rechtsstand 2018",
            "RS2019": "Rechtsstand 2019",
            "UBI": "Bedingungsloses Grundeinkommen"
            },
            "en": {
            "RS2017": "Germany, 2017",
            "RS2018": "Germany, 2018",
            "RS2019": "Germany, 2019",
            "UBI": "Unconditional Basic Income"
            }
        }

    return refnames[lang]

def get_hh_text(lang, t, miete, heizkost):
    """ returns language-specific descriptions of hypothetical household types
    """
    if lang == "en":
        first = "\\small{Own calculations with IZADYNMOD. "
        mietstring = "Assumed monthly rent: \EUR{{{}}}. Assumed monthly heating cost: \EUR{{{}}}.".format(miete, heizkost)
        if t in [33, 34]:
            hh = """The x-axis shows income of the secondary earner. The first earner is
                    assumed to earn an annual income of \EUR{{{}}}. This corresponds to the
                    average annual earnings of a full-time employed male employee in 2018.""".format(51286)
        else:
            hh = ""

    if lang == "de":
        first = "\\small{Eigene Berechnungen mit IZADYNMOD. "
        mietstring = "Unterstellte Kaltmiete: \EUR{{{}}}.  Unterstellte Heizkosten: \EUR{{{}}}".format(miete, heizkost)
        if t in [33, 34]:
            hh = """Die horizontale Achse bezeichnet das Einkommen des Zweitverdienenden.
            Für den Erstverdienenden wird ein jährliches Bruttoeinkommen von \EUR{{{}}}
            unterstellt. Dies entspricht dem Durchschnittsverdienst eines
            vollzeitbeschäftigten männlichen abhängig Beschäftigten.""".format(52186)
        else:
            hh = ""

    end = "} \n"

    fullstring = first + hh + mietstring + end

    return fullstring

def tarif_ubi(x, tb):
    """ UBI Tax schedule
        the function is defined here, as defining it in tax_transfer_ubi.py would lead to
        circular dependencies
    """
    t = 0.0
    if x > tb['G']:
        t = tb['flatrate'] * (x - tb['G'])

    return t






