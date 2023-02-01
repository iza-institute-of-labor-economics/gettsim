import itertools
import urllib.request as mybrowser
import xml.etree.ElementTree as ElementTree

import numpy as np
import pandas as pd
import pytest
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import set_up_policy_environment
from _gettsim_tests import TEST_DATA_DIR
from pandas.testing import assert_series_equal


INPUT_COLS = [
    "hh_id",
    "tu_id",
    "p_id",
    "wohnort_ost",
    "steuerklasse",
    "bruttolohn_m",
    "alter",
    "hat_kinder",
    "arbeitsstunden_w",
    "in_ausbildung",
    "ges_krankenv_zusatzbeitrag",
    "ges_pflegev_zusatz_kinderlos",
]

OUT_COLS = [
    "lohnst_m",
    # "lohnst_soli_m"
]


YEARS = [2022]


@pytest.fixture(scope="module")
def input_data():
    # Loading BMF test data
    lst_data = pd.read_excel(
        TEST_DATA_DIR / "original_testfaelle" / "lohnsteuer_bmf_2022.xlsx",
        header=9,
    )

    # Drop test cases not covered by GETTSIM

    lst_data.columns = lst_data.columns.str.lower()

    lst_data = lst_data[
        (lst_data["af"] == 0)
        & (lst_data["ajahr"] == 0)
        & (lst_data["alter1"] != 1)
        & (lst_data["entsch"] == 0)
        & (lst_data["jfreib"] == 0)
        & (lst_data["jhinzu"] == 0)
        & (lst_data["jre4"] == 0)
        & (lst_data["jre4ent"] == 0)
        & (lst_data["jvbez"] == 0)
        & (lst_data["lzzfreib"] == 0)
        & (lst_data["lzzhinzu"] == 0)
        & (lst_data["krv"] != 2)
        & (lst_data["pkpv"] == 0)
        & (lst_data["pkv"] == 0)
        & (lst_data["pvs"] == 0)
        & (lst_data["sonstb"] == 0)
        & (lst_data["sonstent"] == 0)
        & (lst_data["sterbe"] == 0)
        & (lst_data["vbez"] == 0)
        & (lst_data["vbezm"] == 0)
        & (lst_data["vbezs"] == 0)
        & (lst_data["vbs"] == 0)
        & (lst_data["vkapa"] == 0)
        & (lst_data["vmt"] == 0)
        & (lst_data["zmvb"] == 0)
    ].copy()

    lst_data.head()

    # Only keep relevant variables and rename then to GETTSIM convention
    # lst_data.columns
    var_names = {
        "lfd. nr.": "p_id",
        "stkl": "steuerklasse",
        "zkf": "anz_kinder_mit_kindergeld_tu",
        "krv": "wohnort_ost",
        "re4": "lst_wage",  # in cents
        "lzz": "period_of_obtained_wage",
        "lstlzz": "lohnst",
        "solzlzz": "lohnst_soli",
        "kvz": "ges_krankenv_zusatzbeitrag",
        "pvz": "ges_pflegev_zusatz_kinderlos",
    }
    test_data = lst_data[[*var_names]].rename(columns=var_names).copy()

    # Create IDs
    test_data["tu_id"] = test_data["p_id"]
    test_data["hh_id"] = test_data["p_id"]

    # Create variables needed for GETTSIM (not sure why GETTSIM requires them)
    test_data["alter"] = 25
    test_data.loc[test_data["wohnort_ost"] == 0, "wohnort_ost"] = False
    test_data.loc[test_data["wohnort_ost"] == 1, "wohnort_ost"] = True
    test_data["wohnort_ost"] = test_data["wohnort_ost"].astype(bool)
    test_data.loc[test_data["anz_kinder_mit_kindergeld_tu"] == 0, "hat_kinder"] = False
    test_data.loc[test_data["anz_kinder_mit_kindergeld_tu"] > 0, "hat_kinder"] = True
    test_data["hat_kinder"] = test_data["hat_kinder"].astype(bool)
    test_data["arbeitsstunden_w"] = 40
    test_data["arbeitsstunden_w"] = test_data["arbeitsstunden_w"].astype(float)
    test_data["ges_pflegev_zusatz_kinderlos"] = test_data[
        "ges_pflegev_zusatz_kinderlos"
    ].astype(bool)
    test_data["in_ausbildung"] = False

    # Transform cent values to full Euros
    test_data["lst_wage"] = test_data["lst_wage"] / 100
    test_data["lohnst"] = test_data["lohnst"] / 100
    test_data["lohnst_soli"] = test_data["lohnst_soli"] / 100

    # Take into account period of obtained wage (Lohnzahlungszeitraum, LZZ)
    test_data.loc[test_data["period_of_obtained_wage"] == 4, "bruttolohn_m"] = (
        test_data["lst_wage"] * 360 / 12
    )
    test_data.loc[test_data["period_of_obtained_wage"] == 3, "bruttolohn_m"] = (
        test_data["lst_wage"] / 7 * 360 / 12
    )
    test_data.loc[
        test_data["period_of_obtained_wage"] == 2, "bruttolohn_m"
    ] = test_data["lst_wage"]
    test_data.loc[test_data["period_of_obtained_wage"] == 1, "bruttolohn_m"] = (
        test_data["lst_wage"] / 12
    )

    test_data["lohnst_m"] = test_data["lohnst"]
    test_data["lohnst_soli_m"] = test_data["lohnst_soli"]

    for outvar in ["lohnst_m", "lohnst_soli_m"]:

        test_data.loc[test_data["period_of_obtained_wage"] == 4, outvar] = (
            test_data[outvar] * 360 / 12
        )
        test_data.loc[test_data["period_of_obtained_wage"] == 3, outvar] = (
            test_data[outvar] / 7 * 360 / 12
        )
        test_data.loc[test_data["period_of_obtained_wage"] == 2, outvar] = test_data[
            outvar
        ]
        test_data.loc[test_data["period_of_obtained_wage"] == 1, outvar] = (
            test_data[outvar] / 12
        )

    test_data["lohnst_m"] = test_data["lohnst_m"] // 1

    # Provisionally, calculate amount of claimed Kinderfreibeträge outside of Gettsim
    # (problem to solve when Soli is implemented)
    # test_data["eink_st_kinderfreib_tu"] = (
    #     test_data["anz_kinder_mit_kindergeld_tu"] * (2730 + 1464) * 2
    # )

    return test_data


