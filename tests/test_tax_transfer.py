import pytest
from pandas import DataFrame, Series
from pandas.testing import assert_series_equal, assert_frame_equal
from tax_transfer import kindergeld, soc_ins_contrib, favorability_check, zve
from tax_transfer import tax_sched
from itertools import product
import pandas as pd


# =============================================================================
# test kindergeld
# =============================================================================


def child_benefit_standard_df():
    cols = ['tu_id', 'age', 'w_hours', 'ineducation', 'm_wage']
    data = [[1, 45, 40, False, 3000],
            [1, 40, 0, False, 0],
            [1, 24, 30, True, 700],
            [1, 18, 0, True, 200],
            [1, 17, 2, True, 0],
            [1, 15, 0, True, 0]]

    df = DataFrame(columns=cols, data=data)
    return df


def child_benefit_many_children_df():
    df = DataFrame()
    df['tu_id'] = [0] * 6
    df['age'] = [1, 2, 3, 4, 5, 6]
    df['ineducation'] = [True] * 6
    df['w_hours'] = [0] * 6
    df['m_wage'] = [0] * 6
    return df


def child_benefit_eligibility_conditions():
    cols = ['tu_id', 'age', 'w_hours', 'ineducation', 'm_wage']
    data = [[0, 50, 40, False, 0],
            [0, 12, 0, False, 0],
            [0, 14, 25, True, 800],
            [0, 15, 0, True, 300]]
    df = DataFrame(columns=cols, data=data)
    return df


to_test = [(child_benefit_standard_df(), 2011, 570),
           (child_benefit_standard_df(), 2002, 570),
           (child_benefit_many_children_df(), 2011, 1227),
           (child_benefit_many_children_df(), 2001, 1227),
           (child_benefit_eligibility_conditions(), 2013, 188),
           (child_benefit_eligibility_conditions(), 2000, 188)]


@pytest.mark.parametrize('df, yr, res', to_test)
def test_kindergeld(df, yr, res):
    tb = {'kgeld1': 188, 'kgeld2': 188, 'kgeld3': 194, 'kgeld4': 219,
          'kgage': 25, 'kgfreib': 7680}

    actual = kindergeld(df, tb, yr)
    expected = Series(data=res, index=actual.index, name='kindergeld_tu_basis')

    print(actual, '\n\n')
    print(expected, '\n\n')

    assert_series_equal(actual['kindergeld_tu_basis'], expected)

# =============================================================================
# test soc_ins_contrib
# =============================================================================


def load_ssc_input_data(year):
    assert year in [2010, 2018]
    df = pd.read_excel('tests/test_data/test_dfs_ssc.xlsx')
    input_cols = ['hid', 'tu_id', 'm_wage', 'east', 'age', 'selfemployed',
                  'haskids', 'm_self', 'm_pensions', 'pkv', 'year']
    df = df[input_cols]
    df = df[df['year'] == year]
    return df


def load_ssc_output_data(year, column):
    assert column in ['svbeit', 'rvbeit', 'avbeit', 'gkvbeit', 'pvbeit']
    df = pd.read_excel('tests/test_data/test_dfs_ssc.xlsx')
    df = df[df['year'] == year]
    return df[column]


def load_tb(year):
    df = pd.read_excel('tests/test_data/test_param.xls').set_index('para')
    return df['y{}'.format(year)].to_dict()


years = [2010, 2018]
columns = ['svbeit', 'rvbeit', 'avbeit', 'gkvbeit', 'pvbeit']
to_test = list(product(years, columns))


@pytest.mark.parametrize('year, column', to_test)
def test_soc_ins_contrib(year, column):
    df = load_ssc_input_data(year)
    tb = load_tb(year)
    calculated = soc_ins_contrib(df, tb, year)[column]
    expected = load_ssc_output_data(year, column)
    assert_series_equal(calculated, expected)


# =============================================================================
# test favorability_check
# =============================================================================


def load_favorability_input_data(year):
    assert year in [2010, 2012, 2016]
    df = pd.read_excel('tests/test_data/test_dfs_favorability_check.xlsx')
    input_cols = ['hid', 'tu_id', 'pid', 'zveranl', 'child', 'tax_nokfb_tu',
                  'tax_abg_nokfb_tu', 'tax_kfb_tu', 'tax_abg_kfb_tu',
                  'abgst_tu', 'kindergeld_basis', 'kindergeld_tu_basis',
                  'year']
    df = df[input_cols]
    df = df[df['year'] == year]
    return df


