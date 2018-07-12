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

def taxtransfer(tbinput,settings,ref,hyporun=False):
    datayear = min(settings['taxyear'],2016)
    print("---------------------------------------------")
    print(" TAX TRANSFER SYSTEM ")
    print(" -------------------")
    if hyporun:
        print(" HYPOTHETICAL DATA")
        df = pd.read_pickle(tbinput+'hypo')
    else:
        print(" Year of Database: " + str(datayear))
        df = pd.read_pickle(tbinput+str(datayear))
    # Get the correct parameters for the tax year
    print(" Year of System: "   + str(settings['taxyear']))
    print(" Simulated Reform: " + str(ref))
    print("---------------------------------------------")

    tb = get_params(settings)[str(settings['taxyear'])]


    # 1. Uprating if necessary
    if hyporun == False:
        df = uprate(df,datayear,settings['taxyear'],settings['MAIN_PATH'])

    # 2. Social Security Payments
    ssc_out = ssc(df[['pid','hid','east','m_wage','selfemployed','m_self','m_pensions','age','haskids','pkv']],tb,settings['taxyear'],ref)
    df = pd.merge(df,ssc_out, how='inner',validate='1:1')

    # 3. Unemployment benefit
    #ui_vars = ['pid','hid','m_wage','m_wage_l1','m_wage_l2','east','months_l1','months_l2','alg_soep','age',]
    df = ui(df,tb,settings['taxyear'],ref)
    # 4. Pensions
    #pens_out = pensions(df,tb,taxyear,ref):

    # 5. Income Tax
    taxvars = ['pid','hid','female','head_tu','tu_id','east','m_wage','selfemployed','m_self',
               'm_pensions','age','pkv','zveranl','child','renteneintritt','w_hours','m_kapinc',
               'm_vermiet','m_imputedrent','marstat','handcap_dummy','handcap_degree','rvbeit',
               'gkvbeit','pvbeit','avbeit','ag_rvbeit','ag_gkvbeit','ag_pvbeit','ag_avbeit',
               'adult_num_tu','child_num_tu','alleinerz','comm_dist','comm_freq']
    tax_out = tax(df[taxvars],tb,settings['taxyear'],ref,settings['DATA_PATH'])

    df = pd.merge(df,tax_out, how='outer',validate='1:1')

    # 6. Benefits
    df = ben(df,tb,settings['taxyear'],ref,settings['GRAPH_PATH'])


    # 7. CALCULATE DISPOSABLE INCOME
    df['dpi_ind'] = (df[['m_wage','m_kapinc','m_self','m_vermiet','m_imputedrent','m_pensions','m_transfers','kindergeld','wohngeld']].sum(axis=1)
                    - df[['incometax','soli','gkvbeit','rvbeit','pvbeit','avbeit']].sum(axis=1))
    df = df.join(df.groupby(['hid'])[('dpi_ind')].sum(), on = ['hid'], how='left',rsuffix='_temp')
    df[['dpi_ind','hid','m_wage','m_kapinc','m_self','m_vermiet','m_imputedrent','m_pensions','m_transfers','kindergeld','wohngeld','incometax','soli','gkvbeit','rvbeit','pvbeit','avbeit']][df['dpi_ind_temp']<0]
    ## THIS ATTRIBUTES THE WRONG INDIVIDUAL INCOMES. JOIN IT BACK FIRST
    df['dpi']    = np.maximum(df['dpi_ind_temp'] + df['m_alg2'],0)

    # SHOW OUTPUT
    if hyporun == False:
        tb_out(df,ref,settings['GRAPH_PATH'])

    if hyporun == False:
        print('Saving to:' + settings['DATA_PATH']+ref+'/taxben_results' + str(datayear) + '_' + str(settings['taxyear']) + '.json')
        df.to_json(settings['DATA_PATH']+ref+'/taxben_results' + str(datayear) + '_' + str(settings['taxyear']) + '.json')
    #pd.to_pickle(df,settings['DATA_PATH']+'/taxben_hypo')
    #pd.read_pickle(df,out_path+ref+'/taxben_results2016_2018')

    return df


def uprate(df,dy,ty,path):
    ''' Uprating monetary values to account for difference between data year and simulation year.
    '''
    # define all monetary variables
    # get uprate matrix ,as np.array
    upr = pd.read_excel(path+'/data/params/uprate_cpi.xls',index_col='ausgang')
    factor = upr.loc[dy]['y'+str(ty)]
    print('Uprating monetary variables from year ' + str(dy) + ' to ' + str(ty) + ' with factor ' + str(factor))
    money_vars = ['k_inco','m_pensions','m_transfers','childinc','m_kapinc','m_vermiet','m_imputedrent',
                  'versbez','m_wage','othwage_ly','h_wage','kaltmiete','heizkost','kapdienst','miete']

    for v in money_vars:
        df[v] = factor * df[v]

    return df

def pensions(df,tb,yr,ref):
    ''' for future years, update pension claims
    '''
    cprint('Pensions','red','on_white')
    westost = [df['east'] == False, df['east']]
    year = str(yr)
    # lagged values needed for Rentenformel
    tb_1 = get_params()[str(yr - 1)]
    tb_2 = get_params()[str(yr - 2)]
    tb_3 = get_params()[str(yr - 3)]
    # individuelle monatl. Altersrente (Rentenartfaktor = 1):
    # R = EP * ZF * Rw
    m_wage_west = df['m_wage'][(df['m_wage']>tb['mini_grenzew']) & (df['east'] == False)].mean()
    m_wage_east = df['m_wage'][(df['m_wage']>tb['mini_grenzeo']) & (df['east'] == True)].mean()
    df['EP'] = np.select(westost,[np.minimum(df['m_wage'],tb['rvmaxekw'])/m_wage_west,
                                  np.minimum(df['m_wage'],tb['rvmaxeko'])/m_wage_east])

    #rw_east = rentenwert['rw_east'][rentenwert['yr'] == yr]
    #rw_west = rentenwert['rw_west'][rentenwert['yr'] == yr]
    #################################
    # Neuer Rentenwert für yr > 2018:
    # Rentenformel: https://de.wikipedia.org/wiki/Rentenanpassungsformel

    # Altersvorsorgeanteil = 4 nach 2012
    ava = 4
    lohnkomponente = (meanwages[str(yr-1)]  / (meanwages[str(yr-2)] * (meanwages[str(yr - 2)] / meanwages[str(yr - 3)]) / (meanwages_beit[str(yr - 2)] / meanwages_beit[str(yr - 3)])))
    riesterfaktor = (100 - ava - (tb_1['grvbs'] * 200))/(100 - ava - (tb_1['grvbs'] * 200))
    #nachhfaktor   =
    rentenwert = tb['rw_west'] * lohnkomponente


def ssc(df,tb,yr,ref):
    ''' Calculates Social Security Payments
    '''
    cprint('Social Security Payments...','red','on_white')
