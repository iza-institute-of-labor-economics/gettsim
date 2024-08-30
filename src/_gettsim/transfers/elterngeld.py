"""This module provides functions to compute parental leave benefits (Elterngeld)."""

from _gettsim.shared import policy_info

aggregate_by_group_elterngeld = {
    "kind_anspruchsberechtigt_fg": {
        "source_col": "kind_anspruchsberechtigt",
        "aggr": "any",
    },
    "elterngeld_anzahl_claims_fg": {
        "source_col": "elterngeld_claimed",
        "aggr": "sum",
    },
}


@policy_info(start_date="2011-01-01")
def elterngeld_m(
    elterngeld_anspruchsbedingungen_erfüllt: bool,
    elterngeld_anspruchshöhe_m: float,
) -> float:
    """Parental leave benefit (Elterngeld).

    Parameters
    ----------
    elterngeld_anspruchsbedingungen_erfüllt
        See :func:`elterngeld_anspruchsbedingungen_erfüllt`.
    elterngeld_anspruchshöhe_m
        See :func:`elterngeld_anspruchshöhe_m`.

    Returns
    -------

    """
    if elterngeld_anspruchsbedingungen_erfüllt:
        out = elterngeld_anspruchshöhe_m
    else:
        out = 0.0
    return out


@policy_info(end_date="2010-12-31", name_in_dag="elterngeld_m")
def eltergeld_not_implemented() -> float:
    raise NotImplementedError("Elterngeld is not implemented prior to 2011.")


def elterngeld_anspruchshöhe_m(
    elterngeld_basisbetrag_m: float,
    elterngeld_geschwisterbonus_m: float,
    elterngeld_mehrlingsbonus_m: float,
    elterngeld_params: dict,
) -> float:
    """Elterngeld before checking eligibility.

    Parameters
    ----------
    elterngeld_basisbetrag_m
        See :func:`elterngeld_basisbetrag_m`.
    elterngeld_geschwisterbonus_m
        See :func:`elterngeld_geschwisterbonus_m`.
    elterngeld_mehrlingsbonus_m
        See :func:`elterngeld_mehrlingsbonus_m`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return (
        min(
            max(
                elterngeld_basisbetrag_m,
                elterngeld_params["mindestbetrag"],
            ),
            elterngeld_params["höchstbetrag"],
        )
        + elterngeld_geschwisterbonus_m
        + elterngeld_mehrlingsbonus_m
    )


def elterngeld_anspruchsbedingungen_erfüllt(  # noqa: PLR0913
    elterngeld_claimed: bool,
    arbeitsstunden_w: float,
    kind_anspruchsberechtigt_fg: bool,
    vorjahr_einkommen_unter_bezugsgrenze: bool,
    monate_elterngeldbezug_unter_grenze_fg: bool,
    elterngeld_params: dict,
) -> bool:
    """Individual is eligible to receive Elterngeld.

    Parameters
    ----------
    elterngeld_claimed
        See basic input variable :ref:`elterngeld_claimed <elterngeld_claimed>`.
    arbeitsstunden_w
        See basic input variable :ref:`arbeitsstunden_w <arbeitsstunden_w>`.
    kind_anspruchsberechtigt_fg
        See :func:`kind_anspruchsberechtigt_fg`.
    vorjahr_einkommen_unter_bezugsgrenze
        See :func:`vorjahr_einkommen_unter_bezugsgrenze`.
    monate_elterngeldbezug_unter_grenze_fg
        See :func:`monate_elterngeldbezug_unter_grenze_fg`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return (
        elterngeld_claimed
        and arbeitsstunden_w <= elterngeld_params["max_arbeitsstunden_w"]
        and vorjahr_einkommen_unter_bezugsgrenze
        and kind_anspruchsberechtigt_fg
        and monate_elterngeldbezug_unter_grenze_fg
    )


