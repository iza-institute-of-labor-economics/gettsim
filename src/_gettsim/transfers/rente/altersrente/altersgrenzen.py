"""Age thresholds for public pension eligibility."""

from _gettsim.functions.policy_function import policy_function


@policy_function(end_date="2011-12-31", name_in_dag="altersgrenze_abschlagsfrei")
def altersgrenze_abschlagsfrei_ohne_besond_langj(  # noqa: PLR0913
    rente__altersrente__regelaltersrente__altersgrenze: float,
    rente__altersrente__für_frauen__altersgrenze: float,
    rente__altersrente__langjährig__altersgrenze: float,
    rente__altersrente__wegen_arbeitslosigkeit__altersgrenze: float,
    rente__altersrente__für_frauen__anspruchsberechtigt: bool,
    rente__altersrente__langjährig__anspruchsberechtigt: bool,
    rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt: bool,
) -> float:
    """Full retirement age after eligibility checks, assuming eligibility for
    Regelaltersrente.

    Age at which pension can be claimed without deductions. This age is smaller or equal
    to the normal retirement age (FRA<=NRA) and depends on personal characteristics as
    gender, insurance duration, health/disability, employment status.

    Parameters
    ----------
    rente__altersrente__regelaltersrente__altersgrenze
        See :func:`rente__altersrente__regelaltersrente__altersgrenze`.
    rente__altersrente__für_frauen__altersgrenze
        See :func:`rente__altersrente__für_frauen__altersgrenze`.
    rente__altersrente__langjährig__altersgrenze
        See :func:`rente__altersrente__langjährig__altersgrenze`.
    rente__altersrente__wegen_arbeitslosigkeit__altersgrenze
         See :func:`rente__altersrente__wegen_arbeitslosigkeit__altersgrenze`.
    rente__altersrente__für_frauen__anspruchsberechtigt
        See :func:`rente__altersrente__für_frauen__anspruchsberechtigt`.
    rente__altersrente__langjährig__anspruchsberechtigt
        See :func:`rente__altersrente__langjährig__anspruchsberechtigt`.
    rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt:
        See :func:`rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt`.
    Returns
    -------
    Full retirement age.

    """

    out = rente__altersrente__regelaltersrente__altersgrenze
    if rente__altersrente__für_frauen__anspruchsberechtigt:
        out = min([out, rente__altersrente__für_frauen__altersgrenze])
    if rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt:
        out = min([out, rente__altersrente__wegen_arbeitslosigkeit__altersgrenze])
    if rente__altersrente__langjährig__anspruchsberechtigt:
        out = min([out, rente__altersrente__langjährig__altersgrenze])

    return out