# Einige Prüfgrößen
    ssc = df.copy()
    westost = [df['east'] == False, df['east']]
    ssc['bezgr'] = np.select(westost,[tb['bezgr_o'],tb['bezgr_w']])
    ssc['kinderlos'] = ((ssc['haskids'] == False) & (ssc['age'] > 22))
    ssc['belowmini'] = np.select(westost,[ssc['m_wage'] < tb['mini_grenzew'],ssc['m_wage'] < tb['mini_grenzeo']]) == 1
    ssc['above_thresh_kv'] = np.select(westost,[ssc['m_wage'] > tb['kvmaxekw'],ssc['m_wage'] > tb['kvmaxeko']]) == 1
    ssc['above_thresh_rv'] = np.select(westost,[ssc['m_wage'] > tb['rvmaxekw'],ssc['m_wage'] > tb['rvmaxeko']]) == 1



    # Standard-Beiträge unter Berücksichtigung von Beitragsbemessungsgrenze
    # Rentenversicherung
    ssc['rvbeit']    = tb['grvbs'] * np.minimum(ssc['m_wage'],np.select(westost,[tb['rvmaxekw'],tb['rvmaxeko']]))
    ssc['ag_rvbeit'] = tb['grvbs'] * np.minimum(ssc['m_wage'],np.select(westost,[tb['rvmaxekw'],tb['rvmaxeko']]))
    # Arbeitslosenversicherung
    ssc['avbeit']    = tb['alvbs'] * np.minimum(ssc['m_wage'],np.select(westost,[tb['rvmaxekw'],tb['rvmaxeko']]))
    ssc['ag_avbeit'] = tb['alvbs'] * np.minimum(ssc['m_wage'],np.select(westost,[tb['rvmaxekw'],tb['rvmaxeko']]))
    # GKV Arbeitnehmer
    ssc['gkvbeit']   = tb['gkvbs_an'] * np.minimum(ssc['m_wage'],np.select(westost,[tb['kvmaxekw'],tb['kvmaxeko']]))
    ssc['ag_gkvbeit'] = tb['gkvbs_ag'] * np.minimum(ssc['m_wage'],np.select(westost,[tb['kvmaxekw'],tb['kvmaxeko']]))
    # Pflegeversicherung
    ssc['pvbeit']  = tb['gpvbs'] * np.minimum(ssc['m_wage'],np.select(westost,[tb['kvmaxekw'],tb['kvmaxeko']]))
    ssc.loc[ssc['kinderlos'],'pvbeit'] = ((tb['gpvbs'] + tb['gpvbs_kind']) * np.minimum(ssc['m_wage'],
                                           np.select(westost,[tb['kvmaxekw'],tb['kvmaxeko']])))
    ssc['ag_pvbeit']  = tb['gpvbs'] * np.minimum(ssc['m_wage'],np.select(westost,[tb['kvmaxekw'],tb['kvmaxeko']]))



    # Gleitzone / Midi-Jobs

    if yr >= 2003:
        AN_anteil = tb['grvbs'] + tb['gpvbs'] + tb['alvbs'] + tb['gkvbs_an']
        AG_anteil = tb['grvbs'] + tb['gpvbs'] + tb['alvbs'] + tb['gkvbs_ag']
        DBSV      = AN_anteil + AG_anteil
        pauschmini = tb['mini_ag_gkv'] + tb['mini_ag_grv'] + tb['stpag']
        F         = round(pauschmini / DBSV,4)

        bemes = [F * tb['mini_grenzew']  + ((tb['midi_grenze']/(tb['midi_grenze']-tb['mini_grenzew'])) - (tb['mini_grenzew']/((tb['midi_grenze']-tb['mini_grenzew']))*F)) * (ssc['m_wage'] - tb['mini_grenzew']),
                 F * tb['mini_grenzeo']  + ((tb['midi_grenze']/(tb['midi_grenze']-tb['mini_grenzeo'])) - (tb['mini_grenzeo']/((tb['midi_grenze']-tb['mini_grenzeo']))*F)) * (ssc['m_wage'] - tb['mini_grenzeo'])]
        ssc['bemessungsentgelt'] = np.select(westost,bemes)
        ssc['in_gleitzone'] = ssc['m_wage'].between(np.select(westost,[tb['mini_grenzew'],tb['mini_grenzeo']]),tb['midi_grenze'])

        # Alle Zweige der Versicherung separat. Erst Gesamtbeitrag, dann Arbeitgeber, dann Arbeitnehmer
        # Rente...
        ssc['gb_rv'] = 2 * tb['grvbs'] * ssc['bemessungsentgelt']
        ssc.loc[ssc['in_gleitzone'],'ag_rvbeit'] = tb['grvbs'] * ssc['m_wage']
        ssc.loc[ssc['in_gleitzone'],'rvbeit']    = ssc['gb_rv'] - ssc['ag_rvbeit']
        # GKV...
        ssc['gb_gkv'] = (tb['gkvbs_an'] + tb['gkvbs_ag']) * ssc['bemessungsentgelt']
        ssc.loc[ssc['in_gleitzone'],'ag_gkvbeit'] = tb['gkvbs_ag'] * ssc['m_wage']
        ssc.loc[ssc['in_gleitzone'],'gkvbeit']    = ssc['gb_gkv'] - ssc['ag_gkvbeit']
        # ArbeitslosenV...
        ssc['gb_alv'] = 2 * tb['alvbs'] * ssc['bemessungsentgelt']
        ssc.loc[ssc['in_gleitzone'],'ag_avbeit'] = tb['alvbs'] * ssc['m_wage']
        ssc.loc[ssc['in_gleitzone'],'avbeit']    = ssc['gb_alv'] - ssc['ag_avbeit']
        # PflegeV ...
        ssc['gb_pv'] = 2 * tb['gpvbs'] * ssc['bemessungsentgelt']
        ssc.loc[ssc['in_gleitzone'],'ag_pvbeit'] = tb['gpvbs'] * ssc['m_wage']
        ssc.loc[ssc['in_gleitzone'],'pvbeit']    = (ssc['gb_pv'] - ssc['ag_pvbeit']
                                                    + np.select([ssc['kinderlos'],ssc['kinderlos'] == False],
                                                                [tb['gpvbs_kind'] * ssc['m_wage'],0]))
        # Drop intermediate variables
        ssc = ssc.drop(['gb_rv','gb_gkv','gb_alv','gb_pv','bemessungsentgelt'],axis=1)
    # ENDE GLEITZONE

    # CHECK MINIMUM THRESHOLDS
    for beit in ['rvbeit','gkvbeit','avbeit','pvbeit','ag_rvbeit','ag_gkvbeit','ag_avbeit','ag_pvbeit']:
        ssc.loc[ssc['belowmini'],beit] = 0

    # CHECK MAXIMUM THRESHOLDS

    # Freiwillige GKV der Selbständigen. Entweder Selbständigen-Einkommen oder 3/4 der Bezugsgröße
    ssc.loc[(ssc['selfemployed']) & (ssc['pkv'] == False),'gkvbeit'] = ((tb['gkvbs_an'] + tb['gkvbs_ag']) *
                                                                         np.minimum(ssc['m_self'],0.75 * np.select(westost,[tb['bezgr_w'],tb['bezgr_o']])))
    ssc.loc[(ssc['selfemployed']) & (ssc['pkv'] == False),'pvbeit'] = ((2 * tb['gpvbs'] + np.select([ssc['kinderlos'],ssc['kinderlos'] == False],
                                                                                                    [tb['gpvbs_kind'],0])) *
                                                                        np.minimum(ssc['m_self'],0.75 * np.select(westost,[tb['bezgr_w'],tb['bezgr_o']])))
    # TO DO: GKV auf Renten, die Zahlen den doppelten Pflebebeitragssatz.
    ssc['gkvrbeit'] = tb['gkvbs_an'] * np.minimum(ssc['m_pensions'],np.select(westost,[tb['kvmaxekw'],tb['kvmaxeko']]))
    # doppelter Pflegebeitragssatz
    ssc['pvrbeit']  = 2 * tb['gpvbs'] * np.minimum(ssc['m_pensions'],np.select(westost,[tb['kvmaxekw'],tb['kvmaxeko']]))
    ssc.loc[ssc['kinderlos'],'pvrbeit'] = ((2 * tb['gpvbs'] + tb['gpvbs_kind']) *
                                           np.minimum(ssc['m_pensions'],np.select(westost,[tb['kvmaxekw'],tb['kvmaxeko']])))

    ssc['gkvbeit'] = ssc['gkvbeit'] + ssc['gkvrbeit']
    ssc['pvbeit']  = ssc['pvbeit']  + ssc['pvrbeit']
    # Sum of Social Security Contributions (for employees)
    ssc['svbeit'] = ssc[['rvbeit','avbeit','gkvbeit','pvbeit']].sum(axis=1)

    return ssc

