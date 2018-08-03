# -*- coding: utf-8 -*-
"""
TAX TRANSFER SIMULATION

Eric Sommer, 2018
"""
from imports import *
from termcolor import colored, cprint

import pandas as pd
import numpy as np
import math
import sys


def taxtransfer(df, ref, datayear, taxyear, tb, hyporun=False):
    """ German Tax-Transfer System
        df:     Input Data Frame
        ref:    Name of Reform
        datayear: year of SOEP wave
        taxyear:  year of reform baseline
        tb:     dictionary with tax-benefit parameters
        hyporun: indicator for hypothetical household input (defult: use real SOEP data)
    """
    # 1. Uprating if necessary
    #if hyporun is False:
        #df = uprate(df, datayear, settings['taxyear'], settings['MAIN_PATH'])

    # 2. Social Security Payments
    ssc_out = ssc(df[['pid', 'hid', 'east', 'm_wage', 'selfemployed',
                      'm_self', 'm_pensions', 'age', 'haskids', 'pkv']],
                  tb, taxyear, ref)
    df = pd.merge(df, ssc_out,  how='inner', validate='1:1')
    # 3. Unemployment benefit

    df = ui(df, tb, taxyear, ref)
    # 4. Pensions
    # pens_out = pensions(df, tb, taxyear, ref):

    # 5. Income Tax
    taxvars = ['pid', 'hid', 'female', 'head_tu', 'tu_id', 'east', 'm_wage', 'selfemployed',
               'm_self', 'm_pensions', 'age', 'pkv', 'zveranl', 'child', 'child_num',
               'renteneintritt', 'w_hours', 'm_kapinc', 'm_vermiet', 'm_imputedrent',
               'marstat', 'handcap_dummy', 'handcap_degree', 'rvbeit', 'gkvbeit',
               'pvbeit', 'avbeit', 'adult_num_tu', 'child_num_tu', 'alleinerz', 'ineducation'
               ]
    # 5.1 Calculate Taxable income (zve = zu versteuerndes Einkommen)
    zve_out = zve(df[taxvars], tb, taxyear, ref)

    # 5.2 Apply Tax Schedule
    sched_out = tax_sched(zve_out, tb, taxyear, ref)
    # 5.3 Child benefit (Kindergeld). Yes, this belongs to Income Tax

    kg_out = kindergeld(sched_out, tb, taxyear, ref)
    # 5.4 Günstigerprüfung to obtain final income tax due.
    test_out = tax_test(kg_out, tb, taxyear, ref)

    # 5.5 Solidarity Surcharge
    soli_out = soli(test_out, tb, taxyear, ref)


    # Merge new variables to old data frame
    df = pd.merge(df, soli_out,  how='inner', validate='1:1')

    # 6. SOCIAL TRANSFERS / BENEFITS
    ben_vars = ['pid', 'hid', 'tu_id', 'head', 'head_tu', 'female', 'miete', 'heizkost',
                'hh_korr', 'incometax_tu', 'rvbeit_tu', 'gkvbeit_tu', 'gross_e1', 'gross_e4',
                'gross_e5', 'gross_e6', 'm_alg1', 'm_transfers', 'ertragsanteil', 'm_pensions',
                'm_wage', 'child', 'child_num', 'child_num_tu', 'alleinerz', 'hhsize', 'hhsize_tu',
                'child6_num', 'child15_num', 'child14_24_num', 'child7_13_num', 'child2_num',
                'child3_6_num', 'divdy', 'age', 'child18_num', 'adult_num', 'm_self', 'm_vermiet',
                'm_kapinc', 'm_alg1', 'incometax', 'svbeit', 'soli', 'kindergeld',
                'kindergeld_hh', 'hhtyp', ]
    # 6.1. Wohngeld, Housing Benefit
    wg_out = wg(df, tb, taxyear, ref)

    # 6.2 ALG2, Basic Unemployment Benefit
    alg2_out = alg2(wg_out, tb, taxyear, ref)

    # 6.3. Kinderzuschlag, Additional Child Benefit
    kiz_out = kiz(alg2_out, tb, taxyear, ref)
    df = kiz_out.copy()

    # 7. Drop unnecessary variables
    df = dropstuff(df)

    # 8. Finally, calculate disposable income
    # To be updated!
    df['dpi_ind'] = (df[['m_wage', 'm_kapinc', 'm_self', 'm_vermiet',
                         'm_imputedrent', 'm_pensions', 'm_transfers',
                         'kindergeld', 'wohngeld']].sum(axis=1)
                     - df[['incometax', 'soli', 'abgst', 'gkvbeit', 'rvbeit',
                           'pvbeit', 'avbeit']].sum(axis=1))
    df = df.join(df.groupby(['hid'])[('dpi_ind')].sum(),
                 on=['hid'], how='left', rsuffix='_temp')
    # Finally, add ALG2 which is calculated on HH level
    df['dpi'] = np.maximum(df['dpi_ind_temp'] + df['m_alg2'], 0)

    return df


def uprate(df, dy, ty, path):
    ''' Uprating monetary values to account for difference between
        data year and simulation year.
    '''
    # define all monetary variables
    # get uprate matrix ,as np.array
    upr = pd.read_excel(path+'/data/params/uprate_cpi.xls',
                        index_col='ausgang')
    factor = upr.loc[dy]['y'+str(ty)]
    print('Uprating monetary variables from year ' + str(dy) +
          ' to ' + str(ty) + ' with factor ' + str(factor))
    money_vars = [
                'k_inco', 'm_pensions', 'm_transfers', 'childinc',
                'm_kapinc', 'm_vermiet', 'm_imputedrent',
                'versbez', 'm_wage', 'othwage_ly', 'h_wage',
                'kaltmiete', 'heizkost', 'kapdienst', 'miete'
                ]

    for v in money_vars:
        df[v] = factor * df[v]

    return df


def pensions(df, tb, yr, ref):
    ''' Old-Age Pensions
        TO DO: how to account for increasing pension claims
    '''
    cprint('Pensions', 'red', 'on_white')
    westost = [df['east'] is False, df['east']]
    year = str(yr)
    # lagged values needed for Rentenformel
    tb_1 = get_params()[str(yr - 1)]
    tb_2 = get_params()[str(yr - 2)]
    tb_3 = get_params()[str(yr - 3)]
    # individuelle monatl. Altersrente (Rentenartfaktor = 1):
    # R = EP * ZF * Rw
    m_wage_west = df['m_wage'][(df['m_wage'] > tb['mini_grenzew'])
                               & (~df['east'])].mean()
    m_wage_east = df['m_wage'][(df['m_wage'] > tb['mini_grenzeo'])
                               & (df['east'])].mean()
    df['EP'] = np.select(
            westost, [np.minimum(df['m_wage'], tb['rvmaxekw'])/m_wage_west,
                      np.minimum(df['m_wage'], tb['rvmaxeko'])/m_wage_east]
                )

    # rw_east = rentenwert['rw_east'][rentenwert['yr'] == yr]
    # rw_west = rentenwert['rw_west'][rentenwert['yr'] == yr]
    #################################
    # Neuer Rentenwert für yr > 2018:
    # Rentenformel: https://de.wikipedia.org/wiki/Rentenanpassungsformel
    """
    # Altersvorsorgeanteil = 4 nach 2012
    ava = 4
    lohnkomponente = (meanwages[str(yr-1)] / (meanwages[str(yr-2)] *
                      (meanwages[str(yr - 2)] / meanwages[str(yr - 3)]) /
                      (meanwages_beit[str(yr - 2)] /
                       meanwages_beit[str(yr - 3)])))

    riesterfaktor = ((100 - ava - (tb_1['grvbs'] * 200))
                     / (100 - ava - (tb_1['grvbs'] * 200)))
    # nachhfaktor   =
    rentenwert = tb['rw_west'] * lohnkomponente
    """

