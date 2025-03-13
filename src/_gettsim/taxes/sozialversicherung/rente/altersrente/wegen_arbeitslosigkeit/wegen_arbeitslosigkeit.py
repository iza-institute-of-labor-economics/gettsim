"""Pathway for unemployed individuals.

Revoked for birth cohorts after 1951.
"""

from _gettsim.function_types import policy_function


@policy_function(end_date="1989-12-17", leaf_name="altersgrenze")
def altersgrenze_ohne_staffelung(
    demographics__geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """Full retirement age for unemployed.

    Before the WFG (Gesetz für Wachstum und Beschäftigung) was implemented in 1997 the
    full retirement age was the same for every birth cohort.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    ges_rente_params
        See params documentation
        :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    lowest full retirement age for unemployed.

    """
    # TODO(@MImmesberger): Remove fake dependency (demographics__geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"]


@policy_function(
    start_date="1989-12-18",
    end_date="1996-07-28",
    leaf_name="altersgrenze",
)
def altersgrenze_ohne_vertrauensschutzprüfung_bis_1996(
    altersgrenze_ohne_vertrauensschutzprüfung: float,
) -> float:
    """Full retirement age for unemployed without Vertrauensschutz.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    altersgrenze_ohne_vertrauensschutzprüfung
        See :func:`altersgrenze_ohne_vertrauensschutzprüfung`.

    Returns
    -------
    Full retirement age for unemployed.

    """
    return altersgrenze_ohne_vertrauensschutzprüfung


@policy_function(
    start_date="1996-07-29",
    end_date="2009-12-31",
    leaf_name="altersgrenze",
)
def altersgrenze_mit_vertrauensschutzprüfung(
    demographics__geburtsjahr: int,
    demographics__geburtsmonat: int,
    vertrauensschutz_1997: bool,
    altersgrenze_ohne_vertrauensschutzprüfung: float,
    ges_rente_params: dict,
) -> float:
    """Full retirement age for unemployed with Vertrauensschutz.

    Full retirement age depends on birth year and month. Policy becomes inactive in 2010
    because then all potential beneficiaries have reached the normal retirement age.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    demographics__geburtsjahr
        See basic input variable :ref:`demographics__geburtsjahr <demographics__geburtsjahr>`.
    demographics__geburtsmonat
        See basic input variable :ref:`demographics__geburtsmonat <demographics__geburtsmonat>`.
    vertrauensschutz_1997
        See basic input variable :ref:`vertrauensschutz_1997 <vertrauensschutz_1997>`.
    altersgrenze_ohne_vertrauensschutzprüfung
        See :func:`altersgrenze_ohne_vertrauensschutzprüfung`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age for unemployed.

    """
    if (
        vertrauensschutz_1997
        and demographics__geburtsjahr
        <= ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"]["vertrauensschutz"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            "vertrauensschutz"
        ]["entry_age_old_regime"]

    elif vertrauensschutz_1997:
        out = ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            "vertrauensschutz"
        ][demographics__geburtsjahr][demographics__geburtsmonat]
    else:
        out = altersgrenze_ohne_vertrauensschutzprüfung

    return out


@policy_function(
    start_date="2010-01-01",
    end_date="2017-12-31",
    leaf_name="altersgrenze",
)
def altersgrenze_ohne_vertrauensschutzprüfung_ab_2010(
    altersgrenze_ohne_vertrauensschutzprüfung: float,
) -> float:
    """Full retirement age for unemployed without Vertrauensschutz.

    Full retirement age depends on birth year and month. Policy becomes inactive in 2017
    because then all potential beneficiaries have reached the normal retirement age.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    altersgrenze_ohne_vertrauensschutzprüfung
        See :func:`altersgrenze_ohne_vertrauensschutzprüfung`.

    Returns
    -------
    Full retirement age for unemployed.

    """
    return altersgrenze_ohne_vertrauensschutzprüfung


