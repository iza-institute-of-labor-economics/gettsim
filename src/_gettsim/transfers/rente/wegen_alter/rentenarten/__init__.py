"""Age thresholds for public pension eligibility."""

from _gettsim.shared import policy_info


@policy_info(end_date="2011-12-31", name_in_dag="_ges_rente_altersgrenze_abschlagsfrei")
def _ges_rente_altersgrenze_abschlagsfrei_ohne_besond_langj(
    ges_rente_regelaltersgrenze: float,
    _ges_rente_frauen_altersgrenze: float,
    _ges_rente_langj_altersgrenze: float,
    _ges_rente_arbeitsl_altersgrenze: float,
    ges_rente_vorauss_frauen: bool,
    ges_rente_vorauss_langj: bool,
    ges_rente_vorauss_arbeitsl: bool,
) -> float:
    """Full retirement age after eligibility checks, assuming eligibility for
    Regelaltersrente.

    Age at which pension can be claimed without deductions. This age is smaller or equal
    to the normal retirement age (FRA<=NRA) and depends on personal characteristics as
    gender, insurance duration, health/disability, employment status.

    Parameters
    ----------
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    _ges_rente_frauen_altersgrenze
        See :func:`_ges_rente_frauen_altersgrenze`.
    _ges_rente_langj_altersgrenze
        See :func:`_ges_rente_langj_altersgrenze`.
    _ges_rente_arbeitsl_altersgrenze
         See :func:`_ges_rente_arbeitsl_altersgrenze`.
    ges_rente_vorauss_frauen
        See :func:`ges_rente_vorauss_frauen`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    ges_rente_vorauss_arbeitsl:
        See :func:`ges_rente_vorauss_arbeitsl`.
    Returns
    -------
    Full retirement age.

    """

    out = ges_rente_regelaltersgrenze
    if ges_rente_vorauss_frauen:
        out = min([out, _ges_rente_frauen_altersgrenze])
    if ges_rente_vorauss_arbeitsl:
        out = min([out, _ges_rente_arbeitsl_altersgrenze])
    if ges_rente_vorauss_langj:
        out = min([out, _ges_rente_langj_altersgrenze])

    return out


@policy_info(
    start_date="2012-01-01",
    end_date="2017-12-31",
    name_in_dag="_ges_rente_altersgrenze_abschlagsfrei",
)
def _ges_rente_altersgrenze_abschlagsfrei_mit_besond_langj(
    ges_rente_regelaltersgrenze: float,
    _ges_rente_frauen_altersgrenze: float,
    _ges_rente_langj_altersgrenze: float,
    _ges_rente_besond_langj_altersgrenze: float,
    _ges_rente_arbeitsl_altersgrenze: float,
    ges_rente_vorauss_frauen: bool,
    ges_rente_vorauss_langj: bool,
    ges_rente_vorauss_besond_langj: bool,
    ges_rente_vorauss_arbeitsl: bool,
) -> float:
    """Full retirement age after eligibility checks, assuming eligibility for
    Regelaltersrente.

    Age at which pension can be claimed without deductions. This age is smaller or equal
    to the normal retirement age (FRA<=NRA) and depends on personal characteristics as
    gender, insurance duration, health/disability, employment status.

    Starting in 2012, the pension for the very long term insured (Altersrente für
    besonders langjährig Versicherte) is introduced. Policy becomes inactive in 2018
    because then all potential beneficiaries of the Rente wg. Arbeitslosigkeit and
    Rente für Frauen have reached the normal retirement age.

    Parameters
    ----------
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    _ges_rente_frauen_altersgrenze
        See :func:`_ges_rente_frauen_altersgrenze`.
    _ges_rente_langj_altersgrenze
        See :func:`_ges_rente_langj_altersgrenze`.
    _ges_rente_besond_langj_altersgrenze
        See :func:`_ges_rente_besond_langj_altersgrenze`.
    _ges_rente_arbeitsl_altersgrenze
        See :func:`_ges_rente_arbeitsl_altersgrenze`.
    ges_rente_vorauss_frauen
        See :func:`ges_rente_vorauss_frauen`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    ges_rente_vorauss_besond_langj
        See :func:`ges_rente_vorauss_besond_langj`.
    ges_rente_vorauss_arbeitsl
        See :func:`ges_rente_vorauss_arbeitsl`.

    Returns
    -------
    Full retirement age.

    """

    out = ges_rente_regelaltersgrenze
    if ges_rente_vorauss_frauen:
        out = min([out, _ges_rente_frauen_altersgrenze])
    if ges_rente_vorauss_arbeitsl:
        out = min([out, _ges_rente_arbeitsl_altersgrenze])
    if ges_rente_vorauss_langj:
        out = min([out, _ges_rente_langj_altersgrenze])
    if ges_rente_vorauss_besond_langj:
        out = min([out, _ges_rente_besond_langj_altersgrenze])

    return out


