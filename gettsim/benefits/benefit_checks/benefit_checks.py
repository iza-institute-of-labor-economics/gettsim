def arbeitsl_geld_2_m_minus_eink_hh(
    _regelbedarf_m_vermögens_check_hh,
    kindergeld_m_hh,
    unterhaltsvors_m_hh,
    arbeitsl_geld_2_eink_hh,
):
    out = (
        _regelbedarf_m_vermögens_check_hh
        - arbeitsl_geld_2_eink_hh
        - unterhaltsvors_m_hh
        - kindergeld_m_hh
    )
    return out


def wohngeld_vorrang_hh(
    wohngeld_vermögens_check_hh, arbeitsl_geld_2_m_minus_eink_hh,
):
    out = wohngeld_vermögens_check_hh >= arbeitsl_geld_2_m_minus_eink_hh
    return out


def kinderzuschlag_vorrang_hh(
    kinderzuschlag_vermögens_check_hh, arbeitsl_geld_2_m_minus_eink_hh,
):
    out = kinderzuschlag_vermögens_check_hh >= arbeitsl_geld_2_m_minus_eink_hh
    return out


def wohngeld_kinderzuschlag_vorrang_hh(
    wohngeld_vermögens_check_hh,
    kinderzuschlag_vermögens_check_hh,
    arbeitsl_geld_2_m_minus_eink_hh,
):
    sum_wohngeld_kinderzuschlag = (
        wohngeld_vermögens_check_hh + kinderzuschlag_vermögens_check_hh
    )
    out = sum_wohngeld_kinderzuschlag >= arbeitsl_geld_2_m_minus_eink_hh
    return out
