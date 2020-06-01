def _anz_kinder_in_tu(tu_id, kind):
    return (kind.astype(int)).groupby(tu_id).transform(sum)


def _anz_erwachsene_tu(tu_id, kind):
    return (~kind).groupby(tu_id).sum()


def gemeinsam_veranlagt(tu_id, _anz_erwachsene_tu):
    return tu_id.replace(_anz_erwachsene_tu) == 2


def gemeinsam_veranlagte_tu(gemeinsam_veranlagt, tu_id):
    return gemeinsam_veranlagt.groupby(tu_id).any()


def bruttolohn_m_tu(bruttolohn_m, tu_id):
    return bruttolohn_m.groupby(tu_id).sum()