@policy_info(
    start_date="2018-01-01", name_in_dag="_ges_rente_altersgrenze_abschlagsfrei"
)
def _ges_rente_altersgrenze_abschlagsfrei_ohne_arbeitsl_frauen(
    ges_rente_regelaltersgrenze: float,
    _ges_rente_langj_altersgrenze: float,
    _ges_rente_besond_langj_altersgrenze: float,
    ges_rente_vorauss_langj: bool,
    ges_rente_vorauss_besond_langj: bool,
) -> float:
    """Full retirement age after eligibility checks, assuming eligibility for
    Regelaltersrente.

    Age at which pension can be claimed without deductions. This age is smaller or equal
    to the normal retirement age (FRA<=NRA) and depends on personal characteristics as
    gender, insurance duration, health/disability, employment status.

    Parameters
    ----------
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    _ges_rente_langj_altersgrenze
        See :func:`_ges_rente_langj_altersgrenze`.
    _ges_rente_besond_langj_altersgrenze
        See :func:`_ges_rente_besond_langj_altersgrenze`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    ges_rente_vorauss_besond_langj
        See :func:`ges_rente_vorauss_besond_langj`.

    Returns
    -------
    Full retirement age.

    """

    out = ges_rente_regelaltersgrenze
    if ges_rente_vorauss_langj:
        out = min([out, _ges_rente_langj_altersgrenze])
    if ges_rente_vorauss_besond_langj:
        out = min([out, _ges_rente_besond_langj_altersgrenze])

    return out


@policy_info(end_date="2017-12-31", name_in_dag="_ges_rente_altersgrenze_vorzeitig")
def _ges_rente_altersgrenze_vorzeitig_mit_rente_arbeitsl_frauen(
    ges_rente_vorauss_frauen: bool,
    ges_rente_vorauss_langj: bool,
    ges_rente_vorauss_arbeitsl: bool,
    ges_rente_regelaltersgrenze: float,
    _ges_rente_frauen_altersgrenze_vorzeitig: float,
    _ges_rente_arbeitsl_vorzeitig: float,
    _ges_rente_langj_vorzeitig: float,
) -> float:
    """Earliest possible retirement age after checking for eligibility.

    Early retirement age depends on personal characteristics as gender, insurance
    duration, health/disability, employment status. Policy becomes inactive in 2018
    because then all potential beneficiaries of the Rente wg. Arbeitslosigkeit and Rente
    für Frauen have reached the normal retirement age.

    Parameters
    ----------
    ges_rente_vorauss_frauen
        See :func:`ges_rente_vorauss_frauen`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    ges_rente_vorauss_arbeitsl:
        See :func:`ges_rente_vorauss_arbeitsl`.
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    _ges_rente_frauen_altersgrenze_vorzeitig
        See :func:`_ges_rente_frauen_altersgrenze_vorzeitig`.
    _ges_rente_arbeitsl_vorzeitig
        See :func:`_ges_rente_arbeitsl_vorzeitig`.
    _ges_rente_langj_vorzeitig
        See :func:`_ges_rente_langj_vorzeitig`.

     Returns
    -------
    Early retirement age (potentially with deductions).

    """
    frauen_vorzeitig = _ges_rente_frauen_altersgrenze_vorzeitig

    arbeitsl_vorzeitig = _ges_rente_arbeitsl_vorzeitig

    langjährig_vorzeitig = _ges_rente_langj_vorzeitig

    out = ges_rente_regelaltersgrenze

    if ges_rente_vorauss_langj:
        out = langjährig_vorzeitig
    if ges_rente_vorauss_frauen:
        out = min([out, frauen_vorzeitig])
    if ges_rente_vorauss_arbeitsl:
        out = min([out, arbeitsl_vorzeitig])

    return out


@policy_info(start_date="2018-01-01", name_in_dag="_ges_rente_altersgrenze_vorzeitig")
def _ges_rente_altersgrenze_vorzeitig_ohne_rente_arbeitsl_frauen(
    ges_rente_vorauss_langj: bool,
    ges_rente_regelaltersgrenze: float,
    _ges_rente_langj_vorzeitig: float,
) -> float:
    """Earliest possible retirement age after checking for eligibility.

    Early retirement age depends on personal characteristics as gender, insurance
    duration, health/disability, employment status.

    Parameters
    ----------
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    _ges_rente_langj_vorzeitig
        See :func:`_ges_rente_langj_vorzeitig`.

     Returns
    -------
    Early retirement age (potentially with deductions).

    """

    out = ges_rente_regelaltersgrenze

    if ges_rente_vorauss_langj:
        out = _ges_rente_langj_vorzeitig
    else:
        out = ges_rente_regelaltersgrenze

    return out


