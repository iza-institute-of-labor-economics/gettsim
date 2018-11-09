# -*- coding: utf-8 -*-
"""
IZAMOD SETTINGS
"""
import os
import socket


def get_settings():
    ''' Initialize Global Settings
        maybe add argument 'user' to differentiate
        different platforms with different paths.
    '''
    taxyear = 2015

    # Rechtsstand des Basisjahres ist immer Baseline Reform
    reforms = ['RS' + str(taxyear)]

    # DATA CREATION
    # load raw SOEP data and merge them into one data set
    load_data = 0
    minyear = 2005
    # prepare tax-ben input
    prepare_data = 1

    # prepare descriptive statistics
    show_descr = 1

    # TAX TRANSFER CALCULATION
    taxtrans = 1

    # Run Hypo file for debugging
    run_hypo = 0

    # PATH SETTINGS
    MAIN_PATH = os.getcwd() + '/'
    # SOEP_PATH: Where is the SOEP data stored?
    # Find out whether we are on the GPU.
    if socket.gethostname() == 'gpu1':
        SOEP_PATH = '/data/shares/dynamod/data/raw/soep/'
    else:
        SOEP_PATH = 'V:/soep/datasets/2016/v33.1/long/'
    # The Path for self produced data
    DATA_PATH = MAIN_PATH + 'data/'
    GRAPH_PATH = MAIN_PATH + 'graphs/'

    return {
        'Reforms': reforms,
        'load_data': load_data,
        'minyear': minyear,
        'prepare_data': prepare_data,
        'show_descr': show_descr,
        'taxtrans': taxtrans,
        'taxyear': taxyear,
        'run_hypo': run_hypo,
        'MAIN_PATH': MAIN_PATH,
        'SOEP_PATH': SOEP_PATH,
        'DATA_PATH': DATA_PATH,
        'GRAPH_PATH': GRAPH_PATH
    }
