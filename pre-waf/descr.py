# -*- coding: utf-8 -*-
"""
Created on Wed Sep  5 13:32:44 2018

@author: iza6354
"""
import pandas as pd


def descriptives(df):
    ''' Produce some overview on the data
    '''
    descr = pd.DataFrame()

    descr['LaborForce'] = df[(df['age'].between(17, 65)) &
                             ~df['ineducation'] &
                             ~df['handcap_dummy']
                             ].groupby('syear')['pweight'].sum() / 1000

    descr['InEduc'] = df[df['ineducation']
                         ].groupby('syear')['pweight'].sum() / 1000

    descr['pensioners'] = df[df['pensioner']
                             ].groupby('syear')['pweight'].sum() / 1000

    descr['disabled'] = df[df['handcap_dummy']
                           ].groupby('syear')['pweight'].sum() / 1000

    hhtypen = {1: 'Singles',
               2: 'SingleParents',
               3: 'Couples',
               4: 'Couples_w_Kids'}

    for h in range(1, 5):
        descr[hhtypen[h]] = df[(df['hhtyp'] == h) &
                               df['head_tu']
                               ].groupby('syear')['hweight'].sum() / 1000

    return descr
