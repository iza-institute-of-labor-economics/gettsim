""" Tool to check outcomes against BMF Steuerrechner
    This is for Lohnsteuer only!!
"""
import urllib.request as mybrowser
import xml.etree.ElementTree as ElementTree

import numpy as np
import pandas as pd

from gettsim.config import ROOT_DIR


def get_xml(url):
    """
    Send URL to BMF and obtain xml

    Parameters
    ----------
    url : str
        the ursl to

    Returns
    -------
    xml_ugly: bytes
        the result

    """
    # say hello
    myheader = {
        "User-Agent": """gettsim development:
                    https://github.com/iza-institute-of-labor-economics/gettsim"""
    }
    request = mybrowser.Request(url, headers=myheader)
    response = mybrowser.urlopen(request)
    xml_ugly = response.read()

    return xml_ugly


def get_url(base, specs):
    """
    Formatting of URL

    Parameters
    ----------
    base : str
        the base URL from BMF for the given year
    specs : dict
        Dictionary of arguments for the URL call

    Returns
    -------
    url: str
        the URL we want to send
    """
    url = base
    for spec in specs:
        url = url + f"&{spec}={specs[spec]}"
    return url


def format_url_content(url_base, specs, out_definitions):
    """
    Format URL, send it to BMF and format output

    Parameters
    ----------
    url_base : str
        base URL
    specs : dict
    out_definitions : dict

    Returns
    -------
    df: pandas.DataFrame

    url: str
    """

    out_df = pd.DataFrame(out_definitions, index=["definition"]).T

    url = get_url(url_base, specs)

    df = pd.DataFrame(columns=["name", "value", "type"])
    # get xml results
    xml_ugly = get_xml(url)
    xml_raw = ElementTree.fromstring(xml_ugly)
    # put information into DataFrame
    for index, child in enumerate(xml_raw.iter("ausgabe")):
        df = df.append(pd.DataFrame(child.attrib, index=[index]))

    return (df.set_index("name").join(out_df), url)


def bmf_collect(inc, faktorverfahren=0, faktor="1,000", n_kinder=0, stkl=1, jahr=2021):
    """
    Creates an URL for the API of the official calculator by the German Ministry of Finance,
    document at: https://www.bmf-steuerrechner.de/interface/einganginterface.xhtml

    Returns
    -------

    income tax tue as pd.Series

    """
    url_base = (
        f"http://www.bmf-steuerrechner.de/interface/{jahr}Version1.xhtml?code=eP2021"
    )

    # Possible inputs:
    # https://www.bundesfinanzministerium.de/Content/DE/Downloads/Steuern/Steuerarten/Lohnsteuer/Programmablaufplan/2020-11-09-PAP-2021-anlage-1.pdf?__blob=publicationFile&v=https://www.bundesfinanzministerium.de/Content/DE/Downloads/Steuern/Steuerarten/Lohnsteuer/Programmablaufplan/2020-11-09-PAP-2021-anlage-1.pdf?__blob=publicationFile&v=2
    # AF: Faktorverfahren (0/1)
    # Faktor: eingetragener Faktor
    # LZZ = 1: yearly income, 2: monthly
    # PVZ (1/0): PV-Zusatzbeitrag für Kinderlose
    # RE4: Steuerpflichtiger Arbeitslohn (in Cent!!!)
    # STKL (1-6): Steuerklasse
    # ZKF: Kinderfreibeträge
    # KVZ: GKV Zusatzbeitrag in %
    #
    # Speficy the call. everything that is not specified is treated as a zero value.

    if stkl == 4:
        kinderfb = n_kinder / 2
    else:
        kinderfb = n_kinder

    kinderlos = int(n_kinder == 0)

    specs = {
        "RE4": inc * 100,
        "AF": faktorverfahren,
        "F": faktor,
        "LZZ": 2,
        "STKL": stkl,
        "ZKF": kinderfb,
        "KVZ": "1,00",
        "PVZ": kinderlos,
    }

    tax_df, url = format_url_content(url_base, specs, out_definitions)
    out = tax_df["value"].astype(int)

    # We are only interested in Lohnsteuer and Soli
    out = out.loc[["LSTLZZ", "SOLZLZZ"]]
    # Return in Euros
    return out.loc["LSTLZZ"] / 100


