def _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m(
    arbeitsl_geld_2_eink_hh, unterhaltsvors_m_hh, kindergeld_m_hh, hh_id
):
    sum_eink = arbeitsl_geld_2_eink_hh + unterhaltsvors_m_hh + kindergeld_m_hh
    return hh_id.replace(sum_eink)


def sum_wohngeld_m_arbeitsl_geld_2_eink(
    _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m, _wohngeld_basis_hh_vermögens_check
):
    return (
        _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m
        + _wohngeld_basis_hh_vermögens_check
    )


def sum_kinderzuschlag_arbeitsl_geld_2_eink(
    _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m, _kinderzuschlag_m_vermögens_check
):
    return (
        _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m
        + _kinderzuschlag_m_vermögens_check
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


def _subtract_and_clip_at_zero(minuend, subtrahend):
    return (minuend - subtrahend).clip(lower=0)


def arbeitsl_geld_2_m_wohngeld_m_kinderzuschlag(
    _regelbedarf_m_vermögens_check, sum_wohngeld_m_kinderzuschlag_arbeitsl_geld_2_eink
):
    return (
        _regelbedarf_m_vermögens_check
        - sum_wohngeld_m_kinderzuschlag_arbeitsl_geld_2_eink
    ).clip(lower=0)


def arbeitsl_geld_2_m_kinderzuschlag(
    _regelbedarf_m_vermögens_check, sum_kinderzuschlag_arbeitsl_geld_2_eink
):
    return (
        _regelbedarf_m_vermögens_check - sum_kinderzuschlag_arbeitsl_geld_2_eink
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


def anz_rentner_per_hh(hh_id, rentner):
    return rentner.groupby(hh_id).transform("sum")


def wohngeld_m_vorrang(arbeitsl_geld_2_m_wohngeld_m, arbeitsl_geld_2_m_basis):
    return (arbeitsl_geld_2_m_wohngeld_m == 0) & (arbeitsl_geld_2_m_basis > 0)


def kinderzuschlag_vorrang(arbeitsl_geld_2_m_kinderzuschlag, arbeitsl_geld_2_m_basis):
    return (arbeitsl_geld_2_m_kinderzuschlag == 0) & (arbeitsl_geld_2_m_basis > 0)


def wohngeld_m_kinderzuschlag_vorrang(
    arbeitsl_geld_2_m_wohngeld_m_kinderzuschlag, arbeitsl_geld_2_m_basis
):
    return (arbeitsl_geld_2_m_wohngeld_m_kinderzuschlag == 0) & (
        arbeitsl_geld_2_m_basis > 0
    )
