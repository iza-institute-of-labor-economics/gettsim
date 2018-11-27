# -*- coding: utf-8 -*-
"""

IZA_DYN_MOD

Dynamic application of IZAPSIMOD

Eric Sommer
Hans-Martin v. Gaudecker
Janos Gabler

"""

from settings import get_settings, ubi_settings
from load_data import loaddata
from prepare_data import preparedata
from hypo import hypo_analysis
from tt_list import *
from imports import init, get_params, mw_pensions, say_hello
from descr import descriptives

import time

pd.options.display.float_format = '{:.2f}'.format

start = time.time()


def run_izamod(settings):
    ''' IZA_DYN_MOD

        runs the modules
        - loaddata
        - preparedata
        - tax_transfer

        according to the settings made in settings.py
    '''
    init(settings)
    global main_path
    main_path = settings['MAIN_PATH']
    # LOAD RAW DATA
    if settings['load_data'] == 1:
        rawdata = loaddata(settings['SOEP_PATH'],
                           settings['DATA_PATH']+'SOEP/',
                           settings['minyear'])

        print('Save ' + str(rawdata.shape) + ' Data to: ' +
              settings['DATA_PATH'] + 'SOEP/soep_long')
        pd.to_pickle(rawdata, settings['DATA_PATH'] + 'SOEP/soep_long')
    # DATA PREPARATION
    if settings['prepare_data'] == 1:
        print('Load selected SOEP Data from HD')
        # load data
        soep_long_raw = pd.read_pickle(settings['DATA_PATH'] + 'SOEP/soep_long')
        # call prepare data
        df = preparedata(soep_long_raw)
        # Output of Summary Statistics
        summaries = df.describe()
        summaries.to_excel(pd.ExcelWriter(settings['DATA_PATH'] + 'SOEP/sum_data_out.xlsx'),
                           sheet_name='py_out')
        # Calculate meanwages by year for pensions...
        mw = mw_pensions(df)
        mw.to_json(settings['DATA_PATH'] + 'params/mw_pensions.json')
        # Maybe show some descriptive statistics
        if settings['show_descr'] == 1:
            descr = descriptives(df)
            descr.to_excel(pd.ExcelWriter(settings['DATA_PATH'] + 'SOEP/data_descr.xlsx'),
                           sheet_name='descr')
        # Finally, export data for each SOEP survey year separately
        for y in df['syear'].unique():
            filename = settings['DATA_PATH'] + 'SOEP/taxben_input_' + str(y)
            print("Saving to " + filename)
            pd.to_pickle(df[df['syear'] == y], filename)


    # TAX TRANSFER CALCULATION

    if (settings['taxtrans'] == 1) or (settings['run_hypo'] == 1):
        # Load Tax-Benefit Parameters
        tb = get_params(settings)[str(settings['taxyear'])]
        # Load pension parameters
        mw = pd.read_json(settings['DATA_PATH'] + 'params/mw_pensions.json')
        tb_pens = pd.read_excel(settings['MAIN_PATH'] +
                                '/data/params/pensions.xlsx',
                                index_col='var').transpose()

    if settings['taxtrans'] == 1:
        for ref in settings['Reforms']:
            datayear = min(settings['taxyear'], 2016)
            # LOAD DATA
            df = pd.read_pickle(settings['DATA_PATH'] + 'SOEP/taxben_input_' + str(datayear))
            say_hello(settings['taxyear'],
                      ref,
                      False)
            # CALL TAX TRANSFER, depending on reform
            if ref != "UBI":
                tt_out = tax_transfer(df,
                                      datayear,
                                      settings['taxyear'],
                                      tb,
                                      tb_pens,
                                      mw,
                                      False
                                      )
            else:
                tb_ubi = ubi_settings(tb)
                tt_out = tax_transfer_ubi(df,
                                          datayear,
                                          settings['taxyear'],
                                          tb_ubi,
                                          tb_pens,
                                          mw,
                                          False
                                          )

            print('Saving to:' + settings['DATA_PATH'] + ref +
                  '/taxben_results' + str(datayear) + '_' +
                  str(settings['taxyear']) + '.json')
            tt_out.to_json(settings['DATA_PATH'] +
                           ref +
                           '/taxben_results' +
                           str(datayear) + '_' +
                           str(settings['taxyear']) +
                           '.json')
            # SHOW OUTPUT
            tb_out(tt_out, ref, settings['GRAPH_PATH'])

    # TODO: Show reform effects (necessary right now?)

    # Hypo Run: create hypothetical household data, run tax transfer and produce some outputs.
    if settings['run_hypo'] == 1:
        hypo_analysis(settings['DATA_PATH'], settings, tb)

    print('END IZA_DYN_MOD')

    return True

# -------------------------------------------------------------------------------------------
# Actual run starts here
# Write Run Settings into dictionary
settings = get_settings()

# and run the thing
run_izamod(settings)

end = time.time()
print('-'*80)
print('Total time used: ' +
      time.strftime('%H:%M:%S', time.gmtime(end - start))
      + "Hours.")
print('-'*80)