@policy_function(end_date="1989-12-17", leaf_name="altersgrenze_vorzeitig")
def altersgrenze_vorzeitig_ohne_staffelung(
    demographics__geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """Early retirement age of pension for unemployed.

    Early retirement age does not depend on birth year and month.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    ges_rente_params
        See params documentation
        :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age for unemployed.

    """

    # TODO(@MImmesberger): Remove fake dependency (demographics__geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_arbeitsl_vorzeitig"]


@policy_function(
    start_date="1989-12-18",
    end_date="1996-07-28",
    leaf_name="altersgrenze_vorzeitig",
)
def altersgrenze_vorzeitig_ohne_vertrauensschutz_bis_1996_07(
    altersgrenze_vorzeitig_ohne_vertrauensschutzprüfung: float,
) -> float:
    """Early retirement age of pension for unemployed.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    altersgrenze_vorzeitig_ohne_vertrauensschutzprüfung
        See :func:`altersgrenze_vorzeitig_ohne_vertrauensschutzprüfung`.

    Returns
    -------
    Early retirement age for unemployed.
    """

    return altersgrenze_vorzeitig_ohne_vertrauensschutzprüfung


@policy_function(
    start_date="1996-07-29",
    end_date="1996-09-26",
    leaf_name="altersgrenze_vorzeitig",
)
def altersgrenze_vorzeitig_mit_vertrauensschutz_ab_1996_07_bis_1996_09(
    vertrauensschutz_1997: bool,
    altersgrenze_vorzeitig_ohne_vertrauensschutzprüfung: float,
    ges_rente_params: dict,
) -> float:
    """Early retirement age of pension for unemployed.

    Includes Vertrauensschutz rules implemented from July to September 1996.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------

    vertrauensschutz_2006
        See basic input variable :ref:`vertrauensschutz_2006 <vertrauensschutz_2006>`.
    altersgrenze_vorzeitig_ohne_vertrauensschutzprüfung
        See :func:`altersgrenze_vorzeitig_ohne_vertrauensschutzprüfung`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age for unemployed.
    """

    if vertrauensschutz_1997:
        arbeitsl_vorzeitig = ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            "vertrauensschutz"
        ]
    else:
        arbeitsl_vorzeitig = altersgrenze_vorzeitig_ohne_vertrauensschutzprüfung

    return arbeitsl_vorzeitig


@policy_function(
    start_date="1996-09-27",
    end_date="2004-07-25",
    leaf_name="altersgrenze_vorzeitig",
)
def altersgrenze_vorzeitig_ohne_staffelung_ab_1996_09(
    demographics__geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """Early retirement age of pension for unemployed.

    Early retirement age does not depend on birth year and month.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    ges_rente_params
        See params documentation
        :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age for unemployed.

    """

    # TODO(@MImmesberger): Remove fake dependency (demographics__geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_arbeitsl_vorzeitig"]


@policy_function(
    start_date="2004-07-26",
    end_date="2017-12-31",
    leaf_name="altersgrenze_vorzeitig",
)
def ges_rente_arbeitsl_vorzeitig_mit_vertrauenss_ab_2006(
    vertrauensschutz_2006: bool,
    altersgrenze_vorzeitig_ohne_vertrauensschutzprüfung: float,
    ges_rente_params: dict,
) -> float:
    """Early retirement age of pension for unemployed.

    Includes Vertrauensschutz rules implemented in 2006. Policy becomes inactive in 2018
    because then all potential beneficiaries have reached the normal retirement age.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    vertrauensschutz_2006
        See basic input variable :ref:`vertrauensschutz_2006
        <vertrauensschutz_2006>`.
    altersgrenze_vorzeitig_ohne_vertrauensschutzprüfung
        See :func:`altersgrenze_vorzeitig_ohne_vertrauensschutzprüfung`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age for unemployed.
    """

    if vertrauensschutz_2006:
        arbeitsl_vorzeitig = ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            "vertrauensschutz"
        ]
    else:
        arbeitsl_vorzeitig = altersgrenze_vorzeitig_ohne_vertrauensschutzprüfung

    return arbeitsl_vorzeitig


@policy_function(end_date="2017-12-31")
def altersgrenze_ohne_vertrauensschutzprüfung(
    demographics__geburtsjahr: int,
    demographics__geburtsmonat: int,
    ges_rente_params: dict,
) -> float:
    """Full retirement age for unemployed without Vertrauensschutz.

    Full retirement age depends on birth year and month.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    demographics__geburtsjahr
        See basic input variable :ref:`demographics__geburtsjahr <demographics__geburtsjahr>`.
    demographics__geburtsmonat
        See basic input variable :ref:`demographics__geburtsmonat <demographics__geburtsmonat>`.
    ges_rente_params
        See params documentation
        :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age for unemployed.

    """
    if (
        demographics__geburtsjahr
        <= ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            "entry_age_old_regime"
        ]
    elif (
        demographics__geburtsjahr
        >= ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            "min_birthyear_new_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            "entry_age_new_regime"
        ]
    else:
        out = ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            demographics__geburtsjahr
        ][demographics__geburtsmonat]

    return out


