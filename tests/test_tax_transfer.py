import pytest
from pandas import DataFrame, Series
from pandas.testing import assert_series_equal, assert_frame_equal
from numpy.testing import assert_allclose
from src.analysis.tax_transfer import kindergeld, soc_ins_contrib, favorability_check, zve
from src.analysis.tax_transfer import tax_sched, soli, wg, alg2, kiz, ui, uhv
from itertools import product
from bld.project_paths import project_paths_join as ppj
import pandas as pd


# =============================================================================
# test kindergeld
# =============================================================================


def child_benefit_standard_df():
    cols = ["tu_id", "age", "w_hours", "ineducation", "m_wage"]
    data = [
        [1, 45, 40, False, 3000],
        [1, 40, 0, False, 0],
        [1, 24, 30, True, 700],
        [1, 18, 0, True, 200],
        [1, 17, 2, True, 0],
        [1, 15, 0, True, 0],
    ]

    df = DataFrame(columns=cols, data=data)
    return df


def child_benefit_many_children_df():
    df = DataFrame()
    df["tu_id"] = [0] * 6
    df["age"] = [1, 2, 3, 4, 5, 6]
    df["ineducation"] = [True] * 6
    df["w_hours"] = [0] * 6
    df["m_wage"] = [0] * 6
    return df


def child_benefit_eligibility_conditions():
    cols = ["tu_id", "age", "w_hours", "ineducation", "m_wage"]
    data = [
        [0, 50, 40, False, 0],
        [0, 12, 0, False, 0],
        [0, 14, 25, True, 800],
        [0, 15, 0, True, 300],
    ]
    df = DataFrame(columns=cols, data=data)
    return df


to_test = [
    (child_benefit_standard_df(), 2011, 570),
    (child_benefit_standard_df(), 2002, 570),
    (child_benefit_many_children_df(), 2011, 1227),
    (child_benefit_many_children_df(), 2001, 1227),
    (child_benefit_eligibility_conditions(), 2013, 188),
    (child_benefit_eligibility_conditions(), 2000, 188),
]


@pytest.mark.parametrize("df, yr, res", to_test)
def test_kindergeld(df, yr, res):
    tb = {"kgeld1": 188, "kgeld2": 188, "kgeld3": 194, "kgeld4": 219, "kgage": 25, "kgfreib": 7680}

    actual = kindergeld(df, tb, yr)
    expected = Series(data=res, index=actual.index, name="kindergeld_tu_basis")

    print(actual, "\n\n")
    print(expected, "\n\n")

    assert_series_equal(actual["kindergeld_tu_basis"], expected)


# =============================================================================
# test soc_ins_contrib
# =============================================================================


def load_ssc_input_data(year):
    assert year in [2010, 2018]
    df = pd.read_excel("tests/test_data/test_dfs_ssc.xlsx")
    input_cols = [
        "hid",
        "tu_id",
        "m_wage",
        "east",
        "age",
        "selfemployed",
        "haskids",
        "m_self",
        "m_pensions",
        "pkv",
        "year",
    ]
    df = df[input_cols]
    df = df[df["year"] == year]
    return df


def load_ssc_output_data(year, column):
    assert column in ["svbeit", "rvbeit", "avbeit", "gkvbeit", "pvbeit"]
    df = pd.read_excel("tests/test_data/test_dfs_ssc.xlsx")
    df = df[df["year"] == year]
    return df[column]


def load_tb(year):
    # df = pd.read_excel('tests/test_data/test_param.xls').set_index('para')
    df = pd.read_excel(ppj("IN_DATA","param.xls")).set_index("para")
    return df["y{}".format(year)].to_dict()


years = [2010, 2018]
columns = ["svbeit", "rvbeit", "avbeit", "gkvbeit", "pvbeit"]
to_test = list(product(years, columns))


@pytest.mark.parametrize("year, column", to_test)
def test_soc_ins_contrib(year, column):
    df = load_ssc_input_data(year)
    tb = load_tb(year)
    calculated = soc_ins_contrib(df, tb, year)[column]
    expected = load_ssc_output_data(year, column)
    assert_series_equal(calculated, expected)


