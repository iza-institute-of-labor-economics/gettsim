"""Pathway for the long-term insured."""

from _gettsim.functions.policy_function import policy_function


@policy_function(end_date="1989-12-17", name_in_dag="altersgrenze")
def altersgrenze_ohne_staffelung(
    demographics__geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """
    Full retirement age (FRA) for long term insured.

    FRA is the same for each birth year.

    Calculate the age, at which a long term insured person (at least 35 years) is
    eligible to claim the full pension (without deductions). This pension scheme allows
    for early retirement (e.g. age 63) with deductions. Hence this threshold is needed
    as reference for calculating the zugangsfaktor.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    demographics__geburtsjahr
        See basic input variable :ref:`demographics__geburtsjahr <demographics__geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age for long term insured.

    """
    # TODO(@MImmesberger): Remove fake dependency (demographics__geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"]


@policy_function(
    start_date="1989-12-18",
    end_date="2007-04-19",
    name_in_dag="altersgrenze",
)
def altersgrenze_mit_staffelung_nach_geburtsmonat(
    demographics__geburtsjahr: int,
    demographics__geburtsmonat: int,
    ges_rente_params: dict,
) -> float:
    """
    Full retirement age (FRA) for long term insured.

    FRA depends on birth year and month.

    Calculate the age, at which a long term insured person (at least 35 years) is
    eligible to claim the full pension (without deductions). This pension scheme allows
    for early retirement (e.g. age 63) with deductions. Hence this threshold is needed
    as reference for calculating the zugangsfaktor.

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
    Full retirement age (without deductions) for long term insured.
    """
    if (
        demographics__geburtsjahr
        <= ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            "entry_age_old_regime"
        ]
    elif (
        demographics__geburtsjahr
        >= ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            "min_birthyear_new_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            "entry_age_new_regime"
        ]
    else:
        out = ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            demographics__geburtsjahr
        ][demographics__geburtsmonat]

    return out


@policy_function(start_date="2007-04-20", name_in_dag="altersgrenze")
def altersgrenze_mit_staffelung_nach_geburtsjahr(
    demographics__geburtsjahr: int,
    demographics__geburtsmonat: int,
    ges_rente_params: dict,
) -> float:
    """
    Full retirement age (FRA) for long term insured.

    FRA depends on birth year.

    Calculate the age, at which a long term insured person (at least 35 years) is
    eligible to claim the full pension (without deductions). This pension scheme allows
    for early retirement (e.g. age 63) with deductions. Hence this threshold is needed
    as reference for calculating the zugangsfaktor.

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
    Full retirement age (without deductions) for long term insured.
    """
    if (
        demographics__geburtsjahr
        <= ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            "entry_age_old_regime"
        ]
    elif (
        demographics__geburtsjahr
        >= ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            "min_birthyear_new_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            "entry_age_new_regime"
        ]
    else:
        out = ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            demographics__geburtsjahr
        ][demographics__geburtsmonat]

    return out


@policy_function(end_date="1989-12-17", name_in_dag="altersgrenze_vorzeitig")
def altersgrenze_vorzeitig_ohne_staffelung(
    demographics__geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """Early retirement age (ERA) for Rente für langjährig Versicherte.

    ERA does not depend on birth year and month.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    demographics__geburtsjahr
        See basic input variable :ref:`demographics__geburtsjahr <demographics__geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age

    """

    # TODO(@MImmesberger): Remove fake dependency (demographics__geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_langj_versicherte_vorzeitig"]


@policy_function(
    start_date="1989-12-18",
    end_date="1996-09-26",
    name_in_dag="altersgrenze_vorzeitig",
)
def altersgrenze_vorzeitig_mit_staffelung(
    demographics__geburtsjahr: int,
    ges_rente_params: dict,
) -> float:
    """Early retirement age (ERA) for Renten für Frauen.

    ERA depends on birth year and month.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    demographics__geburtsjahr
        See basic input variable :ref:`demographics__geburtsjahr <demographics__geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age

    """
    if (
        demographics__geburtsjahr
        <= ges_rente_params["altersgrenze_langj_versicherte_vorzeitig"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_langj_versicherte_vorzeitig"][
            "entry_age_old_regime"
        ]
    else:
        out = ges_rente_params["altersgrenze_langj_versicherte_vorzeitig"][
            "entry_age_new_regime"
        ]

    return out


@policy_function(start_date="1996-09-27", name_in_dag="altersgrenze_vorzeitig")
def altersgrenze_vorzeitig_ohne_staffelung_nach_96(
    demographics__geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """Early retirement age (ERA) for Rente für langjährig Versicherte.

    ERA does not depend on birth year and month.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    demographics__geburtsjahr
        See basic input variable :ref:`demographics__geburtsjahr <demographics__geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age
    """

    # TODO(@MImmesberger): Remove fake dependency (demographics__geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_langj_versicherte_vorzeitig"]


@policy_function
def grundsätzlich_anspruchsberechtigt(
    rente__altersrente__wartezeit_35_jahre_erfüllt: bool,
) -> bool:
    """Determining the eligibility for Altersrente für langjährig
    Versicherte (pension for long-term insured). Wartezeit 35 years and
    crossing the age threshold.

    Parameters
    ----------
    rente__altersrente__wartezeit_35_jahre_erfüllt
        See :func:`rente__altersrente__wartezeit_35_jahre_erfüllt`.

    Returns
    -------
    Eligibility as bool.

    """

    return rente__altersrente__wartezeit_35_jahre_erfüllt