def ssc(df, tb, yr, ref):
    ''' Calculates Social Security Payments
      4 branches of social insurances:
            - health
            - old-age pensions
            - unemployment
            - care
        There is a fixed rate on earnings up to a threshold,
        after which no rates are charged.
        'Minijobs' below 450€ are free of contributions
        For 'Midijobs' between 450€ and 850€, the rate increases
        smoothly until the regular one is reached
    '''
    cprint('Social Security Payments...', 'red', 'on_white')
    # a couple of definitions
    ssc = df.copy()
    westost = [~df['east'], df['east']]
    ssc['bezgr'] = np.select(westost,
                             [tb['bezgr_o'], tb['bezgr_w']])
    ssc['kinderlos'] = ((~ssc['haskids']) & (ssc['age'] > 22))
    ssc['belowmini'] = np.select(westost,
                                 [ssc['m_wage'] < tb['mini_grenzew'],
                                  ssc['m_wage'] < tb['mini_grenzeo']]) == 1
    ssc['above_thresh_kv'] = np.select(westost,
                                       [ssc['m_wage'] > tb['kvmaxekw'],
                                        ssc['m_wage'] > tb['kvmaxeko']]) == 1
    ssc['above_thresh_rv'] = np.select(westost,
                                       [ssc['m_wage'] > tb['rvmaxekw'],
                                        ssc['m_wage'] > tb['rvmaxeko']]) == 1

    # Standard rates under consideration of thresholds
    # need to differentiate between East and West Germany
    # Old-Age Pension Insurance / Rentenversicherung
    ssc['rvbeit'] = (tb['grvbs'] *
                     np.minimum(ssc['m_wage'],
                                  np.select(westost,
                                            [tb['rvmaxekw'],  tb['rvmaxeko']]
                                            )))
    '''ssc['ag_rvbeit'] = (tb['grvbs']
                        * np.minimum(ssc['m_wage'],
                                     np.select(westost,
                                               [tb['rvmaxekw'],
                                                tb['rvmaxeko']])))
    '''
    # Unemployment Insurance / Arbeitslosenversicherung
    ssc['avbeit'] = (tb['alvbs'] *
                     np.minimum(ssc['m_wage'],
                                  np.select(westost,
                                            [tb['rvmaxekw'],
                                             tb['rvmaxeko']])))
    '''
    ssc['ag_avbeit'] = (tb['alvbs']
                        * np.minimum(ssc['m_wage'],
                                     np.select(westost,
                                               [tb['rvmaxekw'],
                                                tb['rvmaxeko']])))
    '''
    # Health Insurance for Employees (GKV)
    ssc['gkvbeit'] = (tb['gkvbs_an'] *
                      np.minimum(ssc['m_wage'],
                                   np.select(westost,
                                             [tb['kvmaxekw'],
                                              tb['kvmaxeko']])))
    '''
    ssc['ag_gkvbeit'] = (tb['gkvbs_ag']
                         * np.minimum(ssc['m_wage'],
                                      np.select(westost,
                                                [tb['kvmaxekw'],
                                                 tb['kvmaxeko']])))
    '''
    # Care Insurance / Pflegeversicherung
    ssc['pvbeit'] = (tb['gpvbs'] *
                     np.minimum(ssc['m_wage'],
                                  np.select(westost,
                                            [tb['kvmaxekw'],
                                             tb['kvmaxeko']])))
    # If you are above 23 and without kids, you have to pay a higher rate
    ssc.loc[ssc['kinderlos'],
            'pvbeit'] = ((tb['gpvbs'] + tb['gpvbs_kind']) *
                         np.minimum(ssc['m_wage'],
                                      np.select(westost,
                                                [tb['kvmaxekw'],
                                                 tb['kvmaxeko']])))
    '''
    ssc['ag_pvbeit'] = (tb['gpvbs']
                        * np.minimum(ssc['m_wage'],
                                     np.select(westost,
                                               [tb['kvmaxekw'],
                                                tb['kvmaxeko']])))
    '''
    # Gleitzone / Midi-Jobs

    if yr >= 2003:
        # For midijobs, the rate is not calculated on the wage,
        # but on the 'bemessungsentgelt'
        # Contributions are usually shared equally by employee and
        # employer. We are not interested in employer's contributions,
        # but we need them here as an intermediate step
        AN_anteil = tb['grvbs'] + tb['gpvbs'] + tb['alvbs'] + tb['gkvbs_an']
        AG_anteil = tb['grvbs'] + tb['gpvbs'] + tb['alvbs'] + tb['gkvbs_ag']
        DBSV = AN_anteil + AG_anteil
        pauschmini = tb['mini_ag_gkv'] + tb['mini_ag_grv'] + tb['stpag']
        F = round(pauschmini / DBSV, 4)
        # always needs to differentiate between east and west,
        # was relevant in earlier years
        bemes = [
                F * tb['mini_grenzew']
                + ((tb['midi_grenze'] / (tb['midi_grenze']
                    - tb['mini_grenzew']))
                   - (tb['mini_grenzew'] /
                   ((tb['midi_grenze'] - tb['mini_grenzew']))*F))
                * (ssc['m_wage'] - tb['mini_grenzew']),
                F * tb['mini_grenzeo']
                + ((tb['midi_grenze']/(tb['midi_grenze'] - tb['mini_grenzeo']))
                    - (tb['mini_grenzeo'] /
                       ((tb['midi_grenze']-tb['mini_grenzeo']))*F))
                * (ssc['m_wage'] - tb['mini_grenzeo'])
                ]
        ssc['bemessungsentgelt'] = np.select(westost, bemes)
        # This checks whether wage is in the relevant range
        ssc['in_gleitzone'] = ssc['m_wage'].between(
                            np.select(westost,
                                      [tb['mini_grenzew'],
                                       tb['mini_grenzeo']]),
                                      tb['midi_grenze'])

        # Again, all branches of social insurance
        # First total amount, then employer, then employee

        # Old-Age Pensions
        ssc['gb_rv'] = 2 * tb['grvbs'] * ssc['bemessungsentgelt']
        ssc.loc[ssc['in_gleitzone'], 'ag_rvbeit'] = tb['grvbs'] * ssc['m_wage']
        ssc.loc[ssc['in_gleitzone'],
                'rvbeit'] = ssc['gb_rv'] - ssc['ag_rvbeit']
        # Health
        ssc['gb_gkv'] = ((tb['gkvbs_an'] + tb['gkvbs_ag'])
                         * ssc['bemessungsentgelt'])
        ssc.loc[ssc['in_gleitzone'],
                'ag_gkvbeit'] = tb['gkvbs_ag'] * ssc['m_wage']
        ssc.loc[ssc['in_gleitzone'],
                'gkvbeit'] = ssc['gb_gkv'] - ssc['ag_gkvbeit']
        # Unemployment
        ssc['gb_alv'] = 2 * tb['alvbs'] * ssc['bemessungsentgelt']
        ssc.loc[ssc['in_gleitzone'], 'ag_avbeit'] = tb['alvbs'] * ssc['m_wage']
        ssc.loc[ssc['in_gleitzone'],
                'avbeit'] = ssc['gb_alv'] - ssc['ag_avbeit']
        # Care
        ssc['gb_pv'] = 2 * tb['gpvbs'] * ssc['bemessungsentgelt']
        ssc.loc[ssc['in_gleitzone'], 'ag_pvbeit'] = tb['gpvbs'] * ssc['m_wage']
        ssc.loc[ssc['in_gleitzone'],
                'pvbeit'] = (ssc['gb_pv'] - ssc['ag_pvbeit']
                             + (ssc['kinderlos']
                                * tb['gpvbs_kind'] * ssc['m_wage']))

        # Drop intermediate variables
        ssc = ssc.drop(['gb_rv', 'gb_gkv',
                        'gb_alv', 'gb_pv', 'bemessungsentgelt'], axis=1)
    # END 'GLEITZONE'

    # check whether we are below 450€...set to zero
    for beit in ['rvbeit', 'gkvbeit', 'avbeit', 'pvbeit',
                 'ag_rvbeit', 'ag_gkvbeit', 'ag_avbeit', 'ag_pvbeit']:
        ssc.loc[ssc['belowmini'], beit] = 0
    # Freiwillige GKV der Selbständigen.
    # Entweder Selbständigen-Einkommen oder 3/4 der Bezugsgröße
    ssc.loc[(ssc['selfemployed']) & (~ssc['pkv']),
            'gkvbeit'] = ((tb['gkvbs_an'] + tb['gkvbs_ag'])
                          * np.minimum(ssc['m_self'],
                          0.75 * np.select(westost,
                                           [tb['bezgr_w'], tb['bezgr_o']])))

    ssc.loc[(ssc['selfemployed']) &
            (~ssc['pkv']),
            'pvbeit'] = ((2 * tb['gpvbs'] + np.select(
                        [ssc['kinderlos'], ~ssc['kinderlos']],
                        [tb['gpvbs_kind'], 0]))
                    * np.minimum(ssc['m_self'], 0.75 * np.select(
                            westost, [tb['bezgr_w'], tb['bezgr_o']])))
    # GKV auf Renten, die zahlen den doppelten Pflebebeitragssatz.
    ssc['gkvrbeit'] = (tb['gkvbs_an'] *
                       np.minimum(ssc['m_pensions'],
                                  np.select(westost,
                                            [tb['kvmaxekw'],
                                             tb['kvmaxeko']])))
    # doppelter Pflegebeitragssatz
    ssc['pvrbeit'] = (2 * tb['gpvbs'] *
                      np.minimum(ssc['m_pensions'],
                                   np.select(westost,
                                             [tb['kvmaxekw'],
                                              tb['kvmaxeko']])))
    ssc.loc[ssc['kinderlos'],
            'pvrbeit'] = ((2 * tb['gpvbs'] + tb['gpvbs_kind']) *
                          np.minimum(ssc['m_pensions'],
                                       np.select(westost,
                                                 [tb['kvmaxekw'],
                                                  tb['kvmaxeko']])))

    ssc['gkvbeit'] = ssc['gkvbeit'] + ssc['gkvrbeit']
    ssc['pvbeit'] = ssc['pvbeit'] + ssc['pvrbeit']

    # Sum of Social Security Contributions (for employees)
    ssc['svbeit'] = ssc[['rvbeit', 'avbeit', 'gkvbeit', 'pvbeit']].sum(axis=1)

    return ssc


