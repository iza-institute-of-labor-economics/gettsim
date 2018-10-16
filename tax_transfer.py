# -*- coding: utf-8 -*-
"""
TAX TRANSFER SIMULATION

Eric Sommer, 2018
"""
from imports import aggr, gini
from termcolor import colored, cprint
from settings import get_settings

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# from numba import jit
import math
import sys


def tax_transfer(df, datayear, taxyear, tb, tb_pens = [], mw = [], hyporun=False):
    """German Tax-Transfer System.

    Arguments:

        - *df*: Input Data Frame
        [- *ref*: Name of Reform]
        - *datayear*: year of SOEP wave
        - *taxyear*: year of reform baseline
        - *tb*: dictionary with tax-benefit parameters
        - *tb_pens*: Parameters for pension calculations
        - *mw*: Mean earnings by year, for pension calculations.
        - *hyporun*: indicator for hypothetical household input (defult: use real SOEP data)


    """

    # if hyporun is False:
    # df = uprate(df, datayear, settings['taxyear'], settings['MAIN_PATH'])

    # Social Insurance Contributions
    df = df.join(
        other=soc_ins_contrib(
            df[[
                'pid',
                'hid',
                'east',
                'm_wage',
                'selfemployed',
                'm_self',
                'm_pensions',
                'age',
                'haskids',
                'pkv'
            ]],
            tb,
            taxyear
        ),
        how='inner'
    )

    # Unemployment benefits
    df['m_alg1'] = ui(df, tb, taxyear)

    # Pension benefits
    if hyporun is False:
        df['pen_sim'] = pensions(df, tb, tb_pens, mw, taxyear)

    # Income Tax
    taxvars = [
        'pid',
        'hid',
        'female',
        'head_tu',
        'tu_id',
        'east',
        'm_wage',
        'selfemployed',
        'm_self',
        'm_pensions',
        'age',
        'pkv',
        'zveranl',
        'child',
        'child_num',
        'renteneintritt',
        'w_hours',
        'm_kapinc',
        'm_vermiet',
        'm_imputedrent',
        'marstat',
        'handcap_dummy',
        'handcap_degree',
        'rvbeit',
        'gkvbeit',
        'pvbeit',
        'avbeit',
        'adult_num_tu',
        'child_num_tu',
        'alleinerz',
        'ineducation'
    ]

    # 5.1 Calculate Taxable income (zve = zu versteuerndes Einkommen)
    df = df.join(
        other=zve(
            df[taxvars],
            tb,
            taxyear
        ),
        how='inner'
    )

    # 5.2 Apply Tax Schedule
    df = df.join(
        other=tax_sched(
            df,
            tb,
            taxyear
        ),
        how='inner'
    )

    # 5.3 Child benefit (Kindergeld). Yes, this belongs to Income Tax
    df = df.join(
        other=kindergeld(
            df[['hid',
                'tu_id',
                'age',
                'ineducation',
                'w_hours',
                'm_wage']],
            tb,
            taxyear
        ),
        how='inner'
    )

    # 5.4 Günstigerprüfung to obtain final income tax due.
    # different call here, because 'kindergeld' is overwritten by the function and
    # needs to be updated. not really elegant I must admit...
    temp = favorability_check(df,
                              tb,
                              taxyear
                              )
    for var in [['incometax_tu',
                 'kindergeld',
                 'kindergeld_hh',
                 'kindergeld_tu']]:
        df[var] = temp[var]

    # 5.5 Solidarity Surcharge
    df = df.join(
        other=soli(
            df,
            tb,
            taxyear
        ),
        how='inner'
    )

    # 6. SOCIAL TRANSFERS / BENEFITS
    # 6.1. Wohngeld, Housing Benefit
    # TODO: rename wohngeld ('wohngeld_basis') until final check.
    df = df.join(
        other=wg(
            df,
            tb,
            taxyear
        ),
        how='inner'
    )
    # 6.2 ALG2, Basic Unemployment Benefit
    df = df.join(
        other=alg2(
            df,
            tb,
            taxyear
        ),
        how='inner'
    )

    # 6.3. Kinderzuschlag, Additional Child Benefit
    temp = kiz(
            df,
            tb,
            taxyear
            )
    for var in [['m_alg2',
                 'kiz',
                 'wohngeld',
                 ]]:
        df[var] = temp[var]

    # 7. Drop unnecessary variables. not necessary anymore.s
    # df = dropstuff(df)

    # 8. Finally, calculate disposable income
    # To be updated!
    df['dpi_ind'] = df[[
        'm_wage',
        'm_kapinc',
        'm_self',
        'm_vermiet',
        'm_imputedrent',
        'm_pensions',
        'm_transfers',
        'kindergeld',
    ]].sum(axis=1) - df[[
        'incometax',
        'soli',
        'abgst',
        'gkvbeit',
        'rvbeit',
        'pvbeit',
        'avbeit'
    ]].sum(axis=1)

    df['dpi_ind_temp'] = df.groupby(['hid'])['dpi_ind'].transform(sum)

    # Finally, add benefits that are defined on the household level
    df['dpi'] = round(
            np.maximum(0,
                       df['dpi_ind_temp'] +
                       df['m_alg2'] +
                       df['wohngeld'] +
                       df['kiz']
                       ),
            2)

    # Control output
    df = df.sort_values(by=['hid', 'tu_id', 'pid'])
    df[['hid',
        'tu_id',
        'pid',
        'head',
        'child',
        'age',
        'm_wage',
        'm_kapinc',
        'm_self',
        'm_vermiet',
        'm_imputedrent',
        'm_pensions',
        'm_transfers',
        'kindergeld',
        'wohngeld',
        'kiz',
        'm_alg2',
        'incometax',
        'soli',
        'abgst',
        'gkvbeit',
        'rvbeit',
        'pvbeit',
        'avbeit',
        'dpi_ind',
        'dpi']].to_excel(pd.ExcelWriter('W:\\izamod\\IZA_DYN_MOD/data/taxben_out.xlsx'),
                         sheet_name='py_out')

    return df


def uprate(df, dy, ty, path):
    '''Uprating monetary values to account for difference between
    data year and simulation year.

    '''

    # define all monetary variables
    # get uprate matrix ,as np.array
    upr = pd.read_excel(path + '/data/params/uprate_cpi.xls',
                        index_col='ausgang')
    factor = upr.loc[dy]['y' + str(ty)]
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


def pensions(df, tb, tb_pens, mw, yr):
    ''' Old-Age Pensions

        models 'Rentenformel':
        https://de.wikipedia.org/wiki/Rentenformel
        https://de.wikipedia.org/wiki/Rentenanpassungsformel
    '''

    cprint('Pensions', 'red', 'on_white')

    r = pd.DataFrame(index=df.index.copy())
    r['byear'] = df['byear']
    r['exper'] = df['exper']
    westost = [~df['east'], df['east']]

    # individuelle monatl. Altersrente (Rentenartfaktor = 1):
    # R = EP * ZF * Rw

    # EP: Entgeltpunkte:
    # Take average values for entgeltpunkte by birth year from external statistics (2015)
    avg_ep = pd.read_excel('data/grv_ep.xlsx', header=3, nrows=40)
    avg_ep = avg_ep[~avg_ep['byear'].isna()]
    r = pd.merge(r, avg_ep[['byear', 'avg_ep']], how = 'outer')

    r['EP'] = r['avg_ep'] * r['exper']
    # Add values for current year: ratio of own wage (up to the threshold) to the mean wage
    r['EP'] = r['EP'] + np.select(
        westost, [np.minimum(df['m_wage'], tb['rvmaxekw']) / mw['meanwages'][yr],
                  np.minimum(df['m_wage'], tb['rvmaxeko']) / mw['meanwages'][yr]]
    )
    # ZF: Zugangsfaktor. Depends on the age of entering pensions
    r['regelaltersgrenze'] = 65
    # If born after 1947, each birth year raises the age threshold by one month.
    r.loc[r['byear'] > 1947, 'regelaltersgrenze'] = np.minimum(67,
                                                     ((r['byear'] - 1947) / 12) + 65)
    # For each year entering earlier (later) than the statutory retirement age,
    # you get a penalty (reward) of 3.6 pp.
    r['ZF'] = ((df['age'] - r['regelaltersgrenze']) * .036) + 1

    # Rentenwert: The monetary value of one 'entgeltpunkt'.
    # This depends, among others, of past developments. Hence, some calculations have been made
    # in the data preparation.
    lohnkomponente = mw['meanwages'][yr-1] / (mw['meanwages'][yr-2] *
                                              ((mw['meanwages'][yr-2] / mw['meanwages'][yr-3]) /
                                               (mw['meanwages_sub'][yr-2] /
                                                mw['meanwages_sub'][yr-3])
                                               )
                                              )

    riesterfaktor = (
                    (100 - tb_pens['ava'][yr-1] - tb_pens['rvbeitrag'][yr-1]) /
                    (100 - tb_pens['ava'][yr-2] - tb_pens['rvbeitrag'][yr-2])
                    )
    # Rentnerquotienten
    rq = {}
    for t in [1, 2]:
        rq[t] = (
                (tb_pens['rentenvol'][yr-t] / tb_pens['eckrente'][yr-t]) /
                (tb_pens['beitragsvol'][yr-t] / (tb_pens['rvbeitrag'][yr-t] / 100 *
                                                 tb_pens['eckrente'][yr-t])
                )
               )
    # Nachhaltigskeitsfaktor
    nachhfaktor = 1 + (
                       (1 - (rq[1]/rq[2])) *
                        tb_pens['alpha'][yr]
                       )
    # use external (SOEP) or internal value for rentenwert?
    if yr <= 2017:
        rentenwert = tb_pens['rentenwert_ext'][yr]
    else:
        # Rentenwert must not be lower than in the previous year.
        rentenwert = (tb_pens['rentenwert_ext'][yr-1] *
                         min(1,
                             lohnkomponente *
                             riesterfaktor *
                             nachhfaktor
                             )
                      )
        print('Änderung des Rentenwerts: ' + str(min(1,
                                                     lohnkomponente *
                                                     riesterfaktor *
                                                     nachhfaktor
                                                     )))

    # use all three components for Rentenformel.
    # There is an additional 'Rentenartfaktor', equal to 1 for old-age pensions.
    # It's called 'pensions_sim' to emphasize that this is simulated.
    r['pensions_sim'] = np.maximum(0,
                                   round(r['EP'] * r['ZF'] * rentenwert, 2)
                                   )

    return r['pensions_sim']