def ui(df,tb,taxyear,ref):
    ''' Unemployment/Transitory Benefit based on employment status and income from previous years
    '''
    westost = [df['east'] == False, df['east']]

    df['m_alg1'] = df['alg_soep'].fillna(0)
    # Months of entitlement
    df['mts_contrib'] = df['months_l1'] + df['months_l2']
    df['mts_ue']      = df['months_ue'] + df['months_ue_l1'] + df['months_ue_l2']
    df['alg_wage']    = (np.select(westost,
                         [np.minimum(tb['rvmaxekw'],df['m_wage_l1']), np.minimum(tb['rvmaxeko'],df['m_wage_l1'])]
                         ))
    # BENEFIT AMOUNT
    # CHECK ELEGIBILITY. THEN DIFFERENT RATES FOR PARENTS AND NON-PARENTS. ALSO TAKE INTO ACCOUNT ACTUAL WAGES
    df.loc[(df['mts_ue'] > 0) & (df['mts_ue']<=12) & (df['age'] < 65) & (df['m_pensions'] == 0) & (df['alg_soep'] == 0) & (df['w_hours'] < 15),'m_alg1'] = (np.select(
                        [df['child_num_tu'] == 0,     df['child_num_tu'] >0],
                        [tb['agsatz0'],                  tb['agsatz1']]) * np.maximum(df['alg_wage'] - np.maximum(df['m_wage'] - tb['alg1_frei'],0) ,0))

    print('ALG 1 recipients according to SOEP:' + str(df['counter'][df['alg_soep'] > 0].sum()) )
    print('Additional ALG 1 recipients from simulation:' + str(df['counter'][df['m_alg1'] > 0].sum() - df['counter'][df['alg_soep'] > 0].sum()) )
    return df