def ui(df, tb, taxyear, ref):
    ''' Unemployment/Transitory Benefit
        based on employment status and income from previous years
    '''
    westost = [~df['east'], df['east']]

    df['m_alg1'] = df['alg_soep'].fillna(0)
    # Months of entitlement
    df['mts_contrib'] = df['months_l1'] + df['months_l2']
    df['mts_ue'] = (df['months_ue'] +
                    df['months_ue_l1'] +
                    df['months_ue_l2'])
    # Relevant wage is capped at the contribution thresholds
    df['alg_wage'] = (np.select(westost,
                                [np.minimum(tb['rvmaxekw'], df['m_wage_l1']),
                                 np.minimum(tb['rvmaxeko'], df['m_wage_l1'])]))

    df['ui_wage'] = np.maximum(df['alg_wage'] -
                               np.maximum(df['m_wage'] -
                                          tb['alg1_frei'], 0), 0)
    # BENEFIT AMOUNT
    # Check Eligiblity.
    # Then different rates for parent and non-parents
    # Take into account actual wages
    # Do this only for people for which we don't observe UI payments in SOEP,
    # assuming that their information is more reliable
    # (rethink this for the dynamic model)
    # there are different replacement rates depending on presence of children
    df.loc[(df['mts_ue'] > 0) &
           (df['mts_ue'] <= 12) &
           (df['age'] < 65) &
           (df['m_pensions'] == 0) &
           (df['alg_soep'] == 0) &
           (df['w_hours'] < 15),
           'm_alg1'] = (np.select(
                        [df['child_num_tu'] == 0, df['child_num_tu'] > 0],
                        [tb['agsatz0'],                  tb['agsatz1']]) *
                        df['ui_wage'])

    print('ALG 1 recipients according to SOEP:'
          + str(df['counter'][df['alg_soep'] > 0].sum()))
    print('Additional ALG 1 recipients from simulation:'
          + str(df['counter'][df['m_alg1'] > 0].sum()
                - df['counter'][df['alg_soep'] > 0].sum()))
    return df


