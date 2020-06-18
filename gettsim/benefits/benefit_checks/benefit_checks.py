def wohngeld_m(
    _wohngeld_basis_hh_vermögens_check,
    wohngeld_m_vorrang,
    wohngeld_m_kinderzuschlag_vorrang,
    arbeitsl_geld_2_m_basis,
    anz_rentner_per_hh,
):
    cond = (
        ~wohngeld_m_vorrang
        & ~wohngeld_m_kinderzuschlag_vorrang
        & (arbeitsl_geld_2_m_basis > 0)
    )
    return _wohngeld_basis_hh_vermögens_check.where(
        ~cond & (anz_rentner_per_hh == 0), 0
    )


def kinderzuschlag_m(
    _kinderzuschlag_m_vermögens_check,
    kinderzuschlag_vorrang,
    wohngeld_m_kinderzuschlag_vorrang,
    arbeitsl_geld_2_m_basis,
    anz_rentner_per_hh,
):
    cond = (
        ~kinderzuschlag_vorrang
        & ~wohngeld_m_kinderzuschlag_vorrang
        & (arbeitsl_geld_2_m_basis > 0)
    )
    return _kinderzuschlag_m_vermögens_check.where(~cond & (anz_rentner_per_hh == 0), 0)
