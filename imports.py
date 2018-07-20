# -*- coding: utf-8 -*-
"""
This is where scripts and functions are defined that are regularly
used in various bits of the model.
All import commands to be inserted here.
"""

import pandas as pd
# pd.options.mode.use_inf_as_na = True

import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import os


def init(settings):
    '''checks for existence of folder and creates them if necesarry
    '''
    for r in settings['Reforms']:
        if not os.path.exists(settings['DATA_PATH']+r):
            os.makedirs(settings['DATA_PATH']+r)
        if not os.path.exists(settings['GRAPH_PATH']+r):
            os.makedirs(settings['GRAPH_PATH']+r)
    if not os.path.exists(settings['DATA_PATH']+'SOEP'):
        os.makedirs(settings['DATA_PATH'] + 'SOEP')
    if not os.path.exists(settings['GRAPH_PATH']+'hypo'):
        os.makedirs(settings['GRAPH_PATH'] + 'hypo')


def get_params(settings):
    ''' Load Tax-Benefit Parameters.
    returns A Dictionary of Dictionaries for each year.
    '''
    params = pd.read_excel(settings['MAIN_PATH'] +
                           '/data/params/param.xls', index_col='para')
    par = {}
    for yr in range(1984, 2019):
        yearpar = {}
        col = 'y' + str(yr)
        for i in range(0, len(params)):
            name = params.index[i]
            yearpar.update({name: params.loc[name, col]})

        # TO DO: English Translation
        yearpar['ch_allow'] = yearpar.pop('kifreib')
        # add year
        yearpar.update({'yr': str(yr)})
        # When finished, add to par
        par.update({str(yr): yearpar})



    return par


def regex_replace(df, rx, numlist, x):
    '''
    function that replaces all columns defined by regex
    in a dataframe from the list in numlist to value x.
    '''
    sub = df.filter(regex=rx)

    for v in list(sub):
        df[v] = x[df[v] in numlist]

    return df


def tab(df, row, col):
    ''' Cross-Tabulation. For several nested columns, insert a list for col
    '''
    c = [df[col[0]]]
    if len(col) > 1:
        for l in range(1, len(col)):
            c = c.append(df[col[l]])

    print(pd.crosstab(df[row], columns=c, dropna=False))


def drop(df, dropvars):
    ''' Stata Drop Command. Drops the variable list 'vars' from dataframe df
        A convenience tool
    '''
    df = df.drop(columns=dropvars, axis=1)


def aggr(df, inc, kids=False):
    ''' Function to aggregate some variable
        'inc' among
        - the 2 adults of the tax unit (if they are married!)
          if kids is False.
          Do this for taxable incomes
        - all members (incl. children) of the tax_unit
           if 'hh' is chosen as unit
        returns a variable with suffix _tu or _tu_k, depending on the
        parameter kids
    '''
    if kids is False:
        df[inc+'_verh'] = df['zveranl'] * df[inc]
        df = df.join(
            df.groupby(['tu_id'])[(inc+'_verh')].sum(),
            on=['tu_id'], how='left', rsuffix='_sum')
        df[inc+'_tu'] = np.select([df['zveranl'], ~df['zveranl']],
                                  [df[inc+'_verh_sum'], df[inc]])

    if kids is True:
        df = df.join(
            df.groupby(['tu_id'])[inc].sum(),
            on=['tu_id'], how='left', rsuffix='_sum')
        df[inc+'_tu_k'] = df[inc+'_sum']
    return df


def ols(y, X, show=False):
    ''' Estimates OLS. Requires Data Frames for y and X.
        Constants should be added to X automatically,
        but are not done so yet!!!.
    '''
    #model_name = sm.OLS(np.asarray(y,dtype=float),sm.add_constant(np.asarray(X,dtype=float))).fit()
    #model_name = sm.OLS(y,sm.add_constant(X,has_constant='add')).fit()
    model_name = sm.OLS(y, X.astype(float)).fit()
    if show:
        print(model_name.summary())
    return model_name


def gini(x, w=None):
    '''
    Calculate the Gini coefficient of a numpy array with weights.
    Source: https://stackoverflow.com/questions/48999542/more-efficient-weighted-gini-coefficient-in-python

    '''

    # Array indexing requires reset indexes.
    x = pd.Series(x).reset_index(drop=True)
    if w is None:
        w = np.ones_like(x)
    w = pd.Series(w).reset_index(drop=True)
    n = x.size
    wxsum = sum(w * x)
    wsum = sum(w)
    sxw = np.argsort(x)
    sx = x[sxw] * w[sxw]
    sw = w[sxw]
    pxi = np.cumsum(sx) / wxsum
    pci = np.cumsum(sw) / wsum
    g = 0.0
    for i in np.arange(1, n):
        g = g + pxi.iloc[i] * pci.iloc[i - 1] - pci.iloc[i] * pxi.iloc[i - 1]
    return g