@policy_function(
    start_date="2012-01-01",
    end_date="2017-12-31",
    name_in_dag="altersgrenze_abschlagsfrei",
)
def altersgrenze_abschlagsfrei_mit_besond_langj(  # noqa: PLR0913
    rente__altersrente__regelaltersrente__altersgrenze: float,
    rente__altersrente__für_frauen__altersgrenze: float,
    rente__altersrente__langjährig__altersgrenze: float,
    rente__altersrente__besonders_langjährig__altersgrenze: float,
    rente__altersrente__wegen_arbeitslosigkeit__altersgrenze: float,
    rente__altersrente__für_frauen__anspruchsberechtigt: bool,
    rente__altersrente__langjährig__anspruchsberechtigt: bool,
    rente__altersrente__besonders_langjährig__anspruchsberechtigt: bool,
    rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt: bool,
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
    rente__altersrente__regelaltersrente__altersgrenze
        See :func:`rente__altersrente__regelaltersrente__altersgrenze`.
    rente__altersrente__für_frauen__altersgrenze
        See :func:`rente__altersrente__für_frauen__altersgrenze`.
    rente__altersrente__langjährig__altersgrenze
        See :func:`rente__altersrente__langjährig__altersgrenze`.
    rente__altersrente__besonders_langjährig__altersgrenze
        See :func:`rente__altersrente__besonders_langjährig__altersgrenze`.
    rente__altersrente__wegen_arbeitslosigkeit__altersgrenze
        See :func:`rente__altersrente__wegen_arbeitslosigkeit__altersgrenze`.
    rente__altersrente__für_frauen__anspruchsberechtigt
        See :func:`rente__altersrente__für_frauen__anspruchsberechtigt`.
    rente__altersrente__langjährig__anspruchsberechtigt
        See :func:`rente__altersrente__langjährig__anspruchsberechtigt`.
    rente__altersrente__besonders_langjährig__anspruchsberechtigt
        See :func:`rente__altersrente__besonders_langjährig__anspruchsberechtigt`.
    rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt
        See :func:`rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt`.

    Returns
    -------
    Full retirement age.

    """

    out = rente__altersrente__regelaltersrente__altersgrenze
    if rente__altersrente__für_frauen__anspruchsberechtigt:
        out = min([out, rente__altersrente__für_frauen__altersgrenze])
    if rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt:
        out = min([out, rente__altersrente__wegen_arbeitslosigkeit__altersgrenze])
    if rente__altersrente__langjährig__anspruchsberechtigt:
        out = min([out, rente__altersrente__langjährig__altersgrenze])
    if rente__altersrente__besonders_langjährig__anspruchsberechtigt:
        out = min([out, rente__altersrente__besonders_langjährig__altersgrenze])

    return out


@policy_function(start_date="2018-01-01", name_in_dag="altersgrenze_abschlagsfrei")
def altersgrenze_abschlagsfrei_ohne_arbeitsl_frauen(
    rente__altersrente__regelaltersrente__altersgrenze: float,
    rente__altersrente__langjährig__altersgrenze: float,
    rente__altersrente__besonders_langjährig__altersgrenze: float,
    rente__altersrente__langjährig__anspruchsberechtigt: bool,
    rente__altersrente__besonders_langjährig__anspruchsberechtigt: bool,
) -> float:
    """Full retirement age after eligibility checks, assuming eligibility for
    Regelaltersrente.

    Age at which pension can be claimed without deductions. This age is smaller or equal
    to the normal retirement age (FRA<=NRA) and depends on personal characteristics as
    gender, insurance duration, health/disability, employment status.

    Parameters
    ----------
    rente__altersrente__regelaltersrente__altersgrenze
        See :func:`rente__altersrente__regelaltersrente__altersgrenze`.
    rente__altersrente__langjährig__altersgrenze
        See :func:`rente__altersrente__langjährig__altersgrenze`.
    rente__altersrente__besonders_langjährig__altersgrenze
        See :func:`rente__altersrente__besonders_langjährig__altersgrenze`.
    rente__altersrente__langjährig__anspruchsberechtigt
        See :func:`rente__altersrente__langjährig__anspruchsberechtigt`.
    rente__altersrente__besonders_langjährig__anspruchsberechtigt
        See :func:`rente__altersrente__besonders_langjährig__anspruchsberechtigt`.

    Returns
    -------
    Full retirement age.

    """

    out = rente__altersrente__regelaltersrente__altersgrenze
    if rente__altersrente__langjährig__anspruchsberechtigt:
        out = min([out, rente__altersrente__langjährig__altersgrenze])
    if rente__altersrente__besonders_langjährig__anspruchsberechtigt:
        out = min([out, rente__altersrente__besonders_langjährig__altersgrenze])

    return out


@policy_function(end_date="2017-12-31", name_in_dag="altersgrenze_vorzeitig")
def altersgrenze_vorzeitig_mit_rente_arbeitsl_frauen(  # noqa: PLR0913
    rente__altersrente__für_frauen__anspruchsberechtigt: bool,
    rente__altersrente__langjährig__anspruchsberechtigt: bool,
    rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt: bool,
    rente__altersrente__regelaltersrente__altersgrenze: float,
    rente__altersrente__für_frauen__altersgrenze_vorzeitig: float,
    rente__altersrente__wegen_arbeitslosigkeit__altersgrenze_vorzeitig: float,
    rente__altersrente__langjährig__altersgrenze_vorzeitig: float,
) -> float:
    """Earliest possible retirement age after checking for eligibility.

    Early retirement age depends on personal characteristics as gender, insurance
    duration, health/disability, employment status. Policy becomes inactive in 2018
    because then all potential beneficiaries of the Rente wg. Arbeitslosigkeit and Rente
    für Frauen have reached the normal retirement age.

    Parameters
    ----------
    rente__altersrente__für_frauen__anspruchsberechtigt
        See :func:`rente__altersrente__für_frauen__anspruchsberechtigt`.
    rente__altersrente__langjährig__anspruchsberechtigt
        See :func:`rente__altersrente__langjährig__anspruchsberechtigt`.
    rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt:
        See :func:`rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt`.
    rente__altersrente__regelaltersrente__altersgrenze
        See :func:`rente__altersrente__regelaltersrente__altersgrenze`.
    rente__altersrente__für_frauen__altersgrenze_vorzeitig
        See :func:`rente__altersrente__für_frauen__altersgrenze_vorzeitig`.
    rente__altersrente__wegen_arbeitslosigkeit__altersgrenze_vorzeitig
        See :func:`rente__altersrente__wegen_arbeitslosigkeit__altersgrenze_vorzeitig`.
    rente__altersrente__langjährig__altersgrenze_vorzeitig
        See :func:`rente__altersrente__langjährig__altersgrenze_vorzeitig`.

     Returns
    -------
    Early retirement age (potentially with deductions).

    """
    frauen_vorzeitig = rente__altersrente__für_frauen__altersgrenze_vorzeitig

    arbeitsl_vorzeitig = (
        rente__altersrente__wegen_arbeitslosigkeit__altersgrenze_vorzeitig
    )

    langjährig_vorzeitig = rente__altersrente__langjährig__altersgrenze_vorzeitig

    out = rente__altersrente__regelaltersrente__altersgrenze

    if rente__altersrente__langjährig__anspruchsberechtigt:
        out = langjährig_vorzeitig
    if rente__altersrente__für_frauen__anspruchsberechtigt:
        out = min([out, frauen_vorzeitig])
    if rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt:
        out = min([out, arbeitsl_vorzeitig])

    return out


@policy_function(start_date="2018-01-01", name_in_dag="altersgrenze_vorzeitig")
def altersgrenze_vorzeitig_ohne_rente_arbeitsl_frauen(
    rente__altersrente__langjährig__anspruchsberechtigt: bool,
    rente__altersrente__regelaltersrente__altersgrenze: float,
    rente__altersrente__langjährig__altersgrenze_vorzeitig: float,
) -> float:
    """Earliest possible retirement age after checking for eligibility.

    Early retirement age depends on personal characteristics as gender, insurance
    duration, health/disability, employment status.

    Parameters
    ----------
    rente__altersrente__langjährig__anspruchsberechtigt
        See :func:`rente__altersrente__langjährig__anspruchsberechtigt`.
    rente__altersrente__regelaltersrente__altersgrenze
        See :func:`rente__altersrente__regelaltersrente__altersgrenze`.
    rente__altersrente__langjährig__altersgrenze_vorzeitig
        See :func:`rente__altersrente__langjährig__altersgrenze_vorzeitig`.

     Returns
    -------
    Early retirement age (potentially with deductions).

    """

    out = rente__altersrente__regelaltersrente__altersgrenze

    if rente__altersrente__langjährig__anspruchsberechtigt:
        out = rente__altersrente__langjährig__altersgrenze_vorzeitig
    else:
        out = rente__altersrente__regelaltersrente__altersgrenze

    return out


@policy_function(end_date="2017-12-31", name_in_dag="voraussetzung_vorzeitig_erfüllt")
def voraussetzung_vorzeitig_erfüllt_mit_rente_arbeitsl_frauen(
    rente__altersrente__für_frauen__anspruchsberechtigt: bool,
    rente__altersrente__langjährig__anspruchsberechtigt: bool,
    rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt: bool,
) -> bool:
    """Eligibility for early retirement.

    Can only be claimed if eligible for "Rente für langjährig Versicherte" or "Rente für
    Frauen" or "Rente für Arbeitslose" (or -not yet implemented - for disabled). Policy
    becomes inactive in 2018 because then all potential beneficiaries of the Rente wg.
    Arbeitslosigkeit and Rente für Frauen have reached the normal retirement age.

    Parameters
    ----------
    rente__altersrente__für_frauen__anspruchsberechtigt
        See :func:`rente__altersrente__für_frauen__anspruchsberechtigt`.
    rente__altersrente__langjährig__anspruchsberechtigt
        See :func:`rente__altersrente__langjährig__anspruchsberechtigt`.
    rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt
        See :func:`rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt`.


    Returns
    -------
    Eligibility as bool.

    """

    out = (
        rente__altersrente__für_frauen__anspruchsberechtigt
        or rente__altersrente__langjährig__anspruchsberechtigt
        or rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt
    )

    return out


@policy_function(start_date="2018-01-01", name_in_dag="voraussetzung_vorzeitig_erfüllt")
def voraussetzung_vorzeitig_erfüllt_vorzeitig_ohne_rente_arbeitsl_frauen(
    rente__altersrente__langjährig__anspruchsberechtigt: bool,
) -> bool:
    """Eligibility for early retirement.

    Can only be claimed if eligible for "Rente für langjährig Versicherte".

    Parameters
    ----------
    rente__altersrente__langjährig__anspruchsberechtigt
        See :func:`rente__altersrente__langjährig__anspruchsberechtigt`.

    Returns
    -------
    Eligibility as bool.

    """

    return rente__altersrente__langjährig__anspruchsberechtigt


@policy_function(end_date="2017-12-31", name_in_dag="referenzalter_abschlag")
def referenzalter_abschlag_mit_rente_arbeitsl_frauen(  # noqa: PLR0913
    rente__altersrente__regelaltersrente__altersgrenze: float,
    rente__altersrente__für_frauen__altersgrenze: float,
    rente__altersrente__langjährig__altersgrenze: float,
    rente__altersrente__wegen_arbeitslosigkeit__altersgrenze: float,
    rente__altersrente__für_frauen__anspruchsberechtigt: bool,
    rente__altersrente__langjährig__anspruchsberechtigt: bool,
    rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt: bool,
) -> float:
    """Reference age for deduction calculation in case of early retirement
    (Zugangsfaktor).

    Normal retirement age if not eligible for early retirement. Policy becomes inactive
    in 2018 because then all potential beneficiaries of the Rente wg. Arbeitslosigkeit
    and Rente für Frauen have reached the normal retirement age.

    Parameters
    ----------
    rente__altersrente__regelaltersrente__altersgrenze
        See :func:`rente__altersrente__regelaltersrente__altersgrenze`.
    rente__altersrente__für_frauen__altersgrenze
        See :func:`rente__altersrente__für_frauen__altersgrenze`.
    rente__altersrente__langjährig__altersgrenze
        See :func:`rente__altersrente__langjährig__altersgrenze`.
    rente__altersrente__wegen_arbeitslosigkeit__altersgrenze
        See :func:`rente__altersrente__wegen_arbeitslosigkeit__altersgrenze`.
    rente__altersrente__für_frauen__anspruchsberechtigt
        See :func:`rente__altersrente__für_frauen__anspruchsberechtigt`.
    rente__altersrente__langjährig__anspruchsberechtigt
        See :func:`rente__altersrente__langjährig__anspruchsberechtigt`.
    rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt
        See :func:`rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt`.

     Returns
    -------
    Reference age for deduction calculation.

    """
    if (
        rente__altersrente__langjährig__anspruchsberechtigt
        and rente__altersrente__für_frauen__anspruchsberechtigt
        and rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt
    ):
        out = min(
            [
                rente__altersrente__für_frauen__altersgrenze,
                rente__altersrente__langjährig__altersgrenze,
                rente__altersrente__wegen_arbeitslosigkeit__altersgrenze,
            ]
        )
    elif (
        rente__altersrente__langjährig__anspruchsberechtigt
        and rente__altersrente__für_frauen__anspruchsberechtigt
    ):
        out = min(
            [
                rente__altersrente__für_frauen__altersgrenze,
                rente__altersrente__langjährig__altersgrenze,
            ]
        )
    elif (
        rente__altersrente__langjährig__anspruchsberechtigt
        and rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt
    ):
        out = min(
            [
                rente__altersrente__langjährig__altersgrenze,
                rente__altersrente__wegen_arbeitslosigkeit__altersgrenze,
            ]
        )
    elif rente__altersrente__langjährig__anspruchsberechtigt:
        out = rente__altersrente__langjährig__altersgrenze
    elif rente__altersrente__für_frauen__anspruchsberechtigt:
        out = rente__altersrente__für_frauen__altersgrenze
    elif rente__altersrente__wegen_arbeitslosigkeit__anspruchsberechtigt:
        out = rente__altersrente__wegen_arbeitslosigkeit__altersgrenze
    else:
        out = rente__altersrente__regelaltersrente__altersgrenze

    return out


@policy_function(start_date="2018-01-01", name_in_dag="referenzalter_abschlag")
def referenzalter_abschlag_ohne_rente_arbeitsl_frauen(
    rente__altersrente__regelaltersrente__altersgrenze: float,
    rente__altersrente__langjährig__altersgrenze: float,
    rente__altersrente__langjährig__anspruchsberechtigt: bool,
) -> float:
    """Reference age for deduction calculation in case of early retirement
    (Zugangsfaktor).

    Normal retirement age if not eligible for early retirement.

    Parameters
    ----------
    rente__altersrente__regelaltersrente__altersgrenze
        See :func:`rente__altersrente__regelaltersrente__altersgrenze`.
    rente__altersrente__langjährig__altersgrenze
        See :func:`rente__altersrente__langjährig__altersgrenze`.
    rente__altersrente__langjährig__anspruchsberechtigt
        See :func:`rente__altersrente__langjährig__anspruchsberechtigt`.

     Returns
    -------
    Reference age for deduction calculation.

    """
    if rente__altersrente__langjährig__anspruchsberechtigt:
        out = rente__altersrente__langjährig__altersgrenze
    else:
        out = rente__altersrente__regelaltersrente__altersgrenze

    return out
