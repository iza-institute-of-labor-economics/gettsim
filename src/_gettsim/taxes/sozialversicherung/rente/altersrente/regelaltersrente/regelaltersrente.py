"""Regular pathway."""

from _gettsim.function_types import policy_function


@policy_function(end_date="2007-04-19", leaf_name="altersgrenze")
def altersgrenze_ohne_staffelung(
    demographics__geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """Normal retirement age (NRA).

    NRA is the same for every birth cohort.

    The Regelaltersrente cannot be claimed earlier than at the NRA, i.e. the NRA does
    not serve as reference for calculating deductions. However, it serves as reference
    for calculating gains in the Zugangsfakor in case of later retirement.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    demographics__geburtsjahr
        See basic input variable :ref:`demographics__geburtsjahr <demographics__geburtsjahr>`.
    demographics__geburtsmonat
        See basic input variable :ref:`demographics__geburtsmonat <demographics__geburtsmonat>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.


    Returns
    -------
    Normal retirement age (NRA).

    """
    # TODO(@MImmesberger): Remove fake dependency (demographics__geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["regelaltersgrenze"]


@policy_function(start_date="2007-04-20", leaf_name="altersgrenze")
def altersgrenze_mit_staffelung(
    demographics__geburtsjahr: int, ges_rente_params: dict
) -> float:
    """Normal retirement age (NRA).

    NRA differs by birth cohort.

    The Regelaltersrente cannot be claimed earlier than at the NRA, i.e. the NRA does
    not serve as reference for calculating deductions. However, it serves as reference
    for calculating gains in the Zugangsfakor in case of later retirement.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    demographics__geburtsjahr
        See basic input variable :ref:`demographics__geburtsjahr <demographics__geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.


    Returns
    -------
    Normal retirement age (NRA).

    """
    if (
        demographics__geburtsjahr
        <= ges_rente_params["regelaltersgrenze"]["max_birthyear_old_regime"]
    ):
        out = ges_rente_params["regelaltersgrenze"]["entry_age_old_regime"]
    elif (
        demographics__geburtsjahr
        >= ges_rente_params["regelaltersgrenze"]["min_birthyear_new_regime"]
    ):
        out = ges_rente_params["regelaltersgrenze"]["entry_age_new_regime"]
    else:
        out = ges_rente_params["regelaltersgrenze"][demographics__geburtsjahr]

    return out


@policy_function()
def grundsätzlich_anspruchsberechtigt(
    sozialversicherung__rente__mindestwartezeit_erfüllt: bool,
) -> bool:
    """Determining the eligibility for the Regelaltersrente.

    Parameters
    ----------
    sozialversicherung__rente__mindestwartezeit_erfüllt
        See :func:`sozialversicherung__rente__mindestwartezeit_erfüllt`.

    Returns
    -------
    Eligibility as bool.

    """

    return sozialversicherung__rente__mindestwartezeit_erfüllt
