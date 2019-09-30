"""
Created on Tue Mar 19 14:29:13 2019

@author: iza6354
"""


def ubi_settings(tb):
    """ Set alternative tax benefit parameters for UBI
    """

    tb_ubi = tb.copy()
    # UBI amount for adults
    tb_ubi["ubi_adult"] = 1000
    tb_ubi["ubi_child"] = 0.5 * tb_ubi["ubi_adult"]

    # Minijobgrenze
    tb_ubi["mini_grenzew"] = 0
    tb_ubi["mini_grenzeo"] = tb_ubi["mini_grenzew"]

    # Midijobgrenze
    tb_ubi["midi_grenze"] = 0

    # UBI Flat Rate
    tb_ubi["flatrate"] = 0.48

    # Kindergeld
    for i in range(1, 5):
        tb_ubi["kgeld" + str(i)] = 0

    # Tax Tariff

    return tb_ubi
