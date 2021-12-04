import urllib.request as mybrowser
import xml.etree.ElementTree as ElementTree

import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from pandas.testing import assert_series_equal

from gettsim.config import ROOT_DIR
from gettsim.interface import compute_taxes_and_transfers
from gettsim.policy_environment import set_up_policy_environment


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
        "User-Agent": """gettsim development: https://github.com/iza-institute-of-labor-economics/gettsim"""  # noqa: E501
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
    out_definitions = {
        "BK": "Bemessungsgrundlage für die Kirchenlohnsteuer in Cent",
        "BKS": """Bemessungsgrundlage der sonstigen Bezüge
                (ohne Vergütung für mehrjährige Tätigkeit) für die Kirchenlohnsteuer
                in Cent""",
        "BKV": """Bemessungsgrundlage der Vergütung für mehrjährige Tätigkeit
                  für die Kirchenlohnsteuer in Cent""",
        "LSTLZZ": "Für den Lohnzahlungszeitraum einzubehaltende Lohnsteuer in Cent",
        "SOLZLZZ": """Für den Lohnzahlungszeitraum einzubehaltender
        Solidaritätszuschlag in Cent""",
        "VKVLZZ": """Für den Lohnzahlungszeitraum berücksichtigte Beiträge des
        Arbeitnehmers zur privaten Basis Krankenversicherung und privaten Pflege
        Pflichtversicherung (ggf. auch die Mindestvorsorgepauschale) in Cent beim
        laufenden Arbeitslohn. Für Zwecke der Lohnsteuerbescheinigung sind die
        einzelnen Ausgabewerte außerhalb des eigentlichen
        Lohnsteuerberechnungsprogramms zu addieren;
         hinzuzurechnen sind auch die Ausgabewerte VKVSONST.""",
        "VFRB": """Verbrauchter Freibetrag bei Berechnung des 
        laufenden Arbeitslohns, in Cent""",
    }

    tax_df, url = format_url_content(url_base, specs, out_definitions)
    out = tax_df["value"].astype(int)

    # We are only interested in Lohnsteuer and Soli
    out = out.loc[["LSTLZZ", "SOLZLZZ"]]
    # Return in Euros
    return out.loc["LSTLZZ"] / 100


def gen_lohnsteuer_test():
    """ Calls the BMF API to generate correct lohnsteuer payments"""

    hh = pd.DataFrame(
        {
            "p_id": [1, 2, 3, 4, 5, 6, 7, 8],
            "tu_id": [1, 2, 2, 3, 3, 4, 4, 4],
            "bruttolohn_m": [2000, 3000, 4000, 5000, 0, 2000, 0, 0],
            "alter": [30, 30, 40, 40, 50, 30, 5, 2],
            "kind": [False, False, False, False, False, False, True, True],
            "steuerklasse": [1, 4, 4, 3, 5, 2, 1, 1],
            "year": [2020, 2021, 2021, 2021, 2021, 2020, 2020, 2020],
        }
    )
    hh["child_num_kg"] = hh.groupby("tu_id")["kind"].transform("sum")
    # Get correct lohnsteuer from German Ministry of Finance
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


# HERE THE ACTUAL TEST STARTS

INPUT_COLS = ["p_id", "tu_id", "bruttolohn_m", "alter", "kind", "steuerklasse", "year"]

YEARS = [2021]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_lohn_steuer.csv"
    out = pd.read_csv(ROOT_DIR / "tests" / "test_data" / file_name)
    return out


def test_steuerklassen():
    policy_params, policy_functions = set_up_policy_environment("2021")

    # Tests whether steuerklassen are correctly assigned based on our assumptions
    df = pd.DataFrame(
        {
            "p_id": [1, 2, 3, 4, 5, 6, 7],
            "tu_id": [1, 2, 2, 3, 3, 4, 4],
            "hh_id": [1, 2, 2, 3, 3, 4, 4],
            "alter": [30, 30, 30, 30, 50, 50, 8],
            "kind": [False, False, False, False, False, False, True],
            "bruttolohn_m": [2000, 2000, 2000, 2000, 0, 2000, 0],
            "gemeinsam_veranlagt": [False, True, True, True, True, False, False],
            "steuerklasse": [1, 4, 4, 3, 5, 2, 2],
            "alleinerziehend": [False, False, False, False, False, True, True],
        }
    )
    result = compute_taxes_and_transfers(
        data=df.drop(columns=["steuerklasse"]),
        params=policy_params,
        functions=policy_functions,
        targets=["steuerklasse"],
        columns_overriding_functions=["gemeinsam_veranlagt"],
    )

    assert_series_equal(df["steuerklasse"], result["steuerklasse"])


@pytest.mark.parametrize("year", YEARS)
def test_lohnsteuer(input_data, year, reload_test_data=False):

    if reload_test_data:
        gen_lohnsteuer_test()

    year_data = input_data[input_data["year"] == year]
    df = year_data[INPUT_COLS].copy()
    df["alleinerziehend"] = df["steuerklasse"] == 2

    df["jahr_renteneintr"] = 2060
    df["hat_kinder"] = df.groupby("tu_id")["kind"].transform("sum") > 0

    policy_params, policy_functions = set_up_policy_environment(date=year)

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=["lohn_steuer"],
        columns_overriding_functions="steuerklasse",
    )

    assert_frame_equal(df["lohn_steuer"], year_data["lohn_steuer"], check_dtype=False)
