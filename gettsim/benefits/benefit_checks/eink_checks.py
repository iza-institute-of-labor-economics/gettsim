def _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m(
    arbeitsl_geld_2_eink_hh, unterhaltsvors_m_hh, kindergeld_m_hh
):
    sum_eink = arbeitsl_geld_2_eink_hh + unterhaltsvors_m_hh + kindergeld_m_hh
    breakpoint()
    return sum_eink


def sum_wohngeld_m_arbeitsl_geld_2_eink(
    _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m, _wohngeld_basis_hh_vermögens_check
):
    return (
        _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m
        + _wohngeld_basis_hh_vermögens_check
    )


def sum_wohngeld_m_kinderzuschlag_arbeitsl_geld_2_eink(
    _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m,
    _wohngeld_basis_hh_vermögens_check,
    _kinderzuschlag_m_vermögens_check,
):
    return (
        _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m
        + _wohngeld_basis_hh_vermögens_check
        + _kinderzuschlag_m_vermögens_check
    )


def arbeitsl_geld_2_m_wohngeld_m_kinderzuschlag(
    _regelbedarf_m_vermögens_check, sum_wohngeld_m_kinderzuschlag_arbeitsl_geld_2_eink
):
    return (
        _regelbedarf_m_vermögens_check
        - sum_wohngeld_m_kinderzuschlag_arbeitsl_geld_2_eink
    ).clip(lower=0)


def arbeitsl_geld_2_m_wohngeld_m(
    _regelbedarf_m_vermögens_check, sum_wohngeld_m_arbeitsl_geld_2_eink
):
    return (_regelbedarf_m_vermögens_check - sum_wohngeld_m_arbeitsl_geld_2_eink).clip(
        lower=0
    )


def arbeitsl_geld_2_m_basis(
    _regelbedarf_m_vermögens_check, _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m
):
    return (
        _regelbedarf_m_vermögens_check
        - _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m
    ).clip(lower=0)
