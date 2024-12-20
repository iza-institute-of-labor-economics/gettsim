"""Pathway for unemployed individuals.

Revoked for birth cohorts after 1951.
"""

from _gettsim.shared import policy_info


@policy_info(end_date="1989-12-17", name_in_dag="_ges_rente_arbeitsl_altersgrenze")
def _ges_rente_arbeitsl_altersgrenze_ohne_staffelung(
    geburtsjahr: int,  # noqa: ARG001
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
    # TODO(@MImmesberger): Remove fake dependency (geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"]


@policy_info(
    start_date="1989-12-18",
    end_date="1996-07-28",
    name_in_dag="_ges_rente_arbeitsl_altersgrenze",
)
def _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung_bis_1996(
    _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung: float,
) -> float:
    """Full retirement age for unemployed without Vertrauensschutz.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung
        See :func:`_ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung`.

    Returns
    -------
    Full retirement age for unemployed.

    """
    return _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung


@policy_info(
    start_date="1996-07-29",
    end_date="2009-12-31",
    name_in_dag="_ges_rente_arbeitsl_altersgrenze",
)
def _ges_rente_arbeitsl_altersgrenze_mit_vertrauensschutzprüfung(
    geburtsjahr: int,
    geburtsmonat: int,
    vertra_arbeitsl_1997: bool,
    _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung: float,
    ges_rente_params: dict,
) -> float:
    """Full retirement age for unemployed with Vertrauensschutz.

    Full retirement age depends on birth year and month. Policy becomes inactive in 2010
    because then all potential beneficiaries have reached the normal retirement age.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    vertra_arbeitsl_1997
        See basic input variable :ref:`vertra_arbeitsl_1997 <vertra_arbeitsl_1997>`.
    _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung
        See :func:`_ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age for unemployed.

    """
    if (
        vertra_arbeitsl_1997
        and geburtsjahr
        <= ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"]["vertrauensschutz"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            "vertrauensschutz"
        ]["entry_age_old_regime"]

    elif vertra_arbeitsl_1997:
        out = ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            "vertrauensschutz"
        ][geburtsjahr][geburtsmonat]
    else:
        out = _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung

    return out


@policy_info(
    start_date="2010-01-01",
    end_date="2017-12-31",
    name_in_dag="_ges_rente_arbeitsl_altersgrenze",
)
def _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung_ab_2010(
    _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung: float,
) -> float:
    """Full retirement age for unemployed without Vertrauensschutz.

    Full retirement age depends on birth year and month. Policy becomes inactive in 2017
    because then all potential beneficiaries have reached the normal retirement age.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung
        See :func:`_ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung`.

    Returns
    -------
    Full retirement age for unemployed.

    """
    return _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung


@policy_info(end_date="1989-12-17", name_in_dag="_ges_rente_arbeitsl_vorzeitig")
def _ges_rente_arbeitsl_vorzeitig_ohne_staffelung(
    geburtsjahr: int,  # noqa: ARG001
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

    # TODO(@MImmesberger): Remove fake dependency (geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_arbeitsl_vorzeitig"]


@policy_info(
    start_date="1989-12-18",
    end_date="1996-07-28",
    name_in_dag="_ges_rente_arbeitsl_vorzeitig",
)
def ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss_vor_1996(
    _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss: float,
) -> float:
    """Early retirement age of pension for unemployed.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss
        See :func:`_ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss`.

    Returns
    -------
    Early retirement age for unemployed.
    """

    return _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss


@policy_info(
    start_date="1996-07-29",
    end_date="1996-09-26",
    name_in_dag="_ges_rente_arbeitsl_vorzeitig",
)
def ges_rente_arbeitsl_vorzeitig_mit_vertrauenss_1996(
    vertra_arbeitsl_1997: bool,
    _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss: float,
    ges_rente_params: dict,
) -> float:
    """Early retirement age of pension for unemployed.

    Includes Vertrauensschutz rules implemented from July to September 1996.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------

    vertra_arbeitsl_2006
        See basic input variable :ref:`vertra_arbeitsl_2006 <vertra_arbeitsl_2006>`.
    _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss
        See :func:`_ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age for unemployed.
    """

    if vertra_arbeitsl_1997:
        arbeitsl_vorzeitig = ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            "vertrauensschutz"
        ]
    else:
        arbeitsl_vorzeitig = _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss

    return arbeitsl_vorzeitig


