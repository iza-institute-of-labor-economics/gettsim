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