def zve(df, tb, yr, ref):
    ''' Calculates taxable income
        In fact, you need several taxable incomes because of
        - child allowance vs. child benefit
        - abgeltungssteuer vs. taxing capital income in the tariff
        It's always the most favorable for the taxpayer, but you only after applying
        the tax schedule
    '''
    cprint('Calculate Taxable Income...', 'red', 'on_white')
    # Kapitaleinkommen im Tarif versteuern oder nicht?
    kapinc_in_tarif = yr < 2009
    westost = [~df['east'], df['east']]
    married = [df['zveranl'], ~df['zveranl']]

    # The share of pensions subject to income taxation
    df['ertragsanteil'] = 0
    df.loc[df['renteneintritt'] <= 2004, 'ertragsanteil'] = 0.27
    df.loc[df['renteneintritt'].between(2005, 2020),
           'ertragsanteil'] = 0.5 + 0.02 * (df['renteneintritt'] - 2005)
    df.loc[df['renteneintritt'].between(2021, 2040),
           'ertragsanteil'] = 0.8 + 0.01 * (df['renteneintritt'] - 2020)
    df.loc[df['renteneintritt'] >= 2041, 'ertragsanteil'] = 1

    # Werbungskosten und Sonderausgaben
    df['werbung'] = tb['werbung'] * df['m_wage'] > 0 * ~df['child']
    df['sonder'] = (~df['child']) * tb['sonder']
    ####################################################
    # Income components on annual basis
    # Income from Self-Employment
    df['gross_e1'] = 12 * df['m_self']
    # Earnings
    df['gross_e4'] = np.maximum((12 * df['m_wage']) - df['werbung'], 0)
    # Minijob-Grenze beachten
    df.loc[df['m_wage'] <= np.select(westost,
                                     [tb['mini_grenzew'],
                                      tb['mini_grenzeo']]),
           'gross_e4'] = 0

    # Capital Income
    df['gross_e5'] = np.maximum((12 * df['m_kapinc']), 0)
    # Income from rents
    df['gross_e6'] = 12 * df['m_vermiet']
    # Others (Pensions)
    df['gross_e7'] = np.maximum(
                                12 * (df['ertragsanteil'] * df['m_pensions'])
                                - tb['vorsorgpausch'], 0)
    # Sum of incomes
    df['gross_gde'] = df[['gross_e1', 'gross_e4', 'gross_e6', 'gross_e7']].sum(axis=1)
    # If capital income tax with tariff, add it but account for exemptions
    if kapinc_in_tarif: df['gross_gde'] = (df['gross_gde'] +
                                           np.maximum(df['gross_e5'] -
                                                      tb['spsparf'] -
                                                      tb['spwerbz'], 0))
    # Gross (market) income <> sum of incomes...
    df['m_brutto'] = df[['m_self',
                         'm_wage',
                         'm_kapinc',
                         'm_vermiet',
                         'm_pensions']].sum(axis=1)

    # Behinderten-Pauschbeträge
    hc_degrees = [df['handcap_degree'].between(45, 50),
                  df['handcap_degree'].between(51, 60),
                  df['handcap_degree'].between(61, 70),
                  df['handcap_degree'].between(71, 80),
                  df['handcap_degree'].between(81, 90),
                  df['handcap_degree'].between(91, 100)]
    hc_pausch = [tb['sbhp50'], tb['sbhp60'], tb['sbhp70'],
                 tb['sbhp80'], tb['sbhp90'], tb['sbhp100']]
    df['handc_pausch'] = (df['handcap_dummy']
                          * np.select(hc_degrees, hc_pausch))

    # Aggregate several incomes on the taxpayer couple
    for inc in ['m_wage', 'rvbeit', 'gkvbeit', 'avbeit', 'pvbeit']:
        df = aggr(df, inc, True)
    for inc in ['sonder', 'handc_pausch', 'gross_gde', 'gross_e1',
                'gross_e4', 'gross_e5', 'gross_e6', 'm_wage', 'rvbeit',
                'avbeit', 'gkvbeit', 'pvbeit']:
        df = aggr(df, inc, False)

    # TAX DEDUCTIONS
    # 'Vorsorgeaufwendungen': Deduct part of your social insurance contributions
    # from your taxable income
    # This regulation has been changed often in recent years. In order not to make anyone
    # worse off, the old regulation was maintained. Nowadays the older regulations
    # don't play a large role (i.e. the new one is more beneficial most of the times)
    # but they'd need to be implemented if earlier years are modelled.
    # Vorsorgeaufwendungen until 2004
    # TO DO
    # Vorsorgeaufwendungen since 2005
    # TO DO
    # Vorsorgeaufwendungen since 2010
    # § 10 (3) EStG
    # The share of deductable pension contributions increases each year by 2 pp.
    # ('nachgelagerte Besteuerung'). In 2018, it's 86%. Add other contributions;
    # 4% from health contributions are not deductable
    # The regular maximum amount of deductions is 2800€ per taxpayer

    # only deduct pension contributions up to the ceiling. for couples, it's an approximation.
    df['rvbeit_vors'] = np.minimum(df['rvbeit'], np.select(westost,
                                                          [tb['rvmaxekw'], tb['rvmaxeko']]))
    df['rvbeit_tu_vors'] = np.minimum(df['rvbeit_tu'], 2 * np.select(
                                      westost, [tb['rvmaxekw'], tb['rvmaxeko']]))
    # For couples, give everybody half the total deduction. (maybe improve this))
    vorsorg2010_married = (0.5 * (0.6 + 0.02 * (np.minimum(yr, 2025) - 2005)) *
                                 (12 * df['rvbeit_tu_vors']) + np.minimum(12 * (df['pvbeit_tu'] +
                                  df['avbeit_tu'] + 0.96 * df['gkvbeit_tu']), 2 * 2800))

    vorsorg2010_single = ((0.6 + 0.02 * (np.minimum(yr, 2025) - 2005)) * (12 * df['rvbeit_vors']) +
                                       np.minimum(12 * (df['pvbeit'] + df['avbeit'] +
                                                          0.96 * df['gkvbeit']), 2800))

    df['vorsorge2010'] = np.select(married, [vorsorg2010_married, vorsorg2010_single])

    # TO DO: check various deductions against each other (when modelled)
    df['vorsorge'] = df['vorsorge2010']
    df = aggr(df, 'vorsorge')

    # Altersentlastungsbetrag. Deduction for elderly
    df['altfreib'] = 0
    df.loc[df['age'] > 64, 'altfreib'] = np.minimum(
                                         tb['altentq'] * 12 * (df['m_wage'] +
                                         np.maximum(0, df[['m_kapinc',
                                                           'm_self',
                                                           'm_vermiet']].sum(axis=1))),
                                                    tb['altenth'])
    df = aggr(df, 'altfreib')

    # Entlastungsbetrag für Alleinerziehende. Deduction for Single Parents
    df['hhfreib'] = 0
    if yr < 2015:
        df.loc[df['alleinerz'],'hhfreib'] = tb['hhfreib']
    if yr >= 2015:
            df.loc[df['alleinerz'],'hhfreib'] = (tb['hhfreib'] + (df['child_num_tu'] - 1) * 240)
    # Child Allowance (Kinderfreibetrag)
    # Single Parents get half the allowance, parents get the full amount but share it.
    # This is an assumption!
    df['kifreib'] = 0
    df['kifreib'] = (0.5 * tb['ch_allow'] *
                     df['child_num_tu'] * ~df['child'])
    # Taxable income (zve)
    # For married couples, household income is split between the two.
    # Without child allowance / Ohne Kinderfreibetrag (nokfb):
    df['zve_nokfb'] = 0
    df.loc[~df['zveranl'],
           'zve_nokfb'] = np.maximum(df['gross_gde'] -
                                     df['vorsorge'] -
                                     df['sonder'] -
                                     df['handc_pausch'] -
                                     df['hhfreib'] -
                                     df['altfreib'], 0)
    df.loc[df['zveranl'],
           'zve_nokfb'] = 0.5 * np.maximum(df['gross_gde_tu'] -
                                            df['vorsorge_tu'] -
                                            df['sonder_tu'] -
                                            df['handc_pausch_tu'] -
                                            df['hhfreib'] -
                                            df['altfreib'], 0)

    # Ohne Kinderfreibetrag, aber ohne Kapitalerträge
    df.loc[~df['zveranl'], 'zve_abg_nokfb'] = (
           np.maximum(df['gross_gde']
                      - np.minimum(tb['spsparf'] + tb['spwerbz'],
                                   df['gross_e5']) * (kapinc_in_tarif is False)
                      - df['vorsorge']
                      - df['sonder']
                      - df['handc_pausch']
                      - df['hhfreib']
                      - df['altfreib'], 0))
    df.loc[df['zveranl'], 'zve_abg_nokfb'] = (
            0.5 * np.maximum(df['gross_gde_tu']
                             - (np.minimum(2 * (tb['spsparf'] + tb['spwerbz']),
                                df['gross_e5_tu']) * (kapinc_in_tarif is False))
                             - df['vorsorge_tu']
                             - df['sonder']
                             - df['handc_pausch_tu']
                             - df['hhfreib']
                             - df['altfreib'], 0))
    # Subtract Child allowance to get alternative taxable incomes
    df['zve_kfb'] = np.maximum(df['zve_nokfb'] - df['kifreib'], 0)
    df['zve_abg_kfb'] = np.maximum(df['zve_abg_nokfb'] - df['kifreib'], 0)

    return df


def tax_sched(df, tb, yr, ref):
    ''' Applies the income tax tariff
    '''
    cprint('Income Tax...', 'red', 'on_white')
    kapinc_in_tarif = yr < 2009

    if (yr < 2009):
        inclist = ['nokfb', 'kfb']
    else:
        inclist = ['nokfb', 'abg_nokfb', 'kfb', 'abg_kfb']

    def tarif(x, tb):
        ''' The German Income Tax Tariff
        '''
        y = int(tb['yr'])
        if y < 2002:
            print("Income Tax Pre 2002 not yet modelled!")
        if y > 2002:
            t = 0
            if tb['G'] < x <= tb['M']:
                t = ((((tb['t_m']-tb['t_e'])/(2*(tb['M']-tb['G'])))*(x-tb['G'])
                     + tb['t_e'])*(x-tb['G']))
            if tb['M'] < x <= tb['S']:
                t = ((((tb['t_s']-tb['t_m'])/(2*(tb['S']-tb['M'])))*(x-tb['M'])
                      + tb['t_m'])*(x-tb['M'])
                     + (tb['M']-tb['G'])*((tb['t_m']+tb['t_e'])/2))
            if(x > tb['S']):
                t = ((tb['t_s']*x-tb['t_s']*tb['S']
                      + ((tb['t_s'] + tb['t_m'])/2)*(tb['S'] - tb['M'])
                      + ((tb['t_m']+tb['t_e'])/2)*(tb['M']-tb['G'])))
            if x > tb['R']:
                t = t + (tb['t_r']-tb['t_s'])*(x-tb['R'])
            t = round(t, 2)
        return t

    #####################
    # TAX SCHEDULE FOR VARIOUS DEFINITIONS OF TAXABLE INCOME
    #####################
    cprint('Tax Schedule...', 'red', 'on_white')
    for inc in inclist:
        df['tax_'+inc] = np.vectorize(tarif)(df['zve_'+inc], tb)
        df = aggr(df, 'tax_'+inc)
    ###################

    # Abgeltungssteuer
    df['abgst'] = 0
    if kapinc_in_tarif is False:
        df.loc[~df['zveranl'], 'abgst'] = (
                tb['abgst'] * np.maximum(df['gross_e5']
                                         - tb['spsparf']
                                         - tb['spwerbz'], 0))
        df.loc[df['zveranl'], 'abgst'] = (
                0.5 * tb['abgst'] * np.maximum(df['gross_e5_tu']
                                               - 2 * (tb['spsparf']
                                                          - tb['spwerbz']), 0))
    df = aggr(df, 'abgst')

    return df


