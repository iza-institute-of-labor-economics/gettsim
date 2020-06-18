def wohngeld_m_vorrang(
    _regelbedarf_m_vermögens_check,
    _wohngeld_basis_hh_vermögens_check,
    _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m,
    arbeitsl_geld_2_m_basis,
):
    rest_arbeitsl_geld_2 = (
        _regelbedarf_m_vermögens_check
        - (
            _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m
            + _wohngeld_basis_hh_vermögens_check
        )
    ).clip(lower=0)
    return (rest_arbeitsl_geld_2 == 0) & (arbeitsl_geld_2_m_basis > 0)


def kinderzuschlag_vorrang(
    _regelbedarf_m_vermögens_check,
    _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m,
    _kinderzuschlag_m_vermögens_check,
    arbeitsl_geld_2_m_basis,
):
    rest_arbeitsl_geld_2 = (
        _regelbedarf_m_vermögens_check
        - (
            _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m
            + _kinderzuschlag_m_vermögens_check
        )
    ).clip(lower=0)
    return (rest_arbeitsl_geld_2 == 0) & (arbeitsl_geld_2_m_basis > 0)


def wohngeld_m_kinderzuschlag_vorrang(
    _regelbedarf_m_vermögens_check,
    _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m,
    _wohngeld_basis_hh_vermögens_check,
    _kinderzuschlag_m_vermögens_check,
    arbeitsl_geld_2_m_basis,
):
    rest_arbeitsl_geld_2 = (
        _regelbedarf_m_vermögens_check
        - (
            _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m
            + _wohngeld_basis_hh_vermögens_check
            + _kinderzuschlag_m_vermögens_check
        )
    ).clip(lower=0)
    return (rest_arbeitsl_geld_2 == 0) & (arbeitsl_geld_2_m_basis > 0)


def arbeitsl_geld_2_m_wohngeld_m():
    return