def tax(df,tb,yr,ref,data_path):
    ''' Calculates Income Tax Deductions and Tax Due
    '''
    cprint('Income Tax...','red','on_white')

    def tarif(x,tb):
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
                t=  ((((tb['t_s']-tb['t_m'])/(2*(tb['S']-tb['M'])))*(x-tb['M'])
                    + tb['t_m'])*(x-tb['M'])
                    + (tb['M']-tb['G'])*((tb['t_m']+tb['t_e'])/2))
            if( x > tb['S']):
                t = ((tb['t_s']*x-tb['t_s']*tb['S']
                    + ((tb['t_s']+ tb['t_m'])/2)*(tb['S']-tb['M'])
                    + ((tb['t_m']+tb['t_e'])/2)*(tb['M']-tb['G'])))
            if x > tb['R']:
                t = t + (tb['t_r']-tb['t_s'])*(x-tb['R'])
            t = round(t,2)
        return t

    # settings + definitions
    e5_in_gde = yr < 2009
    westost = [df['east'] == False, df['east']]
    married = [df['zveranl'] , df['zveranl'] == False]

    def aggr(df,inc):
        ''' Function to aggregate the variable inc among the adults of the tax unit
        '''
        df[inc+'_verh'] = df['zveranl'] * df[inc]
        df = df.join(df.groupby(['tu_id'])[(inc+'_verh')].sum(), on = ['tu_id'], how='left',rsuffix='_sum')
        df[inc+'_tu'] = np.select(married,[df[inc+'_verh_sum'],df[inc]])

        return df
    ###############################

    df = df.copy()
    # Ertragsanteil der Rente
    df['ertragsanteil'] = 0
    df.loc[df['renteneintritt'] <= 2004,'ertragsanteil'] = 0.27
    df.loc[df['renteneintritt'].between(2005,2020),'ertragsanteil'] = 0.5 + 0.02 * (df['renteneintritt'] - 2005)
    df.loc[df['renteneintritt'].between(2021,2040),'ertragsanteil'] = 0.8 + 0.01 * (df['renteneintritt'] - 2020)
    df.loc[df['renteneintritt'] >= 2041,'ertragsanteil'] = 1

    # Werbungskosten und Sonderausgaben
    # Pendlerpauschale
    df['pendeltage'] = np.select([df['comm_freq'] == 0,df['comm_freq'] == 1,df['comm_freq'] == 2,df['comm_freq'] == 3],[0,210,42,6])
    if 2001 <= yr <= 2003:
        df['entfpausch'] = np.maximum((0.4 * (df['comm_dist'] - 10) + (np.minimum(10 * 0.36,0.36 * df['comm_dist'])))  * (df['pendeltage'] * (df['w_hours'] > 0)) ,0)
    elif yr == 2007:
        df['entfpausch'] = np.maximum(0,tb['pendpausch'] * (df['comm_dist'] - 20) * df['pendeltage'] * (df['w_hours'] > 0))
    else:
        df['entfpausch'] = tb['pendpausch'] * df['comm_dist'] * df['pendeltage'] * (df['w_hours'] > 0)

    df['werbung'] = (df['m_wage'] > 0) * np.maximum(tb['werbung'],df['entfpausch'])
    df['sonder']  = (df['child'] == False) * tb['sonder']
    ####################################################
    # Einkommenskomponenten (auf jährlicher Basis!)

    df['gross_e1'] = 12 * df['m_self']
    # evtl. Pendlerpauschale abziehen

    df['gross_e4'] = np.maximum((12 * df['m_wage']) - df['werbung'], 0)
    # Minijob-Grenze beachten
    df.loc[df['m_wage']<=np.select(westost,[tb['mini_grenzew'],tb['mini_grenzeo']]),'gross_e4'] = 0

    # Kapitaleinkommen
    df['gross_e5'] = np.maximum((12 * df['m_kapinc']), 0)

    # Mieteinnahmen
    df['gross_e6'] = 12 * df['m_vermiet']

    # Sonstiges (Renten)
    df['gross_e7'] = np.maximum(12 * df['ertragsanteil'] * df['m_pensions'] - tb['vorsorgpausch'],0)
    # Summe der Einkünfte
    if e5_in_gde:
        df['gross_gde'] = df[['gross_e1','gross_e4','gross_e6','gross_e7']].sum(axis=1)
    else:
        df['gross_gde'] = df[['gross_e1','gross_e4','gross_e5','gross_e6','gross_e7']].sum(axis=1)


    df['m_brutto'] = df[['m_self','m_wage','m_kapinc','m_vermiet','m_pensions']].sum(axis=1)


    # Behinderten-Pauschbeträge
    hc_degrees = [df['handcap_degree'].between(45,50),df['handcap_degree'].between(51,60),df['handcap_degree'].between(61,70),df['handcap_degree'].between(71,80),
                  df['handcap_degree'].between(81,90),df['handcap_degree'].between(91,100)]
    hc_pausch = list(tb['sbhp'+str(i)] for i in range(50,110,10))
    df['handc_pausch'] = df['handcap_dummy'] * np.select(hc_degrees,hc_pausch)

    # Aggregate several things on the taxpayer couple
    for inc in ['m_wage','sonder','rvbeit','gkvbeit','avbeit','pvbeit','handc_pausch','gross_gde','gross_e5']:
        df = aggr(df,inc)

    # TAX DEDUCTIONS
    cprint('Vorsorgeaufwendungen...','red','on_white')
    # Vorsorgeaufwendungen bis 2004
    # TO DO
    # Vorsorgeaufwendungen ab 2005
    # TO DO
    # Vorsorgeaufwendungen ab 2010
    vorsorg2010 = [0.5 * (0.4 + 0.04 * (np.minimum(yr,2025) - 2010) * (12 * df['rvbeit_tu'] + np.maximum(12 * (df['pvbeit_tu'] + 0.96 * df['gkvbeit_tu']),np.minimum(0.12 * 12 * df['m_wage_tu'],2 * 1900)))),
                   0.4 + 0.04 * (np.minimum(yr,2025) - 2010) * (12 * df['rvbeit'] + np.maximum(12 * (df['pvbeit'] + 0.96 * df['gkvbeit']),np.minimum(0.12 * 12 * df['m_wage'],1900)))]

    df['vorsorge2010'] = np.select(married,vorsorg2010)

    # Günstigerprüfung der verschiedenen Vorsorgegrößen
    df['vorsorge'] = df['vorsorge2010']
    df = aggr(df,'vorsorge')

    # Altersentlastungsbetrag
    df['altfreib'] = 0
    df.loc[df['age']>64,'altfreib'] = np.minimum(tb['altentq'] * 12 * (df['m_wage'] + np.maximum(0,df[['m_kapinc','m_self','m_vermiet']].sum(axis=1))), tb['altenth'])
    df = aggr(df,'altfreib')

    # Entlastungsbetrag für Alleinerziehende
    if yr < 2015:
        df['hhfreib'] = np.select([df['alleinerz'] == True,df['alleinerz'] == False],[tb['hhfreib'],0])
    if yr >= 2015:
        df['hhfreib'] = np.select([df['alleinerz'] == True,df['alleinerz'] == False],[tb['hhfreib'] + (df['child_num_tu'] - 1) * 240,0])


    # Kinderfreibetrag...Alleinerziehende bekommen nur den halben...Ehepartner auch
    #df['kifreib'] = np.select([df['alleinerz'],~df['alleinerz']],[0.5 * tb['kifreib'] * df['child_num_tu'], tb['kifreib'] * df['child_num_tu']]) * (df['child'] == False)
    df['kifreib'] = 0.5 * tb['kifreib'] * df['child_num_tu'] * (df['child'] == False)
    # ZU VERSTEUERNDEN EINKOMMEN
    # Ohne Kinderfreibetrag
    df['zve_nokfb'] = 0
    df.loc[~df['zveranl'],'zve_nokfb']      = np.maximum(df['gross_gde'] - np.minimum(tb['spsparf'] + tb['spwerbz'],df['gross_e5']) * e5_in_gde - df['vorsorge'] - df['sonder'] - df['handc_pausch'] - df['hhfreib'] - df['altfreib'],0)
    df.loc[df['zveranl'],'zve_nokfb'] = 0.5 * np.maximum(df['gross_gde_tu'] - np.minimum(2 * (tb['spsparf'] + tb['spwerbz']),df['gross_e5_tu']) * e5_in_gde - df['vorsorge_tu'] - df['sonder_tu'] - df['handc_pausch_tu'] - df['hhfreib'] - df['altfreib'],0)

    # Ohne Kinderfreibetrag, aber ohne Kapitalerträge
    df.loc[~df['zveranl'],'zve_abg_nokfb']      = np.maximum(df['gross_gde'] - np.minimum(tb['spsparf'] + tb['spwerbz'],df['gross_e5']) * (e5_in_gde == False) - df['vorsorge'] - df['sonder'] - df['handc_pausch'] - df['hhfreib'] - df['altfreib'],0)
    df.loc[df['zveranl'],'zve_abg_nokfb'] = 0.5 * np.maximum(df['gross_gde_tu'] - np.minimum(2 * (tb['spsparf'] + tb['spwerbz']),df['gross_e5_tu']) * (e5_in_gde == False) - df['vorsorge_tu'] - df['sonder'] - df['handc_pausch_tu'] - df['hhfreib'] - df['altfreib'],0)

    df['zve_kfb'] = np.maximum(df['zve_nokfb'] - df['kifreib'],0)
    df['zve_abg_kfb'] = np.maximum(df['zve_abg_nokfb'] - df['kifreib'],0)
    df[['hid','pid','age','zve_nokfb','gross_e4','gross_e7','gross_gde']][0:10]
    #CONTROL OUTPUT
    #print(*df[:0],sep='\n')


    #df[['hid','tu_id','gross_gde_tu','gross_gde_verh','gross_gde']][df['hid'] == 949]

    if e5_in_gde:
        inclist = ['nokfb','kfb']
    else:
        inclist = ['nokfb','abg_nokfb','kfb','abg_kfb']

    #####################
    # STEUERTARIF
    cprint('Steuertarif...','red','on_white')
    for inc in inclist:
        df['tax_'+inc] = np.vectorize(tarif)(df['zve_'+inc],tb)
        df = aggr(df,'tax_'+inc)
    ###################


    # Abgeltungssteuer
    df['abgst'] = 0
    if e5_in_gde == False:
        df.loc[~df['zveranl'],'abgst'] = tb['abgst'] * np.maximum(df['gross_e5'] - tb['spsparf'] - tb['spwerbz'],0)
        df.loc[df['zveranl'],'abgst']  = 0.5 * tb['abgst'] * np.maximum(df['gross_e5_tu'] - 2 * (tb['spsparf'] - tb['spwerbz']),0)
    df = aggr(df,'abgst')
    # Kindergeld
    df['child_count'] = df.groupby(['tu_id'])['child'].cumsum()
    df['kindergeld'] = 0
    for k in range(1,int(df['child_num_tu'].max())+1):
        z = min(k,4)
        if yr <= 2011:
            df.loc[(df['child_count'] == k) & (df['child']) & (df['m_wage'] <= tb['kgfreib']) ,'kindergeld'] = tb['kgeld'+str(z)]
        if yr > 2011:
            df.loc[(df['child_count'] == k) & (df['child']) & (df['w_hours'] <= 20) ,'kindergeld']           = tb['kgeld'+str(z)]

    df = df.join(df.groupby(['tu_id'])['kindergeld'].sum(), on = ['tu_id'], how='left',rsuffix='_tu')

