def _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m(
    arbeitsl_geld_2_eink_hh, unterhaltsvors_m_hh, kindergeld_m_hh
):
    sum_eink = arbeitsl_geld_2_eink_hh + unterhaltsvors_m_hh + kindergeld_m_hh
    breakpoint()
    return sum_eink


def arbeitsl_geld_2_m_minus_eink(
    _regelbedarf_m_vermögens_check, _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m
):
    out = (
        _regelbedarf_m_vermögens_check
        - _sum_arbeitsl_geld_2_unterhaltsvors_kindergeld_m
    )
    return out


def arbeitsl_geld_2_m_basis(arbeitsl_geld_2_m_minus_eink):
    return arbeitsl_geld_2_m_minus_eink.clip(lower=0)
