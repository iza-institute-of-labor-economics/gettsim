"""Pathway for women.

Revoked for birth cohorts after 1951.
"""

from _gettsim.function_types import policy_function


@policy_function(end_date="1989-12-17", leaf_name="altersgrenze")
def altersgrenze_ohne_staffelung(
    demographics__geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """Full retirement age (FRA) for women.

    FRA is the same for each birth cohort.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    demographics__geburtsjahr
        See basic input variable :ref:`demographics__geburtsjahr <demographics__geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age for women.

    """
    # TODO(@MImmesberger): Remove fake dependency (demographics__geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_für_frauen_abschlagsfrei"]


@policy_function(start_date="1989-12-18", leaf_name="altersgrenze")
def altersgrenze_mit_staffelung(
    demographics__geburtsjahr: int,
    demographics__geburtsmonat: int,
    ges_rente_params: dict,
) -> float:
    """Full retirement age (FRA) for women.

    FRA differs by birth cohort.

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
    Full retirement age for women.

    """
    if (
        demographics__geburtsjahr
        <= ges_rente_params["altersgrenze_für_frauen_abschlagsfrei"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_für_frauen_abschlagsfrei"][
            "entry_age_old_regime"
        ]
    elif (
        demographics__geburtsjahr
        >= ges_rente_params["altersgrenze_für_frauen_abschlagsfrei"][
            "min_birthyear_new_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_für_frauen_abschlagsfrei"][
            "entry_age_new_regime"
        ]
    else:
        out = ges_rente_params["altersgrenze_für_frauen_abschlagsfrei"][
            demographics__geburtsjahr
        ][demographics__geburtsmonat]

    return out


@policy_function(end_date="1989-12-17", leaf_name="altersgrenze_vorzeitig")
def altersgrenze_vorzeitig_ohne_staffelung(
    demographics__geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """Early retirement age (ERA) for Renten für Frauen.

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

    return ges_rente_params["altersgrenze_für_frauen_vorzeitig"]


@policy_function(
    start_date="1989-12-18",
    end_date="1996-09-26",
    leaf_name="altersgrenze_vorzeitig",
)
def altersgrenze_vorzeitig_mit_staffelung(
    demographics__geburtsjahr: int,
    demographics__geburtsmonat: int,
    ges_rente_params: dict,
) -> float:
    """Early retirement age (ERA) for Renten für Frauen.

    ERA depends on birth year and month.

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
    Early retirement age

    """
    if (
        demographics__geburtsjahr
        <= ges_rente_params["altersgrenze_für_frauen_vorzeitig"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_für_frauen_vorzeitig"][
            "entry_age_old_regime"
        ]
    elif (
        demographics__geburtsjahr
        >= ges_rente_params["altersgrenze_für_frauen_vorzeitig"][
            "min_birthyear_new_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_für_frauen_vorzeitig"][
            "entry_age_new_regime"
        ]
    else:
        out = ges_rente_params["altersgrenze_für_frauen_vorzeitig"][
            demographics__geburtsjahr
        ][demographics__geburtsmonat]

    return out


@policy_function(start_date="1996-09-27", leaf_name="altersgrenze_vorzeitig")
def altersgrenze_vorzeitig_ohne_staffelung_nach_1996(
    demographics__geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """Early retirement age (ERA) for Renten für Frauen.

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

    return ges_rente_params["altersgrenze_für_frauen_vorzeitig"]


@policy_function(end_date="1997-12-15", leaf_name="grundsätzlich_anspruchsberechtigt")
def grundsätzlich_anspruchsberechtigt_ohne_prüfung_geburtsjahr(
    demographics__weiblich: bool,
    sozialversicherung__rente__wartezeit_15_jahre_erfüllt: bool,
    jahre_pflichtbeiträge_ab_40: float,
    ges_rente_params: dict,
) -> bool:
    """Eligibility for Altersrente für Frauen (pension for women).

    Eligibility does not depend on birth year.

    Policy becomes inactive in 2018 because then all potential beneficiaries have
    reached the normal retirement age.

    Parameters
    ----------
    demographics__weiblich
        See basic input variable :ref:`demographics__weiblich <demographics__weiblich>`.
    sozialversicherung__rente__wartezeit_15_jahre_erfüllt
        See :func:`sozialversicherung__rente__wartezeit_15_jahre_erfüllt`
    jahre_pflichtbeiträge_ab_40
        See basic input variable :ref:`jahre_pflichtbeiträge_ab_40
        <jahre_pflichtbeiträge_ab_40>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Eligibility as bool.

    """

    out = (
        demographics__weiblich
        and sozialversicherung__rente__wartezeit_15_jahre_erfüllt
        and jahre_pflichtbeiträge_ab_40
        > ges_rente_params["rente_für_frauen_pflichtbeitr_y"]
    )

    return out


@policy_function(
    start_date="1997-12-16",
    end_date="2017-12-31",
    leaf_name="grundsätzlich_anspruchsberechtigt",
)
def grundsätzlich_anspruchsberechtigt_mit_geburtsjahr_prüfung(
    demographics__weiblich: bool,
    sozialversicherung__rente__wartezeit_15_jahre_erfüllt: bool,
    jahre_pflichtbeiträge_ab_40: float,
    demographics__geburtsjahr: int,
    ges_rente_params: dict,
) -> bool:
    """Eligibility for Altersrente für Frauen (pension for women).

    Only individuals born before a certain year are eligible.

    Wartezeit 15 years, contributions for 10 years after age 40, being a woman. Policy
    becomes inactive in 2018 because then all potential beneficiaries have reached the
    normal retirement age.

    Parameters
    ----------
    demographics__weiblich
        See basic input variable :ref:`demographics__weiblich <demographics__weiblich>`.
    sozialversicherung__rente__wartezeit_15_jahre_erfüllt
        See :func:`sozialversicherung__rente__wartezeit_15_jahre_erfüllt`
    jahre_pflichtbeiträge_ab_40
        See basic input variable :ref:`jahre_pflichtbeiträge_ab_40 <jahre_pflichtbeiträge_ab_40>`.
    demographics__geburtsjahr
        See basic input variable :ref:`demographics__geburtsjahr <demographics__geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Eligibility as bool.

    """

    out = (
        demographics__weiblich
        and sozialversicherung__rente__wartezeit_15_jahre_erfüllt
        and jahre_pflichtbeiträge_ab_40
        > ges_rente_params["rente_für_frauen_pflichtbeitr_y"]
        and demographics__geburtsjahr
        < ges_rente_params["first_birthyear_without_rente_für_frauen"]
    )

    return out
