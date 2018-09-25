# -*- coding: utf-8 -*-
"""
Created on Fri Jun 15 08:48:33 2018

@author: iza6354
"""
from imports import *
from settings import get_settings
import statsmodels.api as sm

def call_heckman(df, plot=False):
    ''' creates variables for the Heckman estimation
        calls the estimation
        optional: plots predicted against actual wages
    '''
    # First, create variables
    df['work_dummy'] = df['w_hours'] > 0
    df['missing_wage'] = (df['h_wage'] == 0) | (df['h_wage'].isna())
    df['age2'] = (df['age'] ** 2) / 1000
    df['age3'] = (df['age'] ** 3) / 1000
    df['married'] = df['marstat'] == 1
    df['ln_wage'] = np.select([df['h_wage'] > 0, df['h_wage'] == 0],
                              [np.log(df['h_wage']), np.nan])
    df['exper'] = df['expft'] + 0.5 * df['exppt']
    for var in ['exper', 'expue', 'tenure']:
        df[var] = df[var].fillna(0)
        df[var+'2'] = (df[var] ** 2) / 100

    df['heck_wage'] = np.nan

    for yr in df['syear'].unique():
        print(str(yr))
        for f in [0, 1]:
            print('Female: ' + str(f))
            # find out extreme values of hourly wage
            p1p99 = df['h_wage'][(df['h_wage'] > 0) &
                                 (df['syear'] == yr) &
                                 (df['female'] == f)].describe(
                                                  percentiles=[0.01, 0.99]
                                                               )[['1%', '99%']]
            # define subsample
            sub = ((df['syear'] == yr) &
                   (df['female'] == f) &
                   (~df['child']) &
                   (df['age'].between(15, 70))
                   )

            # define selection variables
            select_vars = ['age',
                           'age2',
                           'age3',
                           'child2_num',
                           'child3_6_num',
                           'child7_16_num',
                           'm_kapinc_tu',
                           'm_vermiet_tu',
                           'unskilled',
                           'university',
                           'foreigner',
                           'east',
                           'married',
                           'couple',
                           'handcap_dummy',
                           'welfare'
                           ]
            # define variables for wage equation
            wage_vars = ['exper',
                         'exper2',
                         'expue',
                         'expue2',
                         'tenure',
                         'tenure2',
                         'unskilled',
                         'university',
                         'foreigner'
                         ]

            # create estimation sample. sex, year and labor force
            heck = df[sub]

            # obtain heckman wages
            heck['heck_wage'] = heckman(
                               heck['ln_wage'][~heck['ln_wage'].isna()],
                               heck[wage_vars][~heck['ln_wage'].isna()].astype(float),
                               heck[wage_vars].astype(float),
                               heck['work_dummy'],
                               heck[select_vars].astype(float),
                                        )
            assert(~heck['heck_wage'].isna().all())
            # assign the predicted wage in the main DataFrame
            df.loc[(df['syear'] == yr) &
                   (df['female'] == f) &
                   (~df['child']) &
                   (df['age'].between(15, 70)),
                   'heck_wage'] = heck['heck_wage']

    if plot:
        for yr in df['syear'].unique():
            for f in [0, 1]:
                plt.clf()
                fig = plt.figure(figsize=(8, 5))
                ax_heck = df['heck_wage'][(df['syear'] == yr) &
                                          (df['female'] == f) &
                                          (df['heck_wage'].between(5, 100))
                                          ].plot.kde(label='Heckman Wage')
                ax_wage = df['h_wage'][(df['syear'] == yr) &
                                       (df['female'] == f) &
                                       (df['h_wage'].between(5, 100))
                                       ].plot.kde(label='Observed Wage')
                ax_heck.set_xlim(0, 100)
                ax_heck.legend(loc=0,
                               ncol=1,
                               fontsize=14,
                               frameon=True)

                plt.savefig(get_settings()['GRAPH_PATH'] +
                            'wageplots/wageplots_y' + str(yr) +
                            '_f' + str(f) + '.png')

    return df['heck_wage']


def heckman(wage_y, wage_X, wage_X2, select_y, select_X):
    ''' Carries out wage estimation with heckman selection model
        - wage_y: log wage
        - wage_X: determinants of wage workers
        - wage_X2: determinants of wages, for the full sample
        - select_y: dummy of whether or not in work
        - select_X: Determinants of Labor Force Participation

        Note that this is a 'pseudo' heckman estimation, as the standard errors are wrong.
        It'll do however for our purposes.
    '''
    # print(str(len(wage_y)))
    # print(str(len(select_y)))
    # 1st stage: Probit estimation
    select_X = sm.add_constant(select_X)
    probit_model = sm.Probit(np.asarray(select_y),
                             np.asarray(select_X)
                             )
    probit_est = probit_model.fit()