out_definitions = {
    "BK": "Bemessungsgrundlage für die Kirchenlohnsteuer in Cent",
    "BKS": """Bemessungsgrundlage der sonstigen Bezüge
              (ohne Vergütung für mehrjährige Tätigkeit) für die Kirchenlohnsteuer in Cent""",
    "BKV": """Bemessungsgrundlage der Vergütung für mehrjährige Tätigkeit
              für die Kirchenlohnsteuer in Cent""",
    "LSTLZZ": "Für den Lohnzahlungszeitraum einzubehaltende Lohnsteuer in Cent",
    "SOLZLZZ": "Für den Lohnzahlungszeitraum einzubehaltender Solidaritätszuschlag in Cent",
    "SOLZS": """Solidaritätszuschlag für sonstige Bezüge
                (ohne Vergütung für mehrjährige Tätigkeit) in Cent""",
    "SOLZV": "Solidaritätszuschlag für die Vergütung für mehrjährige Tätigkeit in Cent",
    "STS": "Lohnsteuer für sonstige Bezüge (ohne Vergütung für mehrjährige Tätigkeit) in Cent",
    "STV": "Lohnsteuer für die Vergütung für mehrjährige Tätigkeit in Cent",
    "VKVLZZ": """Für den Lohnzahlungszeitraum berücksichtigte Beiträge des Arbeitnehmers
                  zur privaten Basis Krankenversicherung und privaten Pflege Pflichtversicherung
                  (ggf. auch die Mindestvorsorgepauschale) in Cent beim laufenden Arbeitslohn.
                  Für Zwecke der Lohnsteuerbescheinigung sind die einzelnen Ausgabewerte
                  außerhalb des eigentlichen Lohnsteuerberechnungsprogramms zu addieren;
                  hinzuzurechnen sind auch die Ausgabewerte VKVSONST.""",
    "VKVSONST": """Für den Lohnzahlungszeitraum berücksichtigte Beiträge des Arbeitnehmers
                  zur privaten Basis Krankenversicherung und privaten Pflege Pflichtversicherung
                  (ggf. auch die Mindestvorsorgepauschale) in Cent bei sonstigen Bezügen.
                  Der Ausgabewert kann auch negativ sein. Für tarifermäßigt zu besteuernde
                  Vergütungen für mehrjährige Tätigkeiten enthält der PAP keinen entsprechenden
                  Ausgabewert.""",
    "VFRB": "Verbrauchter Freibetrag bei Berechnung des laufenden Arbeitslohns, in Cent",
    "VFRBS1": """Verbrauchter Freibetrag bei Berechnung des voraussichtlichen
                 Jahresarbeitslohns, in Cent""",
    "VFRBS2": "Verbrauchter Freibetrag bei Berechnung der sonstigen Bezüge, in Cent",
    "WVFRB": """Für die weitergehende Berücksichtigung des Steuerfreibetrags nach dem DBA Türkei
                verfügbares ZVE über dem Grundfreibetrag bei der Berechnung deslaufenden
                Arbeitslohns, in Cent""",
    "WVFRBM": """Für die weitergehende Berücksichtigung des Steuerfreibetrags nach dem DBA Türkei
                 verfügbares ZVE über dem Grundfreibetrag bei der Berechnung der sonstigen Bezüge,
                 in Cent""",
    "WVFRBO": """Für die weitergehende Berücksichtigung des Steuerfreibetrags nach dem DBA Türkei
                 verfügbares ZVE über dem Grundfreibetrag bei der Berechnung des voraussichtlichen
                 Jahresarbeitslohns, in Cent""",
}

hh = pd.DataFrame(
    {
        "tu_id": [1, 2, 2, 3, 3, 4],
        "pid": [1, 2, 3, 4, 5, 6],
        "bruttolohn_m": [2000, 3000, 4000, 5000, 0, 2000],
        "child_num_kg": [0, 0, 0, 0, 0, 2],
        "steuerklasse": [1, 4, 4, 3, 5, 2],
        "year": [2020, 2021, 2021, 2021, 2021, 2020],
    }
)

hh["lohn_steuer"] = np.vectorize(bmf_collect)(
    hh["bruttolohn_m"],
    faktorverfahren=0,
    faktor="1,0000",
    n_kinder=hh["child_num_kg"],
    stkl=hh["steuerklasse"],
    jahr=hh["year"],
)
# Export
lohnsteuer_test_out = f"{ROOT_DIR}/tests/test_data/test_dfs_lohn_steuer.csv"
hh.to_csv(lohnsteuer_test_out, index=False)