#    df.to_excel(pd.ExcelWriter(data_path+'check_kg.xlsx'),sheet_name='py_out',columns=['tu_id','child','child_count','w_hours','kindergeld','kindergeld_tu'],na_rep='NaN',freeze_panes=(1,0))

    # Günstigerprüfung...auf TU-Ebene!
    cprint('Günstigerprüfung...','red','on_white')
    for inc in inclist:
        df['nettax_' + inc] = df['tax_'+inc+'_tu']
        if 'abg' in inc:
            df['nettax_' + inc] = df['nettax_'+inc] + df['abgst_tu']
        if ('nokfb' in inc) | (yr <= 1996):
            df['nettax_' + inc] = df['nettax_'+inc] - (12 * df['kindergeld_tu'])

    df['minpay'] = df.filter(regex='nettax').min(axis=1)

    df['tax_income'] = 0
    df['incometax']  = 0
    df['abgehakt']   = False
    for inc in inclist:
        df.loc[(df['minpay'] == df['nettax_' + inc]) & (df['abgehakt'] == False),'tax_income'] = df['zve_'+inc]
        # Income Tax in monthly terms!
        df.loc[(df['minpay'] == df['nettax_' + inc]) & (df['abgehakt'] == False),'incometax'] = df['tax_'+inc+'_tu'] / 12
        # set a couple of values to zero if necessary
        if (('nokfb' in inc) == False) | (yr <= 1996):
            df.loc[(df['minpay'] == df['nettax_' + inc]) & (df['abgehakt'] == False),'kindergeld'] = 0
            df.loc[(df['minpay'] == df['nettax_' + inc]) & (df['abgehakt'] == False),'kindergeld_tu'] = 0
        if ('abg' in inc):
            df.loc[(df['minpay'] == df['nettax_' + inc]) & (df['abgehakt'] == False),'abgst'] = 0
            df.loc[(df['minpay'] == df['nettax_' + inc]) & (df['abgehakt'] == False),'abgst_tu'] = 0
        df.loc[(df['minpay'] == df['nettax_' + inc]),'abgehakt'] = True

    # Kindergeld für Gesamthaushalt
    df = df.join(df.groupby(['hid'])['kindergeld'].sum(), on = ['hid'], how='left',rsuffix='_hh')
    # Control output

    #df.to_excel(pd.ExcelWriter(data_path+'check_güsntiger.xlsx'),sheet_name='py_out',columns= ['tu_id','child','zveranl','minpay','incometax','abgehakt','nettax_abg_kfb_tu', 'zve_abg_kfb_tu', 'tax_abg_kfb_tu', 'nettax_abg_kfb_tu', 'zve_abg_kfb_tu', 'tax_abg_kfb_tu', 'nettax_abg_kfb_tu', 'zve_abg_kfb_tu', 'tax_abg_kfb_tu', 'nettax_abg_kfb_tu', 'zve_abg_kfb_tu', 'tax_abg_kfb_tu'],na_rep='NaN',freeze_panes=(0,1))
    #pd.to_pickle(df,data_path+ref+'/taxben_check')
    #df.to_excel(pd.ExcelWriter(data_path+'check_tax_incomes.xlsx'),sheet_name='py_out',columns=['hid','pid','age','female','child','zve_nokfb','zve_kfb','tax_nokfb','tax_kfb','gross_e1','gross_e4','gross_e5','gross_e6','gross_e7','gross_gde'],na_rep='NaN',freeze_panes=(0,1))

    # Soli
    cprint('Solidaritätszuschlag...','red','on_white')

    if yr >= 1991:
        if e5_in_gde:
            df['solibasis'] = df['tax_kfb_tu']
        else:
            df['solibasis'] = df['tax_kfb_tu'] + df['abgst']
        # Soli also in monthly terms
        df['soli'] = np.minimum(tb['solisatz'] * df['solibasis'],np.maximum(0.2 * (df['solibasis'] - tb['solifreigrenze']) / 12,0))

    return df


