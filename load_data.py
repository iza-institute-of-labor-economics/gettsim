# -*- coding: utf-8 -*-
"""
CREATE DATA

PREPARE DATA BASE BASED ON SOEP LONG.

@author: iza6354
"""
from imports import *


def loaddata(soep_path, data_path, minyear):
    '''LOAD RAW DATA

    Arguments:

    - path where SOEP data are stores
    - output path
    - first SOEP wave to consider

    loads necessary variables from SOEP long data and creates a single data frame

    also treats some variables with missing values. (-5, -2, -1 etc. in SOEP)
    and assigns zero values

    '''

    print('Loading Data...')
    # Specifies which variables to input exactly from each dataset
    vl_pequiv = ['hid', 'pid', 'syear', 'd11102ll', 'l11102', 'x11103',
                 'd11101', 'd11104', 'd11105', 'd11106', 'd11107',
                 'e11101', 'e11102', 'e11103', 'e11105', 'e11106',
                 'i11101', 'i11102', 'i11103', 'i11104', 'i11105', 'i11106',
                 'i11107', 'i11108', 'i11109', 'i11110', 'i11111', 'i11112',
                 'i11113', 'i11114', 'i11117', 'w11101', 'w11102', 'w11103',
                 'w11105', 'l11101', 'i11205', 'ijob1', 'ijob2', 'iself',
                 'ioldy', 'iwidy', 'iunby', 'iunay', 'isuby', 'ieret',
                 'imaty', 'istuy', 'imilt', 'ialim', 'ielse', 'icomp',
                 'iprvp', 'i13ly', 'i14ly', 'ixmas', 'iholy', 'igray',
                 'iothy', 'igrv1', 'igrv2', 'renty', 'opery', 'divdy',
                 'chspt', 'house', 'nursh', 'subst', 'sphlp', 'hsup',
                 'ismp1', 'iciv1', 'iwar1', 'iagr1', 'iguv1', 'ivbl1',
                 'icom1', 'iprv1', 'ison1', 'ismp2', 'iciv2', 'iwar2',
                 'iagr2', 'iguv2', 'ivbl2', 'icom2', 'ison2', 'iprv2',
                 'ssold', 'lossr', 'lossc', 'itray', 'alg2', 'adchb',
                 'iachm', 'chsub', 'ichsu', 'ispou', 'irie1', 'irie2',
                 'kidy', 'iwith']
    vl_pgen = ['hid', 'pid', 'syear', 'pgoeffd', 'pgpartnr', 'pgnation',
               'pgpsbil', 'pgerwzeit', 'pgtatzeit', 'pgvebzeit', 'pguebstd',
               'pglfs', 'pgnace', 'pgisced97', 'pgcasmin', 'pgstib',
               'pglabgro', 'pgemplst', 'pgisco08', 'pgisced11']
    vl_pl = ['hid', 'pid', 'pnr', 'syear', 'sample1', 'plb0021',
             'plb0022', 'plb0063', 'plb0157', 'plb0158', 'plb0186',
             'plb0295', 'plb0423', 'plb0424', 'plb0586', 'plb0605',
             'plc0131', 'plc0136', 'plc0137', 'plc0446', 'ple0041',
             'ple0097', 'plk0001']
    vl_pkal = ['hid', 'pid', 'syear', 'kal1a02', 'kal1b02',
               'kal1d02', 'kal1e02', 'kal1n02']
    vl_hl = ['hid', 'syear', 'hlc0111', 'hlc0053', 'hlc0054',
             'hlc0081', 'hlc0082', 'hlc0112', 'hlf0088']
    vl_hgen = ['hid', 'syear', 'hgnuts1', 'hgowner', 'hgsize', 'hgrent',
               'hgcnstyrmax', 'hgcnstyrmin', 'hgheat',
               'hgheatinfo', 'hgtyp1hh']
    vl_biol = ['hid', 'pid', 'syear', 'lb0285']
    vl_kidl = ['hid', 'pid', 'syear', 'k_rel', 'k_nrinhh',
               'k_inco', 'k_pmum', 'ks_ats_r']
    # Load from Stata Format
    pequiv = pd.read_stata(soep_path+'pequiv.dta',
                           convert_categoricals=False,
                           columns=vl_pequiv)
    pgen = pd.read_stata(soep_path+'pgen.dta',
                         convert_categoricals=False,
                         columns=vl_pgen)
    pl = pd.read_stata(soep_path+'pl.dta',
                       convert_categoricals=False,
                       columns=vl_pl)
    pkal = pd.read_stata(soep_path+'pkal.dta',
                         convert_categoricals=False,
                         columns=vl_pkal)
    hl = pd.read_stata(soep_path+'hl.dta',
                       convert_categoricals=False,
                       columns=vl_hl)
    hgen = pd.read_stata(soep_path+'hgen.dta',
                         convert_categoricals=False,
                         columns=vl_hgen)
    biol = pd.read_stata(soep_path+'biol.dta',
                         convert_categoricals=False,
                         columns=vl_biol)
    kidl = pd.read_stata(soep_path+'kidl.dta',
                         convert_categoricals=False,
                         columns=vl_kidl)

    # MERGE THEM TOGETHER
    print('Merging...')
    df = pequiv.copy()
    print('after pequiv '+str(df.shape))
    df = df.merge(pgen, on=['syear', 'pid', 'hid'],
                  validate='1:1', how='outer')
    print('after pgen '+str(df.shape))
    df = df.merge(pl, on=['syear', 'pid', 'hid'], validate='1:1', how='outer')
    print('after pl '+str(df.shape))
    df = df.merge(pkal, on=['syear', 'pid', 'hid'],
                  validate='1:1', how='outer')
    print('after pkal ' + str(df.shape))
    df = df.merge(biol, on=['syear', 'pid', 'hid'], validate='1:1',
                  how='outer')
    print('after biol ' + str(df.shape))
    df = df.merge(kidl, on=['syear', 'hid', 'pid'],
                  validate='1:1', how='outer')
    print('after kidl '+str(df.shape))
    df = df.merge(hl, on=['syear', 'hid'], validate='m:1', how='inner')
    print('after hl ' + str(df.shape))
    df = df.merge(hgen, on=['syear', 'hid'], validate='m:1', how='inner')
    # drop a couple of years
    df = df[df['syear'] >= minyear]

    # get rid of negative values
    negvars = ['i11105',
               'plb0022',
               'plb0063',
               'plb0157',
               'plb0158',
               'plb0186',
               'plb0295',
               'plb0423',
               'plb0424',
               'plb0586',
               'plb0605',
               'plc0131',
               'ijob1',
               'ijob2',
               'iself',
               'ioldy',
               'iwidy',
               'iunby',
               'iunay',
               'isuby',
               'ieret',
               'imaty',
               'istuy',
               'imilt',
               'ialim',
               'ielse',
               'icomp',
               'iprvp',
               'i13ly',
               'i14ly',
               'ixmas',
               'iholy',
               'igray',
               'iothy',
               'igrv1',
               'igrv2',
               'renty',
               'opery',
               'divdy',
               'chspt',
               'house',
               'nursh',
               'subst',
               'sphlp',
               'hsup',
               'ismp1',
               'iciv1',
               'iwar1',
               'iagr1',
               'iguv1',
               'ivbl1',
               'icom1',
               'iprv1',
               'ison1',
               'ismp2',
               'iciv2',
               'iwar2',
               'iagr2',
               'iguv2',
               'ivbl2',
               'icom2',
               'ison2',
               'iprv2',
               'ssold',
               'lossr',
               'lossc',
               'itray',
               'alg2',
               'adchb',
               'iachm',
               'chsub',
               'ichsu',
               'ispou',
               'irie1',
               'irie2',
               'kidy',
               'iwith',
               'kal1a02',
               'kal1b02',
               'kal1d02',
               'kal1e02',
               'kal1n02',
               'pglabgro',
               'pgtatzeit',
               'pgvebzeit',
               'pguebstd',
               'lb0285',
               'ple0041',
               'k_inco',
               'hgowner',
               'hlc0053',
               'hlc0054',
               'hlc0081',
               'hlc0082'
               ]

    for v in negvars:
        df[v] = df[v].replace([-8, -7, -6, -5, -4, -3, -2, -1], 0)
    # Rename a couple of variables
    df = df.rename(columns={'d11106': 'hhsize',
                            'i11103': 'laborinc',
                            'i11110': 'laborinc_ind',
                            'i11104': 'assetinc',
                            'i11105': 'imp_rent',
                            'i11108': 'sose_pension',
                            'i11109': 'tax',
                            'i11117': 'retirement',
                            'w11105': 'pweight',
                            'w11102': 'hweight',
                            'kal1a02': 'months_ft',
                            'kal1b02': 'months_pt',
                            'kal1d02': 'months_ue',
                            'kal1e02': 'months_pen',
                            'kal1n02': 'months_mj',
                            'iself': 'm_self',
                            'd11104': 'marstat',
                            'd11105': 'stell',
                            'ple0041': 'handcap_degree',
                            'plk0001': 'partner_id',
                            'hgnuts1': 'bula',
                            'hlf0088': 'zinszahl',
                            'plb0157': 'comm_freq',
                            'plb0158': 'comm_dist',
                            'plc0136': 'alg_m_l1',
                            'plc0137': 'alg_l1',
                            'hlc0053': 'algII_m_l1',
                            'hlc0054': 'algII_l1',
                            'hlc0081': 'wgeld_m_l1',
                            'hlc0082': 'wgeld_l1'}
                   )

    return df