def kindergeld(df, tb, yr, ref):
    """ Child Benefit
        Basic Amount for each child, hours restriction applies
    """
    df['eligible'] = 1
    if yr > 2011:
        df['eligible'] = df['eligible'].where(
            (df['age'] <= tb['kgage']) &
            (df['w_hours'] <= 20) &
            (df['ineducation']), 0)
    else:
        df['eligible'] = df['eligible'].where(
            (df['age'] <= tb['kgage']) &
            (df['m_wage'] <= tb['kgfreib'] / 12) &
            (df['ineducation']), 0)

    df['child_count'] = df.groupby(['tu_id'])['eligible'].cumsum()

    num_to_amount = {1: tb['kgeld1'], 2: tb['kgeld2'], 3: tb['kgeld3'],
                     4: tb['kgeld4']}
    df['kindergeld'] = df['child_count'].replace(num_to_amount)
    df['kindergeld'] = df['kindergeld'].where(
        df['child_count'] <= 4, tb['kgeld4'])
    df['kindergeld_tu'] = df.groupby('tu_id')['kindergeld'].transform(sum)

    df.drop(['child_count', 'eligible', 'kindergeld'], axis=1, inplace=True)

    return df


def tax_test(df, tb, yr, ref):
    """ 'Higher-Yield Test'
        compares the tax burden that results from various definitions of the tax base
        Most importantly, it compares the tax burden without applying the child allowance (_nokfb)
        AND receiving child benefit with the tax burden including the child allowance (_kfb), but
        without child benefit. The most beneficial (for the household) is chocen.
        If child allowance is claimed, kindergeld is set to zero
        A similar check applies to whether it is more profitable to
        tax capital incomes with the standard 25% rate or to include it in the tariff.
    """
    # Günstigerprüfung...auf TU-Ebene!
    cprint('Günstigerprüfung...', 'red', 'on_white')
    if (yr < 2009):
        inclist = ['nokfb', 'kfb']
    else:
        inclist = ['nokfb', 'abg_nokfb', 'kfb', 'abg_kfb']

    for inc in inclist:
        df['nettax_' + inc] = df['tax_'+inc+'_tu']
        if 'abg' in inc:
            df['nettax_' + inc] = df['nettax_'+inc] + df['abgst_tu']
        # Before 1996, both child allowance and child benefit could be claimed
        if ('nokfb' in inc) | (yr <= 1996):
            df['nettax_' + inc] = (df['nettax_'+inc]
                                   - (12 * df['kindergeld_tu']))
    # get the maximum income, i.e. the minimum payment burden
    df['minpay'] = df.filter(regex='nettax').min(axis=1)
    # relevant tax base
    df['tax_income'] = 0
    # relevant incometax
    df['incometax'] = 0
    df['abgehakt'] = False
    for inc in inclist:
        df.loc[(df['minpay'] == df['nettax_' + inc])
               & (~df['abgehakt']),
               'tax_income'] = df['zve_'+inc]
        # Income Tax in monthly terms! And write only to parents
        df.loc[(df['minpay'] == df['nettax_' + inc])
               & (~df['abgehakt'])
               & (~df['child']),
               'incometax_tu'] = df['tax_'+inc+'_tu'] / 12
        # set kindergeld to zero if necessary
        if (not ('nokfb' in inc)) | (yr <= 1996):
            df.loc[(df['minpay'] == df['nettax_' + inc])
                   & (~df['abgehakt']),
                   'kindergeld'] = 0
            df.loc[(df['minpay'] == df['nettax_' + inc])
                   & (~df['abgehakt']),
                   'kindergeld_tu'] = 0
        if ('abg' in inc):
            df.loc[(df['minpay'] == df['nettax_' + inc])
                   & (~df['abgehakt']),
                   'abgst'] = 0
            df.loc[(df['minpay'] == df['nettax_' + inc])
                   & (~df['abgehakt']),
                   'abgst_tu'] = 0
        df.loc[(df['minpay'] == df['nettax_' + inc]), 'abgehakt'] = True

    # Aggregate Child benefit on the household
    df = df.join(
            df.groupby(['hid'])['kindergeld'].sum(),
            on=['hid'], how='left', rsuffix='_hh')
    # Control output
    # df.to_excel(pd.ExcelWriter(data_path+'check_güsntiger.xlsx'),sheet_name='py_out',columns= ['tu_id','child','zveranl','minpay','incometax','abgehakt','nettax_abg_kfb_tu', 'zve_abg_kfb_tu', 'tax_abg_kfb_tu', 'nettax_abg_kfb_tu', 'zve_abg_kfb_tu', 'tax_abg_kfb_tu', 'nettax_abg_kfb_tu', 'zve_abg_kfb_tu', 'tax_abg_kfb_tu', 'nettax_abg_kfb_tu', 'zve_abg_kfb_tu', 'tax_abg_kfb_tu'],na_rep='NaN',freeze_panes=(0,1))
    # pd.to_pickle(df,data_path+ref+'/taxben_check')
    # df.to_excel(pd.ExcelWriter(data_path+'check_tax_incomes.xlsx'),sheet_name='py_out',columns=['hid','pid','age','female','child','zve_nokfb','zve_kfb','tax_nokfb','tax_kfb','gross_e1','gross_e4','gross_e5','gross_e6','gross_e7','gross_gde'],na_rep='NaN',freeze_panes=(0,1))
    return df

def soli(df, tb, yr, ref):
    """ Solidarity Surcharge ('soli')
        on top of the income tax.
        No Soli if income tax due is below € 920 (solifreigrenze)
        then it increases with 0.2 marginal rate until 5.5% (solisatz)
        of the incometax is reached.
        As opposed to the 'standard' income tax,
        child allowance is always deducted for soli calculation
    """
    cprint('Solidarity Surcharge...', 'red', 'on_white')

    if yr >= 1991:
        if yr >= 2009:
            df['solibasis'] = df['tax_kfb_tu']
        else:
            df['solibasis'] = (df['tax_kfb_tu'] + df['abgst'])
        # Soli also in monthly terms. only for adults
        df['soli_tu'] = (np.minimum(
                    tb['solisatz'] * df['solibasis'],
                    np.maximum(0.2 * (df['solibasis']
                               - tb['solifreigrenze'])/12, 0))
                      * (~df['child']))

    # Apply Income Tax + Soli to individuals
    for tax in ['incometax', 'soli']:
        df[tax] = np.select([df['zveranl'], ~df['zveranl']],
                            [df[tax + '_tu'] / 2, df[tax + '_tu']])
    return df


