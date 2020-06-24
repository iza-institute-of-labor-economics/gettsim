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
    rest_arbeitsl_geld_2 = (
        arbeitsl_geld_2_m_minus_eink_hh - wohngeld_vermögens_check_hh
    ).clip(lower=0)
    return (rest_arbeitsl_geld_2 == 0) & (arbeitsl_geld_2_m_minus_eink_hh > 0)


def kinderzuschlag_vorrang_hh(
    kinderzuschlag_vermögens_check_hh, arbeitsl_geld_2_m_minus_eink_hh,
):
    rest_arbeitsl_geld_2 = (
        arbeitsl_geld_2_m_minus_eink_hh - kinderzuschlag_vermögens_check_hh
    ).clip(lower=0)
    return (rest_arbeitsl_geld_2 == 0) & (arbeitsl_geld_2_m_minus_eink_hh > 0)


def wohngeld_kinderzuschlag_vorrang_hh(
    wohngeld_vermögens_check_hh,
    kinderzuschlag_vermögens_check_hh,
    arbeitsl_geld_2_m_minus_eink_hh,
):
    rest_arbeitsl_geld_2 = (
        arbeitsl_geld_2_m_minus_eink_hh
        - wohngeld_vermögens_check_hh
        - kinderzuschlag_vermögens_check_hh
    ).clip(lower=0)
    return (rest_arbeitsl_geld_2 == 0) & (arbeitsl_geld_2_m_minus_eink_hh > 0)
