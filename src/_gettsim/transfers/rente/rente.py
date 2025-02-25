"""Public pension benefits."""

from _gettsim.functions.policy_function import policy_function


@policy_function
def alter_bei_renteneintritt(
    jahr_renteneintr: int,
    monat_renteneintr: int,
    geburtsjahr: int,
    geburtsmonat: int,
) -> float:
    """Age at retirement in monthly precision.

    Calculates the age of person's retirement in monthly precision.
    As retirement is only possible at first day of month and as
    persons eligible for pension at first of month after reaching the
    age threshold (§ 99 SGB VI) persons who retire in same month will
    be considered a month too young: Substraction of 1/12.


    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    jahr_renteneintr
        See basic input variable :ref:`jahr_renteneintr <jahr_renteneintr>`.
    monat_renteneintr
        See basic input variable :ref:`monat_renteneintr <monat_renteneintr>`.

    Returns
    -------
    Age at retirement.

    """
    return jahr_renteneintr - geburtsjahr + (monat_renteneintr - geburtsmonat - 1) / 12
