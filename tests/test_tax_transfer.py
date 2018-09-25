import pytest
from pandas import DataFrame, Series
from pandas.testing import assert_frame_equal, assert_series_equal
from tax_transfer import kindergeld, soc_ins_contrib
from itertools import product
import pandas as pd
from os import getcwd, listdir


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
    expected = Series(data=res, index=actual.index, name='kindergeld_tu')

    print(actual, '\n\n')
    print(expected, '\n\n')

    assert_series_equal(actual['kindergeld_tu'], expected)

# =============================================================================
# test soc_ins_contrib
# =============================================================================


def load_ssc_input_data(year):
    assert year in [2010, 2018]
    print(getcwd())
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


def ssc_tb(year):
    assert year in [2010, 2018]
    if year == 2010:
        tb = {'gkvbs_ag': 0.07, 'gkvbs_an': 0.079, 'gpvbs': 0.00975,
              'gpvbs_kind': 0.0025, 'bezgr_w': 2555, 'bezgr_o': 2170,
              'kvmaxeko': 3750, 'kvmaxekw': 3750, 'alvbs': 0.014,
              'grvbs': 0.0995, 'rvmaxeko': 4650, 'rvmaxekw': 5500,
              'midi_grenze': 800, 'mini_grenzeo': 400, 'mini_grenzew': 400,
              'mini_ag_gkv': 0.13, 'mini_ag_grv': 0.15, 'stpag': 0.02,
              'miniuml': 0.0108}
    else:
        tb = {'gkvbs_ag': 0.073, 'gkvbs_an': 0.083, 'gpvbs': 0.01275,
              'gpvbs_kind': 0.0025, 'bezgr_w': 3045, 'bezgr_o': 2695,
              'kvmaxeko': 4425, 'kvmaxekw': 4425, 'alvbs': 0.015,
              'grvbs': 0.093, 'rvmaxeko': 5800, 'rvmaxekw': 6500,
              'midi_grenze': 850, 'mini_grenzeo': 450, 'mini_grenzew': 450,
              'mini_ag_gkv': 0.13, 'mini_ag_grv': 0.15, 'stpag': 0.02,
              'miniuml': 0.012}
    return tb


years = [2010, 2018]
columns = ['svbeit', 'rvbeit', 'avbeit', 'gkvbeit', 'pvbeit']
to_test = list(product(years, columns))


@pytest.mark.parametrize('year, column', to_test)
def test_soc_ins_contrib(year, column):
    df = load_ssc_input_data(year)
    tb = ssc_tb(year)
    calculated = soc_ins_contrib(df, tb, year)[column]
    expected = load_ssc_output_data(year, column)

    print(calculated.to_frame(), '\n')
    print(expected.to_frame(), '\n\n')
    assert_series_equal(calculated, expected)
