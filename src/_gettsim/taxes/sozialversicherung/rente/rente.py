"""Public pension benefits."""

from _gettsim.function_types import policy_function


@policy_function()
def alter_bei_renteneintritt(
    jahr_renteneintritt: int,
    monat_renteneintritt: int,
    demographics__geburtsjahr: int,
    demographics__geburtsmonat: int,
) -> float:
    """Age at retirement in monthly precision.

    Calculates the age of person's retirement in monthly precision.
    As retirement is only possible at first day of month and as
    persons eligible for pension at first of month after reaching the
    age threshold (§ 99 SGB VI) persons who retire in same month will
    be considered a month too young: Substraction of 1/12.


    Parameters
    ----------
    demographics__geburtsjahr
        See basic input variable :ref:`demographics__geburtsjahr <demographics__geburtsjahr>`.
    demographics__geburtsmonat
        See basic input variable :ref:`demographics__geburtsmonat <demographics__geburtsmonat>`.
    jahr_renteneintritt
        See basic input variable :ref:`jahr_renteneintritt <jahr_renteneintritt>`.
    monat_renteneintritt
        See basic input variable :ref:`monat_renteneintritt <monat_renteneintritt>`.

    Returns
    -------
    Age at retirement.

    """
    return (
        jahr_renteneintritt
        - demographics__geburtsjahr
        + (monat_renteneintritt - demographics__geburtsmonat - 1) / 12
    )


@policy_function()
def summe_private_gesetzliche_rente_m(
    private_rente_m: float, sozialversicherung__rente__altersrente__betrag_m: float
) -> float:
    """Calculate total individual pension as sum of private and public pension.

    Parameters
    ----------
    private_rente_m
        See basic input variable :ref:`private_rente_m <private_rente_m>`.
    sozialversicherung__rente__altersrente__betrag_m
        See :func:`sozialversicherung__rente__altersrente__betrag_m`.

    Returns
    -------

    """
    out = private_rente_m + sozialversicherung__rente__altersrente__betrag_m
    return out
