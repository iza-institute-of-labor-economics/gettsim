# -*- coding: utf-8 -*-
"""
IZAMOD SETTINGS
"""
import re

# initialize global variables
def get_settings():

    taxyear = 2016

    # Rechtsstand des Basisjahres ist immer Baseline Reform
    reforms = ['RS'+str(taxyear)]

    # DATA CREATION
    # load raw SOEP data and merge them into one data set
    load_data  = 0
    minyear      = 2010
    # prepare tax-ben input
    prepare_data = 0


    # TAX TRANSFER CALCULATION
    taxtrans = 1



    # PATH SETTINGS
    MAIN_PATH = 'W:/izamod/IZA_DYN_MOD/'
    SOEP_PATH = MAIN_PATH + 'data/soep_raw/'
    DATA_PATH = MAIN_PATH + 'data/'
    GRAPH_PATH = MAIN_PATH + 'graphs/'

    return {'Reforms':reforms,
            'load_data': load_data,
            'prepare_data':prepare_data,
            'minyear':minyear,
            'taxtrans':taxtrans,
            'taxyear' : taxyear,
            'MAIN_PATH':MAIN_PATH,
            'SOEP_PATH':SOEP_PATH,
            'DATA_PATH':DATA_PATH,
            'GRAPH_PATH':GRAPH_PATH}