def wg(df, tb, yr, ref):
    """ Housing benefit / Wohngeld
        Social benefit for recipients with income above basic social assistance
        Computation is very complicated, accounts for household size, income, actual rent
        and differs on the municipality level ('Mietstufe'). we assume a medium rent level
    """
    print("Housing Benefit...")

    # Benefit amount depends on parameters M (rent) and Y (income) (§19 WoGG)
    # Calculate them on the level of the tax unit

    # Start with income revelant for the housing beneift

    # tax-relevant share of pensions
    df['pens_steuer'] = df['ertragsanteil'] * df['m_pensions']
    for inc in ['m_alg1', 'm_transfers', 'pens_steuer', 'gross_e1',
                'gross_e4', 'gross_e5', 'gross_e6', 'incometax']:
        df = aggr(df, inc, True)

    # There share of income to be deducted is 0/10/20/30%, depending on whether household is
    # subject to income taxation and/or payroll taxes
    df['wg_abz'] = ((df['incometax_tu_k'] > 0) * 1 +
                    (df['rvbeit_tu_k'] > 0) * 1 +
                    (df['gkvbeit_tu_k'] > 0) * 1)

    df['wg_abzuege'] = (np.select([df['wg_abz'] == 0, df['wg_abz'] == 1,
                                   df['wg_abz'] == 2, df['wg_abz'] == 3],
                                  [tb['wgpabz0'], tb['wgpabz1'],
                                   tb['wgpabz2'], tb['wgpabz3']]))

    # Relevant income is market income + transfers...
    df['wg_grossY'] = (np.maximum(df['gross_e1_tu_k']/12, 0)
                       + np.maximum(df['gross_e4_tu_k']/12, 0)
                       + np.maximum(df['gross_e5_tu_k']/12, 0)
                       + np.maximum(df['gross_e6_tu_k']/12, 0))

    df['wg_otherinc'] = (df['m_alg1_tu_k'] + df['m_transfers_tu_k']
                         + (df['pens_steuer_tu_k']))

    # ... minus a couple of deductions for handicaps or children
    if yr >= 2016:
        df['wg_incdeduct'] = ((df['handcap_degree'] > 0) * tb['wgpfbm80']
                              + (((df['child']) * (df['m_wage'] > 0))
                                 * np.minimum(tb['wgpfb24'], df['m_wage']))
                              + (df['alleinerz'] * tb['wgpfb12'] * ~df['child']))
        df = aggr(df, 'wg_incdeduct', True)
    else:
        sys.exit("Wohngeld-Abzüge vor 2016 noch nicht modelliert")

    df['wgY'] = ((1 - df['wg_abzuege'])
                 * np.maximum((df['wg_grossY']
                               + df['wg_otherinc']
                               - df['wg_incdeduct_tu_k']), 0))

    # Parameter Y in steps of 5 Euros
    df['Y'] = np.maximum(pd.Series(df['wgY']+4).round(-1)-5, 0)
    # There's a minimum Y dependin on the hh size
    for i in range(1, 12):
        df.loc[df['hhsize'] == i, 'Y'] = np.maximum(df['Y'], tb['wgminEK'+str(i)+'p'])
    df.loc[df['hhsize'] >= 12, 'Y'] = np.maximum(df['Y'], tb['wgminEK12p'])

    # Rent
    # There's also min max values for this
    df['max_rent'] = 0
    df['min_rent'] = 0
    if yr >= 2009:
        for i in range(1, 13):
            if i <= 5:
                df.loc[(df['hhsize'] == i), 'max_rent'] = tb['wgmax'+str(i)+'p_m']
            df.loc[(df['hhsize'] == i), 'min_rent'] = tb['wgmin'+str(i)+'p']

        df.loc[(df['hhsize'] > 5), 'max_rent'] = (df['max_rent'] +
                                                  tb['wgmaxplus5_m'] * (df['hhsize'] - 5))
        df.loc[(df['hhsize'] > 12), 'min_rent'] = (df['max_rent'] +
                                                  tb['wgmaxplus5_m'] * (df['hhsize'] - 5))

    df['max_rent'] = df['max_rent'] * df['hh_korr']

    df['wgmiete'] = np.minimum(df['max_rent'], df['miete'] * df['hh_korr'])
    df['wgheiz'] = df['heizkost'] * df['hh_korr']
    df['M'] = np.maximum(df['wgmiete'] + df['wgheiz'], df['min_rent'])

    df['M'] = np.maximum(pd.Series(df['M']+4).round(-1) - 5, 0)

    # Finally, apply Wohngeld Formel. There are parameters a, b, c, depending on hh size
    # To ease notation, I write them first into separate variables from the tb dictionary
    wg = {}
    for x in range(1, 13):
        for z in ['a', 'b', 'c']:
            wg[z] = tb['wg_'+z+'_'+str(x)+'p']

        a = wg['a']
        b = wg['b']
        c = wg['c']

        df.loc[np.minimum(df['hhsize_tu'], 12) == x,
               'wohngeld'] = np.maximum(0, tb['wg_factor'] *
                                        (df['M'] - ((a + (b*df['M']) +
                                         (c*df['Y']))*df['Y'])))

    # Sum of wohngeld within household
    df['wg_head'] = df['wohngeld'] * df['head_tu']
    df = df.join(df.groupby(['hid'])['wg_head'].sum(),
                 on=['hid'], how='left', rsuffix='_hh')
    df = df.rename(columns={'wg_head_hh': 'wohngeld_hh'})

    return df

def alg2(df, tb, yr, ref):
    """ Basic Unemployment Benefit / Social Assistance
        Every household is assigend the sum of "needs" (Regelbedarf)
        These depend on the household composition (# of adults, kids in various age groups)
        and the rent. There are additional needs acknowledged for single parents.
        Income and wealth is tested for, the transfer withdrawal rate is non-constant.
    """
    print("ALG 2...")
    # Additional need
    df['mehrbed'] = ((~df['child']) * df['alleinerz'] *
                      np.minimum(np.maximum(((df['child6_num'] == 1)
                      | (df['child15_num'].between(2, 3))) *
                         tb['a2mbch2'], tb['a2mbch1'] * df['child_num']),
                         tb['a2zu2']/100))

    # 'Regular Need'
    # Different amounts by number of adults and age of kids
    # tb['rs_hhvor'] is the basic 'Hartz IV Satz' for a single person
    if yr <= 2010:
        # Before 2010, other members' amounts were calculated by a share of the head's need
        regelberechnung = [
                tb['rs_hhvor'] * (1 + df['mehrbed']) +
                (tb['rs_hhvor'] * tb['a2ch14'] * df['child14_24_num']) +
                (tb['rs_hhvor'] * tb['a2ch7'] * df['child7_13_num']) +
                (tb['rs_hhvor'] * tb['a2ch0'] * (df['child2_num'] + df['child3_6_num'])),

                tb['rs_hhvor'] * tb['a2part'] * (1 + df['mehrbed']) +
                (tb['rs_hhvor'] * tb['a2part']) +
                (tb['rs_hhvor'] * tb['a2ch18'] * np.maximum((df['adult_num'] - 2), 0)) +
                (tb['rs_hhvor'] * tb['a2ch14'] * df['child14_24_num']) +
                (tb['rs_hhvor'] * tb['a2ch7'] * df['child7_13_num']) +
                (tb['rs_hhvor'] * tb['a2ch0'] * (df['child2_num'] + df['child3_6_num']))
                ]

    else:
        # After 2010,
        regelberechnung = [
                tb['rs_hhvor'] * (1 + df['mehrbed']) +
                (tb['rs_ch14'] * df['child14_24_num']) +
                (tb['rs_ch7'] * df['child7_13_num']) +
                (tb['rs_ch0'] * (df['child2_num'] + df['child3_6_num'])),
                tb['rs_2adults'] * (1 + df['mehrbed']) +
                tb['rs_2adults'] +
                (tb['rs_madults'] * np.maximum((df['adult_num'] - 2), 0)) +
                (tb['rs_ch14'] * df['child14_24_num']) +
                (tb['rs_ch7'] * df['child7_13_num']) +
                (tb['rs_ch0'] * (df['child2_num'] + df['child3_6_num']))
                ]

    df['regelsatz'] = np.select([df['adult_num'] == 1, df['adult_num'] > 1], regelberechnung)

    df = aggr(df, 'regelsatz', True)
    # Only 'appropriate' housing costs are paid. For simplicity apply Housing benefit rules
    # this might be overly restrictive...check number of benefit recipients.
    df['alg2_kdu'] = df['M'] + np.maximum(df['heizkost'] - df['wgheiz'], 0)

    # After introduction of Hartz IV, people becoming unemployed received something on top
    # to smooth the transition.
    if 2005 <= yr <= 2010:
        print('"Armutsgewöhnungszuschlag" noch nicht modelliert.')
    else:
        df['bef_zuschlag'] = 0

    df['regelbedarf'] = df[['regelsatz', 'alg2_kdu', 'bef_zuschlag']].sum(axis=1)

    # Account for household wealth.
    # usually no wealth in the data, infer from capital income...works OK for low wealth HH
    df['assets'] = df['divdy'] / tb['r_assets']

    # df['vermfreib'] = tb['a2vki']
    # there are exemptions depending on individual age for adults
    df['ind_freib'] = 0
    df.loc[(df['byear'] >= 1948) & (~df['child']), 'ind_freib'] = tb['a2ve1'] * df['age']
    df.loc[(df['byear'] < 1948), 'ind_freib'] = tb['a2ve2'] * df['age']
    # add over individuals
    df = df.join(df.groupby(['hid'])['ind_freib'].sum(),
                 on=['hid'], how='left', rsuffix='_hh')

    # there is an overall maximum exemption
    df['maxvermfb'] = 0
    df.loc[(df['byear'] < 1948) & (~df['child']), 'maxvermfb'] = tb['a2voe1']
    df.loc[(df['byear'].between(1948, 1957)), 'maxvermfb'] = tb['a2voe1']
    df.loc[(df['byear'].between(1958, 1963)), 'maxvermfb'] = tb['a2voe3']
    df.loc[(df['byear'] >= 1964) & (~df['child']), 'maxvermfb'] = tb['a2voe4']
    df = df.join(df.groupby(['hid'])['maxvermfb'].sum(),
                 on=['hid'], how='left', rsuffix='_hh')
    # add fixed amounts per child and adult
    df['vermfreibetr'] = np.minimum(df['ind_freib_hh'] + df['child18_num'] * tb['a2vkf'] +
                                    df['adult_num'] * tb['a2verst'],
                                    df['maxvermfb_hh'])

    # If wealth exceeds the exemption, the need is set to zero
    # Note that if the HH has too much wealth, there's no Hosuing Benefit and no
    # additional child benefit as well (because they are always assessed against the need)
    df.loc[(df['assets'] > df['vermfreibetr']), 'regelbedarf'] = 0

    # Income relevant to check against ALG2 claim
    df['alg2_grossek'] = (~(df['child']) *
                          df[['m_wage', 'm_transfers', 'm_self', 'm_vermiet',
                              'm_kapinc', 'm_pensions', 'm_alg1']].sum(axis=1))
    df['alg2_grossek'] = df['alg2_grossek'].fillna(0)
    # ...deduct income tax and social security contributions
    df['alg2_ek'] = ((~df['child'])
                     * np.maximum(df['alg2_grossek'] - df['incometax'] - df['soli'] -
                                  df['svbeit'], 0))
    df['alg2_ek'] = df['alg2_ek'].fillna(0)

    # Determine the amount of income that is not deducted
    # Varios withdrawal rates depending on monthly earnings.
    df['ekanrefrei'] = 0
    df.loc[(df['m_wage'] <= tb['a2grf']), 'ekanrefrei'] = df['m_wage']
    df.loc[(df['m_wage'].between(tb['a2grf'], tb['a2eg1'])),
           'ekanrefrei'] = (tb['a2grf'] + tb['a2an1'] * (df['m_wage'] - tb['a2grf']))
    df.loc[(df['m_wage'].between(tb['a2eg1'], tb['a2eg2']))
           & (df['child18_num'] == 0),
           'ekanrefrei'] = (tb['a2grf'] + tb['a2an1'] * (tb['a2eg1'] - tb['a2grf']) +
                            tb['a2an2'] * (df['m_wage'] - tb['a2eg1']))
    df.loc[(df['m_wage'].between(tb['a2eg1'], tb['a2eg3'])) & (df['child18_num'] > 0),
           'ekanrefrei'] = (tb['a2grf'] + tb['a2an1'] * (tb['a2eg1'] - tb['a2grf']) +
                            tb['a2an2'] * (df['m_wage'] - tb['a2eg1']))

    df.loc[(df['m_wage'] > tb['a2eg2']) & (df['child18_num'] == 0),
           'ekanrefrei'] = (tb['a2grf'] + tb['a2an1'] * (tb['a2eg1'] - tb['a2grf']) +
                            tb['a2an2'] * (tb['a2eg2'] - tb['a2eg1']))
    df.loc[(df['m_wage'] > tb['a2eg3'])
           & (df['child18_num'] > 0),
           'ekanrefrei'] = (tb['a2grf'] + tb['a2an1'] * (tb['a2eg1'] - tb['a2grf']) +
                            tb['a2an2'] * (tb['a2eg3'] - tb['a2eg1']))
    # Children income is fully deducted, except for the first 100 €.
    df.loc[(df['child']), 'ekanrefrei'] = np.minimum(np.maximum(0, df['m_wage'] - 100), 100)
    # This is
    df['ar_alg2_ek'] = np.maximum(df['alg2_ek'] - df['ekanrefrei'], 0)
    # Aggregate on HH
    for var in ['ar_alg2_ek', 'alg2_grossek']:
        df = df.join(df.groupby(['hid'])[var].sum(),
                     on=['hid'], how='left', rsuffix='_hh')
    df['ar_base_alg2_ek'] = df['ar_alg2_ek_hh'] + df['kindergeld_hh']

    # ALG2 ist Differenz zwischen Regelbedarf und Summe der Einkommen.
    # Wird aber erst später berechnet beim Vergleich der unterschiedlichen
    # Leistungen.

    return df

