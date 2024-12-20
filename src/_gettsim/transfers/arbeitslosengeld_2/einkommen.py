"""Income relevant for Arbeitslosengeld II / Bürgergeld calculation."""

from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.shared import policy_info


def arbeitsl_geld_2_eink_m(
    arbeitsl_geld_2_nettoeink_nach_abzug_freibetrag_m: float,
    kind_unterh_erhalt_m: float,
    unterhaltsvors_m: float,
    kindergeld_zur_bedarfsdeckung_m: float,
    kindergeldübertrag_m: float,
) -> float:
    """SGB II income.

    Relevant income according to SGB II. Includes child benefit transfer
    (Kindergeldübertrag).

    Note: When aggregating this target to the household level, deduct
    `_diff_kindergeld_kindbedarf_m_hh`. This is necessary because the Kindergeld
    received by the child may enter `arbeitsl_geld_2_eink_m_hh` twice: once as
    Kindergeld and once as Kindergeldübertrag.

    Parameters
    ----------
    arbeitsl_geld_2_nettoeink_nach_abzug_freibetrag_m
        See :func:`arbeitsl_geld_2_nettoeink_nach_abzug_freibetrag_m`.
    kind_unterh_erhalt_m
        See :func:`kind_unterh_erhalt_m`.
    unterhaltsvors_m
        See :func:`unterhaltsvors_m`.
    kindergeld_zur_bedarfsdeckung_m
        See :func:`kindergeld_zur_bedarfsdeckung_m`.
    kindergeldübertrag_m
        See :func:`kindergeldübertrag_m`.

    Returns
    -------
    Income according to SGB II.

    """
    return (
        arbeitsl_geld_2_nettoeink_nach_abzug_freibetrag_m
        + kind_unterh_erhalt_m
        + unterhaltsvors_m
        + kindergeld_zur_bedarfsdeckung_m
        + kindergeldübertrag_m
    )


def arbeitsl_geld_2_nettoeink_nach_abzug_freibetrag_m(
    arbeitsl_geld_2_nettoeink_vor_abzug_freibetrag_m: float,
    arbeitsl_geld_2_eink_anr_frei_m: float,
) -> float:
    """Net income after deductions for calculation of basic subsistence
    (Arbeitslosengeld II / Bürgergeld).

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_nettoeink_vor_abzug_freibetrag_m
        See :func:`arbeitsl_geld_2_nettoeink_vor_abzug_freibetrag_m`.
    arbeitsl_geld_2_eink_anr_frei_m
        See :func:`arbeitsl_geld_2_eink_anr_frei_m`.

    Returns
    -------
    Income after taxes, social insurance contributions, and other deductions.

    """
    return (
        arbeitsl_geld_2_nettoeink_vor_abzug_freibetrag_m
        - arbeitsl_geld_2_eink_anr_frei_m
    )


def arbeitsl_geld_2_nettoeink_vor_abzug_freibetrag_m(
    arbeitsl_geld_2_bruttoeink_m: float,
    eink_st_m_sn: float,
    soli_st_m_sn: float,
    anz_personen_sn: int,
    sozialv_beitr_arbeitnehmer_m: float,
) -> float:
    """Net income for calculation of basic subsistence (Arbeitslosengeld II /
    Bürgergeld).

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    arbeitsl_geld_2_bruttoeink_m
        See :func:`arbeitsl_geld_2_bruttoeink_m`.
    eink_st_m_sn
        See :func:`eink_st_m_sn`.
    soli_st_m_sn
        See :func:`soli_st_m_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    sozialv_beitr_arbeitnehmer_m
        See :func:`sozialv_beitr_arbeitnehmer_m`.

    Returns
    -------
    Income after taxes, social insurance contributions, and other deductions.

    """
    return (
        arbeitsl_geld_2_bruttoeink_m
        - (eink_st_m_sn / anz_personen_sn)
        - (soli_st_m_sn / anz_personen_sn)
        - sozialv_beitr_arbeitnehmer_m
    )


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


@policy_info(end_date="2005-09-30")
def arbeitsl_geld_2_nettoquote(  # noqa: PLR0913
    bruttolohn_m: float,
    eink_st_m_sn: float,
    soli_st_m_sn: float,
    anz_personen_sn: int,
    sozialv_beitr_arbeitnehmer_m: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate share of net to gross wage.

    Quotienten von bereinigtem Nettoeinkommen und Bruttoeinkommen. § 3 Abs. 2 Alg II-V.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    eink_st_m_sn
        See :func:`eink_st_m_sn`.
    soli_st_m_sn
        See :func:`soli_st_m_sn`.
    anz_personen_sn
        See :func:`anz_personen_sn`.
    sozialv_beitr_arbeitnehmer_m
        See :func:`sozialv_beitr_arbeitnehmer_m`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    # Bereinigtes monatliches Einkommen aus Erwerbstätigkeit nach § 11 Abs. 2 Nr. 1-5.
    alg2_2005_bne = max(
        (
            bruttolohn_m
            - (eink_st_m_sn / anz_personen_sn)
            - (soli_st_m_sn / anz_personen_sn)
            - sozialv_beitr_arbeitnehmer_m
            - arbeitsl_geld_2_params["abzugsfähige_pausch"]["werbung"]
            - arbeitsl_geld_2_params["abzugsfähige_pausch"]["versicherung"]
        ),
        0,
    )

    return alg2_2005_bne / bruttolohn_m


@policy_info(
    end_date="2005-09-30",
    name_in_dag="arbeitsl_geld_2_eink_anr_frei_m",
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


@policy_info(start_date="2005-10-01")
def arbeitsl_geld_2_eink_anr_frei_m(
    bruttolohn_m: float,
    eink_selbst_m: float,
    anz_kinder_bis_17_bg: int,
    _eink_st_kinderfreib_anz_ansprüche: int,
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
    anz_kinder_bis_17_bg
        See :func:`anz_kinder_bis_17_bg`.
    _eink_st_kinderfreib_anz_ansprüche
        See :func:`_eink_st_kinderfreib_anz_ansprüche`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    # Beneficiaries who live with a minor child in a group home or who have a minor
    # child have slightly different thresholds. We currently do not consider the second
    # condition.
    eink_erwerbstätigkeit = bruttolohn_m + eink_selbst_m

    if anz_kinder_bis_17_bg > 0 or _eink_st_kinderfreib_anz_ansprüche > 0:
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
