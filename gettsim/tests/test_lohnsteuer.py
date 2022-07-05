import itertools
import urllib.request as mybrowser
import xml.etree.ElementTree as ElementTree

import numpy as np
import pandas as pd
import pytest
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
        the url specified according to BMF API

    Returns
    -------
    xml_ugly: bytes
        the server response

    """
    # say hello
    myheader = {
        "User-Agent": """gettsim development: https://github.com/iza-institute-of-labor-economics/gettsim"""  # noqa: E501
    }
    request = mybrowser.Request(url, headers=myheader)
    response = mybrowser.urlopen(request)
    xml_ugly = response.read()

    return xml_ugly


def get_bmf_url(base, specs):
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


def get_bmf_data(url_base, specs, out_definitions):
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

    url = get_bmf_url(url_base, specs)

    df = pd.DataFrame(columns=["name", "value", "type"])
    # get xml results
    xml_ugly = get_xml(url)
    xml_raw = ElementTree.fromstring(xml_ugly)
    # put information into DataFrame
    for index, child in enumerate(xml_raw.iter("ausgabe")):
        df = df.append(pd.DataFrame(child.attrib, index=[index]))

    return df.set_index("name").join(out_df)


def bmf_collect(inc, outvar, faktorverfahren, faktor, n_kinder, stkl, jahr):
    """
    Creates an URL for the API of the official calculator by the
    German Ministry of Finance (BMF),
    documented at: https://www.bmf-steuerrechner.de/interface/einganginterface.xhtml
    this url is called and the results are returned

    Returns
    -------

    income tax due as pd.Series

    """
    url_base = f"http://www.bmf-steuerrechner.de/interface/{jahr}Version1.xhtml?"
    if jahr <= 2021:
        url_base += "code=eP2021"
    else:
        url_base += "code=2022eP"

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
        "LZZ": 2,  # i.e. income is monthly
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

    bmf_out = get_bmf_data(url_base, specs, out_definitions)

    out = bmf_out["value"].astype(int)

    # Divide by 100 to get Euro
    return out.loc[outvar] / 100


def gen_lohnsteuer_test():
    """Calls the BMF API to generate correct lohnsteuer payments"""

    hh = pd.DataFrame(
        {
            "p_id": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
            "tu_id": [1, 2, 2, 3, 3, 4, 4, 4, 5, 5, 6],
            "bruttolohn_m": [2000, 3000, 4000, 5000, 0, 2000, 0, 0, 3000, 0, 7500],
            "alter": [30, 30, 40, 40, 50, 30, 5, 2, 40, 12, 50],
            "kind": [
                False,
                False,
                False,
                False,
                False,
                False,
                True,
                True,
                False,
                True,
                False,
            ],
            "steuerklasse": [1, 4, 4, 3, 5, 2, 1, 1, 2, 2, 1],
            "year": [2020, 2021, 2021, 2021, 2021, 2022, 2022, 2022, 2022, 2022, 2020],
        }
    )
    hh["child_num_kg"] = hh.groupby("tu_id")["kind"].transform("sum")
    # Get correct lohnsteuer from German Ministry of Finance
    hh["lohn_st"] = np.vectorize(bmf_collect)(
        hh["bruttolohn_m"],
        outvar="LSTLZZ",
        faktorverfahren=0,
        faktor="1,0000",
        n_kinder=hh["child_num_kg"],
        stkl=hh["steuerklasse"],
        jahr=hh["year"],
    )
    hh["lohn_st_soli"] = np.vectorize(bmf_collect)(
        hh["bruttolohn_m"],
        outvar="SOLZLZZ",
        faktorverfahren=0,
        faktor="1,0000",
        n_kinder=hh["child_num_kg"],
        stkl=hh["steuerklasse"],
        jahr=hh["year"],
    )
    # Export
    lohnsteuer_test_out = f"{ROOT_DIR}/tests/test_data/test_dfs_lohn_st.csv"
    hh.to_csv(lohnsteuer_test_out, index=False)


# HERE THE ACTUAL TEST STARTS

INPUT_COLS = ["p_id", "tu_id", "bruttolohn_m", "alter", "kind", "steuerklasse", "year"]

YEARS = [2020, 2021, 2022]
TEST_COLUMNS = ["lohn_st", "lohn_st_soli"]


@pytest.fixture(scope="module")
def input_data():
    file_name = "test_dfs_lohn_st.csv"
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
            "alleinerz": [False, False, False, False, False, True, True],
            "bruttolohn_m": [2000, 2000, 2000, 2000, 0, 2000, 0],
            "steuerklasse": [1, 4, 4, 3, 5, 2, 2],
        }
    )
    result = compute_taxes_and_transfers(
        data=df.drop(columns=["steuerklasse"]),
        params=policy_params,
        functions=policy_functions,
        targets=["steuerklasse_tu"],
    )

    assert_series_equal(df["steuerklasse"], result["steuerklasse"])


@pytest.mark.parametrize("year, column", itertools.product(YEARS, TEST_COLUMNS))
def test_lohnsteuer(input_data, year, column, reload_test_data=False):
    if reload_test_data:
        gen_lohnsteuer_test()

    year_data = input_data[input_data["year"] == year].reset_index(drop=True)
    df = year_data[INPUT_COLS].copy()
    df["alleinerz"] = df["steuerklasse"] == 2
    df["wohnort_ost"] = False
    df["jahr_renteneintr"] = 2060
    df["hat_kinder"] = df.groupby("tu_id")["kind"].transform("sum") > 0
    df["in_ausbildung"] = ~df["kind"]
    df["arbeitsstunden_w"] = 40 * ~df["kind"]
    policy_params, policy_functions = set_up_policy_environment(date=year)

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=[column],
    )

    assert_series_equal(
        result[column] / 12, year_data[column], check_exact=False, atol=2
    )