#    print(probit_est.summary())
    # Predict probability
    p_work = probit_est.predict(select_X)
    # linear probability
    p_work_linear = probit_est.predict(select_X, linear=True)
    # calculate inverse mills ratio
    wage_X['imr'] = scipy.stats.norm.pdf(p_work_linear) / p_work
    # 2nd stage: (Log) wage estimation, corrected with inverse mills ratio
    wage_X = sm.add_constant(wage_X)

    # print(wage_y.head())
    # print(wage_X.head())
    ols_model = sm.OLS(wage_y, wage_X)
    ols_est = ols_model.fit()
    # What's left is to predict log wages for the full sample (the 'select' sample)
    wage_X2['imr'] = scipy.stats.norm.pdf(p_work_linear) / p_work
    wage_X2 = sm.add_constant(wage_X2)

    se_reg = ols_est.ssr / (ols_est.nobs - 2)
    heck_wage = np.exp(ols_est.predict(exog=wage_X2)) * np.exp((se_reg**2)/2)

    return heck_wage

def preparedata(df):
    '''Prepare Data
    Prepares SOEP for input to tax transfer calculation
    '''
    print(df['syear'].value_counts())
    # Counter
    df['counter'] = 1

    # Deal with Missing Person Identifier and add an artificial one
    df['kinderdaten'] = ~df['k_rel'].isna()
    df = df.sort_values(by=['syear', 'hid', 'pnr'])
    df = df.join(df.groupby(['syear', 'hid'])['pnr'].max(),
                 on=['syear', 'hid'], how='left', rsuffix='_max')
    df['pnr_mis'] = df['pnr'].isna() & ~df['kinderdaten']
    df['pnr_mis_n'] = df.groupby(['syear', 'hid'])['pnr_mis'].cumsum()
    df.loc[df['pnr_mis'], 'pnr'] = df['pnr_max'] + df['pnr_mis_n']

    # Demographics
    # Age
    df['age'] = df['d11101'][df['d11101'] >= 0]

    # drop HH with missing age information
    df['age_mis'] = pd.isna(df['age'])
    df = df.join(df.groupby(['syear', 'hid'])['age_mis'].sum(),
                 on=['syear', 'hid'], how='left', rsuffix='_sum')
    df = df[df['age_mis_sum'] == 0]

    # Birth Year
    df['byear'] = df['syear'] - df['age']
    # Female dummy
    df['female'] = (df['d11102ll'] == 2)
    # Foreigner Dummy
    df['foreigner'] = df['pgnation'] > 1

    df['byear'] = df['byear'].astype(int)
    df['age'] = df['age'].astype(int)
    # Working Age Dummy...currently not used
    # df['work_age'] = df['age'].between(15, 64)

    # A couple of useful dummy variables
    df['pensioner'] = ((df['pgstib'] == 13) | (df['age'] > 64))
    df['ineducation'] = ((((df['pgstib'] > 100) & (df['pgstib'] < 200)) |
                         (df['pgstib'] == 11)) |
                         (df['ks_ats_r'] == 1) |
                         (df['age'] < 18))

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
    # do the same with the generation older than the head
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
    df.loc[(~df['main_unit']) &
           (~df['young_single_unit']) &
           (~df['young_couple_unit']) &
           (~df['old_couple_unit']) &
           (~df['old_single_unit']), 'old_single_unit'] = True
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

    # size of tax unit
    df = df.join(df.groupby(['syear', 'tu_id'])['counter'].sum(),
                 on=['syear', 'tu_id'], how='left', rsuffix='_tu')
    df = df.rename(columns={'counter_tu': 'hhsize_tu'})
    # Produce Child Age Aggregates
    # There are various ones because of different benefits check for different
    # kids age brackets.
    df.sort_values(by=['syear', 'hid', 'age'], ascending=[True, True, False])

    ch_ages = {'0_1': pd.eval('df.child and df.age <= 1'),
               '1_2': pd.eval('df.child and df.age >= 1 and df.age<= 2'),
               '2': pd.eval('df.child and df.age<3'),
               '2_3': pd.eval('df.child and df.age >= 2 and df.age<= 3'),
               '3_6': pd.eval('df.child and df.age >= 3 and df.age<= 6'),
               '6': pd.eval('df.child and df.age <= 6'),
               '7_16': pd.eval('df.child and df.age >= 7 and df.age<= 16'),
               '7_11': pd.eval('df.child and df.age >= 7 and df.age<= 11'),
               '7_13': pd.eval('df.child and df.age >= 7 and df.age<= 13'),
               '11': pd.eval('df.child and df.age <= 11'),
               '12_15': pd.eval('df.child and df.age >= 12 and df.age<= 15'),
               '14_17': pd.eval('df.child and df.age >= 14 and df.age<= 17'),
               '14_24': pd.eval('df.child and df.age >= 14 and df.age<= 24'),
               '14': pd.eval('df.child and df.age <= 14'),
               '15': pd.eval('df.child and df.age <= 15'),
               '18': pd.eval('df.child and df.age < 18')}
    # Sometimes you need the number of kids per HH (e.g. for Unemployment Benefit)
    # Sometimes you need them per tax unit (e.g. child benefit, taxes).
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
    # If the only person in Household, it's an adult.
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
    # There are still few households left for which the 'splitting' did not work
    print('Deleting incorrect Tax Units...' +
          str(df['counter'][df['adult_num_tu'] > 2].sum()) + ' persons.')
    df = df[df['adult_num_tu'] <= 2]
    # 'Correction factor': The share of people a tax unit accrues compared
    # to the 'SOEP' household. This is needed for assessing the needs for
    # social benefits. always between 0 and 1
    df['hh_korr'] = df['hhsize_tu'] / df['hhsize']
    # Ever born kids? Matters for long-term care contributions
    df['haskids'] = (df['lb0285'] > 0) | (df['child_num_tu'] > 0)

    # Handicap Dummy
    df['handcap_dummy'] = df['handcap_degree'] > 50

    # Skill level. sometimes you have casmin classification, sometimes isced. Take what you get
    sel_quali = [df['pgcasmin'].between(0, 2),
                 df['pgcasmin'].between(3, 6),
                 df['pgcasmin'].between(7, 9)]
    sel_isced = [df['pgisced11'].between(0, 2),
                 df['pgisced11'].between(3, 4),
                 df['pgisced11'].between(5, 8)]

    val_quali = [3, 2, 1]
    df['qualification'] = np.select(sel_quali, val_quali)
    df['temp'] = np.select(sel_isced, val_quali)
    df.loc[df['qualification'] == 0, 'qualification'] = df['temp']

    df['unskilled'] = df['qualification'] == 3
    df['university'] = df['qualification'] == 1

    ###########
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
    # Couple Dummy
    df['couple'] = df['hhtyp'].isin([3, 4])

    ######
    # Income from various sources
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
    df['k_inco'] = df['k_inco'].fillna(0)
    df['childinc'] = df['child'] * (df['pglabgro'] + (df['k_inco'] / 12))
    # the following income amounts are household sums
    # only apply it to  the head therefore
    # Capital Income
    df['m_kapinc'] = df['divdy']/12 * df['head']
    # Income from rents, net of operating cost
    df['m_vermiet'] = (np.maximum((df['renty'] - df['opery']), 0)/12 *
                       df['head'])
    # Imputed rents. not interesting for tax-benefit rules, but important
    # to get the right inequality measures (if we care about them)
    df['m_imputedrent'] = (df['imp_rent']) / 12 * df['head']
    # distribute these incomes among the tax units (among the tax unit heads, to be precise)
    for inc in ['kapinc', 'vermiet', 'imputedrent']:
        df['m_'+inc+'_tu'] = df['m_'+inc] * df['hh_korr'] * df['head_tu']

    df['versbez'] = np.select([df['months_pen'] > 0, df['months_pen'] == 0],
                              [df[['iciv1', 'ivbl1',
                                   'iciv2', 'ivbl2']].sum(axis=1) /
                               df['months_pen'], 0])

    # Dummy for welfare recipient
    df['welfare'] = np.select([df['syear'] <= 2004, df['syear'] >= 2005],
                              [(df['D_sozh_current'] == 1) |
                               (df['D_wg_current'] == 1) |
                               (df['D_alg_current'] == 1),
                               (df['D_sozh_current'] == 1) |
                               (df['D_wg_current'] == 1) |
                               (df['D_kiz_current'] == 1) |
                               (df['D_alg2_current'] == 1)
                               ]
                              )

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
    df['othwage_ly'] = df[['i13ly', 'i14ly', 'ixmas', 'iholy',
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
           'm_wage'] = df['pglabgro'] + np.maximum(0,
                                                   df['othwage_ly']/df['months'])
    df.loc[(df['selfemployed']) &
           (~df['pensioner']) &
           (~df['military']) &
           (~df['parentalleave']),
           'm_self'] = df['pglabgro'] + np.maximum(0,
                                                   df['othwage_ly']/df['months'])
    # Division by zero months might lead to infinity values for wages
    # df['m_wage'] = df[np.isinf(df['m_wage'])] = 0
    # df['m_self'] = df[np.isinf(df['m_self'])] = 0
    df['m_wage'] = df['m_wage'].fillna(0)
    df['m_self'] = df['m_self'].fillna(0)
    # Correction: If there's no income, there are no hours.
    # This 'mistake' is less common than positive income with zero hours
    df.loc[(df['m_wage'] == 0) & (df['m_self'] == 0), 'w_hours'] = 0

    # Lagged wages. For UB calculation and Armutsgewöhnungszuschlag
    df = df.sort_values(by=['pid', 'syear'])
    for v in ['m_wage', 'months', 'months_ue']:
        df[v+'_l1'] = df[v].shift(1).fillna(0)

    for v in ['m_wage', 'months', 'wgeld', 'alg', 'months_ue']:
        df[v+'_l2'] = df[v+'_l1'].shift(1).fillna(0)
        if v in ['wgeld', 'alg']:
            df[v+'_m_l2'] = df[v+'_m_l1'].shift(1).fillna(0)

    # Hourly Wage
    df['h_wage'] = np.select([df['w_hours'] == 0, df['w_hours'] > 0],
                             [0, df['m_wage'] / (df['w_hours'] * 4.34)]
                             )
    # df.loc[df['h_wage'] > 0, 'h_wage'] = np.minimum(3, df['h_wage'])

    #########################################
    # Heckman Imputation to assign non-workers an h_wage
    print('Heckman Imputation...')
    df['h_wage_pred'] = call_heckman(df, True)
    # TODO: assign predicted wages to non-workers.

    # Dummy for private health insurance
    df['pkv'] = df['ple0097'] == 2

    print('Living costs...')
    # Housing costs
    for v in ['hgsize', 'hgrent', 'hgheat', 'hgcnstyrmax', 'hgcnstyrmin']:
        df[v] = df[v].replace([-8, -7, -6, -5, -4, -3, -2, -1, 0], np.nan)
    # Dummy for living on own property
    df['eigentum'] = df['hgowner'] == 1
    # df['heim'] = df['hgowner'] == 5
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
    # we need some sensible values for rents in order to determine a proper
    # benefit claim.
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

        imp_rent = sm.OLS(sub['hg'+var],
                          sub.drop(columns=['hg'+var, 'eigentum']).astype(float)).fit()
        # Predict Miete/Heizkosten for all missings + non-owners
        est.loc[(est['hg'+var].isna())
                & (~est['eigentum']),
                'hg' + var] = imp_rent.predict(est.drop(
                                               columns=['hg'+var,
                                                        'eigentum'])
                                               )
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


    # Commuting frequency and distance... do not use
    # df['comm_freq'] = df['comm_freq'].fillna(0)
    # df['comm_dist'] = df['comm_dist'].fillna(0)
    # Some people commute within city, but report comm_freq == 0
    # df.loc[(df['comm_dist'] > 0) & (df['comm_freq'] == 0), 'comm_freq'] = 1

    # Dummy for joint taxation
    df['zveranl'] = (df['marstat'] == 1) & (df['adult_num_tu'] >= 2)

    print('Reduce Dataset...')
    # Get rid of missings:
    for v in ['m_wage', 'm_self', 'miete', 'w_hours']:
        df[v] = df[v].fillna(0)

    # Drop unnecesary stuff
    dropvars = ['d11102ll', 'l11102', 'x11103', 'd11101', 'd11107',
                'e11101', 'e11102', 'e11103', 'e11105', 'e11106',
                'i11101', 'i11102', 'i11106', 'i11107', 'i11111',
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
                'pgnation', 'pgpsbil', 'pgtatzeit', 'pgvebzeit',
                'pguebstd', 'pglfs', 'pgnace', 'pgisced97', 'pgcasmin',
                'pgstib', 'pglabgro', 'pgisco08', 'pgisced11', 'plb0022',
                'plb0063', 'hgowner', 'hgsize', 'hgrent', 'hgcnstyrmax',
                'hgcnstyrmin', 'hgheat', 'hgheatinfo', 'pnr_max', 'pnr_mis',
                'pnr_mis_n', 'age_mis', 'age_mis_sum', 'h', 'nu', 'temp',
                'plb0186', 'plb0295', 'plb0423',
                'plb0424', 'plb0586', 'plb0605', 'plc0446',
                'ks_ats_r', 'hlc0111', 'hlc0112', 'tax']

    df = df.drop(columns=dropvars, axis=1)
    return df
