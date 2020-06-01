def anz_kind_zwischen_0_6_per_hh(hh_id, kind, alter):
    alter_0_bis_6 = (0 <= alter) & (alter <= 6)
    return (kind & alter_0_bis_6).groupby(hh_id).transform("sum")


def anz_kind_zwischen_0_15_per_hh(hh_id, kind, alter):
    alter_0_bis_15 = (0 <= alter) & (alter <= 15)
    return (kind & alter_0_bis_15).groupby(hh_id).transform("sum")


def kind_zwischen_0_6(kind, alter):
    return kind & (0 <= alter) & (alter <= 6)


def kind_zwischen_7_13(kind, alter):
    return kind & (7 <= alter) & (alter <= 13)


def kind_zwischen_14_24(kind, alter):
    return kind & (14 <= alter) & (alter <= 24)


def anz_kinder_hh(hh_id, kind):
    return kind.groupby(hh_id).transform("sum")


def anz_erwachsene_hh(hh_id, kind):
    return (~kind).groupby(hh_id).sum()


def kinder_in_hh(kind, hh_id):
    return kind.groupby(hh_id).any()


def kinder_in_hh_individual(hh_id, kinder_in_hh):
    return hh_id.replace(kinder_in_hh).astype(bool)