def monate_elterngeldbezug_unter_grenze_fg(
    monate_elterngeldbezug_fg: int,
    alleinerz: bool,
    elterngeld_anzahl_claims_fg: int,
    elterngeld_params: dict,
) -> bool:
    """Elterngeld has been claimed for less than the maximum number of months in the
    past.

    Parameters
    ----------
    monate_elterngeldbezug_fg
        See :func:`monate_elterngeldbezug_fg`.
    alleinerz
        See basic input variable :ref:`alleinerz <alleinerz>`.
    elterngeld_anzahl_claims_fg
        See :func:`elterngeld_anzahl_claims_fg`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    if alleinerz:
        out = monate_elterngeldbezug_fg <= elterngeld_params["max_monate_ind"]
    elif elterngeld_anzahl_claims_fg > 1:
        out = monate_elterngeldbezug_fg + 1 <= elterngeld_params["max_monate_paar"]
    else:
        out = monate_elterngeldbezug_fg <= elterngeld_params["max_monate_paar"]
    return out


def vorjahr_einkommen_unter_bezugsgrenze(
    alleinerz: bool,
    elterngeld_zu_verst_eink_vor_geburt_sn: float,
    elterngeld_params: dict,
) -> bool:
    """Income before birth is below income threshold for Elterngeld.

    Parameters
    ----------
    alleinerz
        See basic input variable :ref:`alleinerz <alleinerz>`.
    elterngeld_zu_verst
        See :func:`elterngeld_zu_verst`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    if alleinerz:
        out = (
            elterngeld_zu_verst_eink_vor_geburt_sn
            <= elterngeld_params["max_eink_vorj"]["single"]
        )
    else:
        out = (
            elterngeld_zu_verst_eink_vor_geburt_sn
            <= elterngeld_params["max_eink_vorj"]["paar"]
        )
    return out


def kind_anspruchsberechtigt(
    alter: int,
    elterngeld_params: dict,
) -> bool:
    """Child is young enough to give rise to Elterngeld claim.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return alter <= elterngeld_params["max_monate_paar"]


def elterngeld_basisbetrag_m(
    elterngeld_nettoeinkommen_vorjahr_m: float,
    elterngeld_lohnersatzanteil: float,
    elterngeld_anrechenbares_nettoeinkommen_m: float,
    elterngeld_params: dict,
) -> float:
    """Base parental leave benefit without accounting for floor and ceiling.

    Parameters
    ----------
    elterngeld_nettoeinkommen_vorjahr_m
        See basic input variable :ref:`elterngeld_nettoeinkommen_vorjahr_m
        <elterngeld_nettoeinkommen_vorjahr_m>`.
    elterngeld_lohnersatzanteil
        See :func:`elterngeld_lohnersatzanteil`.
    elterngeld_anrechenbares_nettoeinkommen_m
        See :func:`elterngeld_anrechenbares_nettoeinkommen_m`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    berücksichtigtes_einkommen = min(
        elterngeld_nettoeinkommen_vorjahr_m,
        elterngeld_params["max_berücksichtiges_einkommen"],
    )
    return (
        berücksichtigtes_einkommen - elterngeld_anrechenbares_nettoeinkommen_m
    ) * elterngeld_lohnersatzanteil


@policy_info(start_date="2011-01-01")
def elterngeld_lohnersatzanteil(
    elterngeld_nettoeinkommen_vorjahr_m: float, elterngeld_params: dict
) -> float:
    """Replacement rate of Elterngeld (before applying floor and ceiling rules).

    According to § 2 (2) BEEG the percentage increases below the first step and
    decreases above the second step until prozent_minimum.

    Parameters
    ----------
    elterngeld_nettoeinkommen_vorjahr_m
        See basic input variable
        :ref:`elterngeld_nettoeinkommen_vorjahr_m<elterngeld_nettoeinkommen_vorjahr_m>`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
    Returns
    -------

    """

    # Higher replacement rate if considered income is below a threshold
    if (
        elterngeld_nettoeinkommen_vorjahr_m
        < elterngeld_params["nettoeinkommen_stufen"]["lower_threshold"]
    ):
        out = (
            elterngeld_params["nettoeinkommen_stufen"]["lower_threshold"]
            - elterngeld_nettoeinkommen_vorjahr_m
        ) / elterngeld_params["eink_schritt_korrektur"] * elterngeld_params[
            "prozent_korrektur"
        ] + elterngeld_params[
            "faktor"
        ]

    # Lower replacement rate if considered income is above a threshold
    elif (
        elterngeld_nettoeinkommen_vorjahr_m
        > elterngeld_params["nettoeinkommen_stufen"]["upper_threshold"]
    ):
        # Replacement rate is only lowered up to a specific value
        out = max(
            elterngeld_params["faktor"]
            - (
                elterngeld_nettoeinkommen_vorjahr_m
                - elterngeld_params["nettoeinkommen_stufen"]["upper_threshold"]
            )
            / elterngeld_params["eink_schritt_korrektur"],
            elterngeld_params["prozent_minimum"],
        )
    else:
        out = elterngeld_params["faktor"]

    return out