@pytest.mark.parametrize("year, column", itertools.product(YEARS, OUT_COLS))
def test_lohnsteuer(input_data, year, column):
    input_data = input_data.reset_index(drop=True)
    df = input_data[INPUT_COLS].copy()
    policy_params, policy_functions = set_up_policy_environment(date=year)

    result = compute_taxes_and_transfers(
        data=df,
        params=policy_params,
        functions=policy_functions,
        targets=column,
        columns_overriding_functions=[
            "ges_krankenv_zusatzbeitrag",
            "ges_pflegev_zusatz_kinderlos",
        ],
    )
    assert_series_equal(
        result[column], input_data[column], check_dtype=False, atol=1e-1, rtol=1e-1
    )


def get_xml(url):
    """Send URL to BMF and obtain xml.

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
    """Formatting of URL.

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
    """Format URL, send it to BMF and format output.

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
    if "Der Zugriffscode ist abgelaufen" in str(xml_ugly):
        return "Error"

    xml_raw = ElementTree.fromstring(xml_ugly)
    # put information into DataFrame
    for index, child in enumerate(xml_raw.iter("ausgabe")):
        df = pd.concat([df, pd.DataFrame(child.attrib, index=[index])])

    return df.set_index("name").join(out_df)


def bmf_collect(inc, outvar, n_kinder, stkl, jahr, faktorverfahren=0, faktor="1,0000"):
    """Creates an URL for the API of the official calculator by the German Ministry of
    Finance (BMF), documented at: https://www.bmf-
    steuerrechner.de/interface/einganginterface.xhtml this url is called and the results
    are returned.

    Returns
    -------

    income tax due, depending on the value of outvar

    """
    url_base = f"http://www.bmf-steuerrechner.de/interface/{jahr}Version1.xhtml?"
    # ATTENTION: This bit changes on a yearly basis
    url_base += "code=ext2023"

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
    return out[outvar] / 100


def gen_lohnsteuer_test(year: int):
    """Calls the BMF API to generate correct lohnsteuer payments."""

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
            "year": [year] * 11,
            "ges_krankenv_zusatzbeitrag": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            "ges_pflegev_zusatz_kinderlos": [
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
                True,
            ],
        }
    )
    hh["child_num_kg"] = hh.groupby("tu_id")["kind"].transform("sum")

    # Get correct lohnsteuer from German Ministry of Finance
    hh["lohnst_m"] = np.vectorize(bmf_collect)(
        inc=hh["bruttolohn_m"],
        outvar="LSTLZZ",
        n_kinder=hh["child_num_kg"],
        stkl=hh["steuerklasse"],
        jahr=hh["year"],
    )

    hh["lohnst_soli_m"] = np.vectorize(bmf_collect)(
        hh["bruttolohn_m"],
        outvar="SOLZLZZ",
        n_kinder=hh["child_num_kg"],
        stkl=hh["steuerklasse"],
        jahr=hh["year"],
    )

    return hh


@pytest.mark.parametrize("year, column", itertools.product([2022, 2023], OUT_COLS))
def test_lohnsteuer_api(year, column):
    year_data = gen_lohnsteuer_test(year).reset_index(drop=True)
    df = year_data.copy()
    df["alleinerz"] = df["steuerklasse"] == 2
    df["wohnort_ost"] = False
    df["jahr_renteneintr"] = 2060
    # df["hat_kinder"] = df.groupby("tu_id")["kind"].transform("sum") > 0
    # df["in_ausbildung"] = ~df["kind"]
    df["arbeitsstunden_w"] = 40.0 * ~df["kind"]
    policy_params, policy_functions = set_up_policy_environment(date=year)

    result = compute_taxes_and_transfers(
        data=df.drop(columns=["lohnst_m", "lohnst_soli_m"]),
        params=policy_params,
        functions=policy_functions,
        targets=[column],
        columns_overriding_functions=[
            "ges_krankenv_zusatzbeitrag",
            "ges_pflegev_zusatz_kinderlos",
        ],
    )

    assert_series_equal(
        result[column], year_data[column], check_exact=False, atol=2, check_dtype=False
    )