def load_favorability_output_data(year, column):
    assert column in [
        'incometax_tu', 'kindergeld', 'kindergeld_hh', 'kindergeld_tu']
    df = pd.read_excel('tests/test_data/test_dfs_favorability_check.xlsx')
    df = df[df['year'] == year]
    return df[column]

years = [2010, 2012, 2016]
columns = ['incometax_tu', 'kindergeld', 'kindergeld_hh', 'kindergeld_tu']
to_test = list(product(years, columns))


@pytest.mark.parametrize('year, column', to_test)
def test_favorability_check(year, column):
    df = load_favorability_input_data(year)
    tb = {}
    calculated = favorability_check(df, tb, year)[column]
    expected = load_favorability_output_data(year, column)

    print(calculated.to_frame(), '\n')
    print(expected.to_frame(), '\n\n')
    assert_series_equal(calculated, expected)

# =============================================================================
# test zve
# =============================================================================


def load_zve_input_data(year):
    assert year in [2005, 2009, 2010, 2012, 2018]
    df = pd.read_excel('tests/test_data/test_dfs_zve.xlsx',
                       true_values=['TRUE()'], false_values=['FALSE()'])
    input_cols = [
        'hid', 'tu_id', 'm_wage', 'm_self', 'm_kapinc', 'm_vermiet',
        'renteneintritt', 'm_pensions', 'zveranl', 'child', 'handcap_degree',
        'rvbeit', 'avbeit', 'pvbeit', 'alleinerz', 'age',
        'child_num_tu', 'year', 'east', 'gkvbeit']
    df = df[input_cols]
    df = df[df['year'] == year]
    return df


def load_zve_output_data(year):

    columns = ['zve_nokfb', 'zve_kfb', 'zve_abg_nokfb', 'zve_abg_kfb']
    df = pd.read_excel('tests/test_data/test_dfs_zve.xlsx')
    df = df[df['year'] == year]
    return df[columns]

years = [2005, 2009, 2010, 2012, 2018]


@pytest.mark.parametrize('year', years)
def test_zve(year):
    columns = ['zve_nokfb', 'zve_kfb', 'zve_abg_nokfb', 'zve_abg_kfb']
    df = load_zve_input_data(year)
    tb = load_tb(year)
    tb['ch_allow'] = tb['kifreib']
    calculated = zve(df, tb, year)[columns]
    expected = load_zve_output_data(year)
    assert_frame_equal(calculated, expected)


# =============================================================================
# test tax_sched
# =============================================================================

def load_tax_sched_input_data(year):
    assert year in [2009, 2012, 2015, 2018]
    input_cols = ['hid', 'tu_id', 'zve_nokfb', 'zve_kfb', 'zve_abg_kfb',
                  'zve_abg_nokfb', 'gross_e5', 'zveranl', 'gross_e5_tu']
    df = pd.read_excel('tests/test_data/test_dfs_tax_sched.xlsx')
    df = df[df['year'] == year]
    df = df[input_cols]
    print(df)
    return df


def load_tax_sched_output_data(year):
    columns = ['tax_nokfb', 'tax_kfb', 'tax_abg_nokfb', 'tax_abg_kfb', 'abgst']
    df = pd.read_excel('tests/test_data/test_dfs_tax_sched.xlsx')
    df = df[df['year'] == year]
    return df[columns]

years = [2009, 2012, 2015, 2018]


@pytest.mark.parametrize('year', years)
def test_tax_sched(year):
    columns = ['tax_nokfb', 'tax_kfb', 'tax_abg_nokfb', 'tax_abg_kfb', 'abgst']
    df = load_tax_sched_input_data(year)
    tb = load_tb(year)
    tb['yr'] = year
    calculated = tax_sched(df, tb, year)[columns]
    expected = load_tax_sched_output_data(year)
    print('calculated: \n', calculated, '\n\n')
    print('expected: \n', expected)
    assert_frame_equal(calculated.round(), expected.round(), check_dtype=False)

