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


def wohngeld_m_vorrang_hh(
    _wohngeld_basis_hh_vermögens_check_hh, arbeitsl_geld_2_m_minus_eink_hh,
):
    rest_arbeitsl_geld_2 = (
        arbeitsl_geld_2_m_minus_eink_hh - _wohngeld_basis_hh_vermögens_check_hh
    ).clip(lower=0)
    return (rest_arbeitsl_geld_2 == 0) & (arbeitsl_geld_2_m_minus_eink_hh > 0)


def kinderzuschlag_vorrang_hh(
    _kinderzuschlag_vorläufig_m_vermögens_check_hh, arbeitsl_geld_2_m_minus_eink_hh,
):
    rest_arbeitsl_geld_2 = (
        arbeitsl_geld_2_m_minus_eink_hh - _kinderzuschlag_vorläufig_m_vermögens_check_hh
    ).clip(lower=0)
    return (rest_arbeitsl_geld_2 == 0) & (arbeitsl_geld_2_m_minus_eink_hh > 0)


def wohngeld_m_kinderzuschlag_vorrang_hh(
    _wohngeld_basis_hh_vermögens_check_hh,
    _kinderzuschlag_vorläufig_m_vermögens_check_hh,
    arbeitsl_geld_2_m_minus_eink_hh,
):
    rest_arbeitsl_geld_2 = (
        arbeitsl_geld_2_m_minus_eink_hh
        - _wohngeld_basis_hh_vermögens_check_hh
        - _kinderzuschlag_vorläufig_m_vermögens_check_hh
    ).clip(lower=0)
    return (rest_arbeitsl_geld_2 == 0) & (arbeitsl_geld_2_m_minus_eink_hh > 0)
