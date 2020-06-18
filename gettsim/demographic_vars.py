def alleinerziehend_tu(tu_id, alleinerziehend):
    return alleinerziehend.groupby(tu_id).any()


def alleinerziehend_hh(hh_id, alleinerziehend):
    return alleinerziehend.groupby(hh_id).any()


def _anz_kinder_in_tu(tu_id, kind):
    return (kind.astype(int)).groupby(tu_id).sum()


def _anz_erwachsene_tu(tu_id, kind):
    return (~kind).astype(int).groupby(tu_id).sum()


def gemeinsam_veranlagt(tu_id, _anz_erwachsene_tu):
    return tu_id.replace(_anz_erwachsene_tu) == 2


def gemeinsam_veranlagte_tu(gemeinsam_veranlagt, tu_id):
    return gemeinsam_veranlagt.groupby(tu_id).any()


def bruttolohn_m_tu(bruttolohn_m, tu_id):
    return bruttolohn_m.groupby(tu_id).sum()


def anz_kind_zwischen_0_6_hh(hh_id, kind, alter):
    alter_0_bis_6 = (0 <= alter) & (alter <= 6)
    return ((kind & alter_0_bis_6).astype(int)).groupby(hh_id).sum()


def anz_kind_zwischen_0_15_hh(hh_id, kind, alter):
    alter_0_bis_15 = (0 <= alter) & (alter <= 15)
    return ((kind & alter_0_bis_15).astype(int)).groupby(hh_id).sum()


def kind_zwischen_0_6(kind, alter):
    return kind & (0 <= alter) & (alter <= 6)


def kind_zwischen_7_13(kind, alter):
    return kind & (7 <= alter) & (alter <= 13)


def kind_zwischen_14_24(kind, alter):
    return kind & (14 <= alter) & (alter <= 24)


def anz_kinder_hh(hh_id, kind):
    return kind.astype(int).groupby(hh_id).sum()


def anz_kinder_tu(tu_id, kind):
    return (kind.astype(int)).groupby(tu_id).sum()


def anz_erwachsene_hh(hh_id, kind):
    return (~kind).groupby(hh_id).sum()


def kinder_in_hh(kind, hh_id):
    return kind.groupby(hh_id).any()


def kinder_in_hh_individual(hh_id, kinder_in_hh):
    return hh_id.replace(kinder_in_hh).astype(bool)


def haushaltsgröße(hh_id):
    return hh_id.groupby(hh_id).transform("size")


def haushaltsgröße_hh(hh_id):
    return hh_id.groupby(hh_id).size()


def rentner_in_hh(hh_id, rentner):
    return rentner.groupby(hh_id).any()