# =============================================================================
# test Arbeitslosgendgeld (UI)
# =============================================================================
def load_ui_input_data(year):
    df = pd.read_excel("tests/test_data/test_dfs_ui.xlsx", true_values=["TRUE"])
    df = df[
        [
            "hid",
            "tu_id",
            "m_wage_l1",
            "east",
            "child",
            "months_ue",
            "months_ue_l1",
            "months_ue_l2",
            "alg_soep",
            "m_pensions",
            "w_hours",
            "child_num_tu",
            "age",
            "year",
        ]
    ]
    df = df.astype({"east": bool, "child": bool})
    df = df[df["year"] == year]

    return df


def load_ui_output_data(year):
    df = pd.read_excel("tests/test_data/test_dfs_ui.xlsx")
    df = df[["m_alg1", "year"]][df["year"] == year]

    return df["m_alg1"]


years = [2010, 2011, 2015, 2019]


@pytest.mark.parametrize("year", years)
def test_ui(year):
    df = load_ui_input_data(year)
    tb = load_tb(year)
    tb["yr"] = year
    calculated = ui(df, tb, year)
    expected = load_ui_output_data(year)
    print("calculated: \n", calculated, "\n\n")
    print("expected: \n", expected)
    assert_allclose(calculated, expected, atol=0.01)


# =============================================================================
# test favorability_check
# =============================================================================


def load_favorability_input_data(year):
    assert year in [2010, 2012, 2016]
    df = pd.read_excel("tests/test_data/test_dfs_favorability_check.xlsx")
    input_cols = [
        "hid",
        "tu_id",
        "pid",
        "zveranl",
        "child",
        "tax_nokfb_tu",
        "tax_abg_nokfb_tu",
        "tax_kfb_tu",
        "tax_abg_kfb_tu",
        "abgst_tu",
        "kindergeld_basis",
        "kindergeld_tu_basis",
        "year",
    ]
    df = df[input_cols]
    df = df[df["year"] == year]
    return df


def load_favorability_output_data(year, column):
    assert column in ["incometax_tu", "kindergeld", "kindergeld_hh", "kindergeld_tu"]
    df = pd.read_excel("tests/test_data/test_dfs_favorability_check.xlsx")
    df = df[df["year"] == year]
    return df[column]


years = [2010, 2012, 2016]
columns = ["incometax_tu", "kindergeld", "kindergeld_hh", "kindergeld_tu"]
to_test = list(product(years, columns))


@pytest.mark.parametrize("year, column", to_test)
def test_favorability_check(year, column):
    df = load_favorability_input_data(year)
    tb = {}
    calculated = favorability_check(df, tb, year)[column]
    expected = load_favorability_output_data(year, column)

    print(calculated.to_frame(), "\n")
    print(expected.to_frame(), "\n\n")
    assert_series_equal(calculated, expected)


# =============================================================================
# test zve
# =============================================================================


def load_zve_input_data(year):
    assert year in [2005, 2009, 2010, 2012, 2018]
    df = pd.read_excel("tests/test_data/test_dfs_zve.xlsx")
    input_cols = [
        "hid",
        "tu_id",
        "m_wage",
        "m_self",
        "m_kapinc",
        "m_vermiet",
        "renteneintritt",
        "m_pensions",
        "zveranl",
        "child",
        "handcap_degree",
        "rvbeit",
        "avbeit",
        "pvbeit",
        "alleinerz",
        "age",
        "child_num_tu",
        "year",
        "east",
        "gkvbeit",
    ]
    df = df[input_cols]
    for boolevar in ['east', 'zveranl', 'alleinerz', 'child']:
        df[boolevar] = df[boolevar].astype(bool)

    df = df[df["year"] == year]
    return df


def load_zve_output_data(year):

    columns = ["zve_nokfb", "zve_kfb", "zve_abg_nokfb", "zve_abg_kfb"]
    df = pd.read_excel("tests/test_data/test_dfs_zve.xlsx")
    df = df[df["year"] == year]
    return df[columns]


years = [2005, 2009, 2010, 2012, 2018]


@pytest.mark.parametrize("year", years)
def test_zve(year):
    columns = ["zve_nokfb", "zve_kfb", "zve_abg_nokfb", "zve_abg_kfb"]
    df = load_zve_input_data(year)
    tb = load_tb(year)
    calculated = zve(df, tb, year, hyporun=False)[columns]
    expected = load_zve_output_data(year)

    print(calculated)
    print(expected)

    # allow 1€ difference, caused by strange rounding issues.
    assert_allclose(calculated, expected, atol=1)
    # assert_frame_equal(calculated, expected)


# =============================================================================
# test tax_sched
# =============================================================================


