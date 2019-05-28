# -*- coding: utf-8 -*-
"""
This is where scripts and functions are defined that are regularly
used in various bits of the model.
"""

import pandas as pd

# pd.options.mode.use_inf_as_na = True

import numpy as np
import os
import time


def init(settings):
    """checks for existence of folders and creates them if necesarry
    """
    for r in settings["Reforms"]:
        if not os.path.exists(settings["DATA_PATH"] + r):
            os.makedirs(settings["DATA_PATH"] + r)
        if not os.path.exists(settings["GRAPH_PATH"] + r):
            os.makedirs(settings["GRAPH_PATH"] + r)
    for path in [settings["DATA_PATH"] + "SOEP",
                 settings["DATA_PATH"] + "hypo",
                 settings["GRAPH_PATH"] + "hypo",
                 settings["GRAPH_PATH"] + "wageplots"]:
        if not os.path.exists(path):
            os.makedirs(path)


def get_params(path):
    """ Load Tax-Benefit Parameters.
    returns A Dictionary of Dictionaries for each year.
    """
    params = pd.read_excel(
        path+"/param.xls", index_col="para"
    ).to_dict()

    for yr in range(1984, 2020):
        params["y" + str(yr)]["yr"] = yr
    #    par = {}
    #    for yr in range(1984, 2020):
    #        yearpar = {}
    #        col = 'y' + str(yr)
    #        for i in range(0, len(params)):
    #            name = params.index[i]
    #            yearpar.update({name: params.loc[name, col]})
    #
    #        # add year
    #        yearpar.update({'yr': str(yr)})
    #        # When finished, add to par
    #        par.update({str(yr): yearpar})

    return params


def regex_replace(df, rx, numlist, x):
    """
    function that replaces all columns defined by regex
    in a dataframe from the list in numlist to value x.
    """
    sub = df.filter(regex=rx)

    for v in list(sub):
        df[v] = x[df[v] in numlist]

    return df


def tab(df, row, col):
    """ Cross-Tabulation. For several nested columns, insert a list for col
    """
    c = [df[col[0]]]
    if len(col) > 1:
        for l in range(1, len(col)):
            c = c.append(df[col[l]])

    print(pd.crosstab(df[row], columns=c, dropna=False))


def drop(df, dropvars):
    """ Stata Drop Command. Drops the variable list 'vars' from dataframe df
        A convenience tool
    """
    df = df.drop(columns=dropvars, axis=1)


def aggr(df, inc, unit):
    """ Function to aggregate some (income) variable within the household

        args:
            df: the dataframe in which aggregation takes place. Needs to have
            the variable 'inc', but also ['zveranl', 'hid', 'tu_id']
        inc: the variable to aggregate
        unit: The household members among which you aggregate;
        'adult_married': the 2 adults of the tax unit (if they are married!)
                         Do this for taxable incomes and the like.
                         If they are not married, but form a tax unit,
                         which makes sense from a labor supply point of view,
                         the variable 'inc' is not summed up.
        'all_tu': all members (incl. children) of the tax_unit
        'all_hh': all members (incl. children) of the Household

        returns one series with suffix _tu or _tu_k, depending on the
        parameter 'withkids'
    """
    if unit == 'adult_married':
        df[inc + "_verh"] = df["zveranl"] * df[inc]
        df = df.join(
            df.groupby(["tu_id"])[(inc + "_verh")].sum(), on=["tu_id"], how="left", rsuffix="_sum"
        )
        df[inc + "_tu"] = np.select(
            [df["zveranl"], ~df["zveranl"]], [df[inc + "_verh_sum"], df[inc]]
        )
        return df[inc + "_tu"]

    if unit == 'all_tu':
        df = df.join(df.groupby(["tu_id"])[inc].sum(), on=["tu_id"], how="left", rsuffix="_sum")
        df[inc + "_tu_k"] = df[inc + "_sum"]

        return df[inc + "_tu_k"]

    if unit == 'all_hh':
        df = df.join(df.groupby(["hid"])[inc].sum(), on=["hid"], how="left", rsuffix="_sum")
        df[inc + "_hh"] = df[inc + "_sum"]

        return df[inc + "_hh"]

def gini(x, w=None):
    """
    Calculate the Gini coefficient of a numpy array using sample weights.
    Source: https://stackoverflow.com/questions/48999542/more-efficient-weighted-gini-coefficient-in-python

    """

    # Array indexing requires reset indexes.
    x = pd.Series(x).reset_index(drop=True)
    if w is None:
        w = np.ones_like(x)
    else:
        w = pd.Series(w).reset_index(drop=True)
    n = x.size
    wxsum = sum(w * x)
    wsum = sum(w)
    sxw = np.argsort(x)
    sx = x[sxw] * w[sxw]
    sw = w[sxw]
    pxi = np.cumsum(sx) / wxsum
    pci = np.cumsum(sw) / wsum
    gini = 0.0
    for i in np.arange(1, n):
        gini = gini + pxi.iloc[i] * pci.iloc[i - 1] - pci.iloc[i] * pxi.iloc[i - 1]
    return gini


def say_hello(taxyear, ref, hyporun):
    print("---------------------------------------------")
    print(" TAX TRANSFER SYSTEM ")
    print(" -------------------")
    # print(" Year of Database: " + str(datayear))
    print(" Year of Tax Transfer System: " + str(taxyear))
    print(" Simulated Reform: " + str(ref))
    if hyporun:
        print("RUN WITH SAMPLE HOUSEHOLDS")
    print("---------------------------------------------")
    time.sleep(1)

    return

def tarif_ubi(x, tb):
    """ UBI Tax schedule
        the function is defined here, as defining it in tax_transfer_ubi.py would lead to
        circular dependencies
    """
    t = 0.0
    if x > tb['G']:
        t = tb['flatrate'] * (x - tb['G'])

    return t
