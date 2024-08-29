"""This module provides functions to compute parental leave benefits (Elterngeld)."""

from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.taxes.eink_st import _eink_st_tarif

# elterngeldempf_1 , elterngeldempf_2

aggregate_by_group_elterngeld = {
    "kind_anspruchsberechtigt_fg": {
        "source_col": "kind_anspruchsberechtigt",
        "aggr": "any",
    },
}


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


def elterngeld_anspruchshöhe_m(
    elterngeld_basisbetrag_m: float,
    elterngeld_anrechenbares_einkommen_m: float,
    elterngeld_geschwisterbonus_m: float,
    elterngeld_mehrlingsbonus_m: float,
    elterngeld_params: dict,
) -> float:
    """Parental leave before checking eligibility.

    Parameters
    ----------
    elterngeld_basisbetrag_m
        See :func:`elterngeld_basisbetrag_m`.
    elterngeld_anrechenbares_einkommen_m
        See :func:`elterngeld_anrechenbares_einkommen_m`.
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
                elterngeld_basisbetrag_m - elterngeld_anrechenbares_einkommen_m,
                elterngeld_params["mindestbetrag"],
            ),
            elterngeld_params["höchstbetrag"],
        )
        + elterngeld_geschwisterbonus_m
        + elterngeld_mehrlingsbonus_m
    )


def elterngeld_anspruchsbedingungen_erfüllt(
    alleinerz: bool,
    monate_elterngeldbezug_fg: int,
    hat_kinder: bool,
    arbeitsstunden_w: float,
    kind_anspruchsberechtigt_fg: bool,
    vorjahr_einkommen_unter_bezugsgrenze: bool,
    elterngeld_params: dict,
) -> bool:
    """Individual is eligible to receive Elterngeld.

    Parameters
    ----------
    alleinerz
        See basic input variable :ref:`alleinerz <alleinerz>`.
    monate_elterngeldbezug_fg
        See :func:`monate_elterngeldbezug_fg`.
    hat_kinder
        See :func:`hat_kinder`.
    arbeitsstunden_w
        See basic input variable :ref:`arbeitsstunden_w <arbeitsstunden_w>`.
    kind_anspruchsberechtigt_fg
        See :func:`kind_anspruchsberechtigt_fg`.
    vorjahr_einkommen_unter_bezugsgrenze
        See :func:`vorjahr_einkommen_unter_bezugsgrenze`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    if alleinerz:
        bezugsmonate_unter_grenze = (
            monate_elterngeldbezug_fg <= elterngeld_params["max_monate_ind"]
        )
    else:
        bezugsmonate_unter_grenze = (
            monate_elterngeldbezug_fg <= elterngeld_params["max_monate_paar"]
        )
    out = (
        (hat_kinder and arbeitsstunden_w <= elterngeld_params["max_arbeitsstunden_w"])
        and vorjahr_einkommen_unter_bezugsgrenze
        and kind_anspruchsberechtigt_fg
        and bezugsmonate_unter_grenze
    )
    return out