def ben(df,tb,yr,ref,data_path):
    ''' Benefit Simulation
         - Wohngeld
        - ALG2
        - Kinderzuschlag

        - Sozialhilfe (TODO!)
    '''
    #######################################################
    #### WOHNGELD
    #######################################################
    print("Wohngeld...")
    # Baue M und Y für Wohngeld-Formel
    ## Einkommen
    df['wg_abz'] = (df['incometax']>0) * 1 + (df['rvbeit']>0) * 1 + (df['gkvbeit']>0) * 1
    df['wg_abzuege'] = (np.select([df['wg_abz'] == 0, df['wg_abz'] == 1, df['wg_abz'] == 2, df['wg_abz'] == 3,],
                          [tb['wgpabz0'],             tb['wgpabz1'],      tb['wgpabz2'],    tb['wgpabz3']]))
    df['wg_grossY'] = (np.maximum(df['gross_e1']/12,0) + np.maximum(df['gross_e4']/12,0) +
                      np.maximum(df['gross_e5']/12,0) + np.maximum(df['gross_e6']/12,0))
    df['wg_otherinc'] = df['m_alg1'] + df['m_transfers'] + (df['ertragsanteil'] * df['m_pensions'])

    if yr >= 2016:
        df['wg_incdeduct'] = (df['handcap_degree'] > 0) * tb['wgpfbm80'] + ((df['child'] == True)* (df['m_wage']>0)) * np.minimum(tb['wgpfb24'],df['m_wage']) + ((df['alleinerz'] == True) * tb['wgpfb12'])
    else:
        sys.exit("Wohngeld-Abzüge vor 2016 noch nicht modelliert")


    df['wgY'] = (1 - df['wg_abzuege']) * np.maximum((df['wg_grossY'] + df['wg_otherinc'] - df['wg_incdeduct']),0)
    # TU-Aggregierung
    df = df.join(df.groupby(['tu_id'])['wgY'].sum(), on = ['tu_id'], how='left',rsuffix='_tu')

    df['Y'] = np.maximum(pd.Series(df['wgY_tu']+4).round(-1)-5,0)
    # Minimum Y
    for i in range(1,12):
        df.loc[df['hhsize'] == i,'Y']   = np.maximum(df['Y'],tb['wgminEK'+str(i)+'p'])
    df.loc[df['hhsize'] >= 12,'Y']      = np.maximum(df['Y'],tb['wgminEK12p'])

    # Miete
    # Maximal- und Minimalmiete
    df['max_rent'] = 0
    df['min_rent'] = 0
    if yr >= 2009:
        for i in range(1,13):
            if i <= 5:
                df.loc[(df['hhsize'] == i),'max_rent'] = tb['wgmax'+str(i)+'p_m']
            df.loc[(df['hhsize'] == i),'min_rent'] = tb['wgmin'+str(i)+'p']

        df.loc[(df['hhsize'] > 5),'max_rent'] = df['max_rent'] + tb['wgmaxplus5_m'] * (df['hhsize'] - 5)
        df.loc[(df['hhsize'] > 12),'min_rent'] = df['max_rent'] + tb['wgmaxplus5_m'] * (df['hhsize'] - 5)

    df['max_rent'] = df['max_rent'] * df['hh_korr']

    df['wgmiete']  = np.minimum(df['max_rent'],df['miete'] * df['hh_korr'])
    df['wgheiz']   = df['heizkost'] * df['hh_korr']
    df['M'] = np.maximum(df['wgmiete'] + df['wgheiz'],df['min_rent'])
    # TO DO: Heimbewohner

    df['M'] = np.maximum(pd.Series(df['M']+4).round(-1) - 5,0)

    # Calculate Wohngeld
    wg = {}
    for x in range(1,13):
        for z in ['a','b','c']:
             wg[z] = tb['wg_'+z+'_'+str(x)+'p']

        a = wg['a']
        b = wg['b']
        c = wg['c']

        df.loc[np.minimum(df['hhsize_tu'],12) == x,'wohngeld'] = np.maximum(0, tb['wg_factor'] * (df['M'] - ((a+ (b*df['M']) + (c*df['Y']))*df['Y'])))

    # Ermittle Wohngeld-Summe im Gesamthaushalt
    df['wg_head'] = df['wohngeld'] * df['head_tu']
    df = df.join(df.groupby(['hid'])['wg_head'].sum(), on = ['hid'], how='left',rsuffix='_hh')
    df = df.rename(columns = {'wg_head_hh':'wohngeld_hh'})

    #print(df['wohngeld'].describe())
    #######################################################
    #### ALG 2
    #######################################################
    if yr <= 2004:
        df['m_alg2'] = 0
        df['kiz']    = 0
        df['kdu']    = 0
    else:
        # Mehrbedarf für Alleinerziehende
        df['mehrbed'] = ((df['child'] == False) * df['alleinerz'] *
                          np.minimum(np.maximum(((df['child6_num'] == 1) | (df['child15_num'].between(2,3))) * tb['a2mbch2'],
                                                  tb['a2mbch1'] * df['child_num']), tb['a2zu2']/100 ))

        ### REGELBEDARF
        if yr <= 2010:
            regelberechnung =  [tb['rs_hhvor'] * (1 + df['mehrbed'])                    +
                               (tb['rs_hhvor'] * tb['a2ch14'] * df['child14_24_num'])   +
                               (tb['rs_hhvor'] * tb['a2ch7'] * df['child7_13_num'])     +
                               (tb['rs_hhvor'] * tb['a2ch0'] * (df['child2_num'] + df['child3_6_num'])),
                                tb['rs_hhvor'] * tb['a2part'] * (1 + df['mehrbed'])     +
                               (tb['rs_hhvor'] * tb['a2part'])                          +
                               (tb['rs_hhvor'] * tb['a2ch18'] * np.maximum((df['adult_num'] - 2),0))  +
                               (tb['rs_hhvor'] * tb['a2ch14'] * df['child14_24_num'])   +
                               (tb['rs_hhvor'] * tb['a2ch7'] * df['child7_13_num'])     +
                               (tb['rs_hhvor'] * tb['a2ch0'] * (df['child2_num'] + df['child3_6_num'])) ]

        else:
            regelberechnung =  [tb['rs_hhvor'] * (1 + df['mehrbed'])    +
                               (tb['rs_ch14'] * df['child14_24_num'])  +
                               (tb['rs_ch7'] * df['child7_13_num'])     +
                               (tb['rs_ch0'] * (df['child2_num'] + df['child3_6_num'])),
                                tb['rs_2adults'] * (1 + df['mehrbed'])  +
                               tb['rs_2adults']                         +
                               (tb['rs_madults'] * np.maximum((df['adult_num'] - 2),0))  +
                               (tb['rs_ch14'] * df['child14_24_num'])   +
                               (tb['rs_ch7'] * df['child7_13_num'])     +
                               (tb['rs_ch0'] *(df['child2_num'] + df['child3_6_num'])) ]

        df['regelsatz'] = np.select([df['adult_num']==1,df['adult_num']>1],regelberechnung)
        # 'angemessene Kosten der Unterkunft: Nimm an, dass Wohngeldrichtlinien angewendet werden
        df['alg2_kdu'] = df['M'] + np.maximum(df['heizkost'] - df['wgheiz'],0)

        if 2005 <= yr <= 2010:
            print('"Armutsgewöhnungszuschlag" noch nicht modelliert.')
        else:
            df['bef_zuschlag'] = 0

        df['regelbedarf'] = df[['regelsatz','alg2_kdu','bef_zuschlag']].sum(axis=1)

        # Vermögensanrechnung
        # Schätzung aus Kapitaleinkommen...ist bereits auf HH-Ebene
        df['assets'] = df['divdy'] / tb['r_assets']

        #df['vermfreib'] = tb['a2vki']
        # individuelle Freibeträge
        df['ind_freib'] = 0
        df.loc[(df['byear'] >= 1948)  & (df['child'] == False),'ind_freib'] = tb['a2ve1'] * df['age']
        df.loc[(df['byear'] <  1948)  & (df['child'] == False),'ind_freib'] = tb['a2ve2'] * df['age']
        df = df.join(df.groupby(['hid'])['ind_freib'].sum(), on = ['hid'], how='left',rsuffix='_hh')

        # maximale Freibeträge
        df['maxvermfb'] = 0
        df.loc[(df['byear'] < 1948) & (df['child'] == False),'maxvermfb'] = tb['a2voe1']
        df.loc[(df['byear'].between(1948,1957)) & (df['child'] == False),'maxvermfb'] = tb['a2voe1']
        df.loc[(df['byear'].between(1958,1963)) & (df['child'] == False),'maxvermfb'] = tb['a2voe3']
        df.loc[(df['byear'] >= 1964)  & (df['child'] == False),'maxvermfb'] = tb['a2voe4']
        df = df.join(df.groupby(['hid'])['maxvermfb'].sum(), on = ['hid'], how='left',rsuffix='_hh')


        df['vermfreibetr'] = np.minimum(df['ind_freib_hh'] + df['child18_num'] * tb['a2vkf'] + df['adult_num'] * tb['a2verst'],df['maxvermfb_hh'])
        df.loc[(df['assets'] > df['vermfreibetr']),'regelbedarf'] = 0

        # AlG2-relevantes Einkommen
        df.loc[(df['child'] == False),'alg2_grossek'] = df[['m_wage','m_transfers','m_self','m_vermiet','m_kapinc','m_pensions','m_alg1']].sum(axis=1)
        df['alg2_grossek'] = df['alg2_grossek'].fillna(0)
        df.loc[(df['child'] == False),'alg2_ek']      = np.maximum(df['alg2_grossek'] - df['incometax'] - df['svbeit'],0)
        df['alg2_ek'] = df['alg2_ek'].fillna(0)

        # Anrechnungsfreies Einkommen
        df['ekanrefrei'] = 0
        df.loc[(df['m_wage'] <= tb['a2grf']),'ekanrefrei'] = df['m_wage']
        df.loc[(df['m_wage'].between(tb['a2grf'],tb['a2eg1'])),'ekanrefrei'] = tb['a2grf'] + tb['a2an1'] * (df['m_wage'] - tb['a2grf'])
        df.loc[(df['m_wage'].between(tb['a2eg1'],tb['a2eg2'])) & (df['child18_num'] == 0),'ekanrefrei'] = tb['a2grf'] + tb['a2an1'] * (tb['a2eg1'] - tb['a2grf']) + tb['a2an2'] * (df['m_wage'] - tb['a2eg1'])
        df.loc[(df['m_wage'].between(tb['a2eg1'],tb['a2eg3'])) & (df['child18_num'] > 0),'ekanrefrei']  = tb['a2grf'] + tb['a2an1'] * (tb['a2eg1'] - tb['a2grf']) + tb['a2an2'] * (df['m_wage'] - tb['a2eg1'])

        df.loc[(df['m_wage'] > tb['a2eg2']) & (df['child18_num'] == 0),'ekanrefrei'] = tb['a2grf'] + tb['a2an1'] * (tb['a2eg1'] - tb['a2grf']) + tb['a2an2'] * (tb['a2eg2'] - tb['a2eg1'])
        df.loc[(df['m_wage'] > tb['a2eg3']) & (df['child18_num'] > 0),'ekanrefrei']  = tb['a2grf'] + tb['a2an1'] * (tb['a2eg1'] - tb['a2grf']) + tb['a2an2'] * (tb['a2eg3'] - tb['a2eg1'])
        # Für Kinder
        df.loc[(df['child']),'ekanrefrei'] = np.maximum(0,df['m_wage'] - 100)
        df['ar_alg2_ek'] = np.maximum(df['alg2_ek']-df['ekanrefrei'],0)
        ## Aggregate on HH
        for var in ['ar_alg2_ek','alg2_grossek']:
            df = df.join(df.groupby(['hid'])[var].sum(), on = ['hid'], how='left',rsuffix='_hh')
        df['ar_base_alg2_ek'] = df['ar_alg2_ek_hh'] + df['kindergeld_hh']
        #######################
        ## KINDERZUSCHLAG
        #######################

        # Regelbedarf der Eltern.
        if yr <= 2010:
            # not yet implemented
            kiz_regel = [np.nan,np.nan,np.nan]
        if yr > 2010:
            kiz_regel = [tb['rs_hhvor'] * (1 + df['mehrbed']),
                         tb['rs_2adults'] + ((1 + df['mehrbed']) * tb['rs_2adults']),
                         tb['rs_madults'] * df['adult_num'] ]

        df['kiz_ek_regel'] = np.select([df['adult_num'] == 1,df['adult_num'] == 2,df['adult_num'] >2],kiz_regel)
        df['kiz_miete'] = df['miete'] * df['hh_korr']
        df['kiz_heiz'] = df['heizkost'] * df['hh_korr']
        # Anteil Wohnbedarf der Eltern
        wb = wohnbedarf(yr)
        df['wb_eltern_share'] = 1.0
        for c in [1,2]:
            for r in [1,2,3,4]:
                df.loc[(df['child_num'] == r) & (df['adult_num'] == c),'wb_eltern_share'] = wb[r-1][c-1] / 100
            df.loc[(df['child_num'] >= 5) & (df['adult_num'] == c),'wb_eltern_share'] = wb[4][c-1] / 100

        df['kiz_ek_kdu'] = df['wb_eltern_share'] * (df['kiz_miete'] + df['kiz_heiz'])
        df['kiz_ek_relev'] = df['kiz_ek_regel'] + df['kiz_ek_kdu']

        # max income to be eligible for KIZ: ALG2 relgelsatz w/o children + KIZ
        df['kiz_ek_max'] = df['kiz_ek_relev'] + tb['a2kiz'] * df['child_num']
        # min income to be eligible for KIZ (different for singles and couples)
        df['kiz_ek_min'] = tb['a2kiz_minek_cou'] * (df['hhtyp'] == 4) + (tb['a2kiz_minek_sin'] * (df['alleinerz'] == True))

