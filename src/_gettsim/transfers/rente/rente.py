"""Public pension benefits."""

from _gettsim.functions.policy_function import policy_function


@policy_function
def alter_bei_renteneintritt(
    rente__jahr_renteneintritt: int,
    rente__monat_renteneintritt: int,
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
    rente__jahr_renteneintritt
        See basic input variable :ref:`rente__jahr_renteneintritt <rente__jahr_renteneintritt>`.
    rente__monat_renteneintritt
        See basic input variable :ref:`rente__monat_renteneintritt <rente__monat_renteneintritt>`.

    Returns
    -------
    Age at retirement.

    """
    return (
        rente__jahr_renteneintritt
        - demographics__geburtsjahr
        + (rente__monat_renteneintritt - demographics__geburtsmonat - 1) / 12
    )
