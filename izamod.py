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
from hypo     import create_hypo_data
from taxtransfer import *

pd.options.display.float_format = '{:.2f}'.format


def run_izamod(settings):

    init(settings)
    global main_path
    main_path = settings['MAIN_PATH']

    if settings['load_data'] == 1:
        loaddata(settings['SOEP_PATH'], settings['DATA_PATH']+'SOEP/', settings['minyear'])

    if settings['prepare_data'] == 1:
        preparedata(settings['DATA_PATH']+'SOEP/', settings['GRAPH_PATH'])


    if settings['taxtrans'] == 1:
        for ref in settings['Reforms']:
            taxtransfer(settings['DATA_PATH']+'SOEP/taxben_input_',settings,ref)

    # HYPO RUN
    if settings['run_hypo'] == 1:
        create_hypo_data(settings['DATA_PATH'],settings)
# Write Run Settings into dictionary
settings = get_settings()

#visualize_code()

# and run the thing
run_izamod(settings)








