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
