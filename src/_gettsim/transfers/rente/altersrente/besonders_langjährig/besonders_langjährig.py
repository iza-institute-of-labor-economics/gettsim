"""Pathway for the very long-term insured."""

from _gettsim.function_types import policy_function


@policy_function(
    start_date="2012-01-01",
    end_date="2014-06-22",
    leaf_name="altersgrenze",
)
def altersgrenze_ohne_staffelung(
    demographics__geburtsjahr: int,  # noqa: ARG001
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
    demographics__geburtsjahr
        See basic input variable :ref:`demographics__geburtsjahr <demographics__geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age (without deductions) for very long term insured.

    """
    # TODO(@MImmesberger): Remove fake dependency (demographics__geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_besond_langj_versicherte"]


@policy_function(start_date="2014-06-23", leaf_name="altersgrenze")
def altersgrenze_mit_staffelung(
    demographics__geburtsjahr: int,
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
    demographics__geburtsjahr
        See basic input variable :ref:`demographics__geburtsjahr <demographics__geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age (without deductions) for very long term insured.

    """
    if (
        demographics__geburtsjahr
        <= ges_rente_params["altersgrenze_besond_langj_versicherte"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_besond_langj_versicherte"][
            "entry_age_old_regime"
        ]
    elif (
        demographics__geburtsjahr
        >= ges_rente_params["altersgrenze_besond_langj_versicherte"][
            "min_birthyear_new_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_besond_langj_versicherte"][
            "entry_age_new_regime"
        ]
    else:
        out = ges_rente_params["altersgrenze_besond_langj_versicherte"][
            demographics__geburtsjahr
        ]

    return out


@policy_function(start_date="2012-01-01")
def grundsätzlich_anspruchsberechtigt(
    rente__altersrente__wartezeit_45_jahre_erfüllt: bool,
) -> bool:
    """Determining the eligibility for Altersrente für besonders langjährig Versicherte
    (pension for very long-term insured). Wartezeit 45 years. aka "Rente mit 63".

    Parameters
    ----------
    rente__altersrente__wartezeit_45_jahre_erfüllt
        See :func:`rente__altersrente__wartezeit_45_jahre_erfüllt`


    Returns
    -------
    Eligibility as bool.

    """

    return rente__altersrente__wartezeit_45_jahre_erfüllt