def kiz(df, tb, yr, ref):
    ''' Kinderzuschlag / Additional Child Benefit
    '''


    def wohnbedarf(yr_in):
        ''' Erwachsenen-Wohnbedarf für Kinderzuschlag
            Fixe Anteile am Gesamtbedarf gem. jährlichem Existenzminimumsbericht
        '''
        year = max(yr_in, 2011)
        # cols: number of adults
        # rows: number of kids
        wb = {'2011': [[75.90, 83.11], [61.16, 71.10], [51.21, 62.12], [44.05, 55.15], [38.65, 49.59]],
              '2012': [[76.34, 83.14], [61.74, 71.15], [51.82, 62.18], [44.65, 55.22], [39.23, 49.66]],
              '2013': [[76.34, 83.14], [61.74, 71.15], [51.82, 62.18], [44.65, 55.22], [39.23, 49.66]],
              '2014': [[76.69, 83.30], [62.20, 71.38], [52.31, 62.45], [45.13, 55.50], [39.69, 49.95]],
              '2015': [[76.69, 83.30], [62.20, 71.38], [52.31, 62.45], [45.13, 55.50], [39.69, 49.95]],
              '2016': [[77.25, 83.16], [62.93, 71.17], [53.09, 62.20], [45.92, 55.24], [40.45, 49.69]],
              '2017': [[77.25, 83.16], [62.93, 71.17], [53.09, 62.20], [45.92, 55.24], [40.45, 49.69]],
              '2018': [[77.24, 83.25], [62.92, 71.30], [53.08, 62.36], [45.90, 55.41], [40.43, 49.85]]
             }

        return wb[str(year)]

    print("Kinderzuschlag...")
    # First, calculate the need, but only for parents.
    if yr <= 2010:
        # not yet implemented
        kiz_regel = [np.nan, np.nan, np.nan]
    if yr > 2010:
        kiz_regel = [
                    tb['rs_hhvor'] * (1 + df['mehrbed']),
                    tb['rs_2adults'] + ((1 + df['mehrbed']) * tb['rs_2adults']),
                    tb['rs_madults'] * df['adult_num']
                    ]

    df['kiz_ek_regel'] = np.select([df['adult_num'] == 1,
                                    df['adult_num'] == 2,
                                    df['adult_num'] > 2],
                                   kiz_regel) * (df['head'])
    # Add rents. First, correct rent for the case of several tax units within the HH
    df['kiz_miete'] = df['miete'] * df['hh_korr']
    df['kiz_heiz'] = df['heizkost'] * df['hh_korr']
    # The actual living need is again broken down to the parents.
    # There is a specific share for this, taken from the function 'wohnbedarf' above.
    wb = wohnbedarf(yr)
    df['wb_eltern_share'] = 1.0
    for c in [1, 2]:
        for r in [1, 2, 3, 4]:
            df.loc[(df['child_num_tu'] == r) & (df['adult_num_tu'] == c),
                   'wb_eltern_share'] = wb[r-1][c-1] / 100
        df.loc[(df['child_num_tu'] >= 5) & (df['adult_num_tu'] == c),
               'wb_eltern_share'] = wb[4][c-1] / 100

    # apply this share to living costs
    df['kiz_ek_kdu'] = (df['wb_eltern_share'] * (df['kiz_miete'] + df['kiz_heiz'])) * df['head']

    df['kiz_ek_relev'] = df['kiz_ek_regel'] + df['kiz_ek_kdu']

    # There is a maximum income threshold, depending on the need, plus the potential kiz receipt
    df['kiz_ek_max'] = df['kiz_ek_relev'] + tb['a2kiz'] * df['child_num']
    # min income to be eligible for KIZ (different for singles and couples)
    df['kiz_ek_min'] = (tb['a2kiz_minek_cou'] * (df['hhtyp'] == 4) +
                        (tb['a2kiz_minek_sin'] * (df['alleinerz'])))