def elterngeld_geschwisterbonus_m(
    elterngeld_basisbetrag_m: float,
    geschwisterbonus_anspruchsberechtigt_fg: bool,
    elterngeld_params: dict,
) -> float:
    """Elterngeld bonus for (older) siblings.

    According to § 2a parents of siblings get a bonus.

    Parameters
    ----------
    elterngeld_basisbetrag_m
        See :func:`elterngeld_basisbetrag_m`.
    geschwisterbonus_anspruchsberechtigt_fg
        See :func:`geschwisterbonus_anspruchsberechtigt_fg`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    if geschwisterbonus_anspruchsberechtigt_fg:
        out = max(
            elterngeld_params["geschwisterbonus_aufschlag"] * elterngeld_basisbetrag_m,
            elterngeld_params["geschwisterbonus_minimum"],
        )
    else:
        out = 0.0
    return out


def elterngeld_mehrlingsbonus_m(
    _elterngeld_anz_mehrlinge_fg: int, elterngeld_params: dict
) -> float:
    """Elterngeld bonus for multiples.

    Parameters
    ----------
    _elterngeld_anz_mehrlinge_fg
        See :func:`_elterngeld_anz_mehrlinge_fg`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return _elterngeld_anz_mehrlinge_fg * elterngeld_params["mehrlingbonus"]


def geschwisterbonus_anspruchsberechtigt_fg(
    anz_kinder_bis_2_fg: int,
    anz_kinder_bis_5_fg: int,
    elterngeld_params: dict,
) -> bool:
    """Siblings that give rise to Elterngeld siblings bonus.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    geschwister_unter_3 = (
        anz_kinder_bis_2_fg >= elterngeld_params["geschwisterbonus_altersgrenzen"][3]
    )
    geschwister_unter_6 = (
        anz_kinder_bis_5_fg >= elterngeld_params["geschwisterbonus_altersgrenzen"][6]
    )

    return geschwister_unter_3 or geschwister_unter_6


def _elterngeld_anz_mehrlinge_fg(
    anz_mehrlinge_jüngstes_kind_fg: int,
) -> int:
    """Number of multiples of the youngest child.

    Parameters
    ----------
    anz_mehrlinge_jüngstes_kind_fg
        See :func:`anz_mehrlinge_jüngstes_kind_fg`.

    Returns
    -------

    """
    out = anz_mehrlinge_jüngstes_kind_fg - 1
    return out


def elterngeld_anrechenbares_nettoeinkommen_m(
    bruttolohn_m: float,
    lohnst_m: float,
    soli_st_lohnst_m: float,
) -> float:
    """Income that reduces the Elterngeld claim.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    lohnst_m
        See :func:`lohnst_m`.
    soli_st_lohnst_m
        See :func:`soli_st_lohnst_m`.

    Returns
    -------

    """
    return bruttolohn_m - lohnst_m - soli_st_lohnst_m


def anrechenbares_elterngeld_m(
    elterngeld_m: float,
    _elterngeld_anz_mehrlinge_fg: int,
    elterngeld_params: dict,
) -> float:
    """Elterngeld that can be considered as income for other transfers.

    Relevant for Wohngeld and Grundsicherung im Alter.

    For Arbeitslosengeld II / Bürgergeld as well as Kinderzuschlag the whole amount of
    Elterngeld is considered as income, except for the case in which the parents still
    worked right before they had children. See:
    https://www.kindergeld.org/elterngeld-einkommen/

    Parameters
    ----------
    elterngeld_m
        See :func:`elterngeld_m`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
    _elterngeld_anz_mehrlinge_fg
        See :func:`_elterngeld_anz_mehrlinge_fg`.

    Returns
    -------

    """
    out = max(
        elterngeld_m
        - ((1 + _elterngeld_anz_mehrlinge_fg) * elterngeld_params["mindestbetrag"]),
        0,
    )
    return out


# elterngeld_zu_verst_eink_vor_geburt_sn


def elterngeld_nettolohn_approximation_m(
    bruttolohn_m: float,
    lohnst_m: float,
    soli_st_lohnst_m: float,
    elterngeld_params: dict,
) -> float:
    """Approximation of net wage used to calculate Elterngeld.

    This target can be used as an input in another GETTSIM call to compute Elterngeld.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    lohnst_m
        See :func:`lohnst_m`.
    soli_st_lohnst_m
        See :func:`soli_st_lohnst_m`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
    """
    prox_ssc = elterngeld_params["sozialv_pausch"] * bruttolohn_m
    return bruttolohn_m - prox_ssc - lohnst_m - soli_st_lohnst_m