@policy_info(end_date="2017-12-31", name_in_dag="ges_rente_vorauss_vorzeitig")
def ges_rente_vorauss_vorzeitig_mit_rente_arbeitsl_frauen(
    ges_rente_vorauss_frauen: bool,
    ges_rente_vorauss_langj: bool,
    ges_rente_vorauss_arbeitsl: bool,
) -> bool:
    """Eligibility for early retirement.

    Can only be claimed if eligible for "Rente für langjährig Versicherte" or "Rente für
    Frauen" or "Rente für Arbeitslose" (or -not yet implemented - for disabled). Policy
    becomes inactive in 2018 because then all potential beneficiaries of the Rente wg.
    Arbeitslosigkeit and Rente für Frauen have reached the normal retirement age.

    Parameters
    ----------
    ges_rente_vorauss_frauen
        See :func:`ges_rente_vorauss_frauen`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    ges_rente_vorauss_arbeitsl
        See :func:`ges_rente_vorauss_arbeitsl`.


    Returns
    -------
    Eligibility as bool.

    """

    out = (
        ges_rente_vorauss_frauen
        or ges_rente_vorauss_langj
        or ges_rente_vorauss_arbeitsl
    )

    return out


@policy_info(start_date="2018-01-01", name_in_dag="ges_rente_vorauss_vorzeitig")
def ges_rente_vorauss_vorzeitig_ohne_rente_arbeitsl_frauen(
    ges_rente_vorauss_langj: bool,
) -> bool:
    """Eligibility for early retirement.

    Can only be claimed if eligible for "Rente für langjährig Versicherte".

    Parameters
    ----------
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.

    Returns
    -------
    Eligibility as bool.

    """

    return ges_rente_vorauss_langj


@policy_info(end_date="2017-12-31", name_in_dag="referenzalter_abschlag")
def _referenzalter_abschlag_mit_rente_arbeitsl_frauen(
    ges_rente_regelaltersgrenze: float,
    _ges_rente_frauen_altersgrenze: float,
    _ges_rente_langj_altersgrenze: float,
    _ges_rente_arbeitsl_altersgrenze: float,
    ges_rente_vorauss_frauen: bool,
    ges_rente_vorauss_langj: bool,
    ges_rente_vorauss_arbeitsl: bool,
) -> float:
    """Reference age for deduction calculation in case of early retirement
    (Zugangsfaktor).

    Normal retirement age if not eligible for early retirement. Policy becomes inactive
    in 2018 because then all potential beneficiaries of the Rente wg. Arbeitslosigkeit
    and Rente für Frauen have reached the normal retirement age.

    Parameters
    ----------
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    _ges_rente_frauen_altersgrenze
        See :func:`_ges_rente_frauen_altersgrenze`.
    _ges_rente_langj_altersgrenze
        See :func:`_ges_rente_langj_altersgrenze`.
    _ges_rente_arbeitsl_altersgrenze
        See :func:`_ges_rente_arbeitsl_altersgrenze`.
    ges_rente_vorauss_frauen
        See :func:`ges_rente_vorauss_frauen`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    ges_rente_vorauss_arbeitsl
        See :func:`ges_rente_vorauss_arbeitsl`.

     Returns
    -------
    Reference age for deduction calculation.

    """
    if (
        ges_rente_vorauss_langj
        and ges_rente_vorauss_frauen
        and ges_rente_vorauss_arbeitsl
    ):
        out = min(
            [
                _ges_rente_frauen_altersgrenze,
                _ges_rente_langj_altersgrenze,
                _ges_rente_arbeitsl_altersgrenze,
            ]
        )
    elif ges_rente_vorauss_langj and ges_rente_vorauss_frauen:
        out = min([_ges_rente_frauen_altersgrenze, _ges_rente_langj_altersgrenze])
    elif ges_rente_vorauss_langj and ges_rente_vorauss_arbeitsl:
        out = min([_ges_rente_langj_altersgrenze, _ges_rente_arbeitsl_altersgrenze])
    elif ges_rente_vorauss_langj:
        out = _ges_rente_langj_altersgrenze
    elif ges_rente_vorauss_frauen:
        out = _ges_rente_frauen_altersgrenze
    elif ges_rente_vorauss_arbeitsl:
        out = _ges_rente_arbeitsl_altersgrenze
    else:
        out = ges_rente_regelaltersgrenze

    return out


@policy_info(start_date="2018-01-01", name_in_dag="referenzalter_abschlag")
def _referenzalter_abschlag_ohne_rente_arbeitsl_frauen(
    ges_rente_regelaltersgrenze: float,
    _ges_rente_langj_altersgrenze: float,
    ges_rente_vorauss_langj: bool,
) -> float:
    """Reference age for deduction calculation in case of early retirement
    (Zugangsfaktor).

    Normal retirement age if not eligible for early retirement.

    Parameters
    ----------
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    _ges_rente_langj_altersgrenze
        See :func:`_ges_rente_langj_altersgrenze`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.

     Returns
    -------
    Reference age for deduction calculation.

    """
    if ges_rente_vorauss_langj:
        out = _ges_rente_langj_altersgrenze
    else:
        out = ges_rente_regelaltersgrenze

    return out