#        Übersetzung §6a BKGG auf deutsch:
#     1. Um KIZ zu bekommen, muss das Bruttoeinkommen minus Wohngeld und Kindergeld über 600 bzw. 900 € liegen.
#     2. Das Nettoeinkommen minus Wohngeld muss unterhalb des Bedarfs plus Gesamtkinderzuschlag liegen.
#     3. Dann wird geschaut, wie viel von dem Einkommen (Erwachsene UND Kinder !) noch auf KIZ angerechnet wird.
#        Wenn das zu berücksichtigende Einkommen UNTER der Höchsteinkommensgrenze und UNTER der Bemessungsgrundlage liegt, wird
#        der volle KIZ gezahlt
#        Wenn es ÜBER der Bemessungsgrundlage liegt, wird die Differenz abgezogen mit 50% Abschmelzung.
        df['kiz_ek_gross'] =  df['alg2_grossek_hh']
        df['kiz_ek_net']   =  df['ar_alg2_ek_hh']

        # Anzurechnendes Einkommen.
        df['kiz_ek_anr'] = np.maximum(0,round((df['ar_alg2_ek_hh'] - df['kiz_ek_relev'])/10)*5)
        # Höhe KIZ
        df['kiz'] = 0
        df['kiz_incrange'] = (df['kiz_ek_gross'] >= df['kiz_ek_min']) & (df['kiz_ek_net'] <= df['kiz_ek_max'])
        df.loc[df['kiz_incrange'],'kiz'] = np.maximum((tb['a2kiz'] * df['child_num_tu'])- df['kiz_ek_anr'],0)

        #print('IS KIZ CONSTANT WITHIN HOUSEHOLDS??')
        #df = df.join(df.groupby(['tu_id'])['kiz'].std(), on = ['tu_id'], how='left',rsuffix='_std').fillna(0)
        #print(df[['hid','tu_id','pid','kiz']][df['kiz_std'] != 0])
        #assert((len(df.groupby(['tu_id'])['kiz'].std().value_counts())==1) & (df.groupby(['tu_id'])['kiz'].std().value_counts().index[0] == 0))
        ###############################
        # Check eligibility for benefits
        ###############################
        df['ar_wg_alg2_ek']  = df['ar_base_alg2_ek'] + df['wohngeld']
        df['ar_kiz_alg2_ek']  = df['ar_base_alg2_ek'] + df['kiz']
        df['ar_wgkiz_alg2_ek']  = df['ar_base_alg2_ek'] + df['wohngeld'] + df['kiz']

        for v in ['base','wg','kiz','wgkiz']:
            df['fehlbedarf_'+v] = df['regelbedarf'] - df['ar_'+v+'_alg2_ek']
            df['m_alg2_'+v]    = np.maximum(df['fehlbedarf_'+v],0)
        # Check which benefits are superior to others
        for v in ['wg','kiz','wgkiz']:
            df[v+'_vorrang'] = (df['m_alg2_'+v] == 0) & (df['m_alg2_base'] > 0)

        df['m_alg2'] = df['m_alg2_base']

        df.loc[(df['wg_vorrang']) | (df['kiz_vorrang']) | (df['wgkiz_vorrang']),'m_alg2'] = 0
        df.loc[(df['wg_vorrang'] == False) & (df['wgkiz_vorrang'] == False) & (df['m_alg2_base'] > 0),'wohngeld'] = 0
        df.loc[(df['kiz_vorrang'] == False) & (df['wgkiz_vorrang'] == False) & (df['m_alg2_base'] > 0),'kiz'] = 0

        assert(df['m_alg2'].notna().all())
        # set ALG2 only for TU Head?

        # Drop Stuff
        dropvars = ['belowmini', 'above_thresh_kv', 'above_thresh_rv', 'gkvrbeit', 'pvrbeit',
                     'ertragsanteil', 'pendeltage', 'entfpausch', 'handc_pausch', 'm_wage_verh',
                     'sonder_verh', 'rvbeit_verh', 'rvbeit_verh_sum', 'gkvbeit_verh', 'gkvbeit_verh_sum',
                     'avbeit_verh', 'avbeit_verh_sum', 'pvbeit_verh', 'pvbeit_verh_sum', 'handc_pausch_verh',
                     'handc_pausch_verh_sum', 'gross_gde_verh', 'gross_gde_verh_sum', 'gross_e5_verh',
                     'gross_e5_verh_sum', 'vorsorge', 'vorsorge_verh', 'vorsorge_verh_sum', 'altfreib_verh',
                     'altfreib_verh_sum', 'tax_nokfb_verh', 'tax_nokfb_verh_sum', 'tax_abg_nokfb_verh',
                     'tax_abg_nokfb_verh_sum', 'tax_kfb_verh', 'tax_kfb_verh_sum', 'tax_abg_kfb_verh',
                     'tax_abg_kfb_verh_sum', 'abgst_verh', 'abgst_verh_sum', 'child_count', 'nettax_nokfb',
                     'nettax_abg_nokfb', 'nettax_kfb', 'nettax_abg_kfb', 'minpay', 'wg_abz', 'wg_abzuege',
                     'wg_grossY', 'wg_otherinc', 'wg_incdeduct',  'wgY', 'wgY_tu', 'max_rent', 'min_rent',
                     'wgmiete', 'wgheiz', 'mehrbed', 'bef_zuschlag', 'ind_freib', 'ind_freib_hh', 'maxvermfb',
                     'maxvermfb_hh', 'vermfreibetr', 'kiz_ek_regel', 'kiz_miete', 'kiz_heiz', 'wb_eltern_share',
                     'kiz_ek_kdu', 'kiz_ek_relev', 'kiz_ek_max', 'kiz_ek_min', 'kiz_ek_gross', 'kiz_ek_net',
                     'kiz_ek_anr', 'kiz_incrange', 'ar_wg_alg2_ek', 'ar_kiz_alg2_ek', 'ar_wgkiz_alg2_ek',
                     'fehlbedarf_base', 'm_alg2_base', 'fehlbedarf_wg', 'm_alg2_wg', 'fehlbedarf_kiz', 'm_alg2_kiz',
                      'fehlbedarf_wgkiz', 'm_alg2_wgkiz', 'wg_vorrang', 'kiz_vorrang', 'wgkiz_vorrang']
        drop(df,dropvars)

    return df

