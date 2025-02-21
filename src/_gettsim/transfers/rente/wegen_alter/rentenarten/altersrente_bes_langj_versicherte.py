"""Pathway for the very long-term insured."""

from _gettsim.functions.policy_function import policy_function


@policy_function(
    start_date="2012-01-01",
    end_date="2014-06-22",
    name_in_dag="_ges_rente_besond_langj_altersgrenze",
)
def _ges_rente_besond_langj_altersgrenze_ohne_staffelung(
    geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """
    Full retirement age (FRA) for very long term insured.

    FRA is the same for each birth year.

    Calculate the threshold from which very long term insured people (at least 45
    years) can claim their full pension without deductions.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age (without deductions) for very long term insured.

    """
    # TODO(@MImmesberger): Remove fake dependency (geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_besond_langj_versicherte"]


@policy_function(
    start_date="2014-06-23", name_in_dag="_ges_rente_besond_langj_altersgrenze"
)
def _ges_rente_besond_langj_altersgrenze_mit_staffelung(
    geburtsjahr: int,
    ges_rente_params: dict,
) -> float:
    """
    Full retirement age (FRA) for very long term insured.

    FRA depends on birth year and month.

    Calculate the threshold from which very long term insured people (at least 45
    years) can claim their full pension without deductions.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age (without deductions) for very long term insured.

    """
    if (
        geburtsjahr
        <= ges_rente_params["altersgrenze_besond_langj_versicherte"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_besond_langj_versicherte"][
            "entry_age_old_regime"
        ]
    elif (
        geburtsjahr
        >= ges_rente_params["altersgrenze_besond_langj_versicherte"][
            "min_birthyear_new_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_besond_langj_versicherte"][
            "entry_age_new_regime"
        ]
    else:
        out = ges_rente_params["altersgrenze_besond_langj_versicherte"][geburtsjahr]

    return out


@policy_function(start_date="2012-01-01")
def ges_rente_vorauss_besond_langj(
    ges_rente_wartezeit_45: bool,
) -> bool:
    """Determining the eligibility for Altersrente für besonders langjährig Versicherte
    (pension for very long-term insured). Wartezeit 45 years. aka "Rente mit 63".

    Parameters
    ----------
    ges_rente_wartezeit_45
        See :func:`ges_rente_wartezeit_45`


    Returns
    -------
    Eligibility as bool.

    """

    return ges_rente_wartezeit_45
