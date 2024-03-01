from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.shared import dates_active


def arbeitsl_geld_2_eink_m(  # noqa: PLR0913
    arbeitsl_geld_2_bruttoeink_m: float,
    eink_st_y_tu: float,
    soli_st_y_sn: float,
    anz_erwachsene_tu: int,
    sozialv_beitr_m: float,
    arbeitsl_geld_2_eink_anr_frei_m: float,
    kind: bool,
) -> float:
    """Income (after deduction of taxes, social insurance contributions, and other
    deductions) for calculation of basic subsistence.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_bruttoeink_m
        See :func:`arbeitsl_geld_2_eink_m`.
    sozialv_beitr_m
        See :func:`sozialv_beitr_m`.
    eink_st_y_tu
        See :func:`eink_st_y_tu`.
    soli_st_y_sn
        See :func:`soli_st_y_sn`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    arbeitsl_geld_2_eink_anr_frei_m
        See :func:`arbeitsl_geld_2_eink_anr_frei_m`.
    kind
        See basic input variable :ref:`kind <kind>`.

    Returns
    -------
    Income of a person by unemployment insurance.

    """
    if kind:
        # TODO (@hmgaudecker): Rewrite once groupings are implemented.
        # https://github.com/iza-institute-of-labor-economics/gettsim/pull/601
        out = (
            arbeitsl_geld_2_bruttoeink_m
            - sozialv_beitr_m
            - arbeitsl_geld_2_eink_anr_frei_m
        )
    else:
        out = (
            arbeitsl_geld_2_bruttoeink_m
            - (eink_st_y_tu / anz_erwachsene_tu / 12)
            - (soli_st_y_sn / anz_erwachsene_tu / 12)
            - sozialv_beitr_m
            - arbeitsl_geld_2_eink_anr_frei_m
        )

    return out


def arbeitsl_geld_2_bruttoeink_m(  # noqa: PLR0913
    bruttolohn_m: float,
    sonstig_eink_m: float,
    eink_selbst_m: float,
    eink_vermietung_m: float,
    kapitaleink_brutto_m: float,
    sum_ges_rente_priv_rente_m: float,
    arbeitsl_geld_m: float,
    elterngeld_m: float,
) -> float:
    """Sum up the gross income for calculation of basic subsistence.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`hh_id <hh_id>`.
    sonstig_eink_m
        See basic input variable :ref:`sonstig_eink_m <sonstig_eink_m>`.
    eink_selbst_m
        See basic input variable :ref:`eink_selbst_m <eink_selbst_m>`.
    eink_vermietung_m
        See basic input variable :ref:`eink_vermietung_m <eink_vermietung_m>`.
    kapitaleink_brutto_m
        See basic input variable :ref:`kapitaleink_brutto_m <kapitaleink_brutto_m>`.
    sum_ges_rente_priv_rente_m
        See basic input variable :ref:`sum_ges_rente_priv_rente_m
        <sum_ges_rente_priv_rente_m>`.
    arbeitsl_geld_m
        See :func:`arbeitsl_geld_m`.
    elterngeld_m
        See :func:`elterngeld_m`.

    Returns
    -------
    Income by unemployment insurance before tax.

    """
    out = (
        bruttolohn_m
        + sonstig_eink_m
        + eink_selbst_m
        + eink_vermietung_m
        + kapitaleink_brutto_m
        + sum_ges_rente_priv_rente_m
        + arbeitsl_geld_m
        + elterngeld_m
    )

    return out


@dates_active(end="2005-09-30")
def arbeitsl_geld_2_nettoquote(  # noqa: PLR0913
    bruttolohn_m: float,
    eink_st_y_tu: float,
    soli_st_y_sn: float,
    anz_erwachsene_tu: int,
    sozialv_beitr_m: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate share of net to gross wage.

    Quotienten von bereinigtem Nettoeinkommen und Bruttoeinkommen. § 3 Abs. 2 Alg II-V.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    eink_st_y_tu
        See :func:`eink_st_y_tu`.
    soli_st_y_sn
        See :func:`soli_st_y_sn`.
    anz_erwachsene_tu
        See :func:`anz_erwachsene_tu`.
    sozialv_beitr_m
        See :func:`sozialv_beitr_m`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    # Bereinigtes monatliches Einkommen aus Erwerbstätigkeit nach § 11 Abs. 2 Nr. 1-5.
    alg2_2005_bne = max(
        (
            bruttolohn_m
            - (eink_st_y_tu / anz_erwachsene_tu / 12)
            - (soli_st_y_sn / anz_erwachsene_tu / 12)
            - sozialv_beitr_m
            - arbeitsl_geld_2_params["abzugsfähige_pausch"]["werbung"]
            - arbeitsl_geld_2_params["abzugsfähige_pausch"]["versicherung"]
        ),
        0,
    )

    return alg2_2005_bne / bruttolohn_m


@dates_active(
    end="2005-09-30",
    change_name="arbeitsl_geld_2_eink_anr_frei_m",
)
def arbeitsl_geld_2_eink_anr_frei_m_basierend_auf_nettoquote(
    bruttolohn_m: float,
    arbeitsl_geld_2_nettoquote: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Share of income which remains to the individual.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    arbeitsl_geld_2_nettoquote
        See :func:`arbeitsl_geld_2_nettoquote`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    out = piecewise_polynomial(
        x=bruttolohn_m,
        thresholds=arbeitsl_geld_2_params["eink_anr_frei"]["thresholds"],
        rates=arbeitsl_geld_2_params["eink_anr_frei"]["rates"],
        intercepts_at_lower_thresholds=arbeitsl_geld_2_params["eink_anr_frei"][
            "intercepts_at_lower_thresholds"
        ],
        rates_multiplier=arbeitsl_geld_2_nettoquote,
    )
    return out


@dates_active(start="2005-10-01")
def arbeitsl_geld_2_eink_anr_frei_m(
    bruttolohn_m: float,
    eink_selbst_m: float,
    anz_kinder_bis_17_hh: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate share of income, which remains to the individual since 10/2005.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.
    Sozialgesetzbuch (SGB) Zweites Buch (II) - Bürgergeld, Grundsicherung für
    Arbeitsuchende. SGB II §11b Abs 3
    https://www.gesetze-im-internet.de/sgb_2/__11b.html

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    eink_selbst_m
        See basic input variable :ref:`eink_selbst_m <eink_selbst_m>`.
    anz_kinder_bis_17_hh
        See :func:`anz_kinder_bis_17_hh`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    # Beneficiaries who live with a minor child in a group home or who have a minor
    # child have slightly different thresholds. We currently do not consider the second
    # condition.
    eink_erwerbstätigkeit = bruttolohn_m + eink_selbst_m

    if anz_kinder_bis_17_hh > 0:
        out = piecewise_polynomial(
            x=eink_erwerbstätigkeit,
            thresholds=arbeitsl_geld_2_params["eink_anr_frei_kinder"]["thresholds"],
            rates=arbeitsl_geld_2_params["eink_anr_frei_kinder"]["rates"],
            intercepts_at_lower_thresholds=arbeitsl_geld_2_params[
                "eink_anr_frei_kinder"
            ]["intercepts_at_lower_thresholds"],
        )
    else:
        out = piecewise_polynomial(
            x=eink_erwerbstätigkeit,
            thresholds=arbeitsl_geld_2_params["eink_anr_frei"]["thresholds"],
            rates=arbeitsl_geld_2_params["eink_anr_frei"]["rates"],
            intercepts_at_lower_thresholds=arbeitsl_geld_2_params["eink_anr_frei"][
                "intercepts_at_lower_thresholds"
            ],
        )
    return out
