# -*- coding: utf-8 -*-
"""
Compare stata + python output.
"""

import pandas as pd
import matplotlib.pyplot as plt

def check_hypo(settings):
    taxyear = str(settings['taxyear'])
    types = {11: "Single, keine Kinder",
             22: "Alleinerziehend, ein Kind (3 Jahre)",
             24: "Alleinerziehend, zwei Kinder (3 und 8 Jahre)",
             31: "Paar, Alleinverdiener HH, keine Kinder",
             32: "Paar, Alleinverdiener HH, zwei Kinder"
             }


    # Get Stata output
    try:
        stata = pd.read_stata(settings['DATA_PATH'] + 'hypo/stata_check_' +
                              taxyear + '.dta',
                              convert_categoricals=False
                              )
    except FileNotFoundError:
        print('There is no Stata hypo output for year' + str(taxyear))
        return False
    # Filter households
    stata = stata[stata['typ_bud'] <= 32]

    # rename a bit
    rename_vars = {'y_c_RS' + taxyear: 'dpi_stata',
                   'childben_RS' + taxyear: 'kindergeld_hh_stata',
                   'inct_RS' + taxyear: 'tax_stata',
                   'contrib_RS' + taxyear: 'svbeit_stata',
                   'ub_RS' + taxyear: 'm_alg2_stata',
                   'kiz_RS' + taxyear: 'kiz_stata',
                   'houseben_RS' + taxyear: 'wohngeld_stata',
                   }
    stata = stata.rename(columns=rename_vars)

    # yearly to monthly
    for var in rename_vars.values():
        stata[var] = stata[var] / 12

    # now, get the python output
    pyth = pd.read_json(settings['DATA_PATH'] + 'hypo/python_check' +
                        taxyear + '.json')
    pyth = pyth.rename(columns={'dpi': 'dpi_pyth',
                                'kindergeld_hh': 'kindergeld_hh_pyth',
                                'svbeit': 'svbeit_pyth',
                                'm_alg2': 'm_alg2_pyth',
                                'kiz': 'kiz_pyth',
                                'wohngeld': 'wohngeld_pyth'
                                })

    pyth['tax_pyth'] = pyth['incometax_tu'] + pyth['soli_tu']
    # merge them
    df = pd.merge(pyth,
                  stata,
                  how='inner',
                  on=['typ_bud', 'y_wage'],
                  suffixes=['_pyth', '_stata']
                  )

    df = df.sort_values(by=['typ_bud', 'y_wage'])
    # check difference in dpi
    for var in ['dpi',
                'kindergeld_hh',
                'tax',
                'svbeit',
                'm_alg2',
                'kiz',
                'wohngeld']:
        df['diff_' + var] = df[var + '_pyth'] - df[var + '_stata']
        print('Check ' + var)
        print(df.groupby('typ_bud')['diff_' + var].describe())
        # plot themdf
        # fig.figsize(8, 8)
        for typ in df['typ_bud'].unique():
            plt.clf()
            fig = plt.figure(figsize=(10, 5))
            ax = fig.add_subplot(111)
            grp = df[df['typ_bud'] == typ]
            ax.plot(grp['m_wage_pyth'],
                    grp[var + '_pyth'],
                    'k-',
                    label='Python')
            ax.plot(grp['m_wage_pyth'],
                    grp[var + '_stata'],
                    'k:',
                    label='Stata')
            ax.set_title(str(types[typ]), size=14)
            ax.set_ylabel(var, size=14)
            ax.set_xlabel('Gross Wage')
            ax.legend(loc='best')
            plt.savefig(settings['GRAPH_PATH'] +
                        'hypo/check_' + var + '_'
                        + str(typ) +
                        '.png')

    return True