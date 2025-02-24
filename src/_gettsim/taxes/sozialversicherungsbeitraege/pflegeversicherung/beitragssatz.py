"""Contribution rate to public long-term care insurance."""

from _gettsim.functions.policy_function import policy_function


@policy_function(
    start_date="1995-01-01",
    end_date="2004-12-31",
    name_in_dag="beitragssatz",
)
def beitragssatz_ohne_zusatz_fuer_kinderlose(
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
    name_in_dag="beitragssatz",
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


@policy_function(start_date="2023-07-01", name_in_dag="beitragssatz")
def beitragssatz_mit_kinder_abschlag(
    ges_pflegev_anz_kinder_bis_24: int,
    zusatzbetrag_kinderlos: bool,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's long-term care insurance contribution rate.

    Since July 2023, the contribution rate is reduced for individuals with children
    younger than 25.

    Parameters
    ----------
    ges_pflegev_anz_kinder_bis_24: int,
        See :func:`ges_pflegev_anz_kinder_bis_24`.
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
    if ges_pflegev_anz_kinder_bis_24 >= 2:
        out -= sozialv_beitr_params["beitr_satz"]["ges_pflegev"][
            "abschlag_kinder"
        ] * min(ges_pflegev_anz_kinder_bis_24 - 1, 4)

    return out


@policy_function(start_date="2005-01-01")
def zusatzbetrag_kinderlos(
    ges_pflegev_hat_kinder: bool,
    alter: int,
    sozialv_beitr_params: dict,
) -> bool:
    """Whether additional care insurance contribution for childless individuals applies.

    Not relevant before 2005 because the contribution rate was independent of the number
    of children.

    Parameters
    ----------
    ges_pflegev_hat_kinder
        See basic input variable :ref:`ges_pflegev_hat_kinder <ges_pflegev_hat_kinder>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    sozialv_beitr_params: dict,
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    mindestalter = sozialv_beitr_params["ges_pflegev_zusatz_kinderlos_mindestalter"]
    return (not ges_pflegev_hat_kinder) and alter >= mindestalter