def load_tax_sched_input_data(year):
    assert year in [2009, 2012, 2015, 2018]
    input_cols = [
        "hid",
        "tu_id",
        "zve_nokfb",
        "zve_kfb",
        "zve_abg_kfb",
        "zve_abg_nokfb",
        "gross_e5",
        "zveranl",
        "gross_e5_tu",
    ]
    df = pd.read_excel("tests/test_data/test_dfs_tax_sched.xlsx")
    df = df[df["year"] == year]
    df = df[input_cols]
    return df


def load_tax_sched_output_data(year):
    columns = ["tax_nokfb", "tax_kfb", "tax_abg_nokfb", "tax_abg_kfb", "abgst"]
    df = pd.read_excel("tests/test_data/test_dfs_tax_sched.xlsx")
    df = df[df["year"] == year]
    return df[columns]


years = [2009, 2012, 2015, 2018]


@pytest.mark.parametrize("year", years)
def test_tax_sched(year):
    columns = ["tax_nokfb", "tax_kfb", "tax_abg_nokfb", "tax_abg_kfb", "abgst"]
    df = load_tax_sched_input_data(year)
    tb = load_tb(year)
    tb["yr"] = year
    calculated = tax_sched(df, tb, year)[columns]
    expected = load_tax_sched_output_data(year)
    assert_frame_equal(
        calculated, expected, check_dtype=False, check_exact=False, check_less_precise=0
    )


# =============================================================================
# test soli
# =============================================================================


def load_soli_input_data(year):
    assert year in [2003, 2012, 2016, 2018]
    input_cols = [
        "hid",
        "tu_id",
        "pid",
        "zveranl",
        "tax_kfb_tu",
        "tax_abg_kfb_tu",
        "abgst_tu",
        "child",
        "incometax_tu",
    ]
    df = pd.read_excel("tests/test_data/test_dfs_soli.xlsx")
    df = df[df["year"] == year]
    print(df)
    return df


def load_soli_output_data(year):
    columns = ["soli", "soli_tu"]
    df = pd.read_excel("tests/test_data/test_dfs_soli.xlsx")
    df = df[df["year"] == year]
    return df[columns]


years = [2003, 2012, 2016, 2018]


@pytest.mark.parametrize("year", years)
def test_soli(year):
    columns = ["soli", "soli_tu"]
    df = load_soli_input_data(year)
    tb = load_tb(year)
    calculated = soli(df, tb, year)[columns]
    expected = load_soli_output_data(year)
    print("calculated: \n", calculated, "\n\n")
    print("expected: \n", expected)
    assert_frame_equal(calculated, expected)

# =============================================================================
# test uhv
# =============================================================================
def load_uhv_input_data(year):
    input_cols=['hid',
                'tu_id',
                'alleinerz',
                'age',
                'm_wage',
                'm_transfers',
                'm_kapinc',
                'm_vermiet',
                'm_self',
                'm_alg1',
                'm_pensions',
                'zveranl',
                'year']
    df = pd.read_excel("tests/test_data/test_dfs_uhv.xlsx")
    df = df[df["year"] == year]
    df = df[input_cols]
    return df

def load_uhv_output_data(year):
        df = pd.read_excel("tests/test_data/test_dfs_uhv.xlsx")
        df = df[df["year"] == year]
        return df["uhv"]

years = [2017, 2019]
@pytest.mark.parametrize("year", years)
def test_uhv(year):
    df = load_uhv_input_data(year)
    tb = load_tb(year)
    calculated = uhv(df, tb, year)
    expected = load_uhv_output_data(year)
    print("calculated: \n", calculated, "\n\n")
    print("expected: \n", expected)
    assert_series_equal(calculated, expected, check_dtype=False)


# =============================================================================
# test wg
# =============================================================================


def load_wg_input_data(year):
    assert year in [2006, 2009, 2013, 2016]
    input_cols = [
        "hid",
        "tu_id",
        "head_tu",
        "hh_korr",
        "hhsize",
        "child",
        "miete",
        "heizkost",
        "alleinerz",
        "child11_num_tu",
        "cnstyr",
        "m_wage",
        "m_pensions",
        "ertragsanteil",
        "m_alg1",
        "m_transfers",
        "uhv",
        "gross_e1",
        "gross_e4",
        "gross_e5",
        "gross_e6",
        "incometax",
        "rvbeit",
        "gkvbeit",
        "handcap_degree",
        "divdy",
        "year",
        "hhsize_tu",
    ]

    df = pd.read_excel("tests/test_data/test_dfs_wg.xlsx")
    df = df[df["year"] == year]
    df = df[input_cols]
    print(df)
    return df


