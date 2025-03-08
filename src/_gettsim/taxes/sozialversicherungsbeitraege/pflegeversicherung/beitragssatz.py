"""Contribution rate to public long-term care insurance."""

from _gettsim.functions.policy_function import policy_function


@policy_function(
    start_date="1995-01-01",
    end_date="2004-12-31",
    leaf_name="beitragssatz",
)
def beitragssatz_ohne_zusatz_für_kinderlose(
    sozialv_beitr_params: dict,
) -> float:
    """Employee's long-term care insurance contribution rate.

    Before 2005, the contribution rate was independent of the number of children.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """

    return sozialv_beitr_params["beitr_satz"]["ges_pflegev"]


@policy_function(
    start_date="2005-01-01",
    end_date="2023-06-30",
    leaf_name="beitragssatz",
)
def beitragssatz_zusatz_kinderlos_dummy(
    zusatzbetrag_kinderlos: bool,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's long-term care insurance contribution rate.

    Since 2005, the contribution rate is increased for childless individuals.

    Parameters
    ----------
    zusatzbetrag_kinderlos
        See :func:`zusatzbetrag_kinderlos`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    out = sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]

    # Add additional contribution for childless individuals
    if zusatzbetrag_kinderlos:
        out += sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]

    return out


@policy_function(start_date="2023-07-01", leaf_name="beitragssatz")
def beitragssatz_mit_kinder_abschlag(
    anzahl_kinder_bis_24: int,
    zusatzbetrag_kinderlos: bool,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's long-term care insurance contribution rate.

    Since July 2023, the contribution rate is reduced for individuals with children
    younger than 25.

    Parameters
    ----------
    anzahl_kinder_bis_24: int,
        See :func:`anzahl_kinder_bis_24`.
    zusatzbetrag_kinderlos
        See :func:`zusatzbetrag_kinderlos`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    out = sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]

    # Add additional contribution for childless individuals
    if zusatzbetrag_kinderlos:
        out += sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]

    # Reduced contribution for individuals with two or more children under 25
    if anzahl_kinder_bis_24 >= 2:
        out -= sozialv_beitr_params["beitr_satz"]["ges_pflegev"][
            "abschlag_kinder"
        ] * min(anzahl_kinder_bis_24 - 1, 4)

    return out


@policy_function(start_date="2005-01-01")
def zusatzbetrag_kinderlos(
    hat_kinder: bool,
    demographics__alter: int,
    sozialv_beitr_params: dict,
) -> bool:
    """Whether additional care insurance contribution for childless individuals applies.

    Not relevant before 2005 because the contribution rate was independent of the number
    of children.

    Parameters
    ----------
    hat_kinder
        See basic input variable :ref:`hat_kinder <hat_kinder>`.
    demographics__alter
        See basic input variable :ref:`demographics__alter <demographics__alter>`.
    sozialv_beitr_params: dict,
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    mindestalter = sozialv_beitr_params["ges_pflegev_zusatz_kinderlos_mindestalter"]
    return (not hat_kinder) and demographics__alter >= mindestalter


@policy_function()
def anzahl_kinder_bis_24(
    demographic_vars__anzahl_kinder_bis_24_elternteil_1: int,
    demographic_vars__anzahl_kinder_bis_24_elternteil_2: int,
) -> int:
    """Number of children under 25 years of age.
    Parameters
    ----------
    demographic_vars__anzahl_kinder_bis_24_elternteil_1
        See :func:`demographic_vars__anzahl_kinder_bis_24_elternteil_1`.
    demographic_vars__anzahl_kinder_bis_24_elternteil_2
        See :func:`demographic_vars__anzahl_kinder_bis_24_elternteil_2`.

    Returns
    -------
    """
    return (
        demographic_vars__anzahl_kinder_bis_24_elternteil_1
        + demographic_vars__anzahl_kinder_bis_24_elternteil_2
    )
