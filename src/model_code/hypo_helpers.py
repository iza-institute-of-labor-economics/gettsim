# -*- coding: utf-8 -*-
from src.analysis.tax_transfer_ubi import ubi_settings


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