@policy_info(
    start_date="1996-09-27",
    end_date="2004-07-25",
    name_in_dag="_ges_rente_arbeitsl_vorzeitig",
)
def _ges_rente_arbeitsl_vorzeitig_ohne_staffelung_nach_1997(
    geburtsjahr: int,  # noqa: ARG001
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

    # TODO(@MImmesberger): Remove fake dependency (geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_arbeitsl_vorzeitig"]


@policy_info(
    start_date="2004-07-26",
    end_date="2017-12-31",
    name_in_dag="_ges_rente_arbeitsl_vorzeitig",
)
def ges_rente_arbeitsl_vorzeitig_mit_vertrauenss_ab_2006(
    vertra_arbeitsl_2006: bool,
    _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss: float,
    ges_rente_params: dict,
) -> float:
    """Early retirement age of pension for unemployed.

    Includes Vertrauensschutz rules implemented in 2006. Policy becomes inactive in 2018
    because then all potential beneficiaries have reached the normal retirement age.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    vertra_arbeitsl_2006
        See basic input variable :ref:`vertra_arbeitsl_2006
        <vertra_arbeitsl_2006>`.
    _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss
        See :func:`_ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age for unemployed.
    """

    if vertra_arbeitsl_2006:
        arbeitsl_vorzeitig = ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            "vertrauensschutz"
        ]
    else:
        arbeitsl_vorzeitig = _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss

    return arbeitsl_vorzeitig


@policy_info(end_date="2017-12-31")
def _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung(
    geburtsjahr: int,
    geburtsmonat: int,
    ges_rente_params: dict,
) -> float:
    """Full retirement age for unemployed without Vertrauensschutz.

    Full retirement age depends on birth year and month.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    ges_rente_params
        See params documentation
        :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age for unemployed.

    """
    if (
        geburtsjahr
        <= ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            "entry_age_old_regime"
        ]
    elif (
        geburtsjahr
        >= ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            "min_birthyear_new_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            "entry_age_new_regime"
        ]
    else:
        out = ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][geburtsjahr][
            geburtsmonat
        ]

    return out


@policy_info(end_date="2017-12-31")
def _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss(
    geburtsjahr: int,
    geburtsmonat: int,
    ges_rente_params: dict,
) -> float:
    """Early retirement age of pension for unemployed without Vertrauensschutz.

    Relevant if the early retirement age depends on birth year and month.

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
    Early retirement age for unemployed.
    """

    if (
        geburtsjahr
        <= ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            "max_birthyear_old_regime"
        ]
    ):
        arbeitsl_vorzeitig = ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            "entry_age_old_regime"
        ]
    elif (
        geburtsjahr
        >= ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            "min_birthyear_new_regime"
        ]
    ):
        arbeitsl_vorzeitig = ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            "entry_age_new_regime"
        ]
    else:
        arbeitsl_vorzeitig = ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            geburtsjahr
        ][geburtsmonat]

    return arbeitsl_vorzeitig


@policy_info(end_date="2007-04-29", name_in_dag="ges_rente_vorauss_arbeitsl")
def _ges_rente_vorauss_arbeitsl_ohne_2007_reform(
    arbeitsl_1y_past_585: bool,
    ges_rente_wartezeit_15: bool,
    pflichtbeitr_8_in_10: bool,
) -> bool:
    """Eligibility for Altersrente für Arbeitslose (pension for unemployed).

    Wartezeit 15 years, 8 contribution years past 10 years, being unemployed for at
    least 1 year after age 58 and 6 months. The person is also required to be
    unemployed at the time of claiming the pension. As there are no restrictions
    regarding voluntary unemployment this requirement may be viewed as always satisfied
    and is therefore not included when checking for eligibility.

    Parameters
    ----------
    arbeitsl_1y_past_585
        See basic input variable
        :ref:`arbeitsl_1y_past_585 <arbeitsl_1y_past_585>`.
    ges_rente_wartezeit_15
        See :func:`ges_rente_wartezeit_15`
    pflichtbeitr_8_in_10
        See basic input variable :ref:`pflichtbeitr_8_in_10 <pflichtbeitr_8_in_10>`.

    Returns
    -------
    Eligibility as bool.

    """

    out = arbeitsl_1y_past_585 and ges_rente_wartezeit_15 and pflichtbeitr_8_in_10

    return out


@policy_info(
    start_date="2007-04-30",
    end_date="2017-12-31",
    name_in_dag="ges_rente_vorauss_arbeitsl",
)
def _ges_rente_vorauss_arbeitsl_mit_2007_reform(
    arbeitsl_1y_past_585: bool,
    ges_rente_wartezeit_15: bool,
    pflichtbeitr_8_in_10: bool,
    geburtsjahr: int,
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
    arbeitsl_1y_past_585
        See basic input variable :ref:`arbeitsl_1y_past_585 <arbeitsl_1y_past_585>`.
    ges_rente_wartezeit_15
        See :func:`ges_rente_wartezeit_15`
    pflichtbeitr_8_in_10
        See basic input variable :ref:`pflichtbeitr_8_in_10 <pflichtbeitr_8_in_10>`.
    geburtsjahr
        See :func:`geburtsjahr`
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Eligibility as bool.

    """

    out = (
        arbeitsl_1y_past_585
        and ges_rente_wartezeit_15
        and pflichtbeitr_8_in_10
        and geburtsjahr < ges_rente_params["first_birthyear_without_rente_für_arbeitsl"]
    )

    return out