def soc_ins_contrib(df, tb, yr):
    '''Calculates Social Insurance Contributions

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

    cprint('Social Insurance Contributions...', 'red', 'on_white')

    # initiate dataframe, indices must be identical
    ssc = pd.DataFrame(index=df.index.copy())

    # a couple of definitions
    westost = [~df['east'], df['east']]
    # 'Bezugsgröße'
    ssc['bezgr'] = np.select(
        westost,
        [tb['bezgr_o'], tb['bezgr_w']]
    )
    ssc['kinderlos'] = ((~df['haskids']) & (df['age'] > 22))
    ssc['belowmini'] = 1 == np.select(
        westost,
        [df['m_wage'] < tb['mini_grenzew'], df['m_wage'] < tb['mini_grenzeo']]
    )
    ssc['above_thresh_kv'] = 1 == np.select(
        westost,
        [df['m_wage'] > tb['kvmaxekw'], df['m_wage'] > tb['kvmaxeko']]
    )
    ssc['above_thresh_rv'] = 1 == np.select(
        westost,
        [df['m_wage'] > tb['rvmaxekw'], df['m_wage'] > tb['rvmaxeko']]
    )

    # Standard rates under consideration of thresholds
    # need to differentiate between East and West Germany
    # Old-Age Pension Insurance / Rentenversicherung

    # This is probably the point where Entgeltpunkte should be updated as well.
    ssc['rvbeit'] = tb['grvbs'] * np.minimum(
        df['m_wage'],
        np.select(
            westost,
            [tb['rvmaxekw'], tb['rvmaxeko']]
        )
    )
    # Unemployment Insurance / Arbeitslosenversicherung
    ssc['avbeit'] = tb['alvbs'] * np.minimum(
        df['m_wage'],
        np.select(
            westost,
            [tb['rvmaxekw'], tb['rvmaxeko']]
        )
    )
    # Health Insurance for Employees (GKV)
    ssc['gkvbeit'] = tb['gkvbs_an'] * np.minimum(
        df['m_wage'],
        np.select(
            westost,
            [tb['kvmaxekw'], tb['kvmaxeko']]
        )
    )
    # Care Insurance / Pflegeversicherung
    ssc['pvbeit'] = tb['gpvbs'] * np.minimum(
        df['m_wage'],
        np.select(
            westost,
            [tb['kvmaxekw'], tb['kvmaxeko']]
        )
    )
    # If you are above 23 and without kids, you have to pay a higher rate
    ssc.loc[ssc['kinderlos'], 'pvbeit'] = (tb['gpvbs'] + tb['gpvbs_kind']) * np.minimum(
        df['m_wage'],
        np.select(
            westost,
            [tb['kvmaxekw'], tb['kvmaxeko']]
        )
    )

    # Gleitzone / Midi-Jobs
    if yr >= 2003:
        # For midijobs, the rate is not calculated on the wage,
        # but on the 'bemessungsentgelt'
        # Contributions are usually shared equally by employee (AN) and
        # employer (AG). We are actually not interested in employer's contributions,
        # but we need them here as an intermediate step
        AN_anteil = tb['grvbs'] + tb['gpvbs'] + tb['alvbs'] + tb['gkvbs_an']
        AG_anteil = tb['grvbs'] + tb['gpvbs'] + tb['alvbs'] + tb['gkvbs_ag']
        DBSV = AN_anteil + AG_anteil
        pauschmini = tb['mini_ag_gkv'] + tb['mini_ag_grv'] + tb['stpag']
        F = round(pauschmini / DBSV, 4)
        # always needs to differentiate between east and west.
        # This used to be relevant until 1999
        bemes_west = (F * tb['mini_grenzew'] +
                      ((tb['midi_grenze'] / (tb['midi_grenze'] - tb['mini_grenzew'])) -
                       (tb['mini_grenzew'] / ((tb['midi_grenze'] - tb['mini_grenzew'])) * F)
                       ) *
                      (df['m_wage'] - tb['mini_grenzew'])
                      )

        bemes_ost = (F * tb['mini_grenzeo'] +
                     ((tb['midi_grenze']/(tb['midi_grenze'] - tb['mini_grenzeo'])) -
                      (tb['mini_grenzeo'] / ((tb['midi_grenze'] - tb['mini_grenzeo'])) * F)) *
                     (df['m_wage'] - tb['mini_grenzeo'])
                     )
        ssc['bemessungsentgelt'] = np.select(westost, [bemes_west, bemes_ost])
        # This checks whether wage is in the relevant range
        ssc['in_gleitzone'] = df['m_wage'].between(
                            np.select(westost,
                                      [tb['mini_grenzew'],
                                       tb['mini_grenzeo']
                                       ]),
                                                   tb['midi_grenze']
                                                    )
        # Again, all branches of social insurance
        # First total amount, then employer, then employee

        # Old-Age Pensions
        ssc['gb_rv'] = 2 * tb['grvbs'] * ssc['bemessungsentgelt']
        ssc.loc[ssc['in_gleitzone'], 'ag_rvbeit'] = tb['grvbs'] * df['m_wage']
        ssc.loc[ssc['in_gleitzone'], 'rvbeit'] = ssc['gb_rv'] - ssc['ag_rvbeit']

        # Health
        ssc['gb_gkv'] = ((tb['gkvbs_an'] + tb['gkvbs_ag']) * ssc['bemessungsentgelt'])
        ssc.loc[ssc['in_gleitzone'], 'ag_gkvbeit'] = tb['gkvbs_ag'] * df['m_wage']
        ssc.loc[ssc['in_gleitzone'], 'gkvbeit'] = ssc['gb_gkv'] - ssc['ag_gkvbeit']

        # Unemployment
        ssc['gb_alv'] = 2 * tb['alvbs'] * ssc['bemessungsentgelt']
        ssc.loc[ssc['in_gleitzone'], 'ag_avbeit'] = tb['alvbs'] * df['m_wage']
        ssc.loc[ssc['in_gleitzone'], 'avbeit'] = ssc['gb_alv'] - ssc['ag_avbeit']

        # Long-Term Care
        ssc['gb_pv'] = 2 * tb['gpvbs'] * ssc['bemessungsentgelt']
        ssc.loc[ssc['in_gleitzone'], 'ag_pvbeit'] = tb['gpvbs'] * df['m_wage']
        ssc.loc[ssc['in_gleitzone'], 'pvbeit'] = (
            ssc['gb_pv'] - ssc['ag_pvbeit'] +
            (ssc['kinderlos'] * tb['gpvbs_kind'] * ssc['bemessungsentgelt'])
        )

        # Drop intermediate variables
        ssc = ssc.drop(
            [
                'gb_rv',
                'gb_gkv',
                'gb_alv',
                'gb_pv',
                'bemessungsentgelt'
            ],
            axis=1
        )
    # END 'GLEITZONE'

    # check whether we are below 450€...set to zero
    for beit in [
        'rvbeit',
        'gkvbeit',
        'avbeit',
        'pvbeit',
        'ag_rvbeit',
        'ag_gkvbeit',
        'ag_avbeit',
        'ag_pvbeit'
    ]:
        ssc.loc[ssc['belowmini'], beit] = 0

    # Self-employed may insure via the public health insurance
    # In that case, they pay the full contribution (employer + employee),
    # which is either assessed on their self-employemtn income or 3/4 of the 'Bezugsgröße'
    ssc.loc[(df['selfemployed']) & (~df['pkv']),
            'gkvbeit'] = ((tb['gkvbs_an'] + tb['gkvbs_ag'])
                          * np.minimum(df['m_self'],
                          0.75 * np.select(westost,
                                           [tb['bezgr_w'], tb['bezgr_o']])))
    # Same holds for care insurance
    ssc.loc[(df['selfemployed']) &
            (~df['pkv']),
            'pvbeit'] = ((2 * tb['gpvbs'] + np.select(
                        [ssc['kinderlos'], ~ssc['kinderlos']],
                        [tb['gpvbs_kind'], 0])
                          ) *
                np.minimum(df['m_self'], 0.75 * np.select(westost,
                                                          [tb['bezgr_w'], tb['bezgr_o']])
                           )
                         )
    # Health insurance for pensioners; they pay the standard health insurance rate...
    ssc['gkvrbeit'] = (tb['gkvbs_an'] *
                       np.minimum(df['m_pensions'],
                                  np.select(westost,
                                            [tb['kvmaxekw'],
                                             tb['kvmaxeko']])))
    # but twice the care insurance rate.
    ssc['pvrbeit'] = (2 * tb['gpvbs'] *
                      np.minimum(df['m_pensions'],
                                 np.select(westost,
                                           [tb['kvmaxekw'],
                                            tb['kvmaxeko']])))
    ssc.loc[ssc['kinderlos'],
            'pvrbeit'] = ((2 * tb['gpvbs'] + tb['gpvbs_kind']) *
                          np.minimum(df['m_pensions'],
                                     np.select(westost,
                                               [tb['kvmaxekw'],
                                                tb['kvmaxeko']])))

    ssc['gkvbeit'] = ssc['gkvbeit'] + ssc['gkvrbeit']
    ssc['pvbeit'] = ssc['pvbeit'] + ssc['pvrbeit']

    # Sum of Social Insurance Contributions (for employees)
    ssc['svbeit'] = ssc[['rvbeit', 'avbeit', 'gkvbeit', 'pvbeit']].sum(axis=1)

    return ssc[['svbeit', 'rvbeit', 'avbeit', 'gkvbeit', 'pvbeit']]


def ui(df, tb, taxyear):
    '''Return the Unemployment Benefit based on
    employment status and income from previous years.

    '''

    westost = [~df['east'], df['east']]

    m_alg1 = df['alg_soep'].fillna(0)
    # Months of entitlement
    mts_ue = (
        df['months_ue'] +
        df['months_ue_l1'] +
        df['months_ue_l2']
    )
    # Relevant wage is capped at the contribution thresholds
    alg_wage = np.select(
        westost,
        [
            np.minimum(tb['rvmaxekw'], df['m_wage_l1']),
            np.minimum(tb['rvmaxeko'], df['m_wage_l1'])
        ]
    )

    ui_wage = np.maximum(0, alg_wage - np.maximum(df['m_wage'] - tb['alg1_frei'], 0))

    # BENEFIT AMOUNT
    # Check Eligiblity.
    # Then different rates for parent and non-parents
    # Take into account actual wages
    # Do this only for people for which we don't observe UI payments in SOEP,
    # assuming that their information is more reliable
    # (rethink this for the dynamic model)
    # there are different replacement rates depending on presence of children
    m_alg1.loc[
        (mts_ue > 0) &
        (mts_ue <= 12) &
        (df['age'] < 65) &
        (df['m_pensions'] == 0) &
        (df['alg_soep'] == 0) &
        (df['w_hours'] < 15)
    ] = ui_wage * np.select(
        [df['child_num_tu'] == 0, df['child_num_tu'] > 0],
        [tb['agsatz0'], tb['agsatz1']]
    )

    print('ALG 1 recipients according to SOEP:' + str(df['counter'][df['alg_soep'] > 0].sum()))
    print(
        'Additional ALG 1 recipients from simulation:' +
        str(df['counter'][m_alg1 > 0].sum() - df['counter'][df['alg_soep'] > 0].sum())
    )

    return m_alg1


# @jit(nopython=True)
def zve(df, tb, yr):
    '''Calculate taxable income (zve = zu versteuerndes Einkommen)
        In fact, you need several taxable incomes because of
        - child allowance vs. child benefit
        - abgeltungssteuer vs. taxing capital income in the tariff
        It's always the most favorable for the taxpayer, but you know that only after applying
        the tax schedule
    '''
    cprint('Calculate Taxable Income...', 'red', 'on_white')
    # Kapitaleinkommen im Tarif versteuern oder nicht?
    kapinc_in_tarif = yr < 2009
    westost = [~df['east'], df['east']]
    married = [df['zveranl'], ~df['zveranl']]
    # create output dataframe and transter some important variables
    zve = pd.DataFrame(index=df.index.copy())
    for v in ['hid', 'tu_id', 'zveranl']:
        zve[v] = df[v]

    # The share of pensions subject to income taxation
    zve['ertragsanteil'] = 0
    df.loc[df['renteneintritt'] <= 2004, 'ertragsanteil'] = 0.27
    df.loc[df['renteneintritt'].between(2005, 2020),
           'ertragsanteil'] = 0.5 + 0.02 * (df['renteneintritt'] - 2005)
    df.loc[df['renteneintritt'].between(2021, 2040),
           'ertragsanteil'] = 0.8 + 0.01 * (df['renteneintritt'] - 2020)
    df.loc[df['renteneintritt'] >= 2041, 'ertragsanteil'] = 1

    # Werbungskosten und Sonderausgaben
    zve['werbung'] = tb['werbung'] * (df['m_wage'] > 0) * (~df['child'])
    zve['sonder'] = (~df['child']) * tb['sonder']
    ####################################################
    # Income components on annual basis
    # Income from Self-Employment
    zve['gross_e1'] = 12 * df['m_self']
    # Earnings
    zve['gross_e4'] = np.maximum((12 * df['m_wage']) - zve['werbung'], 0)
    # Minijob-Grenze beachten
    zve.loc[df['m_wage'] <= np.select(westost,
                                     [tb['mini_grenzew'],
                                      tb['mini_grenzeo']]),
           'gross_e4'] = 0

    # Capital Income
    zve['gross_e5'] = np.maximum((12 * df['m_kapinc']), 0)
    # Income from rents
    zve['gross_e6'] = 12 * df['m_vermiet']
    # Others (Pensions)
    zve['gross_e7'] = np.maximum(
        12 * (zve['ertragsanteil'] * df['m_pensions']) - tb['vorsorgpausch'], 0
    )
    # Sum of incomes
    zve['gross_gde'] = zve[['gross_e1', 'gross_e4', 'gross_e6', 'gross_e7']].sum(axis=1)
    # If capital income tax with tariff, add it but account for exemptions
    if kapinc_in_tarif:
        zve['gross_gde'] = (
            zve['gross_gde'] +
            np.maximum(zve['gross_e5'] - tb['spsparf'] - tb['spwerbz'], 0)
        )
    # Gross (market) income <> sum of incomes...
    zve['m_brutto'] = df[['m_self',
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
    zve['handc_pausch'] = np.select(hc_degrees, hc_pausch)
    zve['handc_pausch'].fillna(0, inplace=True)

    # Aggregate several incomes on the taxpayer couple
    for inc in ['m_wage', 'rvbeit', 'gkvbeit', 'avbeit', 'pvbeit']:
        zve[inc+'_tu_k'] = aggr(df, inc, True)
        zve[inc+'_tu'] = aggr(df, inc, False)
    for inc in ['sonder', 'handc_pausch', 'gross_gde', 'gross_e1',
                'gross_e4', 'gross_e5', 'gross_e6', 'gross_e7']:
        zve[inc+'_tu'] = aggr(zve, inc, False)

    # TAX DEDUCTIONS
    # 'Vorsorgeaufwendungen': Deduct part of your social insurance contributions
    # from your taxable income
    # This regulation has been changed often in recent years. In order not to make anyone
    # worse off, the old regulation was maintained. Nowadays the older regulations
    # don't play a large role (i.e. the new one is more beneficial most of the times)
    # but they'd need to be implemented if earlier years are modelled.
    # Vorsorgeaufwendungen until 2004
    # TODO
    # Vorsorgeaufwendungen since 2010
    # § 10 (3) EStG
    # The share of deductable pension contributions increases each year by 2 pp.
    # ('nachgelagerte Besteuerung'). In 2018, it's 86%. Add other contributions;
    # 4% from health contributions are not deductable

    # only deduct pension contributions up to the ceiling. multiply by 2
    # because it's both employee and employer contributions.
    zve['rvbeit_vors'] = np.minimum(2 * df['rvbeit'],
                                    2 * tb['grvbs'] * np.select(westost,
                                              [tb['rvmaxekw'], tb['rvmaxeko']])
                                    )
    # calculate x% of relevant employer and employee contributions
    # then subtract employer contributions
    zve['vorsorge2010'] = ~df['child'] * ((0.6 +
                          0.02 * (np.minimum(yr, 2025) - 2005)) * (12 * zve['rvbeit_vors']) -
                          (12 * 0.5 * zve['rvbeit_vors']) +
                          (12 * (df['pvbeit'] +
                                 df['avbeit'] +
                                 0.96 * df['gkvbeit'])
                           ))

    # zve['vorsorge2010'] = np.select(married, [vorsorg2010_married, vorsorg2010_single])

    # TO DO: check various deductions against each other (when modelled)
    zve['vorsorge'] = zve['vorsorge2010']
    # Summing up not necessary! they already got half
    zve['vorsorge_tu'] = aggr(zve, 'vorsorge', False)
    # Tax Deduction for elderly ("Altersentlastungsbetrag")
    # does not affect pensions.
    zve['altfreib'] = 0
    zve.loc[df['age'] > 64, 'altfreib'] = np.minimum(
                                         tb['altentq'] *
                                         12 * (df['m_wage'] +
                                               np.maximum(0, df[['m_kapinc',
                                                                 'm_self',
                                                                 'm_vermiet']].sum(axis=1))
                                               ),
                                         tb['altenth']
                                                     )
    zve['altfreib_tu'] = aggr(zve, 'altfreib', False)
    # Entlastungsbetrag für Alleinerziehende. Deduction for Single Parents.
    # Used to be called 'Haushaltsfreibetrag'
    zve['hhfreib'] = 0
    if yr < 2015:
        zve.loc[df['alleinerz'], 'hhfreib'] = tb['hhfreib']
    if yr >= 2015:
        zve.loc[df['alleinerz'], 'hhfreib'] = (tb['hhfreib'] + (df['child_num_tu'] - 1) * 240)
    # Child Allowance (Kinderfreibetrag)
    # Single Parents get half the allowance, parents get the full amount but share it.
    # Note that this is an assumption, parents can share them differently.
    zve['kifreib'] = 0
    zve['kifreib'] = (0.5 * tb['ch_allow'] *
                      df['child_num_tu'] * ~df['child'])
    # Taxable income (zve)
    # For married couples, household income is split between the two.
    # Without child allowance / Ohne Kinderfreibetrag (nokfb):
    zve['zve_nokfb'] = 0
    zve.loc[~df['zveranl'], 'zve_nokfb'] = np.maximum(
        0,
        zve['gross_gde'] -
        zve['vorsorge'] -
        zve['sonder'] -
        zve['handc_pausch'] -
        zve['hhfreib'] -
        zve['altfreib']
    )
    zve.loc[df['zveranl'], 'zve_nokfb'] = 0.5 * np.maximum(
        0,
        zve['gross_gde_tu'] -
        zve['vorsorge_tu'] -
        zve['sonder_tu'] -
        zve['handc_pausch_tu'] -
        zve['hhfreib'] -
        zve['altfreib_tu']
    )
    # No Child Allowance, but with capital income
    zve.loc[~df['zveranl'], 'zve_abg_nokfb'] = np.maximum(
        0,
        zve['gross_gde'] +
        np.maximum(0, zve['gross_e5'] - tb['spsparf'] - tb['spwerbz']) -
        zve['vorsorge'] -
        zve['sonder'] -
        zve['handc_pausch'] -
        zve['hhfreib'] -
        zve['altfreib']
    )
    zve.loc[df['zveranl'], 'zve_abg_nokfb'] = 0.5 * np.maximum(
        0,
        zve['gross_gde_tu'] +
        np.maximum(0, zve['gross_e5_tu'] - 2 * tb['spsparf'] - 2 * tb['spwerbz']) -
        zve['vorsorge_tu'] -
        zve['sonder_tu'] -
        zve['handc_pausch_tu'] -
        zve['hhfreib'] -
        zve['altfreib_tu']
    )

    # Subtract Child allowance to get alternative taxable incomes
    zve['zve_kfb'] = np.maximum(zve['zve_nokfb'] - zve['kifreib'], 0)
    zve['zve_abg_kfb'] = np.maximum(zve['zve_abg_nokfb'] - zve['kifreib'], 0)

    return zve[['zve_nokfb', 'zve_abg_nokfb', 'zve_kfb', 'zve_abg_kfb', 'kifreib',
                'gross_e1', 'gross_e4', 'gross_e5', 'gross_e6', 'gross_e7',
                'gross_e1_tu', 'gross_e4_tu', 'gross_e5_tu', 'gross_e6_tu', 'gross_e7_tu',
                'ertragsanteil']]


def tax_sched(df, tb, yr):
    ''' Applies the income tax tariff for various definitions of taxable income
        also calculates tax on capital income (Abgeltungssteuer)
    '''
    cprint('Income Tax...', 'red', 'on_white')
    # Before 2009, no separate taxation of capital income
    if (yr < 2009):
        inclist = ['nokfb', 'kfb']
    else:
        inclist = ['nokfb', 'abg_nokfb', 'kfb', 'abg_kfb']

    def tarif(x, tb):
        ''' The German Income Tax Tariff
            modelled only after 2002 so far
            It's not calculated as in the tax code, but rather a gemoetric decomposition of the
            area beneath the marginal tax rate function.
            This facilitates the implementation of alternative tax schedules
        '''
        y = int(tb['yr'])
        if y < 2002:
            print("Income Tax Pre 2002 not yet modelled!")
        if y > 2002:
            t = 0
            if tb['G'] < x <= tb['M']:
                t = ((((tb['t_m'] - tb['t_e']) /
                       (2 * (tb['M'] - tb['G']))) * (x - tb['G']) +
                      tb['t_e']
                      ) * (x - tb['G'])
                     )
            if tb['M'] < x <= tb['S']:
                t = ((((tb['t_s'] - tb['t_m']) /
                       (2 * (tb['S'] - tb['M']))
                       ) * (x-tb['M']) +
                      tb['t_m']
                      ) * (x - tb['M']) +
                     (tb['M'] - tb['G']) * ((tb['t_m'] + tb['t_e']) / 2)
                     )
            if(x > tb['S']):
                t = ((tb['t_s'] * x - tb['t_s'] * tb['S'] +
                      ((tb['t_s'] + tb['t_m']) / 2) * (tb['S'] - tb['M']) +
                      ((tb['t_m'] + tb['t_e']) / 2) * (tb['M'] - tb['G'])
                      )
                     )
            if x > tb['R']:
                t = t + (tb['t_r'] - tb['t_s']) * (x - tb['R'])
            t = round(t, 2)
        return t

    cprint('Tax Schedule...', 'red', 'on_white')
    # create ts dataframe and copy three important variables
    ts = pd.DataFrame(index=df.index.copy())
    for v in ['hid', 'tu_id', 'zveranl']:
        ts[v] = df[v]

    for inc in inclist:
        # apply the tariff. Need np.vectorize for handing a series
        # to the function along with other parameters.
        # need to convert this one to panda series...
        ts['tax_'+inc] = np.vectorize(tarif)(df['zve_'+inc], tb)
        ts['tax_'+inc+'_tu'] = aggr(ts, 'tax_'+inc, False)
    ################

    # Abgeltungssteuer
    ts['abgst'] = 0
    if (yr >= 2009):
        ts.loc[~ts['zveranl'], 'abgst'] = (
                tb['abgst'] * np.maximum(df['gross_e5'] -
                                         tb['spsparf'] -
                                         tb['spwerbz'], 0))
        ts.loc[ts['zveranl'], 'abgst'] = (
                0.5 * tb['abgst'] * np.maximum(df['gross_e5_tu'] -
                                               2 * (tb['spsparf'] +
                                                    tb['spwerbz']), 0))
    ts['abgst_tu'] = aggr(ts, 'abgst')
    # drop some vars to avoid duplicates in join. More elegant way would be to modifiy joint
    # command above.
    ts = ts.drop(columns=['zveranl', 'hid', 'tu_id'], axis=1)
    # Here, I don't specify exactly the return variables because they may differ by year.
    return ts


def kindergeld(df, tb, yr):
    """ Child Benefit
        Basic Amount for each child, hours restriction applies
    """
    kg = pd.DataFrame(index=df.index.copy())
    kg['tu_id'] = df['tu_id']
    kg['eligible'] = 1
    if yr > 2011:
        kg['eligible'] = kg['eligible'].where(
            (df['age'] <= tb['kgage']) &
            (df['w_hours'] <= 20) &
            (df['ineducation']), 0
        )
    else:
        kg['eligible'] = kg['eligible'].where(
            (df['age'] <= tb['kgage']) &
            (df['m_wage'] <= tb['kgfreib'] / 12) &
            (df['ineducation']), 0)

    kg['child_count'] = kg.groupby(['tu_id'])['eligible'].cumsum()

    kg_amounts = {1: tb['kgeld1'], 2: tb['kgeld2'], 3: tb['kgeld3'], 4: tb['kgeld4']}
    kg['kindergeld_basis'] = kg['child_count'].replace(kg_amounts)
    # ES: the where method replaces all values for which the condition is FALSE!!
    kg['kindergeld_basis'] = kg['kindergeld_basis'].where(kg['child_count'] < 4, tb['kgeld4'])
    kg['kindergeld_tu_basis'] = kg.groupby('tu_id')['kindergeld_basis'].transform(sum)

    # kg.drop(['child_count', 'eligible', 'kindergeld'], axis=1, inplace=True)

    return kg[['kindergeld_basis', 'kindergeld_tu_basis']]


def favorability_check(df, tb, yr):
    """ 'Higher-Yield Tepst'
        compares the tax burden that results from various definitions of the tax base
        Most importantly, it compares the tax burden without applying the child allowance (_nokfb)
        AND receiving child benefit with the tax burden including the child allowance (_kfb), but
        without child benefit. The most beneficial (for the household) is chocen.
        If child allowance is claimed, kindergeld is set to zero
        A similar check applies to whether it is more profitable to
        tax capital incomes with the standard 25% rate or to include it in the tariff.
    """
    fc = pd.DataFrame(index=df.index.copy())
    fc['tu_id'] = df['tu_id']
    fc['hid'] = df['hid']
    fc['pid'] = df['pid']
    fc['kindergeld'] = df['kindergeld_basis']
    fc['kindergeld_tu'] = df['kindergeld_tu_basis']

    cprint('Günstigerprüfung...', 'red', 'on_white')
    if (yr < 2009):
        inclist = ['nokfb', 'kfb']
    else:
        inclist = ['nokfb', 'abg_nokfb', 'kfb', 'abg_kfb']
    '''
    df = df.sort_values(by=['hid', 'tu_id', 'pid'])
    df[['hid', 'tu_id', 'child', 'tax_nokfb_tu', 'tax_kfb_tu',
              'kindergeld_basis' ,'kindergeld_tu_basis']].to_excel('Z:/test/fav_check.xlsx')
    '''
    for inc in inclist:
        # Nettax is defined on the maximum within the tax unit.
        # Reason: This way, kids get assigned the tax payments of their parents,
        # ensuring correct treatment afterwards
        fc['tax_'+inc+'_tu'] = df['tax_'+inc+'_tu']
        fc = fc.join(fc.groupby(['tu_id'])['tax_'+inc+'_tu'].max(),
                     on=['tu_id'], how='left', rsuffix='_max')
        fc = fc.rename(columns={'tax_'+inc+'_tu_max': 'nettax_' + inc})
        # for those tax bases without capital taxes in tariff,
        # add abgeltungssteuer
        if 'abg' not in inc:
            fc['nettax_' + inc] = fc['nettax_'+inc] + df['abgst_tu']
        # For those tax bases without kfb, subtract kindergeld.
        # Before 1996, both child allowance and child benefit could be claimed
        if ('nokfb' in inc) | (yr <= 1996):
            fc['nettax_' + inc] = (fc['nettax_'+inc] -
                                   (12 * df['kindergeld_tu_basis']))
    # get the maximum income, i.e. the minimum payment burden
    fc['minpay'] = fc.filter(regex='nettax').min(axis=1)
    # relevant tax base. not really needed...
    # fc['tax_income'] = 0
    # relevant incometax associated with this tax base
    fc['incometax_tu'] = 0
    # secures that every tax unit gets 'treated'
    fc['abgehakt'] = False
    for inc in inclist:
        '''
        fc.loc[(fc['minpay'] == fc['nettax_' + inc])
               & (~fc['abgehakt'])
               & (~df['child']),
               'tax_income'] = df['zve_'+inc]
        '''
        # Income Tax in monthly terms! And write only to parents
        fc.loc[(fc['minpay'] == fc['nettax_' + inc])
               & (~fc['abgehakt'])
               & (~df['child']),
               'incometax_tu'] = df['tax_'+inc+'_tu'] / 12
        # set kindergeld to zero if necessary
        if (not ('nokfb' in inc)) | (yr <= 1996):
            fc.loc[(fc['minpay'] == fc['nettax_' + inc])
                   & (~fc['abgehakt']),
                   'kindergeld'] = 0
            fc.loc[(fc['minpay'] == fc['nettax_' + inc])
                   & (~fc['abgehakt']),
                   'kindergeld_tu'] = 0
        if ('abg' in inc):
            fc.loc[(fc['minpay'] == fc['nettax_' + inc])
                   & (~fc['abgehakt']),
                   'abgst'] = 0
            fc.loc[(fc['minpay'] == fc['nettax_' + inc])
                   & (~fc['abgehakt']),
                   'abgst_tu'] = 0
        fc.loc[(fc['minpay'] == fc['nettax_' + inc]), 'abgehakt'] = True

    # Aggregate Child benefit on the household.
    fc = fc.join(
             fc.groupby(['hid'])['kindergeld'].sum(),
             on=['hid'], how='left', rsuffix='_hh')

    # Control output
    # df.to_excel(pd.ExcelWriter(data_path+'check_güsntiger.xlsx'),sheet_name='py_out',columns= ['tu_id','child','zveranl','minpay','incometax','abgehakt','nettax_abg_kfb_tu', 'zve_abg_kfb_tu', 'tax_abg_kfb_tu', 'nettax_abg_kfb_tu', 'zve_abg_kfb_tu', 'tax_abg_kfb_tu', 'nettax_abg_kfb_tu', 'zve_abg_kfb_tu', 'tax_abg_kfb_tu', 'nettax_abg_kfb_tu', 'zve_abg_kfb_tu', 'tax_abg_kfb_tu'],na_rep='NaN',freeze_panes=(0,1))
    # pd.to_pickle(df,data_path+ref+'/taxben_check')
    # df.to_excel(pd.ExcelWriter(data_path+'check_tax_incomes.xlsx'),sheet_name='py_out',columns=['hid','pid','age','female','child','zve_nokfb','zve_kfb','tax_nokfb','tax_kfb','gross_e1','gross_e4','gross_e5','gross_e6','gross_e7','gross_gde'],na_rep='NaN',freeze_panes=(0,1))
    return fc[['hid', 'pid', 'incometax_tu',
               'kindergeld', 'kindergeld_hh', 'kindergeld_tu']]


def soli(df, tb, yr):
    """ Solidarity Surcharge ('soli')
        on top of the income tax and capital income tax.
        No Soli if income tax due is below € 920 (solifreigrenze)
        Then it increases with 0.2 marginal rate until 5.5% (solisatz)
        of the incometax is reached.
        As opposed to the 'standard' income tax,
        child allowance is always deducted for soli calculation
    """

    soli = pd.DataFrame(index=df.index.copy())
    soli['tu_id'] = df['tu_id']
    soli['hid'] = df['hid']
    soli['pid'] = df['pid']

    cprint('Solidarity Surcharge...', 'red', 'on_white')

    if yr >= 1991:
        if yr >= 2009:
            soli['solibasis'] = df['tax_kfb_tu'] + df['abgst_tu']
        else:
            soli['solibasis'] = df['tax_abg_kfb_tu']
        # Soli also in monthly terms. only for adults
        soli['soli_tu'] = (np.minimum(tb['solisatz'] * soli['solibasis'],
                                      np.maximum(0.2 * (soli['solibasis'] -
                                                 tb['solifreigrenze']), 0)
                                      )
                                      * ~df['child'] * (1/12)
                           )

    # Assign income Tax + Soli to individuals
    soli['incometax'] = np.select([df['zveranl'], ~df['zveranl']],
                                  [df['incometax_tu'] / 2, df['incometax_tu']])
    soli['soli'] = np.select([df['zveranl'], ~df['zveranl']],
                             [soli['soli_tu'] / 2, soli['soli_tu']])
    return soli[['incometax', 'soli', 'soli_tu']]


def wg(df, tb, yr):
    """ Housing benefit / Wohngeld
        Social benefit for recipients with income above basic social assistance
        Computation is very complicated, accounts for household size, income, actual rent
        and differs on the municipality level ('Mietstufe' (1,...,6)).
        As we don't have information on the last item, we assume 'Mietstufe' 3, corresponding
        to an average level
    """
    cprint('Wohngeld...', 'red', 'on_white')

    # Benefit amount depends on parameters M (rent) and Y (income) (§19 WoGG)
    # Calculate them on the level of the tax unit

    wg = pd.DataFrame(index=df.index.copy())
    wg['hid'] = df['hid']
    wg['tu_id'] = df['tu_id']
    # Start with income revelant for the housing beneift
    # tax-relevant share of pensions
    wg['pens_steuer'] = df['ertragsanteil'] * df['m_pensions']
    for inc in ['m_alg1', 'm_transfers', 'gross_e1',
                'gross_e4', 'gross_e5', 'gross_e6',
                'incometax', 'rvbeit', 'gkvbeit']:
        wg[inc+'_tu_k'] = aggr(df, inc, True)

    wg['pens_steuer_tu_k'] = aggr(wg, 'pens_steuer', True)

    # There share of income to be deducted is 0/10/20/30%, depending on whether household is
    # subject to income taxation and/or payroll taxes
    wg['wg_abz'] = ((wg['incometax_tu_k'] > 0) * 1 +
                    (wg['rvbeit_tu_k'] > 0) * 1 +
                    (wg['gkvbeit_tu_k'] > 0) * 1)

    wg_abz_amounts = {0: tb['wgpabz0'],
                      1: tb['wgpabz1'],
                      2: tb['wgpabz2'],
                      3: tb['wgpabz3']}

    wg['wg_abzuege'] = wg['wg_abz'].replace(wg_abz_amounts)

    # Relevant income is market income + transfers...
    wg['wg_grossY'] = (np.maximum(wg['gross_e1_tu_k']/12, 0)
                       + np.maximum(wg['gross_e4_tu_k']/12, 0)
                       + np.maximum(wg['gross_e5_tu_k']/12, 0)
                       + np.maximum(wg['gross_e6_tu_k']/12, 0))

    wg['wg_otherinc'] = (wg['m_alg1_tu_k'] +
                         wg['m_transfers_tu_k'] +
                         (wg['pens_steuer_tu_k']))

    # ... minus a couple of lump-sum deductions for handicaps,
    # children income or being single parent
    wg['workingchild'] = df['child'] & (df['m_wage'] > 0)
    if yr < 2016:
        wg['wg_incdeduct'] = ((df['handcap_degree'] > 80) * tb['wgpfbm80'] +
                              df['handcap_degree'].between(1, 80) * tb['wgpfbu80'] +
                              (wg['workingchild'] * np.minimum(tb['wgpfb24'], df['m_wage'])) +
                              (df['alleinerz'] * (~df['child']) *
                               df['child11_num_tu'] * tb['wgpfb12'])
                              )
    else:
        wg['wg_incdeduct'] = ((df['handcap_degree'] > 0) * tb['wgpfbm80'] +
                              (wg['workingchild'] * np.minimum(tb['wgpfb24'], df['m_wage'])) +
                              (df['alleinerz'] * tb['wgpfb12'] * (~df['child']))
                              )

    wg['wg_incdeduct_tu_k'] = aggr(wg, 'wg_incdeduct', True)

    wg['wgY'] = ((1 - wg['wg_abzuege']) *
                 np.maximum(0,
                            (wg['wg_grossY'] +
                             wg['wg_otherinc'] -
                             wg['wg_incdeduct_tu_k']))
                 )

    # Parameter Y in steps of 5 Euros
    wg['Y'] = np.maximum(0, pd.Series(wg['wgY'] + 4).round(-1)-5)
    # There's a minimum Y depending on the hh size
    for i in range(1, 12):
        wg.loc[df['hhsize'] == i, 'Y'] = np.maximum(wg['Y'], tb['wgminEK' + str(i) + 'p'])
    wg.loc[df['hhsize'] >= 12, 'Y'] = np.maximum(wg['Y'], tb['wgminEK12p'])

    # Obtain relevant rent 'M'
    # There are also min and max values for this. Before 2009, they differed by construction
    # year of the house
    wg['max_rent'] = 0
    wg['min_rent'] = 0
    cnstyr = {'a': 1, 'm': 2, 'n': 3}
    for i in range(1, 13):
        # first, maximum rent.
        # fixed amounts for the households with size 1 to 5
        # afterwards, fix amount for every additional hh member
        if yr >= 2009:
            if i <= 5:
                wg.loc[(df['hhsize'] == i), 'max_rent'] = tb['wgmax' + str(i) + 'p_m']

            wg.loc[(df['hhsize'] > 5), 'max_rent'] = (tb['wgmax5p_m'] +
                                                      tb['wgmaxplus5_m'] * (df['hhsize'] - 5))
        if yr < 2009:
            for c in cnstyr:
                if i <= 5:
                    wg.loc[(df['hhsize'] == i)
                           & (df['cnstyr'] == cnstyr[c]),
                           'max_rent'] = tb['wgmax' + str(i) + 'p_' + c]

                wg.loc[(df['hhsize'] > 5)
                       & (df['cnstyr'] == cnstyr[c]),
                       'max_rent'] = (tb['wgmax5p_' + c] +
                                      tb['wgmaxplus5_' + c] * (df['hhsize'] - 5))

        # min rent never depended on construction year
        wg.loc[(df['hhsize'] == i), 'min_rent'] = tb['wgmin' + str(i) + 'p']

    wg.loc[(df['hhsize'] >= 12), 'min_rent'] = tb['wgmin12p']
    # check for failed assignments
    assert(~wg['max_rent'].isna().all())
    assert(~wg['min_rent'].isna().all())

    # distribute max rent among the tax units
    wg['max_rent'] = wg['max_rent'] * df['hh_korr']

    wg['wgmiete'] = np.minimum(wg['max_rent'], df['miete'] * df['hh_korr'])
    wg['wgheiz'] = df['heizkost'] * df['hh_korr']
    wg['M'] = np.maximum(wg['wgmiete'] + wg['wgheiz'],
                         wg['min_rent'])
    wg['M'] = np.maximum(pd.Series(wg['M']+4).round(-1) - 5, 0)

    # Finally, apply Wohngeld Formel. There are parameters a, b, c, depending on hh size
    # To ease notation, I write them first into separate variables from the tb dictionary
    wgeld = {}
    # Call it wohngeld_basis for now, might be set back to zero later on.
    wg['wohngeld_basis'] = 0
    for x in range(1, 13):
        for z in ['a', 'b', 'c']:
            wgeld[z] = tb['wg_'+z+'_'+str(x)+'p']

        a = wgeld['a']
        b = wgeld['b']
        c = wgeld['c']

        wg.loc[np.minimum(df['hhsize_tu'], 12) == x,
               'wohngeld_basis'] = np.maximum(0,
                                        tb['wg_factor'] *
                                        (wg['M'] - ((a + (b * wg['M']) +
                                                    (c * wg['Y'])) *
                                                    wg['Y'])
                                         )
                                        )

    # Wealth test for Wohngeld
    # 60.000 € pro Haushalt + 30.000 € für jedes Mitglied (Verwaltungsvorschrift)
    wg['assets'] = df['divdy'] / tb['r_assets']
    wg.loc[(wg['assets'] > (60000 + (30000 * (df['hhsize'] - 1)))), 'wohngeld'] = 0

    # Sum of wohngeld within household
    wg['wg_head'] = wg['wohngeld_basis'] * df['head_tu']
    wg = wg.join(wg.groupby(['hid'])['wg_head'].sum(),
                 on=['hid'], how='left', rsuffix='_hh')
    wg = wg.rename(columns={'wg_head_hh': 'wohngeld_basis_hh'})
    df['hhsize_tu'].describe()
    wg.to_excel(get_settings()['DATA_PATH'] + 'wg_check_hypo.xlsx')
    return wg[['wohngeld_basis', 'wohngeld_basis_hh', 'gkvbeit_tu_k', 'rvbeit_tu_k']]


def alg2(df, tb, yr):
    """ Basic Unemployment Benefit / Social Assistance
        Every household is assigend the sum of "needs" (Regelbedarf)
        These depend on the household composition (# of adults, kids in various age groups)
        and the rent. There are additional needs acknowledged for single parents.
        Income and wealth is tested for, the transfer withdrawal rate is non-constant.
    """
    cprint('ALG 2...', 'red', 'on_white')

    alg2 = pd.DataFrame(index=df.index.copy())
    alg2['hid'] = df['hid']
    alg2['tu_id'] = df['tu_id']
    # Additional need for single parents
    # Maximum 60% of the standard amount on top (a2zu2)
    # if you have at least one kid below 6 or two or three below 15, you 36%
    # alternatively, you get 12% per kid, depending on what's higher.
    alg2['mehrbed'] = (df['alleinerz'] *
                       np.minimum(tb['a2zu2']/100,
                                  np.maximum(tb['a2mbch1'] * df['child_num'],
                                             ((df['child6_num'] >= 1)
                                             | (df['child15_num'].between(2, 3))) *
                                             tb['a2mbch2'])
                                  )
                       )


    # 'Regular Need'
    # Different amounts by number of adults and age of kids
    # tb['rs_hhvor'] is the basic 'Hartz IV Satz' for a single person
    if yr <= 2010:
        # Before 2010, other members' amounts were calculated by a share of the head's need
        regelberechnung = [
                tb['rs_hhvor'] * (1 + alg2['mehrbed']) +
                (tb['rs_hhvor'] * tb['a2ch14'] * df['child14_24_num']) +
                (tb['rs_hhvor'] * tb['a2ch7'] * df['child7_13_num']) +
                (tb['rs_hhvor'] * tb['a2ch0'] * (df['child2_num'] + df['child3_6_num'])),

                tb['rs_hhvor'] * tb['a2part'] * (1 + alg2['mehrbed']) +
                (tb['rs_hhvor'] * tb['a2part']) +
                (tb['rs_hhvor'] * tb['a2ch18'] * np.maximum((df['adult_num'] - 2), 0)) +
                (tb['rs_hhvor'] * tb['a2ch14'] * df['child14_24_num']) +
                (tb['rs_hhvor'] * tb['a2ch7'] * df['child7_13_num']) +
                (tb['rs_hhvor'] * tb['a2ch0'] * (df['child2_num'] + df['child3_6_num']))
                            ]

    else:
        # After 2010,
        regelberechnung = [
                tb['rs_hhvor'] * (1 + alg2['mehrbed']) +
                (tb['rs_ch14'] * df['child14_24_num']) +
                (tb['rs_ch7'] * df['child7_13_num']) +
                (tb['rs_ch0'] * (df['child2_num'] + df['child3_6_num'])),

                tb['rs_2adults'] * (1 + alg2['mehrbed']) +
                tb['rs_2adults'] +
                (tb['rs_madults'] * np.maximum((df['adult_num'] - 2), 0)) +
                (tb['rs_ch14'] * df['child14_24_num']) +
                (tb['rs_ch7'] * df['child7_13_num']) +
                (tb['rs_ch0'] * (df['child2_num'] + df['child3_6_num']))
                            ]

    alg2['regelsatz'] = np.select([df['adult_num'] == 1, df['adult_num'] > 1], regelberechnung)
    '''
    print(pd.crosstab(alg2['mehrbed'], df['typ_bud']))
    print(pd.crosstab(alg2['regelsatz'],  df['typ_bud']))
    print(pd.crosstab(df['typ_bud'], df['child6_num']))
    '''
    # alg2['regelsatz_tu_k'] = aggr(alg2, 'regelsatz', True)
    # Only 'appropriate' housing costs are paid. For simplicity apply Housing benefit rules
    # this might be overly restrictive...check number of benefit recipients.
    # alg2['alg2_kdu'] = df['M'] + np.maximum(df['heizkost'] - df['wgheiz'], 0)
    # For now, just assume they are paid...
    alg2['alg2_kdu'] = df['miete'] + df['heizkost']

    # After introduction of Hartz IV until 2010, people becoming unemployed
    # received something on top to smooth the transition. not yet modelled...
    if 2005 <= yr <= 2010:
        print('"Armutsgewöhnungszuschlag" noch nicht modelliert.')
        alg2['bef_zuschlag'] = 0
    else:
        alg2['bef_zuschlag'] = 0

    alg2['regelbedarf'] = alg2[['regelsatz', 'alg2_kdu', 'bef_zuschlag']].sum(axis=1)

    # Account for household wealth.
    # usually no wealth in the data, infer from capital income...works OK for low wealth HH
    alg2['assets'] = df['divdy'] / tb['r_assets']

    # df['vermfreib'] = tb['a2vki']
    # there are exemptions depending on individual age for adults
    alg2['ind_freib'] = 0
    alg2.loc[(df['byear'] >= 1948) & (~df['child']), 'ind_freib'] = tb['a2ve1'] * df['age']
    alg2.loc[(df['byear'] < 1948), 'ind_freib'] = tb['a2ve2'] * df['age']
    # sum over individuals
    alg2 = alg2.join(alg2.groupby(['hid'])['ind_freib'].sum(),
                     on=['hid'], how='left', rsuffix='_hh')

    # there is an overall maximum exemption
    alg2['maxvermfb'] = 0
    alg2.loc[(df['byear'] < 1948) & (~df['child']), 'maxvermfb'] = tb['a2voe1']
    alg2.loc[(df['byear'].between(1948, 1957)), 'maxvermfb'] = tb['a2voe1']
    alg2.loc[(df['byear'].between(1958, 1963)), 'maxvermfb'] = tb['a2voe3']
    alg2.loc[(df['byear'] >= 1964) & (~df['child']), 'maxvermfb'] = tb['a2voe4']
    alg2 = alg2.join(alg2.groupby(['hid'])['maxvermfb'].sum(),
                     on=['hid'], how='left', rsuffix='_hh')
    # add fixed amounts per child and adult
    alg2['vermfreibetr'] = np.minimum(alg2['maxvermfb_hh'],
                                      alg2['ind_freib_hh'] +
                                      df['child18_num'] * tb['a2vkf'] +
                                      df['adult_num'] * tb['a2verst']
                                      )

    # If wealth exceeds the exemption, the need is set to zero
    alg2.loc[(alg2['assets'] > alg2['vermfreibetr']), 'regelbedarf'] = 0

    # Income relevant to check against ALG2 claim
    alg2['alg2_grossek'] = (df[['m_wage',
                                'm_transfers',
                                'm_self',
                                'm_vermiet',
                                'm_kapinc',
                                'm_pensions',
                                'm_alg1']].sum(axis=1)
                            )
    alg2['alg2_grossek'] = alg2['alg2_grossek'].fillna(0)
    # ...deduct income tax and social security contributions
    alg2['alg2_ek'] = (np.maximum(alg2['alg2_grossek'] -
                                  df['incometax'] -
                                  df['soli'] -
                                  df['svbeit'], 0)
                       )
    alg2['alg2_ek'] = alg2['alg2_ek'].fillna(0)

    # Determine the amount of income that is not deducted
    # Varios withdrawal rates depending on monthly earnings.
    alg2['ekanrefrei'] = 0
    # 100€ is always 'free'
    alg2.loc[(df['m_wage'] <= tb['a2grf']), 'ekanrefrei'] = df['m_wage']
    # until 1000€, you may keep 20% (withdrawal rate: 80%)
    alg2.loc[(df['m_wage'].between(tb['a2grf'], tb['a2eg1'])),
             'ekanrefrei'] = (tb['a2grf'] +
                              tb['a2an1'] * (df['m_wage'] - tb['a2grf']))
    # from 1000 to 1200 €, you may keep only 10%
    alg2.loc[(df['m_wage'].between(tb['a2eg1'], tb['a2eg2']))
             & (df['child18_num'] == 0),
             'ekanrefrei'] = (tb['a2grf'] +
                              tb['a2an1'] * (tb['a2eg1'] - tb['a2grf']) +
                              tb['a2an2'] * (df['m_wage'] - tb['a2eg1'])
                              )
    # If you have kids, this range goes until 1500 €,
    alg2.loc[(df['m_wage'].between(tb['a2eg1'], tb['a2eg3'])) &
             (df['child18_num'] > 0),
             'ekanrefrei'] = (tb['a2grf'] +
                              tb['a2an1'] * (tb['a2eg1'] - tb['a2grf']) +
                              tb['a2an2'] * (df['m_wage'] - tb['a2eg1'])
                              )
    # beyond 1200/1500€, you can't keep anything.
    alg2.loc[(df['m_wage'] > tb['a2eg2']) &
             (df['child18_num'] == 0),
             'ekanrefrei'] = (tb['a2grf'] +
                              tb['a2an1'] * (tb['a2eg1'] - tb['a2grf']) +
                              tb['a2an2'] * (tb['a2eg2'] - tb['a2eg1'])
                              )
    alg2.loc[(df['m_wage'] > tb['a2eg3']) &
             (df['child18_num'] > 0),
             'ekanrefrei'] = (tb['a2grf'] +
                              tb['a2an1'] * (tb['a2eg1'] - tb['a2grf']) +
                              tb['a2an2'] * (tb['a2eg3'] - tb['a2eg1'])
                              )
    # Children income is fully deducted, except for the first 100 €.
    alg2.loc[(df['child']), 'ekanrefrei'] = np.maximum(0, df['m_wage'] - 100)
    # the final alg2 amount is the difference between the theoretical need and the
    # relevant income. this will be calculated later when several benefits have to be compared.
    alg2['ar_alg2_ek'] = np.maximum(alg2['alg2_ek'] - alg2['ekanrefrei'], 0)
    # Aggregate on HH
    for var in ['ar_alg2_ek', 'alg2_grossek']:
        alg2 = alg2.join(alg2.groupby(['hid'])[var].sum(),
                         on=['hid'], how='left', rsuffix='_hh')
    alg2['ar_base_alg2_ek'] = alg2['ar_alg2_ek_hh'] + df['kindergeld_hh']
    '''
    out = df.join(alg2.drop(columns=['hid', 'tu_id'],
                            axis=1),
                  how='outer')
    out = out.sort_values(by=['hid', 'tu_id', 'pid'])
    out[(out['hhsize'] > 1) &
        (out['child_num'] > 0)].to_excel('Z:/test/alg2_check.xlsx')
    '''

    return alg2[['ar_base_alg2_ek', 'ar_alg2_ek_hh', 'alg2_grossek_hh',
                 'mehrbed', 'assets', 'vermfreibetr', 'regelbedarf', 'regelsatz']]


def kiz(df, tb, yr):
    ''' Kinderzuschlag / Additional Child Benefit
        The purpose of Kinderzuschlag (Kiz) is to keep families out of ALG2. If they
        would be eligible to ALG2 due to the fact that their claim rises because of their children,
        they can claim Kiz.

        Also determines which benefit (if any) the household actually receives.
    '''

    ''' In contrast to ALG2, Kiz considers only the rental costs that are attributed
        to the parents.
        This is done by some fixed share which is updated on annual basis
        ('jährlicher Existenzminimumsbericht')
    '''
    # cols: number of adults
    # rows: number of kids
    wohnbedarf = {'2011': [[75.90, 83.11],
                           [61.16, 71.10],
                           [51.21, 62.12],
                           [44.05, 55.15],
                           [38.65, 49.59]],
                  '2012': [[76.34, 83.14],
                           [61.74, 71.15],
                           [51.82, 62.18],
                           [44.65, 55.22],
                           [39.23, 49.66]],
                  '2013': [[76.34, 83.14],
                           [61.74, 71.15],
                           [51.82, 62.18],
                           [44.65, 55.22],
                           [39.23, 49.66]],
                  '2014': [[76.69, 83.30],
                           [62.20, 71.38],
                           [52.31, 62.45],
                           [45.13, 55.50],
                           [39.69, 49.95]],
                  '2015': [[76.69, 83.30],
                           [62.20, 71.38],
                           [52.31, 62.45],
                           [45.13, 55.50],
                           [39.69, 49.95]],
                  '2016': [[77.25, 83.16],
                           [62.93, 71.17],
                           [53.09, 62.20],
                           [45.92, 55.24],
                           [40.45, 49.69]],
                  '2017': [[77.25, 83.16],
                           [62.93, 71.17],
                           [53.09, 62.20],
                           [45.92, 55.24],
                           [40.45, 49.69]],
                  '2018': [[77.24, 83.25],
                           [62.92, 71.30],
                           [53.08, 62.36],
                           [45.90, 55.41],
                           [40.43, 49.85]]
                  }

    cprint('Kinderzuschlag...', 'red', 'on_white')

    kiz = pd.DataFrame(index=df.index.copy())
    kiz['hid'] = df['hid']
    kiz['tu_id'] = df['tu_id']

    # First, calculate the need as for ALG2, but only for parents.
    if yr <= 2010:
        # not yet implemented
        kiz_regel = [tb['rs_hhvor'] * (1 + df['mehrbed']),
                     tb['rs_hhvor'] * tb['a2part'] * (2 + df['mehrbed']),
                     tb['rs_hhvor'] * tb['a2ch18'] * df['adult_num_tu']
                     ]
    if yr > 2010:
        kiz_regel = [tb['rs_hhvor'] * (1 + df['mehrbed']),
                     tb['rs_2adults'] + ((1 + df['mehrbed']) * tb['rs_2adults']),
                     tb['rs_madults'] * df['adult_num_tu']
                     ]

    kiz['kiz_ek_regel'] = np.select([df['adult_num_tu'] == 1,
                                    df['adult_num_tu'] == 2,
                                    df['adult_num_tu'] > 2],
                                    kiz_regel)
    # Add rents. First, correct rent for the case of several tax units within the HH
    kiz['kiz_miete'] = df['miete'] * df['hh_korr']
    kiz['kiz_heiz'] = df['heizkost'] * df['hh_korr']
    # The actual living need is again broken down to the parents.
    # There is a specific share for this, taken from the dict 'wohnbedarf' above.
    wb = wohnbedarf[str(max(yr, 2011))]
    kiz['wb_eltern_share'] = 1.0
    for c in [1, 2]:
        for r in [1, 2, 3, 4]:
            kiz.loc[(df['child_num_tu'] == r) & (df['adult_num_tu'] == c),
                    'wb_eltern_share'] = wb[r-1][c-1] / 100
        kiz.loc[(df['child_num_tu'] >= 5) & (df['adult_num_tu'] == c),
                'wb_eltern_share'] = wb[4][c-1] / 100

    # apply this share to living costs
    kiz['kiz_ek_kdu'] = kiz['wb_eltern_share'] * (kiz['kiz_miete'] + kiz['kiz_heiz'])

    kiz['kiz_ek_relev'] = kiz['kiz_ek_regel'] + kiz['kiz_ek_kdu']

    # There is a maximum income threshold, depending on the need, plus the potential kiz receipt
    kiz['kiz_ek_max'] = kiz['kiz_ek_relev'] + tb['a2kiz'] * df['child_num_tu']
    # min income to be eligible for KIZ (different for singles and couples)
    kiz['kiz_ek_min'] = (tb['a2kiz_minek_cou'] * (df['hhtyp'] == 4) +
                         (tb['a2kiz_minek_sin'] * (df['alleinerz'])))

#        Übersetzung §6a BKGG auf deutsch:
#     1. Um KIZ zu bekommen, muss das Bruttoeinkommen minus Wohngeld
#        und Kindergeld über 600 € (Alleinerziehende) bzw. 900 € (Paare) liegen.
#     2. Das Nettoeinkommen minus Wohngeld muss unterhalb des Bedarfs
#        plus Gesamtkinderzuschlag liegen.
#     3. Dann wird geschaut, wie viel von dem Einkommen
#        (Erwachsene UND Kinder !) noch auf KIZ angerechnet wird.
#        Wenn das zu berücksichtigende Einkommen UNTER der
#        Höchsteinkommensgrenze und UNTER der Bemessungsgrundlage liegt, wird
#        der volle KIZ gezahlt
#        Wenn es ÜBER der Bemessungsgrundlage liegt,
#        wird die Differenz zur Hälfte abgezogen.
    kiz['kiz_ek_gross'] = df['alg2_grossek_hh']
    kiz['kiz_ek_net'] = df['ar_alg2_ek_hh']

    # Deductable income. 50% withdrawal rate, rounded to 5€ values.
    # TODO: deduct child income
    kiz['kiz_ek_anr'] = np.maximum(0,
                                   round((df['ar_alg2_ek_hh'] -
                                          kiz['kiz_ek_relev'])/10)
                                   * 5
                                   )
    # Amount of additional child benefit
    kiz['kiz'] = 0
    # Dummy variable whether household is in the relevant income range.
    kiz['kiz_incrange'] = ((kiz['kiz_ek_gross'] >= kiz['kiz_ek_min'])
                           & (kiz['kiz_ek_net'] <= kiz['kiz_ek_max'])
                           )
    # Finally, calculate the amount.
    kiz.loc[kiz['kiz_incrange'], 'kiz'] = np.maximum(0,
                                                     (tb['a2kiz'] * df['child_num_tu']) -
                                                     kiz['kiz_ek_anr'])

    # Extend the amount to the other hh members for complementarity with wohngeld and alg2
    kiz = kiz.join(kiz.groupby(['hid'])[('kiz')].max(),
                   on=['hid'], how='left', rsuffix='_temp')

    kiz['kiz'] = kiz['kiz_temp']
    ###############################
    # Check eligibility for benefits
    ###############################
    # transfer some variables...
    kiz['ar_base_alg2_ek'] = df['ar_base_alg2_ek']
    kiz['wohngeld_basis'] = df['wohngeld_basis_hh']

    kiz['ar_wg_alg2_ek'] = kiz['ar_base_alg2_ek'] + kiz['wohngeld_basis']
    kiz['ar_kiz_alg2_ek'] = kiz['ar_base_alg2_ek'] + kiz['kiz']
    kiz['ar_wgkiz_alg2_ek'] = (kiz['ar_base_alg2_ek'] + kiz['wohngeld_basis'] + kiz['kiz'])

    for v in ['base', 'wg', 'kiz', 'wgkiz']:
        kiz['fehlbedarf_'+v] = df['regelbedarf'] - kiz['ar_'+v+'_alg2_ek']
        kiz['m_alg2_'+v] = np.maximum(kiz['fehlbedarf_'+v], 0)


    # There is a rule which benefits are superior to others
    # If there is a positive ALG2 claim, but the need can be covered with
    # Housing Benefit (and possibly add. child benefit),
    # the HH has to claim the housing benefit and addit. child benefit.
    # There is no way you can receive ALG2 and Wohngeld at the same time!
    for v in ['wg', 'kiz', 'wgkiz']:
        kiz[v+'_vorrang'] = (kiz['m_alg2_'+v] == 0) & (kiz['m_alg2_base'] > 0)

    kiz['m_alg2'] = kiz['m_alg2_base']
    # If this is the case set alg2 to zero.
    kiz.loc[(kiz['wg_vorrang']) |
            (kiz['kiz_vorrang']) |
            (kiz['wgkiz_vorrang']),
            'm_alg2'] = 0
    # If other benefits are not sufficient, set THEM to zero instead.
    kiz['wohngeld'] = kiz['wohngeld_basis']
    kiz.loc[(~kiz['wg_vorrang']) &
            (~kiz['wgkiz_vorrang']) &
            (kiz['m_alg2_base'] > 0),
            'wohngeld'] = 0
    kiz.loc[(~kiz['kiz_vorrang']) &
            (~kiz['wgkiz_vorrang']) &
            (kiz['m_alg2_base'] > 0),
            'kiz'] = 0

    # control output
    '''
    kiz['regelbedarf'] = df['regelbedarf']
    kiz['child'] = df['child']
    kiz['age'] = df['age']
    kiz['hhtyp'] = df['hhtyp']
    kiz = kiz.sort_values(by=['hid', 'tu_id', 'pid'])
    kiz[kiz['hhtyp'].isin([2, 4]) &
        (df['hh_korr'] < 1)].to_excel('Z:/test/vorrang_check.xlsx')
    '''
    # TO DO: Correct benefit receipt of pensioners.
    # For them, 'sozialhilfe' needs to be modelled

    assert(kiz['m_alg2'].notna().all())
    assert(kiz['wohngeld'].notna().all())
    assert(kiz['kiz'].notna().all())

    return kiz[['kiz', 'wohngeld', 'm_alg2']]


def tb_out(df, graph_path, ref):
    ''' Tax-Benefit Output
        Debugging Tool.
        Produces some aggregates on
        - total tax revenue
        - Benefit recipients
        - Income inequality
    '''
    print('-'*80)
    print('TAX BENEFIT AGGREGATES')
    print('-'*80)
    cprint('Revenues', 'red', 'on_white')
    # Incometax over all persons. SV Beiträge too
    #

    for tax in ['incometax_tu', 'soli_tu', 'gkvbeit', 'rvbeit', 'pvbeit', 'avbeit']:
        if tax in ['incometax_tu', 'soli_tu']:
            df['w_sum_'+tax] = df[tax] * df['hweight'] * df['head_tu']
        else:
            df['w_sum_'+tax] = df[tax] * df['pweight']
        print(tax + " : " + str(round(
                                df['w_sum_'+tax].sum()/1e9 * 12
                                , 2)) + " bn €.")
    cprint('Benefit recipients', 'red', 'on_white')
    for ben in ['m_alg1', 'm_alg2', 'wohngeld', 'kiz']:
        print(ben + " :" + str(round(
                                df['hweight'][(df[ben] > 0)
                                & (df['head_tu'])].sum()/1e6, 2)) +
                               " Million Households.")
        df['w_sum_'+ben] = df[ben] * df['hweight'] * df['head_tu']
        print(ben + " : " + str(round(df['w_sum_'+ben].sum()/1e9 * 12, 2)) + " bn €.")
        print('Recipients by Household Type (in 1000): ')
        print(df[(df['head_tu']) &
                 (df[ben] > 0) &
                 (~df['pensioner'])].groupby('hhtyp')['hweight'].sum()/1e3)

    print('-'*80)

    # Check Income Distribution:
    # Equivalence Scale (modified OECD scale)
    df['eq_scale'] = (1 +
                      0.5 * np.maximum(
                            (df['hhsize'] - df['child14_num'] - 1), 0) +
                      0.3 * (df['child14_num']))
    df['dpi_eq'] = df['dpi'] / df['eq_scale']
    print(df['dpi_eq'].describe())
    plt.clf()
    ax = df['dpi_eq'].plot.kde(xlim=(0, 4000))
    ax.set_title('Distribution of equivalized disp. income ' + str(ref))
    # print(graph_path + 'dist_dpi_' + ref + '.png')
    # plt.savefig(graph_path + 'dist_dpi_' + ref + '.png')
    print('-'*80)
    print('Gini-Coefficient Disp. Income: ', gini(df['dpi_eq'], df['pweight']))
    print('-'*80)

    return True
