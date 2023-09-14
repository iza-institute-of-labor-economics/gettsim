"""This module provides functions to compute parental leave benefits (Elterngeld)."""
from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.taxes.eink_st import _eink_st_tarif


def elterngeld_m(  # noqa: PLR0913
    elterngeld_eink_relev_m: float,
    elternzeit_anspruch: bool,
    elterngeld_eink_erlass_m: float,
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
    elternzeit_anspruch
        See :func:`elternzeit_anspruch`.
    elterngeld_eink_erlass_m
        See :func:`elterngeld_eink_erlass_m`.
    elterngeld_geschw_bonus_m
        See :func:`elterngeld_geschw_bonus_m`.
    elterngeld_mehrlinge_bonus_m
        See :func:`elterngeld_mehrlinge_bonus_m`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """

    if (elterngeld_eink_relev_m < 0) or (not elternzeit_anspruch):
        out = 0.0
    else:
        # Bound from above and below
        out = (
            min(
                max(elterngeld_eink_erlass_m, elterngeld_params["mindestbetrag"]),
                elterngeld_params["höchstbetrag"],
            )
            + elterngeld_geschw_bonus_m
            + elterngeld_mehrlinge_bonus_m
        )
    return out


def _elterngeld_proxy_eink_vorj_elterngeld_m(
    _ges_rentenv_beitr_bemess_grenze_m: float,
    bruttolohn_vorj_m: float,
    elterngeld_params: dict,
    eink_st_params: dict,
    eink_st_abzuege_params: dict,
    soli_st_params: dict,
) -> float:
    """Calculating the claim for benefits depending on previous wage.

    Parameters
    ----------
    _ges_rentenv_beitr_bemess_grenze_m
        See :func:`_ges_rentenv_beitr_bemess_grenze_m`.
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
    # Relevant wage is capped at the contribution thresholds
    max_wage = min(bruttolohn_vorj_m, _ges_rentenv_beitr_bemess_grenze_m)

    # We need to deduct lump-sum amounts for contributions, taxes and soli
    prox_ssc = elterngeld_params["sozialv_pausch"] * max_wage

    # Fictive taxes (Lohnsteuer) are approximated by applying the wage to the tax tariff
    prox_income = 12 * max_wage - eink_st_abzuege_params["werbungskostenpauschale"]
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

    out = max_wage - prox_ssc - prox_tax / 12 - prox_soli / 12

    return max(out, 0.0)


def elternzeit_anspruch(  # noqa: PLR0913
    alter_monate_jüngstes_mitglied_vg: float,
    m_elterngeld_mut_vg: int,
    m_elterngeld_vat_vg: int,
    m_elterngeld: int,
    kind: bool,
    elterngeld_params: dict,
) -> bool:
    """Check parental leave eligibility.

    # ToDo: Check meaning and naming and make description of m_elterngeld_mut_vg,
    # ToDo: m_elterngeld_vat_vg, and m_elterngeld more precise

    Parameters
    ----------
    alter_monate_jüngstes_mitglied_vg
        See :func:`alter_monate_jüngstes_mitglied_vg`.
    m_elterngeld_mut_vg
        See basic input variable :ref:`m_elterngeld_mut_vg <m_elterngeld_mut_vg>`.
    m_elterngeld_vat_vg
        See basic input variable :ref:`m_elterngeld_vat_vg <m_elterngeld_vat_vg>`.
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
        (alter_monate_jüngstes_mitglied_vg <= elterngeld_params["max_monate_paar"])
        and (
            m_elterngeld_mut_vg + m_elterngeld_vat_vg
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
    elterngeld_kind_vg: int,
    elterngeld_vorschulkind_vg: int,
    elternzeit_anspruch: bool,
    elterngeld_params: dict,
) -> bool:
    """Check for sibling bonus on parental leave benefit.

    Parameters
    ----------
    elterngeld_kind_vg
        See :func:`elterngeld_kind_vg`.
    elternzeit_anspruch
        See :func:`elternzeit_anspruch`.
    elterngeld_vorschulkind_vg
        See :func:`elterngeld_vorschulkind_vg`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    if elternzeit_anspruch:
        out = (
            elterngeld_kind_vg
            == next(
                iter(elterngeld_params["geschw_bonus_altersgrenzen_kinder"].values())
            )
        ) or (
            elterngeld_vorschulkind_vg
            >= list(elterngeld_params["geschw_bonus_altersgrenzen_kinder"].values())[1]
        )
    else:
        out = False
    return out


def _elterngeld_anz_mehrlinge_anspruch(
    elternzeit_anspruch: bool,
    anz_mehrlinge_jüngstes_kind_vg: int,
) -> int:
    """Check for multiple bonus on parental leave benefit.

    Parameters
    ----------
    elternzeit_anspruch
        See :func:`elternzeit_anspruch`.
    anz_mehrlinge_jüngstes_kind_vg
        See :func:`anz_mehrlinge_jüngstes_kind_vg`.

    Returns
    -------

    """
    out = anz_mehrlinge_jüngstes_kind_vg - 1 if elternzeit_anspruch else 0
    return out


def elterngeld_nettolohn_m(
    bruttolohn_m: float,
    eink_st_y_tu: float,
    soli_st_y_tu: float,
    anz_erwachsene_tu: int,
    sozialv_beitr_m: float,
) -> float:
    """Calculate the net wage.

    Taxes and social insurance contributions are needed for the calculation.


    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    eink_st_y_tu
        See :func:`eink_st_y_tu`.
    soli_st_y_tu
        See :func:`soli_st_y_tu`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    sozialv_beitr_m
        See :func:`sozialv_beitr_m`.

    Returns
    -------

    """
    out = (
        bruttolohn_m
        - (eink_st_y_tu / anz_erwachsene_tu / 12)
        - (soli_st_y_tu / anz_erwachsene_tu / 12)
        - sozialv_beitr_m
    )

    return max(out, 0.0)


def elterngeld_eink_relev_m(
    _elterngeld_proxy_eink_vorj_elterngeld_m: float,
    elterngeld_nettolohn_m: float,
) -> float:
    """Calculating the relevant wage for the calculation of elterngeld.

    According to § 2 (1) BEEG elterngeld is calculated by the loss of income due to
    child raising.


    Parameters
    ----------
    _elterngeld_proxy_eink_vorj_elterngeld_m
        See :func:`_elterngeld_proxy_eink_vorj_elterngeld_m`.
    elterngeld_nettolohn_m
        See :func:`elterngeld_nettolohn_m`.

    Returns
    -------

    """
    return _elterngeld_proxy_eink_vorj_elterngeld_m - elterngeld_nettolohn_m


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
    anz_mehrlinge_jüngstes_kind_vg: int,
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
    anz_mehrlinge_jüngstes_kind_vg
        See :func:`anz_mehrlinge_jüngstes_kind_vg`.

    Returns
    -------

    """
    out = max(
        elterngeld_m
        - ((1 + anz_mehrlinge_jüngstes_kind_vg) * elterngeld_params["mindestbetrag"]),
        0,
    )
    return out