#        Übersetzung §6a BKGG auf deutsch:
#     1. Um KIZ zu bekommen, muss das Bruttoeinkommen minus Wohngeld
#        und Kindergeld über 600 bzw. 900 € liegen.
#     2. Das Nettoeinkommen minus Wohngeld muss unterhalb des Bedarfs
#        plus Gesamtkinderzuschlag liegen.
#     3. Dann wird geschaut, wie viel von dem Einkommen
#        (Erwachsene UND Kinder !) noch auf KIZ angerechnet wird.
#        Wenn das zu berücksichtigende Einkommen UNTER der
#        Höchsteinkommensgrenze und UNTER der Bemessungsgrundlage liegt, wird
#        der volle KIZ gezahlt
#        Wenn es ÜBER der Bemessungsgrundlage liegt,
#        wird die Differenz zur Hälfte abgezogen.
    df['kiz_ek_gross'] = df['alg2_grossek_hh']
    df['kiz_ek_net'] = df['ar_alg2_ek_hh']

    # Anzurechnendes Einkommen.
    # TO DO: Kindereinkommen abziehen!
    df['kiz_ek_anr'] = np.maximum(0, round((df['ar_alg2_ek_hh'] - df['kiz_ek_relev'])/10)*5)
    # Amount of additional child benefit
    df['kiz'] = 0
    df['kiz_incrange'] = ((df['kiz_ek_gross'] >= df['kiz_ek_min'])
                          & (df['kiz_ek_net'] <= df['kiz_ek_max']))
    df.loc[df['kiz_incrange'], 'kiz'] = np.maximum((tb['a2kiz'] * df['child_num']) -
                                                    df['kiz_ek_anr'], 0)

    # Extend the amount to the other hh members for technical reasons
    # Schreibe den Betrag für die anderen HH-Mitglieder,
    # notwendig für die folgende Berechnung.
    df= df.join(df.groupby(['hid'])[('kiz')].max(),
             on=['hid'], how='left', rsuffix='_temp')

    df['kiz'] = df['kiz_temp']
    ###############################
    # Check eligibility for benefits
    ###############################
    df['ar_wg_alg2_ek'] = df['ar_base_alg2_ek'] + df['wohngeld']
    df['ar_kiz_alg2_ek'] = df['ar_base_alg2_ek'] + df['kiz']
    df['ar_wgkiz_alg2_ek'] = (df['ar_base_alg2_ek'] + df['wohngeld'] + df['kiz'])

    for v in ['base', 'wg', 'kiz', 'wgkiz']:
        df['fehlbedarf_'+v] = df['regelbedarf'] - df['ar_'+v+'_alg2_ek']
        df['m_alg2_'+v] = np.maximum(df['fehlbedarf_'+v], 0)
    # There is a rule which benefits are superior to others
    # If there is a positive ALG2 claim, but the need can be covered with
    # Housing Benefit (and possibly add. child benefit),
    # the HH has to claim the housing benefit and addit. child benefit.
    # There is no way you can receive ALG2 and Wohngeld at the same time!
    for v in ['wg', 'kiz', 'wgkiz']:
        df[v+'_vorrang'] = (df['m_alg2_'+v] == 0) & (df['m_alg2_base'] > 0)

    df['m_alg2'] = df['m_alg2_base']
    # If this is the case set alg2 to zero
    df.loc[(df['wg_vorrang']) | (df['kiz_vorrang']) | (df['wgkiz_vorrang']), 'm_alg2'] = 0
    # If other benefits are not sufficient, set THEM to zero instead.
    df.loc[(~df['wg_vorrang']) & (~df['wgkiz_vorrang']) & (df['m_alg2_base'] > 0), 'wohngeld'] = 0
    df.loc[(~df['kiz_vorrang']) & (~df['wgkiz_vorrang']) & (df['m_alg2_base'] > 0), 'kiz'] = 0

    assert(df['m_alg2'].notna().all())

    return df

def dropstuff(df):
    ''' Drop variables not used anymore
    '''

    dropvars = ['belowmini', 'above_thresh_kv', 'above_thresh_rv',
                'gkvrbeit', 'pvrbeit', 'ertragsanteil',
                'handc_pausch',
                'handc_pausch_verh',
                'handc_pausch_verh_sum', 'gross_gde_verh',
                'gross_gde_verh_sum', 'gross_e5_verh',
                'gross_e5_verh_sum', 'vorsorge', 'vorsorge_verh',
                'vorsorge_verh_sum', 'altfreib_verh',
                'altfreib_verh_sum', 'tax_nokfb_verh',
                'tax_nokfb_verh_sum', 'tax_abg_nokfb_verh',
                'tax_abg_nokfb_verh_sum', 'tax_kfb_verh',
                'tax_kfb_verh_sum', 'tax_abg_kfb_verh',
                'tax_abg_kfb_verh_sum', 'abgst_verh',
                'abgst_verh_sum', 'nettax_nokfb',
                'nettax_abg_nokfb', 'nettax_kfb', 'nettax_abg_kfb',
                'minpay', 'pens_steuer', 'm_alg1_sum', 'm_alg1_tu_k',
                'm_transfers_sum', 'm_transfers_tu_k', 'pens_steuer_sum',
                'pens_steuer_tu_k', 'gross_e1_sum', 'gross_e1_tu_k',
                'gross_e4_sum', 'gross_e4_tu_k', 'gross_e5_sum',
                'gross_e5_tu_k', 'gross_e6_sum', 'gross_e6_tu_k',
                'incometax_sum', 'incometax_tu_k',
                'wg_abz', 'wg_abzuege', 'wg_grossY',
                'wg_otherinc', 'wg_incdeduct', 'wgY',
                'max_rent', 'min_rent', 'wgmiete', 'wgheiz', 'mehrbed',
                'bef_zuschlag', 'ind_freib', 'ind_freib_hh', 'maxvermfb',
                'maxvermfb_hh', 'vermfreibetr', 'kiz_ek_regel',
                'kiz_miete', 'kiz_heiz', 'wb_eltern_share', 'kiz_ek_kdu',
                'kiz_ek_relev', 'kiz_ek_max', 'kiz_ek_min',
                'kiz_ek_gross', 'kiz_ek_net', 'kiz_ek_anr',
                'kiz_incrange', 'ar_wg_alg2_ek', 'ar_kiz_alg2_ek',
                'ar_wgkiz_alg2_ek', 'fehlbedarf_base', 'm_alg2_base',
                'fehlbedarf_wg', 'm_alg2_wg', 'fehlbedarf_kiz',
                'm_alg2_kiz', 'fehlbedarf_wgkiz', 'm_alg2_wgkiz',
                'wg_vorrang', 'kiz_vorrang', 'wgkiz_vorrang', 'kiz_temp'
                ]
    df = df.drop(columns=dropvars, axis=1)
    return df

def tb_out(df, ref, graph_path):
    print('-'*80)
    print('TAX BENEFIT AGGREGATES')
    print('-'*80)
    cprint('Revenues', 'red', 'on_white')
    # Incometax over all persons. SV Beiträge too
    #

    for tax in ['gkvbeit_tu_k', 'rvbeit_tu_k', 'pvbeit_tu_k', 'avbeit_tu_k',
                'incometax_tu', 'soli_tu']:
        df['w_sum_'+tax] = df[tax] * df['hweight'] * df['head_tu']
        if tax in ['incometax_tu', 'soli_tu']:
            df.loc[df['zveranl'], 'w_sum_'+tax] = 2 * df['w_sum_'+tax]
        print(tax + " : " + str(df['w_sum_'+tax].sum()/1e9 * 12) + " bn €.")
    cprint('Benefit recipients', 'red', 'on_white')
    for ben in ['m_alg1', 'm_alg2', 'wohngeld', 'kiz']:
        print(ben + " :" + str(df['hweight'][(df[ben] > 0)
                               & (df['head_tu'])].sum()/1e6)
              + " Million Households.")
        df['w_sum_'+ben] = df[ben] * df['hweight'] * df['head_tu']
        print(ben + " : " + str(df['w_sum_'+ben].sum()/1e9 * 12) + " bn €.")

    print('-'*80)

    # Check Income Distribution:
    df['eq_scale'] = (1
                      + 0.5 * np.maximum(
                              (df['hhsize'] - df['child14_num'] - 1), 0)
                      + 0.3 * (df['child14_num']))
    df['dpi_eq'] = df['dpi'] / df['eq_scale']
    df['dpi_eq'].describe()
    plt.clf()
    ax = df['dpi_eq'].plot.kde(xlim=(0, 4000))
    ax.set_title('Distribution of equivalized disp. income ' + str(ref))
    plt.savefig(graph_path + 'dist_dpi_' + ref + '.png')
    print('-'*80)
    print('Gini-Coefficient Disp. Income: ', gini(df['dpi_eq'], df['pweight']))
    print('-'*80)

    return True