@policy_function(end_date="2017-12-31")
def altersgrenze_vorzeitig_ohne_vertrauensschutzprüfung(
    demographics__geburtsjahr: int,
    demographics__geburtsmonat: int,
    ges_rente_params: dict,
) -> float:
    """Early retirement age of pension for unemployed without Vertrauensschutz.

    Relevant if the early retirement age depends on birth year and month.

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
    Early retirement age for unemployed.
    """

    if (
        demographics__geburtsjahr
        <= ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            "max_birthyear_old_regime"
        ]
    ):
        arbeitsl_vorzeitig = ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            "entry_age_old_regime"
        ]
    elif (
        demographics__geburtsjahr
        >= ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            "min_birthyear_new_regime"
        ]
    ):
        arbeitsl_vorzeitig = ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            "entry_age_new_regime"
        ]
    else:
        arbeitsl_vorzeitig = ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            demographics__geburtsjahr
        ][demographics__geburtsmonat]

    return arbeitsl_vorzeitig


@policy_function(end_date="2007-04-29", leaf_name="grundsätzlich_anspruchsberechtigt")
def grundsätzlich_anspruchsberechtigt_bis_2007(
    arbeitslos_für_1_jahr_nach_alter_58_ein_halb: bool,
    sozialversicherung__rente__wartezeit_15_jahre_erfüllt: bool,
    pflichtbeitrag_in_8_von_10_jahren: bool,
) -> bool:
    """Eligibility for Altersrente für Arbeitslose (pension for unemployed).

    Wartezeit 15 years, 8 contribution years past 10 years, being unemployed for at
    least 1 year after age 58 and 6 months. The person is also required to be
    unemployed at the time of claiming the pension. As there are no restrictions
    regarding voluntary unemployment this requirement may be viewed as always satisfied
    and is therefore not included when checking for eligibility.

    Parameters
    ----------
    arbeitslos_für_1_jahr_nach_alter_58_ein_halb
        See basic input variable
        :ref:`arbeitslos_für_1_jahr_nach_alter_58_ein_halb <arbeitslos_für_1_jahr_nach_alter_58_ein_halb>`.
    sozialversicherung__rente__wartezeit_15_jahre_erfüllt
        See :func:`sozialversicherung__rente__wartezeit_15_jahre_erfüllt`
    pflichtbeitrag_in_8_von_10_jahren
        See basic input variable :ref:`pflichtbeitrag_in_8_von_10_jahren <pflichtbeitrag_in_8_von_10_jahren>`.

    Returns
    -------
    Eligibility as bool.

    """

    out = (
        arbeitslos_für_1_jahr_nach_alter_58_ein_halb
        and sozialversicherung__rente__wartezeit_15_jahre_erfüllt
        and pflichtbeitrag_in_8_von_10_jahren
    )

    return out


@policy_function(
    start_date="2007-04-30",
    end_date="2017-12-31",
    leaf_name="grundsätzlich_anspruchsberechtigt",
)
def grundsätzlich_anspruchsberechtigt_ab_2007(
    arbeitslos_für_1_jahr_nach_alter_58_ein_halb: bool,
    sozialversicherung__rente__wartezeit_15_jahre_erfüllt: bool,
    pflichtbeitrag_in_8_von_10_jahren: bool,
    demographics__geburtsjahr: int,
    ges_rente_params: dict,
) -> bool:
    """Eligibility for Altersrente für Arbeitslose (pension for unemployed).

    Wartezeit 15 years, 8 contributionyears past 10 years, being at least 1 year
    unemployed after age 58 and 6 months and being born before 1952. The person is also
    required to be unemployed at the time of claiming the pension. As there are no
    restrictions regarding voluntary unemployment this requirement may be viewed as
    always satisfied and is therefore not included when checking for eligibility. Policy
    becomes inactive in 2018 because then all potential beneficiaries have reached the
    normal retirement age.

    Parameters
    ----------
    arbeitslos_für_1_jahr_nach_alter_58_ein_halb
        See basic input variable :ref:`arbeitslos_für_1_jahr_nach_alter_58_ein_halb <arbeitslos_für_1_jahr_nach_alter_58_ein_halb>`.
    sozialversicherung__rente__wartezeit_15_jahre_erfüllt
        See :func:`sozialversicherung__rente__wartezeit_15_jahre_erfüllt`
    pflichtbeitrag_in_8_von_10_jahren
        See basic input variable :ref:`pflichtbeitrag_in_8_von_10_jahren <pflichtbeitrag_in_8_von_10_jahren>`.
    demographics__geburtsjahr
        See :func:`demographics__geburtsjahr`
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Eligibility as bool.

    """

    out = (
        arbeitslos_für_1_jahr_nach_alter_58_ein_halb
        and sozialversicherung__rente__wartezeit_15_jahre_erfüllt
        and pflichtbeitrag_in_8_von_10_jahren
        and demographics__geburtsjahr
        < ges_rente_params["first_birthyear_without_rente_für_arbeitsl"]
    )

    return out