def vorjahr_einkommen_unter_bezugsgrenze(
    alleinerz: bool,
    _zu_verst_eink_mit_kinderfreib_vorj_sn: float, # TODO potentially rename
    elterngeld_params: dict,
) -> bool:
    """Income before birth is below income threshold for Elterngeld.

    Parameters
    ----------
    alleinerz
        See basic input variable :ref:`alleinerz <alleinerz>`.
    _zu_verst_eink_mit_kinderfreib_vorj_sn
        See :func:`_zu_verst_eink_mit_kinderfreib_vorj_sn`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    if alleinerz:
        out = (
            _zu_verst_eink_mit_kinderfreib_vorj_sn
            <= elterngeld_params["max_eink_vorj_allein"]
        )
    else:
        out = (
            _zu_verst_eink_mit_kinderfreib_vorj_sn
            <= elterngeld_params["max_eink_vorj_zsm"]
        )
    return out


def kind_anspruchsberechtigt(
    alter: float,
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
    elterngeld_einkommen_vorjahr_m: float, elterngeld_lohnersatzanteil: float
) -> float:
    """Base parental leave benefit without accounting for floor and ceiling.

    Parameters
    ----------
    elterngeld_einkommen_vorjahr_m
        See :func:`elterngeld_einkommen_vorjahr_m`.
    elterngeld_lohnersatzanteil
        See :func:`elterngeld_lohnersatzanteil`.

    Returns
    -------

    """
    return elterngeld_einkommen_vorjahr_m * elterngeld_lohnersatzanteil


# TODO move to lohnsteuer
def _elterngeld_proxy_eink_vorj_elterngeld_m(
    elterngeld_bruttolohn_vor_geburt_m: float,
    elterngeld_params: dict,
    eink_st_params: dict,
    eink_st_abzuege_params: dict,
    soli_st_params: dict,
) -> float:
    """Income before birth.

    Income 12 months before birth is used to calculate the replacement rate and the base
    benefit.

    Parameters
    ----------
    elterngeld_bruttolohn_vor_geburt_m
        See basic input variable :ref:`elterngeld_bruttolohn_vor_geburt_m
        <elterngeld_bruttolohn_vor_geburt_m>`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    soli_st_params
        See params documentation :ref:`soli_st_params <soli_st_params>`.

    Returns
    -------

    """
    # We need to deduct lump-sum amounts for contributions, taxes and soli
    prox_ssc = elterngeld_params["sozialv_pausch"] * elterngeld_bruttolohn_vor_geburt_m

    # Fictive taxes (Lohnsteuer) are approximated by applying the wage to the tax tariff
    prox_income = (
        12 * elterngeld_bruttolohn_vor_geburt_m
        - eink_st_abzuege_params[
            "werbungskostenpauschale"
        ]  # TODO substract werbekosten from nettolohn?
    )
    prox_income = max(prox_income, 0.0)

    prox_tax = _eink_st_tarif(
        prox_income,
        eink_st_params,
    )

    prox_soli = piecewise_polynomial(
        prox_tax,
        thresholds=soli_st_params["soli_st"]["thresholds"],
        rates=soli_st_params["soli_st"]["rates"],
        intercepts_at_lower_thresholds=soli_st_params["soli_st"][
            "intercepts_at_lower_thresholds"
        ],
    )

    out = elterngeld_bruttolohn_vor_geburt_m - prox_ssc - prox_tax / 12 - prox_soli / 12

    return max(out, 0.0)


def elterngeld_einkommen_vorjahr_m(  # TODO naming
    _elterngeld_proxy_eink_vorj_elterngeld_m: float,
    elterngeld_nettolohn_m: float,
) -> float:
    """Calculating the relevant wage for the calculation of elterngeld.

    Elterngeld payment is reduced by income during the claiming period (§ 2 (1) and (3)
    BEEG).

    Parameters
       ----------
       _elterngeld_proxy_eink_vorj_elterngeld_m
           See :func:`_elterngeld_proxy_eink_vorj_elterngeld_m`.
       elterngeld_nettolohn_m
           See :func:`elterngeld_nettolohn_m`.

       Returns
       -------

    """
    relev = (
        _elterngeld_proxy_eink_vorj_elterngeld_m - elterngeld_nettolohn_m
    )  # TODO nettolohn doesnt make sense here
    return max(relev, 0.0)


def elterngeld_lohnersatzanteil(
    elterngeld_einkommen_vorjahr_m: float, elterngeld_params: dict
) -> float:
    """Calculate the share of net income which is reimbursed when receiving elterngeld.

    According to § 2 (2) BEEG the percentage increases below the first step and
    decreases above the second step until prozent_minimum.

    # ToDo: Split this function up in a function before and after 2011. Before 2011 the
    # ToDo: replacement rate was not lowered for high incomes.

    Parameters
    ----------
    elterngeld_einkommen_vorjahr_m
        See :func:`elterngeld_einkommen_vorjahr_m`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
    Returns
    -------

    """

    # Higher replacement rate if considered income is below a threshold
    if (
        elterngeld_einkommen_vorjahr_m
        < elterngeld_params["nettoeinkommen_stufen"]["lower_threshold"]
    ):
        out = (
            elterngeld_params["nettoeinkommen_stufen"]["lower_threshold"]
            - elterngeld_einkommen_vorjahr_m
        ) / elterngeld_params["eink_schritt_korrektur"] * elterngeld_params[
            "prozent_korrektur"
        ] + elterngeld_params[
            "faktor"
        ]

    # Lower replacement rate if considered income is above a threshold
    elif (
        elterngeld_einkommen_vorjahr_m
        > elterngeld_params["nettoeinkommen_stufen"]["upper_threshold"]
    ):
        # Replacement rate is only lowered up to a specific value
        out = max(
            elterngeld_params["faktor"]
            - (
                elterngeld_einkommen_vorjahr_m
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
    elterngeld_geschwisterbonus_anspruchsberechtigt_fg: bool,
    elterngeld_params: dict,
) -> float:
    """Elterngeld bonus for (older) siblings.

    According to § 2a parents of siblings get a bonus.

    Parameters
    ----------
    elterngeld_basisbetrag_m
        See :func:`elterngeld_basisbetrag_m`.
    elterngeld_geschwisterbonus_anspruchsberechtigt_fg
        See :func:`elterngeld_geschwisterbonus_anspruchsberechtigt_fg`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    if elterngeld_geschwisterbonus_anspruchsberechtigt_fg:
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
    """Calculate the bonus for multiples.

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


def elterngeld_geschwisterbonus_anspruchsberechtigt_fg(
    anz_kinder_bis_2_fg: int,
    anz_kinder_bis_5_fg: int,
    elterngeld_params: dict,
) -> bool:
    """Check if there are siblings that give rise to Elterngeld siblings bonus.

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


def elterngeld_anrechenbares_einkommen_m(
    mutterschaftsgeld_m: float,
    dienstbezüge_bei_beschäftigungsverbot_m: float,
    elterngeld_vergleichbare_leistungen_m: float,
    ersatzeinnahmen_m: float,
) -> float:
    """Calculate reducing income for Elterngeld.

    Parameters
    ----------
    mutterschaftsgeld_m
        See basic input variable :ref:`mutterschaftsgeld_m`<mutterschaftsgeld_m>.
    dienstbezüge_bei_beschäftigungsverbot_m
        See basic input variable
        :ref:`dienstbezüge_bei_beschäftigungsverbot_m`<dienstbezüge_bei_beschäftigungsverbot_m>.
    elterngeld_vergleichbare_leistungen_m
        See basic input variable :ref:`elterngeld_vergleichbare_leistungen_m
        <elterngeld_vergleichbare_leistungen_m>`.
    ersatzeinnahmen_m
        See basic input variable :ref: èrsatzeinnahmen_m <èrsatzeinnahmen_m>.

    Returns
    -------

    """

    out = (  # TODO Throw out unnecessary input vars
        mutterschaftsgeld_m
        + dienstbezüge_bei_beschäftigungsverbot_m
        + elterngeld_vergleichbare_leistungen_m
        + ersatzeinnahmen_m
    )
    return out


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