def load_wg_output_data(year):
    columns = ["wohngeld_basis_hh"]
    df = pd.read_excel("tests/test_data/test_dfs_wg.xlsx")
    df = df[df["year"] == year]
    return df[columns]


years = [2006, 2009, 2013, 2016]


@pytest.mark.parametrize("year", years)
def test_wg(year):
    columns = ["wohngeld_basis_hh"]
    df = load_wg_input_data(year)
    tb = load_tb(year)
    calculated = wg(df, tb, year, False)[columns]
    expected = load_wg_output_data(year)
    print("calculated: \n", calculated, "\n\n")
    print("expected: \n", expected)
    assert_frame_equal(calculated, expected)


# =============================================================================
# test alg2
# =============================================================================


def load_alg2_input_data(year):
    assert year in [2006, 2009, 2010, 2011, 2013, 2016, 2019]
    input_cols = [
        "hid",
        "tu_id",
        "head_tu",
        "hh_korr",
        "hhsize",
        "child",
        "age",
        "byear",
        "miete",
        "heizkost",
        "alleinerz",
        "adult_num",
        "child6_num",
        "child15_num",
        "child18_num",
        "child_num",
        "child14_24_num",
        "child7_13_num",
        "child3_6_num",
        "child2_num",
        "m_wage",
        "m_pensions",
        "m_kapinc",
        "m_alg1",
        "m_transfers",
        "m_self",
        "m_vermiet",
        "incometax",
        "soli",
        "svbeit",
        "kindergeld_hh",
        "uhv",
        "divdy",
        "year",
    ]

    df = pd.read_excel("tests/test_data/test_dfs_alg2.xlsx")
    df = df[df["year"] == year]
    df = df[input_cols]
    print(df)
    return df


def load_alg2_output_data(year):
    columns = ["ar_base_alg2_ek", "ar_alg2_ek_hh", "regelbedarf"]
    df = pd.read_excel("tests/test_data/test_dfs_alg2.xlsx")
    df = df[df["year"] == year]
    return df[columns]


years = [2006, 2009, 2011, 2013, 2016, 2019]


@pytest.mark.parametrize("year", years)
def test_alg2(year):
    columns = ['ar_base_alg2_ek', 'ar_alg2_ek_hh', 'regelbedarf']
    df = load_alg2_input_data(year)
    tb = load_tb(year)
    calculated = alg2(df, tb, year)[columns]
    expected = load_alg2_output_data(year)
    print("calculated: \n", calculated, "\n\n")
    print("expected: \n", expected)
    assert_frame_equal(calculated, expected)


# =============================================================================
# test kiz
# =============================================================================


def load_kiz_input_data(year):
    assert year in [2006, 2009, 2011, 2013, 2016, 2019]
    input_cols = [
        "hid",
        "tu_id",
        "head",
        "hhtyp",
        "hh_korr",
        "hhsize",
        "child",
        "pensioner",
        "age",
        "miete",
        "heizkost",
        "alleinerz",
        "mehrbed",
        "adult_num_tu",
        "child_num_tu",
        "alg2_grossek_hh",
        "ar_alg2_ek_hh",
        "wohngeld_basis_hh",
        "regelbedarf",
        "ar_base_alg2_ek",
        "kindergeld_hh",
        "uhv",
        "year",
    ]

    df = pd.read_excel("tests/test_data/test_dfs_kiz.xlsx")
    df = df[df["year"] == year]
    df = df[input_cols]
    print(df)
    return df


def load_kiz_output_data(year):
    columns = ["kiz", "m_alg2", "wohngeld"]
    df = pd.read_excel("tests/test_data/test_dfs_kiz.xlsx")
    df = df[df["year"] == year]
    return df[columns]


years = [2006, 2009, 2011, 2013, 2016, 2019]


@pytest.mark.parametrize("year", years)
def test_kiz(year):
    columns = ["kiz", "m_alg2", "wohngeld"]
    df = load_kiz_input_data(year)
    tb = load_tb(year)
    calculated = kiz(df, tb, year, False)[columns]
    expected = load_kiz_output_data(year)
    print("calculated: \n", calculated, "\n\n")
    print("expected: \n", expected)
    assert_frame_equal(calculated, expected, check_dtype=False)
