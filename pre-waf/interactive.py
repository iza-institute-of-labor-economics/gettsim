# -*- coding: utf-8 -*-
"""
just a routine to load some definitions for interactive use
"""
from imports import *
from settings import get_settings

pd.set_option("display.max_columns", 20)
settings = get_settings()
data_path = settings["DATA_PATH"]
out_path = data_path
soep_path = settings["SOEP_PATH"]
graph_path = settings["GRAPH_PATH"]
minyear = 2010
datayear = 2016
taxyear = 2018
yr = taxyear
tbinput = settings["DATA_PATH"] + "SOEP/taxben_input_"
ref = "RS" + str(taxyear)
# df = pd.read_pickle(data_path+'taxben_input')

# df = pd.read_json(out_path+ref+'/taxben_results' + str(datayear) + '_' + str(taxyear) + '.json')
