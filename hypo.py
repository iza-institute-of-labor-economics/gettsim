# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 14:36:30 2018

@author: iza6354
"""
from imports import *
from taxtransfer import *

"""
Hypothetical Household Types
   11: Single, keine Kinder
   22: Alleinerziehend, ein Kind (3 Jahre)
   24: Alleinerziehend, zwei Kinder (3 und 8 Jahre)
   31: Paar, Alleinverdiener HH, keine Kinder
   32: Paar, Alleinverdiener HH, zwei Kinder
   33: Paar, geringes Partnereinkommen, keine Kinder
   34: Paar, geringes Partnereinkommen, zwei Kinder
   35: Paar, mittleres Partnereinkommen, keine Kinder
   36: Paar, mittleres Partnereinkommen, zwei Kinder
   37: Paar, hohes Partnereinkommen, keine Kinder
   38: Paar, hohes Partnereinkommen, zwei Kinder
"""

def create_hypo_data(data_path, settings):

    # DEFINE STEPS IN YEARLY WAGES
    wagestep = 200

    df = pd.read_pickle(data_path + 'SOEP/taxben_input_2016')
    # drop all rows
    df = df.iloc[0:0]

    # append rows with zeros
    s2 = pd.Series(np.zeros(len(list(df))), index=list(df))
    for i in range(0, 5):
        df = df.append(s2, ignore_index=True)

    # Some of them need to be boolean values
    df['selfemployed'] = False
    df['pkv'] = False
    df['ineducation'] = False

    df['months'] = 12
    df['typ'] = df.index + 1

    df_typ2 = df[df['typ'] == 2]
    # Alleinerziehende
    df = df.append([df_typ2], ignore_index=True)

    df_typ3 = df[df['typ'] == 3]
    # Paare mit und ohne kinder
    df = df.append([df_typ3]*7, ignore_index=True)

    df = df.sort_values(by=['typ'])
    df['n_typ'] = df.groupby(['typ']).cumcount()+1

    df.loc[df['typ'] == 1, 'typ_bud'] = 11
    df.loc[df['typ'] == 2, 'typ_bud'] = 20 + 2 * df['n_typ']
    df.loc[df['typ'] == 3, 'typ_bud'] = 30 + df['n_typ']

    df[['typ', 'typ_bud']]

    # Set some variables
    df.loc[df['typ_bud'] == 11, 'hhtyp_old'] = 1
    df.loc[(df['typ_bud'] >= 30) & ((df['typ_bud'] % 2) != 0), 'hhtyp_old'] = 2
    df.loc[(df['typ_bud'] == 22) | (df['typ_bud'] == 24), 'hhtyp_old'] = 3
    df.loc[(df['typ_bud'] >= 30) & ((df['typ_bud'] % 2) == 0), 'hhtyp_old'] = 4

    df['alleinerz'] = df['hhtyp_old'] == 2
    # Verdopple die Reihen und erhöhe den Lohn
    df = df.append([df] * 500, ignore_index=True)
    df = df.sort_values(by=['typ_bud'])
    df['n_typ_bud'] = df.groupby(['typ_bud']).cumcount()
    df['y_wage'] = df['n_typ_bud'] * wagestep

    df['head'] = True
    df['head_tu'] = True
    df['age'] = 30
    df['child'] = False
    df['female'] = False

    # verdopple die Reihen mit Paarhaushalten
    df = df.append([df[df['typ_bud'] > 30]], ignore_index=True)
    df = df.sort_values(by=['typ_bud', 'y_wage'])
    df['female'] = (df.groupby(['typ_bud', 'y_wage']).cumcount()) > 0


    # 'produziere' Kinder...klone hid etc. von Erwachsenen und manipuliere Alter.
    # Dann wieder dranmergen

    kids = df[df['typ_bud'].isin([22, 24, 32, 34, 36, 38])
              & (df['y_wage'] == 0)]

    kids = kids.append([kids]*500, ignore_index=True)
    kids = kids.sort_values(by=['typ_bud'])
    kids['n_typ_bud'] = kids.groupby(['typ_bud']).cumcount()
    kids['y_wage'] = kids['n_typ_bud'] * wagestep
    # dupliziere, aber nicht für ALleinerz. mit einem Kind
    kids = kids.append(kids[kids['typ_bud'] != 22])
    kids = kids.sort_values(by=['typ_bud', 'y_wage'])
    kids['n'] = kids.groupby(['typ_bud', 'y_wage']).cumcount()
    # first kid is 3, second kid is 8
    kids['age'] = 3
    kids.loc[kids['n'] == 1, 'age'] = 8
    kids['child'] = True
    kids['ineducation'] = True
    kids['female'] = True

    # append kids
    df = df.append(kids)
    print(df['typ_bud'].value_counts())
    df = df.sort_values(by=['typ_bud', 'y_wage'])
    df = df.reset_index(drop=True)

    # drop missings
    df = df.dropna(subset=['typ_bud'])

    # Personal ID
    df['pid'] = df.index
    # create household id
    df['hid'] = df['y_wage'] * 1000 + df['typ_bud'].astype(int)
    df['tu_id'] = df['hid']

    # Children variables
    df = df.drop(['child_num', 'child_num_tu'], 1)
    df = df.join(df.groupby(['hid'])['child'].sum(), on=['hid'],
                 how='left', rsuffix="_num")
    df['child_num_tu'] = df['child_num']

    df['child3_6_num'] = 1 * ((df['typ_bud'] % 2) == 0)
    for var in ['7_11', '7_13', '7_16', '12_15']:
        df['child'+var+'_num'] = (1 * (df['typ_bud'] >= 24)
                                  + (df['typ_bud'] % 2 == 0))

    df['child6'] = df['child3_6_num']
    for var in ['11', '15', '18', '']:
        df['child'+var+'_num'] = df['child3_6_num'] + df['child7_16_num']

    # Erster Mann ist immer Head, der Rest sind Frauen und Mädchen
    df['head'] = ~df['female']

    df['haskids'] = df['child_num'] > 0
    df['adult_num'] = 1 + (df['typ_bud'] >= 31) * 1
    df['hhsize'] = df['adult_num'] + df['child_num']

    tuvars = ['child3_6', 'child7_11', 'child7_13', 'child7_16',
              'child12_15', 'child14_24', 'child2', 'child11',
              'child15', 'child18', 'child', 'adult']

    for var in tuvars:
        df[var+'num_tu'] = df[var+'_num']

    df['hhsize_tu'] = df['hhsize']

    # Miete und Heizkosten.
    df['cnstyr'] = 2
    df.loc[df['hhsize'] == 1, 'heizkost'] = 56
    df.loc[df['typ_bud'].isin([22, 24, 31, 33, 35, 37]), 'heizkost'] = 90
    df.loc[df['typ_bud'].isin([32, 34, 36, 38]), 'heizkost'] = 110

    df.loc[df['hhsize'] == 1, 'miete'] = 380 - df['heizkost']
    df.loc[df['typ_bud'].isin([22, 24, 31, 33, 35, 37]),
           'miete'] = 510 - df['heizkost']
    df.loc[df['typ_bud'].isin([32, 34, 36, 38]),
           'miete'] = 600 - df['heizkost']

    df['east'] = False
    df['zveranl'] = df['typ_bud'] >= 30

    # Teile das Jahreseinkommen auf für Paare...
    # s gibt erstmal nur alleinverdiener
    df['y_wage_ind'] = df['y_wage']
    df.loc[df['female'], 'y_wage_ind'] = 0
    df['m_wage'] = df['y_wage_ind'] / 12
    df.loc[df['m_wage'] > 0, 'w_hours'] = 40

    df = df.sort_values(by=['typ_bud', 'y_wage', 'female'])
    df = df.dropna(subset=['typ_bud'])
    # Drop Doppeltverdiener
    df = df[df['typ_bud'] < 33]

    pd.to_pickle(df, data_path + 'SOEP/taxben_input_hypo')
    # df.to_stata(data_path+'hypo.dta')

    taxout_hypo = taxtransfer(settings['DATA_PATH'] + 'SOEP/taxben_input_',
                              settings,
                              'RS2018',
                              True)

    # EMTR Graphen
    # keep only those that get earnings
    df = taxout_hypo.copy()
    df = df.sort_values(by=['typ_bud', 'y_wage'])
    # create writer for excel
    hypo_writer = pd.ExcelWriter(data_path + 'check_hypo.xlsx')
    out_vars = ['typ_bud', 'female', 'age', 'head', 'child', 'y_wage',
                'm_wage', 'w_hours', 'dpi', 'wohngeld', 'kiz',
                'kindergeld', 'svbeit', 'tax_income', 'incometax']
    for typ in [11, 22, 24, 31, 32]:
        df[df['typ_bud'] == typ].to_excel(hypo_writer,
                                          sheet_name='typ_' + str(typ),
                                          columns=out_vars, na_rep='NaN',
                                          freeze_panes=(1, 0))

    # graph it
    # data set with heads only
    h = df[df['head']]
    h = h.sort_values(by = ['typ_bud', 'y_wage'])
    h['emtr'] = (1 - (h['dpi'] - h['dpi'].shift(1))
                 / (h['m_wage'] - h['m_wage'].shift(1)))

    # GRAPH SETTINGS
    maxinc = 50000

    for t in [11, 22, 24, 31, 32]:
        plt.clf()
        ax = h[(h['typ_bud'] == t)
               & (h['y_wage'] <= maxinc)].plot.line(x='y_wage',y='emtr')
        fig = ax.get_figure()
        fig.savefig(settings['GRAPH_PATH'] + 'hypo/emtr_'
                                           + str(t) +'.png')
#        for f in [0,1]:
#            plt.clf()
#            plotdata = df[['w_hours','syear','female']].query('syear == @y & female == @f')
#            hours = np.array(plotdata['w_hours'])
#            plt.hist(hours,bins=13,range=(1,60))
#            plt.title('Hours Distribution, Year: '+ str(y)+ ', Female: ' +str(f))
#            plt.savefig(graph_path+'hrs_dist/'+str(y)+'_f'+str(f)+'.png')
