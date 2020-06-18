def arbeitsl_geld_2_m_minus_eink(
    _regelbedarf_m_vermögens_check_hh,
    kindergeld_m_hh,
    unterhaltsvors_m_hh,
    arbeitsl_geld_2_eink_hh,
    hh_id,
):
    out = (
        _regelbedarf_m_vermögens_check_hh
        - arbeitsl_geld_2_eink_hh
        - unterhaltsvors_m_hh
        - kindergeld_m_hh
    )
    return hh_id.replace(out)


def wohngeld_m_vorrang(
    _wohngeld_basis_hh_vermögens_check, arbeitsl_geld_2_m_minus_eink,
):
    rest_arbeitsl_geld_2 = (
        arbeitsl_geld_2_m_minus_eink - _wohngeld_basis_hh_vermögens_check
    ).clip(lower=0)
    return (rest_arbeitsl_geld_2 == 0) & (arbeitsl_geld_2_m_minus_eink > 0)


def kinderzuschlag_vorrang(
    _kinderzuschlag_m_vermögens_check, arbeitsl_geld_2_m_minus_eink,
):
    rest_arbeitsl_geld_2 = (
        arbeitsl_geld_2_m_minus_eink - _kinderzuschlag_m_vermögens_check
    ).clip(lower=0)
    return (rest_arbeitsl_geld_2 == 0) & (arbeitsl_geld_2_m_minus_eink > 0)


def wohngeld_m_kinderzuschlag_vorrang(
    _wohngeld_basis_hh_vermögens_check,
    _kinderzuschlag_m_vermögens_check,
    arbeitsl_geld_2_m_minus_eink,
):
    rest_arbeitsl_geld_2 = (
        arbeitsl_geld_2_m_minus_eink
        - _wohngeld_basis_hh_vermögens_check
        - _kinderzuschlag_m_vermögens_check
    ).clip(lower=0)
    return (rest_arbeitsl_geld_2 == 0) & (arbeitsl_geld_2_m_minus_eink > 0)
