"""This module provides functions to compute parental leave benefits (Elterngeld)."""

import numpy

from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.shared import policy_info
from _gettsim.taxes.eink_st import _eink_st_tarif


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
    elterngeld_geschw_bonus_m: float,
    elterngeld_mehrlinge_bonus_m: float,
    elterngeld_params: dict,
) -> float:
    """Parental leave before checking eligibility.

    Parameters
    ----------
    elterngeld_basisbetrag_m
        See :func:`elterngeld_basisbetrag_m`.
    elterngeld_anrechenbares_einkommen_m
        See :func:`elterngeld_anrechenbares_einkommen_m`.
    elterngeld_geschw_bonus_m
        See :func:`elterngeld_geschw_bonus_m`.
    elterngeld_mehrlinge_bonus_m
        See :func:`elterngeld_mehrlinge_bonus_m`.
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
        + elterngeld_geschw_bonus_m
        + elterngeld_mehrlinge_bonus_m
    )


def elterngeld_anspruchsbedingungen_erfüllt(
    hat_kinder: bool,
    arbeitsstunden_w: float,
    elternzeit_anspruch: bool,
    vorjahr_einkommen_unter_bezugsgrenze: bool,
    elterngeld_params: dict,
) -> bool:
    """Check the eligibility of Elterngeld.

    Parameters
    ----------
    hat_kinder
        See :func:`hat_kinder`.
    arbeitsstunden_w
        See basic input variable :ref:`arbeitsstunden_w <arbeitsstunden_w>`.
    alleinerz:
        See basic input variable :ref: `alleinerz` <alleinerz>.
    _zu_verst_eink_mit_kinderfreib_vorj_sn
        See :func:`_zu_verst_eink_mit_kinderfreib_vorj_sn`.
    elternzeit_anspruch
        See :func:`elternzeit_anspruch`
    vorjahr_einkommen_unter_bezugsgrenze
        See :func:`vorjahr_einkommen_unter_bezugsgrenze`.
    elterngeld_params
        See params documentation :ref: `elterngeld_params <elterngeld_params>`.
    Returns
    -------

    """
    out = (
        (hat_kinder and arbeitsstunden_w <= elterngeld_params["max_arbeitsstunden_w"])
        and vorjahr_einkommen_unter_bezugsgrenze
        and (elternzeit_anspruch == True)
    )
    return out


def vorjahr_einkommen_unter_bezugsgrenze(
    alleinerz: bool,
    _zu_verst_eink_mit_kinderfreib_vorj_sn: float,
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


def elterngeld_bezugsmonate_unter_grenze(
    alter_monate_jüngstes_kind: float,
    monate_elterngeldbezug_elternteil_1: int,
    monate_elterngeldbezug_elternteil_2: int,
    m_elterngeld: int,
    kind: bool,
    elterngeld_params: dict,
) -> bool:
    """Check parental leave eligibility.

    Parameters
    ----------
    alter_monate_jüngstes_mitglied_hh
        See :func:`alter_monate_jüngstes_mitglied_hh`.
    monate_elterngeldbezug_elternteil_1
        See basic input variable :ref:`monate_elterngeldbezug_elternteil_1
        <monate_elterngeldbezug_elternteil_1>`.
    monate_elterngeldbezug_elternteil_2
        See basic input variable :ref:`monate_elterngeldbezug_elternteil_2
        <monate_elterngeldbezug_elternteil_2>`.
    m_elterngeld
        See basic input variable :ref:`m_elterngeld <m_elterngeld>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    kind_jünger_als_grenze = (
        alter_monate_jüngstes_kind < elterngeld_params["max_monate_paar"]
    )
    if alleinerz:
        out = (
            kind_jünger_als_grenze
            and monate_elterngeldbezug <= elterngeld_params["max_monate_ind"]
        )
    out = (
        (alter_monate_jüngstes_kind <= elterngeld_params["max_monate_paar"])
        and (
            monate_elterngeldbezug_elternteil_1 + monate_elterngeldbezug_elternteil_2
            < elterngeld_params["max_monate_paar"]
        )
        and (m_elterngeld <= elterngeld_params["max_monate_ind"])
    )

    return out


@policy_info(skip_vectorization=True)
def monate_elterngeldbezug_partner(
    monate_elterngeldbezug: numpy.ndarray[int],
    p_id: numpy.ndarray[int],
    p_id_elternteil_1: numpy.ndarray[int],
    p_id_elternteil_2: numpy.ndarray[int],
) -> numpy.ndarray[int]:
    """Number of months of parental leave benefit for partner.

    Parameters
    ----------
    monate_elterngeldbezug
        See basic input variable :ref:`monate_elterngeldbezug <monate_elterngeldbezug>`.
    p_id
        See basic input variable :ref:`p_id <p_id>`.
    p_id_elternteil_1
        See basic input variable :ref:`p_id_elternteil_1 <p_id_elternteil_1>`.
    p_id_elternteil_2
        See basic input variable :ref:`p_id_elternteil_2 <p_id_elternteil_2>`.

    Returns
    -------

    """
    # TODO do this on child level instead


# TODO either use this (and move to lohnsteuer) or remove _zu_verst_eink_mit_kinderfreib_vorj_sn
def _elterngeld_proxy_eink_vorj_elterngeld_m(
    bruttolohn_vorj_m: float,
    elterngeld_params: dict,
    eink_st_params: dict,
    eink_st_abzuege_params: dict,
    soli_st_params: dict,
) -> float:
    """Calculating the claim for benefits depending on previous wage.

    Parameters
    ----------

    bruttolohn_vorj_m
        See basic input variable :ref:`bruttolohn_vorj_m <bruttolohn_vorj_m>`.
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
    prox_ssc = elterngeld_params["sozialv_pausch"] * bruttolohn_vorj_m

    # Fictive taxes (Lohnsteuer) are approximated by applying the wage to the tax tariff
    prox_income = (
        12 * bruttolohn_vorj_m - eink_st_abzuege_params["werbungskostenpauschale"] # TODO substract werbekosten from nettolohn!
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

    out = bruttolohn_vorj_m - prox_ssc - prox_tax / 12 - prox_soli / 12

    return max(out, 0.0)

# TODO use only on input variable (monate_elterngeldbezug) and aggregate on child level,
# compute kind_anspruch on child level and then go back to parental level
def elternzeit_anspruch(  # noqa: PLR0913
    alter_monate_jüngstes_mitglied_hh: float,
    monate_elterngeldbezug_elternteil_1_hh: int,
    monate_elterngeldbezug_elternteil_2_hh: int,
    m_elterngeld: int,
    kind: bool,
    elterngeld_params: dict,
) -> bool:
    """Check parental leave eligibility.


    Parameters
    ----------
    alter_monate_jüngstes_mitglied_hh
        See :func:`alter_monate_jüngstes_mitglied_hh`.
    monate_elterngeldbezug_elternteil_1_hh
        See basic input variable :ref:`monate_elterngeldbezug_elternteil_1_hh <monate_elterngeldbezug_elternteil_1_hh>`.
    monate_elterngeldbezug_elternteil_2_hh
        See basic input variable :ref:`monate_elterngeldbezug_elternteil_2_hh <monate_elterngeldbezug_elternteil_2_hh>`.
    m_elterngeld
        See basic input variable :ref:`m_elterngeld <m_elterngeld>`.
    kind
        See basic input variable :ref:`kind <kind>`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    out = (
        (alter_monate_jüngstes_mitglied_hh <= elterngeld_params["max_monate_paar"])
        and (
            monate_elterngeldbezug_elternteil_1_hh
            + monate_elterngeldbezug_elternteil_2_hh
            < elterngeld_params["max_monate_paar"]
        )
        and (not kind)
        and (m_elterngeld <= elterngeld_params["max_monate_ind"])
    )

    return out


def elterngeld_kind(
    geburtsjahr: int,
    elterngeld_params: dict,
) -> bool:
    """Check for sibling bonus on parental leave benefit.

    # ToDo: why use datum and geburtsjahr instead of alter?

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    current_year = elterngeld_params["datum"].astype("datetime64[Y]").astype(int) + 1970 # TODO use age
    out = current_year - geburtsjahr < next(
        iter(elterngeld_params["geschw_bonus_altersgrenzen_kinder"].keys())
    )
    return out


def elterngeld_vorschulkind(
    geburtsjahr: int,
    elterngeld_params: dict,
) -> bool:
    """Check for sibling bonus on parental leave benefit.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    current_year = elterngeld_params["datum"].astype("datetime64[Y]").astype(int) + 1970 # TODO use age
    out = (
        current_year - geburtsjahr
        < list(elterngeld_params["geschw_bonus_altersgrenzen_kinder"].keys())[1]
    )
    return out


def elterngeld_geschw_bonus_anspruch(
    elterngeld_kind_hh: int,
    elterngeld_vorschulkind_hh: int,
    elternzeit_anspruch: bool,
    elterngeld_params: dict,
) -> bool:
    """Check for sibling bonus on parental leave benefit.

    Parameters
    ----------
    elterngeld_kind_hh
        See :func:`elterngeld_kind_hh`.
    elternzeit_anspruch
        See :func:`elternzeit_anspruch`.
    elterngeld_vorschulkind_hh
        See :func:`elterngeld_vorschulkind_hh`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    if elternzeit_anspruch:
        out = (
            elterngeld_kind_hh
            == next(
                iter(elterngeld_params["geschw_bonus_altersgrenzen_kinder"].values()) # TODO make this easier?
            )
        ) or (
            elterngeld_vorschulkind_hh
            >= list(elterngeld_params["geschw_bonus_altersgrenzen_kinder"].values())[1]
        )
    else:
        out = False
    return out


def _elterngeld_anz_mehrlinge_anspruch(
    elternzeit_anspruch: bool,
    anz_mehrlinge_jüngstes_kind_hh: int,
) -> int:
    """Check for multiple bonus on parental leave benefit.

    Parameters
    ----------
    elternzeit_anspruch
        See :func:`elternzeit_anspruch`.
    anz_mehrlinge_jüngstes_kind_hh
        See :func:`anz_mehrlinge_jüngstes_kind_hh`.

    Returns
    -------

    """
    out = anz_mehrlinge_jüngstes_kind_hh - 1 if elternzeit_anspruch else 0 # TODO move away from hh?
    return out


### relevant income new
def elterngeld_eink_relev_m( # TODO naming
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
    relev = _elterngeld_proxy_eink_vorj_elterngeld_m - elterngeld_nettolohn_m # TODO nettolohn doesnt make sense here
    return max(relev, 0.0)


def elterngeld_anteil_eink_erlass(
    elterngeld_eink_relev_m: float, elterngeld_params: dict
) -> float:
    """Calculate the share of net income which is reimbursed when receiving elterngeld.

    According to § 2 (2) BEEG the percentage increases below the first step and
    decreases above the second step until prozent_minimum.

    # ToDo: Split this function up in a function before and after 2011. Before 2011 the
    # ToDo: replacement rate was not lowered for high incomes.

    Parameters
    ----------
    elterngeld_eink_relev_m
        See :func:`elterngeld_eink_relev_m`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
    Returns
    -------

    """

    # Higher replacement rate if considered income is below a threshold
    if (
        elterngeld_eink_relev_m
        < elterngeld_params["nettoeinkommen_stufen"]["lower_threshold"]
    ):
        out = (
            elterngeld_params["nettoeinkommen_stufen"]["lower_threshold"]
            - elterngeld_eink_relev_m
        ) / elterngeld_params["eink_schritt_korrektur"] * elterngeld_params[
            "prozent_korrektur"
        ] + elterngeld_params[
            "faktor"
        ]

    # Lower replacement rate if considered income is above a threshold
    elif (
        elterngeld_eink_relev_m
        > elterngeld_params["nettoeinkommen_stufen"]["upper_threshold"]
    ):
        # Replacement rate is only lowered up to a specific value
        out = max(
            elterngeld_params["faktor"]
            - (
                elterngeld_eink_relev_m
                - elterngeld_params["nettoeinkommen_stufen"]["upper_threshold"]
            )
            / elterngeld_params["eink_schritt_korrektur"],
            elterngeld_params["prozent_minimum"],
        )
    else:
        out = elterngeld_params["faktor"]

    return out


def elterngeld_eink_erlass_m( # TODO naming
    elterngeld_eink_relev_m: float, elterngeld_anteil_eink_erlass: float
) -> float:
    """Calculate base parental leave benefit.

    Parameters
    ----------
    elterngeld_eink_relev_m
        See :func:`elterngeld_eink_relev_m`.
    elterngeld_anteil_eink_erlass
        See :func:`elterngeld_anteil_eink_erlass`.

    Returns
    -------

    """
    return elterngeld_eink_relev_m * elterngeld_anteil_eink_erlass


def elterngeld_geschw_bonus_m(
    elterngeld_eink_erlass_m: float,
    elterngeld_geschw_bonus_anspruch: bool,
    elterngeld_params: dict,
) -> float:
    """Calculate the bonus for siblings.

    According to § 2a parents of siblings get a bonus.

    Parameters
    ----------
    elterngeld_eink_erlass_m
        See :func:`elterngeld_eink_erlass_m`.
    elterngeld_geschw_bonus_anspruch
        See :func:`elterngeld_geschw_bonus_anspruch`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    if elterngeld_geschw_bonus_anspruch:
        out = max(
            elterngeld_params["geschw_bonus_aufschlag"] * elterngeld_eink_erlass_m,
            elterngeld_params["geschw_bonus_minimum"],
        )
    else:
        out = 0.0
    return out


def elterngeld_mehrlinge_bonus_m(
    _elterngeld_anz_mehrlinge_anspruch: int, elterngeld_params: dict
) -> float:
    """Calculate the bonus for multiples.

    Parameters
    ----------
    _elterngeld_anz_mehrlinge_anspruch
        See :func:`_elterngeld_anz_mehrlinge_anspruch`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return float(
        _elterngeld_anz_mehrlinge_anspruch * elterngeld_params["mehrlingbonus"]
    )


def elterngeld_anr_m( # TODO improve naming
    elterngeld_m: float,
    elterngeld_params: dict,
    anz_mehrlinge_jüngstes_kind_hh: int,
) -> float:
    """Calculate elterngeld above threshold which is considered as income for transfers
    such as wohngeld and grunds_im_alter.
    For arbeitsl_geld_2 as well as kinderzuschl the whole amount of elterngeld is
    considered as income, except for the case in which the parents still worked
    right before they had children.
    See: https://www.kindergeld.org/elterngeld-einkommen/

    Parameters
    ----------
    elterngeld_m
        See :func:`elterngeld_m`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
    anz_mehrlinge_jüngstes_kind_hh
        See :func:`anz_mehrlinge_jüngstes_kind_hh`.

    Returns
    -------

    """
    out = max(
        elterngeld_m
        - ((1 + anz_mehrlinge_jüngstes_kind_hh) * elterngeld_params["mindestbetrag"]),
        0,
    )
    return out


###anrechenbares einkommen als output
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

    out = ( # TODO Throw out unnecessary input vars
        mutterschaftsgeld_m
        + dienstbezüge_bei_beschäftigungsverbot_m
        + elterngeld_vergleichbare_leistungen_m
        + ersatzeinnahmen_m
    )
    return out
