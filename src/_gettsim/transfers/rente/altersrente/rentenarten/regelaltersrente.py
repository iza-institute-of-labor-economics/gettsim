"""Regular pathway."""

from _gettsim.functions.policy_function import policy_function


@policy_function(end_date="2007-04-19", name_in_dag="ges_rente_regelaltersgrenze")
def ges_rente_regelaltersgrenze_ohne_staffelung(
    geburtsjahr: int,  # noqa: ARG001
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
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.


    Returns
    -------
    Normal retirement age (NRA).

    """
    # TODO(@MImmesberger): Remove fake dependency (geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["regelaltersgrenze"]


@policy_function(start_date="2007-04-20", name_in_dag="ges_rente_regelaltersgrenze")
def ges_rente_regelaltersgrenze_mit_staffelung(
    geburtsjahr: int, ges_rente_params: dict
) -> float:
    """Normal retirement age (NRA).

    NRA differs by birth cohort.

    The Regelaltersrente cannot be claimed earlier than at the NRA, i.e. the NRA does
    not serve as reference for calculating deductions. However, it serves as reference
    for calculating gains in the Zugangsfakor in case of later retirement.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.


    Returns
    -------
    Normal retirement age (NRA).

    """
    if geburtsjahr <= ges_rente_params["regelaltersgrenze"]["max_birthyear_old_regime"]:
        out = ges_rente_params["regelaltersgrenze"]["entry_age_old_regime"]
    elif (
        geburtsjahr >= ges_rente_params["regelaltersgrenze"]["min_birthyear_new_regime"]
    ):
        out = ges_rente_params["regelaltersgrenze"]["entry_age_new_regime"]
    else:
        out = ges_rente_params["regelaltersgrenze"][geburtsjahr]

    return out


def ges_rente_vorauss_regelrente(ges_rente_wartezeit_5: bool) -> bool:
    """Determining the eligibility for the Regelaltersrente.

    Parameters
    ----------
    ges_rente_wartezeit_5
        See :func:`ges_rente_wartezeit_5`.

    Returns
    -------
    Eligibility as bool.

    """

    return ges_rente_wartezeit_5