def tb_out(df,ref,graph_path):
    print('-'*80)
    print('TAX BENEFIT AGGREGATES')
    print('-'*80)
    cprint('Revenues','red','on_white')
    # Incometax over all persons. SV Beiträge too
    #

    for tax in ['gkvbeit','rvbeit','pvbeit','avbeit','incometax','soli']:
        df['w_sum_'+tax] = df[tax] * df['hweight'] * df['head_tu']
        print(tax + " : " + str(df['w_sum_'+tax].sum()/1e9 * 12) + " bn €.")
    cprint('Benefit recipients','red','on_white')
    for ben in ['m_alg1','m_alg2','wohngeld','kiz']:
        print(ben +" :" + str(df['hweight'][(df[ben]>0) & (df['head_tu'])].sum()/1e6) + " Million Households.")
    print('-'*80)

    # Check Income Distribution:
    df['eq_scale'] = 1 + 0.5 * np.maximum((df['hhsize'] - df['child14_num'] - 1),0) + 0.3 * (df['child14_num'])
    df['dpi_eq']  = df['dpi'] / df['eq_scale']
    df['dpi_eq'].describe()
    plt.clf()
    ax = df['dpi_eq'].plot.kde(xlim=(0,4000))
    ax.set_title('Distribution of equivalized disp. income ' + str(ref))
    plt.savefig(graph_path+'dist_dpi_'+ref+'.png')
    print('-'*80)
    print('Gini-Coefficient Disp. Income: ', gini(df['dpi_eq'],df['pweight']))
    print('-'*80)

    return True


