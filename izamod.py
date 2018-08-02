# -*- coding: utf-8 -*-
"""

 _____ ______  ___  ___  ______________            ________   _______ _   _ _____ _   _
|_   _|___  / / _ \ |  \/  |  _  |  _  \    ____   | ___ \ \ / /_   _| | | |  _  | \ | |
  | |    / / / /_\ \| .  . | | | | | | |   / __ \  | |_/ /\ V /  | | | |_| | | | |  \| |
  | |   / /  |  _  || |\/| | | | | | | |  / / _` | |  __/  \ /   | | |  _  | | | | . ` |
 _| |_./ /___| | | || |  | \ \_/ / |/ /  | | (_| | | |     | |   | | | | | \ \_/ / |\  |
 \___/\_____/\_| |_/\_|  |_/\___/|___/    \ \__,_| \_|     \_/   \_/ \_| |_/\___/\_| \_/
                                           \____/


@author: iza6354
"""

from settings import get_settings
from load_data import loaddata
from prepare_data import preparedata
from hypo import create_hypo_data
from taxtransfer import *

pd.options.display.float_format = '{:.2f}'.format


def run_izamod(settings):

    init(settings)
    global main_path
    main_path = settings['MAIN_PATH']

    if settings['load_data'] == 1:
        rawdata = loaddata(settings['SOEP_PATH'], settings['DATA_PATH']+'SOEP/',
                 settings['DATA_PATH']+'SOEP/',
                           settings['minyear'])

        print('Save ' + str(rawdata.shape) + ' Data to: ' + settings['DATA_PATH'] + 'soep_long')
        pd.to_pickle(rawdata, settings['DATA_PATH'] + 'soep_long')

    if settings['prepare_data'] == 1:
        ########################
        ## DATA PREPARATION
        #######################
        print('Load selected SOEP Data from HD')
        # load data
        soep_long_raw = pd.read_pickle(settings['DATA_PATH'] + 'soep_long')
        df = preparedata(soep_long_raw)
        
        # Export data for each SOEP survey year separately
        for y in df['syear'].unique():
            filename = settings['DATA_PATH'] + 'taxben_input_' + str(y)
            print("Saving to " + filename)
            pd.to_pickle(df[df['syear'] == y], filename)

    if settings['taxtrans'] == 1:
        ########################
        ### TAX TRANSFER
        ########################
        # Load Tax-Benefit Parameters
        tb = get_params(settings)[str(settings['taxyear'])]
        for ref in settings['Reforms']:
            # call tax transfer
            datayear = min(settings['taxyear'], 2016)
            print("---------------------------------------------")
            print(" TAX TRANSFER SYSTEM ")
            print(" -------------------")
            print(" Year of Database: " + str(datayear))

            df = pd.read_pickle(settings['DATA_PATH'] + 'SOEP/taxben_input_' + str(datayear))
            # Get the correct parameters for the tax year
            print(" Year of System: " + str(settings['taxyear']))
            print(" Simulated Reform: " + str(ref))
            print("---------------------------------------------")
            tt_out = taxtransfer(df, ref, datayear, settings['taxyear'], tb, False)
            print('Saving to:' + settings['DATA_PATH'] + ref
              + '/taxben_results' + str(datayear) + '_'
              + str(taxyear) + '.json')
            tt_out.to_json(settings['DATA_PATH']+ref+'/taxben_results' +
                           str(datayear) + '_' + str(settings['taxyear']) + '.json')

            # SHOW OUTPUT
            tb_out(tt_out, ref, settings['GRAPH_PATH'])

    # HYPO RUN
    if settings['run_hypo'] == 1:
        create_hypo_data(settings['DATA_PATH'], settings)

# Write Run Settings into dictionary
settings = get_settings()

# visualize_code()

# and run the thing
run_izamod(settings)








