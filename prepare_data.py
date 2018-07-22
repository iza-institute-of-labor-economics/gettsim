# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 08:48:33 2018

@author: iza6354
"""
from imports import *


def preparedata(df):

    df['syear'].value_counts()

    # Counter
    df['counter'] = 1

    # Deal with Missing PNR
    df['kinderdaten'] = ~df['k_rel'].isna()
    df = df.sort_values(by=['syear', 'hid', 'pnr'])
    df = df.join(df.groupby(['syear', 'hid'])['pnr'].max(),
                 on=['syear', 'hid'], how='left', rsuffix='_max')
    df['pnr_mis'] = df['pnr'].isna() & ~df['kinderdaten']
    df['pnr_mis_n'] = df.groupby(['syear', 'hid'])['pnr_mis'].cumsum()
    df.loc[df['pnr_mis'], 'pnr'] = df['pnr_max'] + df['pnr_mis_n']
    drop(df, ['pnr_mis', 'pnr_max', 'pnr_mis_n'])

    # Demographics
    # Age
    df['age'] = df['d11101'][df['d11101'] >= 0]
    # Birth Year
    df['byear'] = df['syear'] - df['age']
    # Female dummy
    df['female'] = (df['d11102ll'] == 2)
    # Foreigner Dummy
    df['foreigner'] = df['pgnation'] > 1
    
    df['byear'] = df['byear'].astype(int)
    df['age'] = df['age'].astype(int)
    df['work_age'] = df['age'].between(15, 64)

    # drop HH with missing age information
    df['age_mis'] = pd.isna(df['age'])
    df = df.join(df.groupby(['syear', 'hid'])['age_mis'].sum(),
                 on=['syear', 'hid'], how='left', rsuffix='_sum')
    df = df.drop(df[df['age_mis_sum'] > 0].index)

    # Employment Status
    df['pensioner'] = ((df['pgstib'] == 13) | (df['age'] > 64))
    df['ineducation'] = (((df['pgstib'] > 100) & (df['pgstib'] < 200)) |
                         (df['pgstib'] == 11))
    df['military'] = df['pgstib'] == 15
    df['parentalleave'] = df['pglfs'] == 4
    df['civilservant'] = df['pgstib'] > 600
    df['pubsector'] = df['pgoeffd'] == 1
    df['selfemployed'] = ((df['pgstib'] > 400) & (df['pgstib'] < 500))
    df['renteneintritt'] = (df['pensioner'] *
                            (df['syear'] - 1 - (df['age'] - 65)))
    
    # Region
    df['east'] = df['l11102'] == 2
    # Position within the HH
    # Head
    df['head'] = df['stell'] == 1
    # Spouse of Head
    df['spouse'] = df['stell'] == 2
    # Child of head, can be above 18!
    df['child'] = (((df['stell'] == 3) & (df['age'] < 16)) | 
                   ((df['age'] <= 16) | ((df['age'] < 25) & 
                    df['ineducation'])))
    # other members
    df['othmem'] = ~df[['head', 'spouse', 'child']].any(axis=1)
    # Make sure there is exactly one head per HH
    df['h'] = 1 * df['head']
    df = df.sort_values(by=['syear', 'hid', 'head', 'child'],
                        ascending=[True, True, False, True])
    df['head_num'] = df.groupby(['syear', 'hid'])['h'].cumsum()
    assert df['head_num'].all() == 1

    #######################################################
    # Split households. This is e.g. necessary for income tax assessment,
    # for which couples and their children form 'tax units' on their own
    # In the end, each of these tax units should have one or two adults
    # plus their dependent children
    ######################################################
    print('Splitting of households...')
    # 'Main Unit' consists of head, spouse and children
    df['main_unit'] = ((df[['head', 'spouse']].any(axis=1)) | 
                       ((df['child']) & ((df['partner_id'] < 0) | 
                                         (pd.isna(df['partner_id'])))))
    # This captures adult members which are not a head without partner
    df['young_single_unit'] = ((df['age'] < 40) & (~df['main_unit']) &  
                               ((df['partner_id'] < 0) | 
                                (pd.isna(df['partner_id']))))
    # The same for couples which are not head
    df['young_couple_unit'] = ((~df['main_unit']) & 
                               (~df['young_single_unit']) & 
                               (df['stell'].isin([3, 4, 5])) &
                               (df['partner_id'] > 0))    

    # check if both partners are present (due to miscoding)
    df = df.join(df.groupby(['syear', 'hid'])['young_couple_unit'].sum(),
                 on=['syear', 'hid'], how='left', rsuffix='_sum')
    # if there is only one partner, it's a single
    df.loc[(df['young_couple_unit_sum'] == 1) & 
           (~df['main_unit']), 'young_single_unit'] = True
    df.loc[(df['young_couple_unit_sum'] == 1), 'young_couple_unit'] = False
    # Add grandchildren of head to young couple unit
    df.loc[(~df['young_single_unit']) & 
           (~df['young_couple_unit']) & 
           (~df['main_unit']) &
           (df['young_couple_unit_sum'] == 2) & 
           (df['k_rel'].isin([25, 26])), 'young_couple_unit'] = True
    # ...unless they are above 18
    df.loc[(~df['young_single_unit']) & 
           (~df['young_couple_unit']) &
           (~df['main_unit']) &
           (df['young_couple_unit_sum'] == 0) &
           (df['age'] >= 18), 'young_single_unit'] = True

    # df = df.join(df.groupby(['syear','hid'])['identi'].first(), on = ['syear','hid'], how='left', rsuffix = 'fier')
    # do the same with the generation older than the ehad
    df['old_dummy'] = ((df['stell'] == 4) &
                       (~df['main_unit']) &
                       (~df['young_single_unit']) &
                       (~df['young_couple_unit']))
    df = df.join(df.groupby(['syear', 'hid'])['old_dummy'].sum(),
                 on=['syear', 'hid'], how='left', rsuffix='_sum')
    df['old_couple_unit'] = df['old_dummy'] & df['old_dummy_sum'] == 2
    df['old_single_unit'] = df['old_dummy'] & df['old_dummy_sum'] == 1
    # Apply the same checks on presence of partner
    df.loc[(~df['main_unit']) &
           (~df['young_single_unit']) &
           (~df['young_couple_unit']) &
           (~df['old_couple_unit']) &
           (~df['old_single_unit']) &
           (df['partner_id'] == 1), 'main_unit'] = True
    # treat residuals as single units
    df.loc[(~df['main_unit'])
           & (~df['young_single_unit'])
           & (~df['young_couple_unit'])
           & (~df['old_couple_unit'])
           & (~df['old_single_unit']), 'old_single_unit'] = True
    # combine old and young units
    df['single_unit'] = df['young_single_unit'] | df['old_single_unit']
    df['couple_unit'] = df['young_couple_unit'] | df['old_couple_unit']
    # drop some vars
    df = df.drop(columns=['young_single_unit',
                          'young_couple_unit_sum',
                          'young_couple_unit',
                          'old_single_unit',
                          'old_couple_unit'], axis=1)

    # Create 'new unit' dummy
    df['new_unit'] = df['main_unit'] & df['head']
    df.loc[(~df['main_unit']) &
           (df['single_unit']) &
           (~df['couple_unit']), 'new_unit'] = True
    df.loc[(~df['main_unit']) &
           (df['single_unit']) &
           (~df['couple_unit']) &
           (df['child']), 'new_unit'] = False
    df.loc[(~df['main_unit']) & 
           (~df['single_unit']) &
           (df['couple_unit']), 'new_unit'] = True
    # Set 'new_unit' to zero for the second partner of a couple unit.
    df = df.sort_values(by=['syear', 'hid', 'couple_unit', 'single_unit'],
                        ascending=[True, True, False, False])
    df['n'] = df.groupby(['syear', 'hid'])['counter'].cumsum()
    df.loc[(~df['main_unit']) & 
           (~df['single_unit']) &
           (df['couple_unit']) &
           (df['n'] > 1), 'new_unit'] = False
    # Produce new unit id
    df = df.sort_values(by=['syear', 'hid', 'head', 'main_unit',
                            'single_unit', 'couple_unit', 'new_unit', 'pnr'],
                        ascending=[True, True, False, False,
                                   False, False, False, True])
    df['nu'] = 1 * df['new_unit']
    df['new_unit_id'] = df.groupby(['syear', 'hid'])['nu'].apply(
                                        lambda x: x.cumsum())
    # Tax Unit ID: 'tu_id'
    # note: tu_id is nested within hid
    if df['new_unit_id'].max() < 10:
        df['tu_id'] = df['hid'] * 10 + df['new_unit_id']

    # Assign head of tax unit
    df = df.sort_values(by=['syear', 'hid', 'head', 'child'],
                        ascending=[True, True, False, False])
    df.loc[df.groupby(['syear', 'tu_id'])['pid'].head(1).index,
           'head_tu'] = True
    df['head_tu'] = df['head_tu'].fillna(False)

    # size of taxunit
    df = df.join(df.groupby(['syear', 'tu_id'])['counter'].sum(),
                 on=['syear', 'tu_id'], how='left', rsuffix='_tu')
    df = df.rename(columns={'counter_tu': 'hhsize_tu'})
    # Produce Child Age Aggregates
    # There are various ones because of different benefits check for different
    # kids age brackets.
    df.sort_values(by=['syear', 'hid', 'age'], ascending=[True, True, False])

    ch_ages = {'0_1':  pd.eval('df.child and df.age <= 1'),
               '1_2':  pd.eval('df.child and df.age >= 1 and df.age<= 2'),
               '2':     pd.eval('df.child and df.age<3'),
               '2_3':  pd.eval('df.child and df.age >= 2 and df.age<= 3'),
               '3_6':   pd.eval('df.child and df.age >= 3 and df.age<= 6'),
               '6':     pd.eval('df.child and df.age <= 6'),
               '7_16':  pd.eval('df.child and df.age >= 7 and df.age<= 16'),
               '7_11':  pd.eval('df.child and df.age >= 7 and df.age<= 11'),
               '7_13':  pd.eval('df.child and df.age >= 7 and df.age<= 13'),
               '11':     pd.eval('df.child and df.age <= 11'),
               '12_15':  pd.eval('df.child and df.age >= 12 and df.age<= 15'),
               '14_17': pd.eval('df.child and df.age >= 14 and df.age<= 17'),
               '14_24': pd.eval('df.child and df.age >= 14 and df.age<= 24'),
               '14':     pd.eval('df.child and df.age <= 14'),
               '15':     pd.eval('df.child and df.age <= 15'),
               '18':    pd.eval('df.child and df.age < 18')}

    for id in ['hid', 'tu_id']:
        for c in ch_ages:
            df['temp'] = ch_ages[c]
            c = c + '_num'
            if id == 'tu_id':
                c = c + '_tu'
            df = df.join(df.groupby(['syear', id])['temp'].sum(),
                         on=['syear', id], how='left', rsuffix=c)
            df = df.rename(columns={'temp'+c: 'child'+c})
            df['child'+c] = df['child'+c].astype(int)
    
    df = df.join(df.groupby(['syear', 'tu_id'])['child'].sum(),
                 on=['syear', 'tu_id'], how='left', rsuffix='_num_tu')
    # If only person in Household, it's an adult.
    df = df.join(df.groupby(['syear', 'hid'])['counter'].first(),
                 on=['syear', 'hid'], rsuffix='_first')
    df.loc[(df['child_num_tu'] == df['hhsize_tu']) & 
           (df['counter_first'] == 1), 'child'] = False
    df = df.drop(columns=['counter_first', 'child_num_tu'], axis=1)
    # Recount children
    df = df.join(df.groupby(['syear', 'tu_id'])['child'].sum(),
                 on=['syear', 'tu_id'], how='left', rsuffix='_num_tu')
    df = df.join(df.groupby(['syear', 'hid'])['child'].sum(),
                 on=['syear', 'hid'], how='left', rsuffix='_num')
    # Get number of adults
    for ending in ['', '_tu']:
        df['adult_num'+ending] = df['hhsize'+ending] - df['child_num'+ending]
        print(pd.crosstab(df['child_num'+ending], df['adult_num'+ending]))
    # There are still households left for which the 'splitting' did not work
    print('Deleting incorrect Tax Units...' +
          str(df['counter'][df['adult_num_tu'] > 2].sum()) + ' persons.')
    df = df[df['adult_num_tu'] <= 2]
    # 'Correction factor': The share of people a tax unit accrues compared
    # to the 'SOEP' household. This is needed for assessing the needs for 
    # social benefits 
    df['hh_korr'] = df['hhsize_tu'] / df['hhsize']
    # check whether tax units are well defined
    # CONTROL OUTPUT
    # df[df['adult_num_tu'] > 2].to_excel(pd.ExcelWriter(data_path+'check_tax_units.xlsx'),sheet_name='py_out',columns=['syear','hid','pid','pnr','hhsize','head','main_unit','single_unit','couple_unit','new_unit','new_unit_id','nu','tu_id','age','female','child','stell','k_rel','k_pmum','partner_id','adult_num_tu'],na_rep='NaN',freeze_panes=(0,1))
    # Ever born kids? Matters for 'pflegeversicherung'
    df['haskids'] = (df['lb0285'] > 0) | (df['child_num_tu'] > 0)

    # Handicap Dummy
    df['handcap_dummy'] = df['handcap_degree'] > 50
    
    # Skill level
    sel_quali = [df['pgcasmin'].between(0, 2),
                 df['pgcasmin'].between(3, 6),
                 df['pgcasmin'].between(7, 9)]
    sel_isced = [df['pgisced11'].between(0, 2),
                 df['pgisced11'].between(3, 4),
                 df['pgisced11'].between(5, 8)]
    # sel_stib = [(df['pgstib'].between(520,529) or df['pgstib'].le(220) or df['pgstib'].equals(440)) and df['qualification'].equals(0),
    #            (df['pgstib'].between(230,439) or df['pgstib'].isin([510,530,610,620])) and df['qualification'] == 0,
    #            (df['pgstib'].between(540,559) or df['pgstib'].between(630,649)) and df['qualification'] == 0]
    val_quali = [3, 2, 1]
    df['qualification'] = np.select(sel_quali, val_quali)
    df['temp'] = np.select(sel_isced, val_quali)
    df.loc[df['qualification'] == 0, 'qualification'] = df['temp']
    
    df['unskilled'] = df['qualification'] == 3
    df['university'] = df['qualification'] == 1

    ######
    # Income from varoius sources
    ######
    print('Income Components...')
    df['transfers'] = df['i11106'] + df['i11107']
    df['alg_soep'] = df['plc0131']
    # Months worked the year before
    df['months'] = np.minimum(df[['months_ft',
                                  'months_pt',
                                  'months_mj']].sum(axis=1), 12)
    # Set months to 12 if there is labor income
    df.loc[(df['pglabgro'] > 0) & ((pd.isna(df['months'])) |
           (df['months'] == 0) |
           (df['months'] <= 0)), 'months'] = 12

    # Public and private pensions
    df['pensions_pub'] = df[['igrv1', 'igrv2', 'ismp1', 'ismp2',
                             'iciv1', 'iciv2', 'iwar1', 'iwar2',
                             'iagr1', 'iagr2', 'iguv1', 'iguv2']].sum(axis=1)
    df['pensions_priv'] = df[['ivbl1', 'ivbl2', 'icom1', 'icom2',
                              'iprv1', 'iprv2', 'ison1', 'ison2',
                              'irie1', 'irie2']].sum(axis=1)
    df['pensions'] = df[['pensions_pub', 'pensions_priv']].sum(axis=1)
    # correct implausible values for months of pensions
    df.loc[((df['months_pen'] == 0) | 
           (pd.isna(['months_pen']))) &
           (df['pensions'] > 0), 'months_pen'] = 12
    df.loc[(pd.isna(df['months_pen']))
           & (df['pensions'] == 0), 'months_pen'] = 0
    
    df['months_pen'] = df['months_pen'].fillna(0)
    df['m_pensions'] = np.select([df['months_pen'] > 0,
                                 df['months_pen'] == 0],
                                 [df['pensions'] / df['months_pen'], 0])

    # Private Transfers, e.g. alimony payments
    df['m_trans1'] = df[['ialim', 'iachm', 'ichsu',
                         'ispou', 'ielse']].sum(axis=1) / 12
    df['m_trans2'] = (df['head_tu'] * (df[['nursh', 'sphlp', 'hsup',
                                       'ssold', 'chsub']].sum(axis=1) / 12) * 
                      df['hh_korr'])
    df['m_transfers'] = df[['m_trans1', 'm_trans2']].sum(axis=1)
    df = df.drop(columns=['pensions_pub', 'pensions_priv', 
                          'm_trans1', 'm_trans2'])
    # Child income
    df['childinc'] = df['child'] * (df['pglabgro'] + (df['k_inco'] / 12))
    # the following income amounts are household sums
    # only give the head therefore
    # Capital Income
    df['m_kapinc'] = df['divdy']/12 * df['head']
    # Income from rents, net of operating cost
    df['m_vermiet'] = (np.maximum((df['renty'] - df['opery']), 0)/12 * 
                       df['head'])
    # Imputed rents. not interesting for tax-benefit rules, but important 
    # to get the right inequality measures
    df['m_imputedrent'] = (df['imp_rent']) / 12 * df['head']
    # df['m_imputedrent'] = (df['imp_rent'] - df['hlc0111'] + df['hlc0112']) /12 * df['head']
    # distribute these incomes among the tax units
    for inc in ['kapinc', 'vermiet', 'imputedrent']:
        df['m_'+inc+'_tu'] = df['m_'+inc] * df['hh_korr'] * df['head_tu']

    df['versbez'] = np.select([df['months_pen'] > 0, df['months_pen'] == 0],
                              [df[['iciv1', 'ivbl1',
                                   'iciv2', 'ivbl2']].sum(axis=1) /
                               df['months_pen'], 0])

    # Weekly hours of work
    # use actual hours worked if there is no overtime
    # or if overtime is not compensated.
    # otherwise, use agreed hours
    df['w_hours'] = np.select([(df['pguebstd'] == 0) | (df['plb0605'] == 0),
                              (df['pgtatzeit'] == 0) & (df['pgvebzeit'] > 0)],
                              [df['pgtatzeit'], df['pgvebzeit']])

    # Produce Hours Distribution by year and sex
#    for y in df['syear'].unique():
#        for f in [0,1]:
#            plt.clf()
#            plotdata = df[['w_hours','syear','female']].query('syear == @y & female == @f')
#            hours = np.array(plotdata['w_hours'])
#            plt.hist(hours,bins=13,range=(1,60))
#            plt.title('Hours Distribution, Year: '+ str(y)+ ', Female: ' +str(f))
#            plt.savefig(graph_path+'hrs_dist/'+str(y)+'_f'+str(f)+'.png')

    # Monthly Wage
    df['m_wage'] = 0
    df['m_self'] = 0
    df['othwage_ly'] = df[['i13ly','i14ly','ixmas', 'iholy',
                           'igray', 'iothy', 'itray']].sum(axis=1)
    df.loc[(df['othwage_ly'] > 0) & 
           ((pd.isna(df['months'])) | 
           (df['months'] == 0)), 'months'] = 12
    # Depending on status, either labor income or self-employment income
    # Important for income taxation and for labor supply estimation
    df.loc[(~df['selfemployed']) &
           (~df['pensioner']) &
           (~df['military']) &
           (~df['parentalleave']),
           'm_wage'] = df['pglabgro'] + np.maximum(
                                            df['othwage_ly']/df['months'], 0)
    df.loc[(df['selfemployed']) &
           (~df['pensioner']) &
           (~df['military']) &
           (~df['parentalleave']),
           'm_self'] = df['pglabgro'] + np.maximum(
                                            df['othwage_ly']/df['months'], 0)
    df['m_wage'] = df['m_wage'].fillna(0)

    # Correction: If there's no income, there are no hours.
    # This 'mistake' is less common than positive income with zero hours
    df.loc[(df['m_wage'] == 0) & (df['m_self'] == 0), 'w_hours'] = 0

    # Lagged wages. For UB calculation and Armutsgewöhnungszuschlag
    df = df.sort_values(by=['pid', 'syear'])
    for v in ['m_wage', 'months', 'months_ue']:
        df[v+'_l1'] = df[v].shift(1).fillna(0)

    for v in ['m_wage', 'months', 'wgeld', 'alg', 'months_ue']:
        df[v+'_l2'] = df[v+'_l1'].shift(2).fillna(0)
        if v in ['wgeld', 'alg']:
            df[v+'_m_l2'] = df[v+'_m_l1'].shift(2).fillna(0)

    # Hourly Wage
    df['h_wage'] = df['m_wage'] / (df['w_hours'] * 4.34)

    # Privat versichert
    df['pkv'] = df['ple0097'] == 2
    # TO DO: Heckman Imputation or comparable to assign non-workers 
    # an hourly wage

    print('Living costs...')
    # Housing costs
    for v in ['hgsize', 'hgrent', 'hgheat', 'hgcnstyrmax', 'hgcnstyrmin']:
        df[v] = df[v].replace([-8, -7, -6, -5, -4, -3, -2, -1, 0], np.nan)
    # Dummy for living on own property
    df['eigentum'] = df['hgowner'] == 1
    #df['heim'] = df['hgowner'] == 5
    # impute missing values for flat size
    df = df.join(df.groupby(['syear', 'bula', 'hhsize'])['hgsize'].mean(),
                 on=['syear', 'bula', 'hhsize'], how='left', rsuffix='_mean')
    df['wohnfl'] = np.select([pd.isna(df['hgsize']), ~pd.isna(df['hgsize'])],
                             [df['hgsize_mean'], df['hgsize']])
    # Construction Year. sometimes important for housing benefit
    df.loc[(~(pd.isna(df['hgcnstyrmax'])) & 
            (~pd.isna(df['hgcnstyrmin']))),
           'baujahr'] = (df['hgcnstyrmax'] + df['hgcnstyrmin'])/2
    sel_cnstyr = [df['baujahr'].between(1800, 1965),
                  (df['baujahr'].between(1966, 2000)) |
                  (pd.isna(df['baujahr'])), df['baujahr'].between(2001, 2020)]
    df['cnstyr'] = np.select(sel_cnstyr, [1, 2, 3])

    # Impute missing rents via estimation
    for var in ['rent', 'heat']:
        print('Imputing ' + var + '...')
        est = pd.concat([df[['hg'+var, 'eigentum']],
                         pd.get_dummies(df['cnstyr'],
                                        prefix='cns',
                                        drop_first=True),
                         pd.get_dummies(df['bula'],
                                        prefix='bl',
                                        drop_first=True),
                         pd.get_dummies(df['syear'],
                                        prefix='y',
                                        drop_first=True)], axis=1)
        sub = est[(~pd.isna(est['hg'+var]))
                  & (~est['eigentum'])]
        # OLS is defined in imports.py
        imp_rent = ols(sub['hg'+var],
                       sub.drop(columns=['hg'+var, 'eigentum']), show=True)
        # Predict Miete/Heizkosten for all missings + non-owners
        est.loc[(est['hg'+var].isna()) & (~est['eigentum']),
                'hg' + var] = imp_rent.predict(est.drop(
                                columns=['hg'+var, 'eigentum']))
        if var == 'rent':
            df['kaltmiete'] = est['hgrent'] * df['hh_korr']
        if var == 'heat':
            df['heizkost'] = est['hgheat'] * df['hh_korr']

    df.loc[df['hgheatinfo'] == 3, 'heizkost'] = 0
    df['heizkost'] = df['heizkost'].fillna(0)
    # Capital payments of owners
    df['kapdienst'] = (np.select([df['eigentum'], ~df['eigentum']],
                                 [df['zinszahl'] + 36/12 * df['wohnfl'], 0]) *
                       df['hh_korr'])
    df['miete'] = np.select([df['eigentum'], ~df['eigentum']],
                            [df['kapdienst'], df['kaltmiete']])

    # Household Types
    # Singles
    df.loc[(df['adult_num_tu'] == 1) & (df['child_num_tu'] == 0), 'hhtyp'] = 1
    # Single Parents    
    df.loc[(df['adult_num_tu'] == 1) & (df['child_num_tu'] > 0), 'hhtyp'] = 2
    # Couples
    df.loc[(df['adult_num_tu'] == 2) & (df['child_num_tu'] == 0), 'hhtyp'] = 3
    # Couples with kids
    df.loc[(df['adult_num_tu'] == 2) & (df['child_num_tu'] > 0), 'hhtyp'] = 4
    
    # Single Parents dummy
    df['alleinerz'] = (df['adult_num_tu'] == 1) & (df['child_num_tu'] > 0)

    # Commuting...
    #df['comm_freq'] = df['comm_freq'].fillna(0)
    #df['comm_dist'] = df['comm_dist'].fillna(0)
    # Some people commute within city, but report comm_freq == 0
    #df.loc[(df['comm_dist'] > 0) & (df['comm_freq'] == 0), 'comm_freq'] = 1

    # Some labels
    # Marital Status...Maybe rather rename and label?
    df['marstat_lb'] = df['marstat'].map({1: 'Married',
                                          2: 'Single',
                                          3: 'Widowed',
                                          4: 'Divorced',
                                          5: 'Separated'})
    df['quali_lb'] = df['qualification'].map({1: 'High-Skilled',
                                              2: 'Medium-Skilled',
                                              3: 'Unskilled'})
    # Dummy for joint taxation
    df['zveranl'] = (df['marstat'] == 1) & (df['adult_num_tu'] >= 2)
    

    print('Reduce Dataset...')
    # Get rid of missings:
    for v in ['m_wage', 'm_self', 'miete', 'w_hours']:
        df[v] = df[v].fillna(0)

    print("Pensions Calculations...")
    # Einige Berechnungen für die Rentenformel
    #    rent = df[['syear','m_wage','female','east','pweight','svbeit']][(df['m_wage'] > 100)]
    #
    #    # TO DO: Berechne gewichtetes Mittel
    #
    #    meanwages = rent.groupby(['syear'])['m_wage'].mean()
    #    # Beitragspflichtige Löhne
    #    meanwages_beit = rent[rent['svbeit'] > 0].groupby(['syear']).mean()
    #    # Rentnerquotient
    #    rentenvol = df.groupby(['syear'])['m_pensions'].sum()
    #    beitragsvol = df.groupby(['syear'])['rvbeit'].sum()
    #    # TO DO: Save them somewhere
    #
    #    rentenstuff = pd.DataFrame(columns=[meanwages,meanwages_beit,rentenvol,beitragsvol])

    # Drop unnecesary stuff
    dropvars = ['d11102ll', 'l11102', 'x11103', 'd11101', 'd11107',
                'e11101', 'e11102', 'e11103', 'e11105', 'e11106',
                'i11101', 'i11102',  'i11106', 'i11107', 'i11111',
                'i11112', 'i11113', 'i11114', 'w11101', 'w11103',
                'l11101', 'i11205', 'ijob1', 'ijob2', 'ioldy', 'iwidy',
                'iunby', 'iunay', 'isuby', 'ieret', 'imaty', 'istuy',
                'imilt', 'ialim', 'ielse', 'icomp', 'iprvp', 'i13ly',
                'i14ly', 'ixmas', 'iholy', 'igray', 'iothy', 'igrv1',
                'igrv2', 'renty', 'opery', 'chspt', 'house', 'nursh',
                'subst', 'sphlp', 'hsup', 'ismp1', 'iciv1', 'iwar1',
                'iagr1', 'iguv1', 'ivbl1', 'icom1', 'iprv1', 'ison1',
                'ismp2', 'iciv2', 'iwar2', 'iagr2', 'iguv2', 'ivbl2',
                'icom2', 'ison2', 'iprv2', 'ssold', 'lossr', 'lossc',
                'itray', 'adchb', 'iachm', 'chsub', 'ichsu', 'ispou',
                'irie1', 'irie2', 'kidy', 'iwith', 'pgoeffd', 'pgpartnr',
                'pgnation', 'pgpsbil', 'pgerwzeit', 'pgtatzeit', 'pgvebzeit',
                'pguebstd', 'pglfs', 'pgnace', 'pgisced97', 'pgcasmin',
                'pgstib', 'pglabgro', 'pgisco08', 'pgisced11', 'plb0022',
                'plb0063', 'hgowner', 'hgsize', 'hgrent', 'hgcnstyrmax',
                'hgcnstyrmin', 'hgheat', 'hgheatinfo', 'pnr_max', 'pnr_mis',
                'pnr_mis_n', 'age_mis', 'age_mis_sum', 'h', 'nu', 'temp',
                'plb0186', 'plb0295', 'plb0423',
                'plb0424', 'plb0586', 'plb0605', 'plc0446']
    drop(df, dropvars)
    # Output of Summary Statistics
    summaries = df.describe()
    summaries.to_excel(pd.ExcelWriter(data_path+'sum_data_out.xlsx'),
                       sheet_name='py_out')
    