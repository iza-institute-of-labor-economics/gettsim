"""This module provides functions to compute parental leave benefits (Elterngeld)."""

from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.taxes.eink_st import _eink_st_tarif


###Elterngeld neu
def elterngeld_m(  # noqa: PLR0913
    elterngeld_eink_relev_m: float,
    elterngeld_anspruch: bool,
    elterngeld_eink_erlass_m: float,
    elterngeld_anrechenbares_einkommen_m: float,
    elterngeld_geschw_bonus_m: float,
    elterngeld_mehrlinge_bonus_m: float,
    elterngeld_params: dict,
) -> float:
    """Calculate parental leave benefit (elterngeld).

    For the calculation, the relevant wage and the eligibility for bonuses is needed.

    Parameters
    ----------
    elterngeld_eink_relev_m
        See :func:`elterngeld_eink_relev_m`.
    elterngeld_anspruch
        See :func:`elterngeld_anspruch`.
    elterngeld_eink_erlass_m
        See :func:`elterngeld_eink_erlass_m`.
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

    if (elterngeld_eink_relev_m < 0) or (not elterngeld_anspruch):
        out = 0.0
    else:
        # Bound from above and below
        out = (
            min(
                max(
                    elterngeld_eink_erlass_m - elterngeld_anrechenbares_einkommen_m,
                    elterngeld_params["mindestbetrag"],
                ),
                elterngeld_params["höchstbetrag"],
            )
            + elterngeld_geschw_bonus_m
            + elterngeld_mehrlinge_bonus_m
        )
    return out


# i have changed the elternzeit_anspruch function to the elterngeld_anspruch
# to better accomodate to the haushaltsfinanzierungsgesetz


### claim function (rudimentary)
def elterngeld_anspruch(
    hat_kinder: bool,
    arbeitsstunden_w: float,
    alleinerz: bool,
    _zu_verst_eink_mit_kinderfreib_vorj_sn: float,
    elternzeit_anspruch: bool,
    elterngeld_params: dict,
) -> bool:
    """Check the eligibility of Elterngeld.

    Parameters
    ----------
    hat_kinder
        See basic input variable :ref:`hat_kinder <hat_kinder>`.
    arbeitsstunden_w
        See basic input variable :ref:`arbeitsstunden_w <arbeitsstunden_w>`.
    alleinerz:
        See basic input variable :ref: `alleinerz` <alleinerz>
    _zu_verst_eink_mit_kinderfreib_vorj_sn
        See :func:`_zu_verst_eink_mit_kinderfreib_vorj_sn`
    elternzeit_anspruch
        See :func:`elternzeit_anspruch`
    elterngeld_params
        See params documentation :ref: `elterngeld_params <elterngeld_params>`
    Returns
    -------

    """

    out = (
        (
            hat_kinder == True
            and arbeitsstunden_w <= elterngeld_params["max_arbeitsstunden_w"]
        )
        and (
            (
                alleinerz == True
                and _zu_verst_eink_mit_kinderfreib_vorj_sn
                <= elterngeld_params["max_eink_vorj_allein"]
            )
            or (
                _zu_verst_eink_mit_kinderfreib_vorj_sn
                <= elterngeld_params["max_eink_vorj_zsm"]
            )
        )
        and (elternzeit_anspruch == True)
    )
    return out


###Income approximation new, removed BBmG
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
        12 * bruttolohn_vorj_m - eink_st_abzuege_params["werbungskostenpauschale"]
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


# original function capped the taxable income at the gBBG, which is not covered by the BEEG.
# Due to §2f (3), the BBmG is not relevant in this calculation


def elternzeit_anspruch(  # noqa: PLR0913
    alter_monate_jüngstes_mitglied_hh: float,
    m_elterngeld_mut_hh: int,
    m_elterngeld_vat_hh: int,
    m_elterngeld: int,
    kind: bool,
    elterngeld_params: dict,
) -> bool:
    """Check parental leave eligibility.

    # ToDo: Check meaning and naming and make description of m_elterngeld_mut_hh,
    # ToDo: m_elterngeld_vat_hh, and m_elterngeld more precise

    Parameters
    ----------
    alter_monate_jüngstes_mitglied_hh
        See :func:`alter_monate_jüngstes_mitglied_hh`.
    m_elterngeld_mut_hh
        See basic input variable :ref:`m_elterngeld_mut_hh <m_elterngeld_mut_hh>`.
    m_elterngeld_vat_hh
        See basic input variable :ref:`m_elterngeld_vat_hh <m_elterngeld_vat_hh>`.
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
            m_elterngeld_mut_hh + m_elterngeld_vat_hh
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
    current_year = elterngeld_params["datum"].astype("datetime64[Y]").astype(int) + 1970
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
    current_year = elterngeld_params["datum"].astype("datetime64[Y]").astype(int) + 1970
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
                iter(elterngeld_params["geschw_bonus_altersgrenzen_kinder"].values())
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
    out = anz_mehrlinge_jüngstes_kind_hh - 1 if elternzeit_anspruch else 0
    return out


def elterngeld_nettolohn_m(
    bruttolohn_m: float,
    eink_st_y_sn: float,
    soli_st_y_sn: float,
    anz_personen_sn: int,
    sozialv_beitr_m: float,
) -> float:
    """Calculate the net wage.

    Taxes and social insurance contributions are needed for the calculation.


    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    eink_st_y_sn
        See :func:`eink_st_y_sn`.
    soli_st_y_sn
        See :func:`soli_st_y_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    sozialv_beitr_m
        See :func:`sozialv_beitr_m`.

    Returns
    -------

    """
    out = (
        bruttolohn_m
        - (eink_st_y_sn / anz_personen_sn / 12)
        - (soli_st_y_sn / anz_personen_sn / 12)
        - sozialv_beitr_m
    )

    return max(out, 0.0)


### relevant income new
def elterngeld_eink_relev_m(
    _elterngeld_proxy_eink_vorj_elterngeld_m: float,
    elterngeld_nettolohn_m: float,
) -> float:
    """Calculating the relevant wage for the calculation of elterngeld.

       According to § 2 (1) and (3) BEEG elterngeld is calculated by the loss of income due to
       child raising and is reduced by aquired income during the claiming of Elterngeld.

    Parameters
       ----------
       _elterngeld_proxy_eink_vorj_elterngeld_m
           See :func:`_elterngeld_proxy_eink_vorj_elterngeld_m`.
       elterngeld_nettolohn_m
           See :func:`elterngeld_nettolohn_m`.

       Returns
       -------

    """
    relev = _elterngeld_proxy_eink_vorj_elterngeld_m - elterngeld_nettolohn_m
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


def elterngeld_eink_erlass_m(
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


def elterngeld_anr_m(
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
        See basic input variable :ref:`dienstbezüge_bei_beschäftigungsverbot_m`<dienstbezüge_bei_beschäftigungsverbot_m>.
    elterngeld_vergleichbare_leistungen_m
        See basic input variable :ref:`elterngeld_vergleichbare_leistungen_m <elterngeld_vergleichbare_leistungen_m>`.
    ersatzeinnahmen_m
        See basic input variable :ref: èrsatzeinnahmen_m <èrsatzeinnahmen_m>.

    Returns
    -------

    """

    out = (
        mutterschaftsgeld_m
        + dienstbezüge_bei_beschäftigungsverbot_m
        + elterngeld_vergleichbare_leistungen_m
        + ersatzeinnahmen_m
    )
    return out


# This function calculates the income, that leads to a 1:1 reduction in the Elterngeld payment
# It is calculated according to §3 (1) BEEG
