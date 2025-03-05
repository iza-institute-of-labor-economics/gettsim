"""Income relevant for calculation of Arbeitslosengeld II / Bürgergeld."""

from _gettsim.functions.policy_function import policy_function
from _gettsim.piecewise_functions import piecewise_polynomial


@policy_function
def anzurechnendes_einkommen_m(
    nettoeinkommen_nach_abzug_freibetrag_m: float,
    unterhalt__kind_betrag_m: float,
    unterhaltsvorschuss__betrag_m: float,
    kindergeld_zur_bedarfsdeckung_m: float,
    kindergeldübertrag_m: float,
) -> float:
    """SGB II income.

    Relevant income according to SGB II. Includes child benefit transfer
    (Kindergeldübertrag).

    Note: When aggregating this target to the household level, deduct
    `differenz_kindergeld_kindbedarf_m_hh`. This is necessary because the Kindergeld
    received by the child may enter `anzurechnendes_einkommen_m_hh` twice: once as
    Kindergeld and once as Kindergeldübertrag.

    Parameters
    ----------
    nettoeinkommen_nach_abzug_freibetrag_m
        See :func:`nettoeinkommen_nach_abzug_freibetrag_m`.
    unterhalt__kind_betrag_m
        See :func:`unterhalt__kind_betrag_m`.
    unterhaltsvorschuss__betrag_m
        See :func:`unterhaltsvorschuss__betrag_m`.
    kindergeld_zur_bedarfsdeckung_m
        See :func:`kindergeld_zur_bedarfsdeckung_m`.
    kindergeldübertrag_m
        See :func:`kindergeldübertrag_m`.

    Returns
    -------
    Income according to SGB II.

    """
    return (
        nettoeinkommen_nach_abzug_freibetrag_m
        + unterhalt__kind_betrag_m
        + unterhaltsvorschuss__betrag_m
        + kindergeld_zur_bedarfsdeckung_m
        + kindergeldübertrag_m
    )


@policy_function
def nettoeinkommen_nach_abzug_freibetrag_m(
    nettoeinkommen_vor_abzug_freibetrag_m: float,
    anrechnungsfreies_einkommen_m: float,
) -> float:
    """Net income after deductions for calculation of basic subsistence
    (Arbeitslosengeld II / Bürgergeld).

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    nettoeinkommen_vor_abzug_freibetrag_m
        See :func:`nettoeinkommen_vor_abzug_freibetrag_m`.
    anrechnungsfreies_einkommen_m
        See :func:`anrechnungsfreies_einkommen_m`.

    Returns
    -------
    Income after taxes, social insurance contributions, and other deductions.

    """
    return nettoeinkommen_vor_abzug_freibetrag_m - anrechnungsfreies_einkommen_m


@policy_function
def nettoeinkommen_vor_abzug_freibetrag_m(
    bruttoeinkommen_m: float,
    eink_st_m_sn: float,
    soli_st_m_sn: float,
    demographic_vars__anzahl_personen_sn: int,
    sozialversicherungsbeitraege__betrag_arbeitnehmer_m: float,
) -> float:
    """Net income for calculation of basic subsistence (Arbeitslosengeld II /
    Bürgergeld).

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    bruttoeinkommen_m
        See :func:`bruttoeinkommen_m`.
    eink_st_m_sn
        See :func:`eink_st_m_sn`.
    soli_st_m_sn
        See :func:`soli_st_m_sn`.
    demographic_vars__anzahl_personen_sn
        See :func:`demographic_vars__anzahl_personen_sn`.
    sozialversicherungsbeitraege__betrag_arbeitnehmer_m
        See :func:`sozialversicherungsbeitraege__betrag_arbeitnehmer_m`.

    Returns
    -------
    Income after taxes, social insurance contributions, and other deductions.

    """
    return (
        bruttoeinkommen_m
        - (eink_st_m_sn / demographic_vars__anzahl_personen_sn)
        - (soli_st_m_sn / demographic_vars__anzahl_personen_sn)
        - sozialversicherungsbeitraege__betrag_arbeitnehmer_m
    )


@policy_function
def bruttoeinkommen_m(  # noqa: PLR0913
    einkommen__bruttolohn_m: float,
    einkommen__sonstige_m: float,
    einkommen__aus_selbstständigkeit_m: float,
    einkommen__aus_vermietung_m: float,
    einkommen__bruttokapitaleinkommen_m: float,
    rente__altersrente__sum_private_gesetzl_rente_m: float,
    arbeitslosengeld__betrag_m: float,
    elterngeld__betrag_m: float,
) -> float:
    """Sum up the gross income for calculation of basic subsistence.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.

    Parameters
    ----------
    einkommen__bruttolohn_m
        See basic input variable :ref:`demographics__hh_id <demographics__hh_id>`.
    einkommen__sonstige_m
        See basic input variable :ref:`einkommen__sonstige_m <einkommen__sonstige_m>`.
    einkommen__aus_selbstständigkeit_m
        See basic input variable :ref:`einkommen__aus_selbstständigkeit_m <einkommen__aus_selbstständigkeit_m>`.
    einkommen__aus_vermietung_m
        See basic input variable :ref:`einkommen__aus_vermietung_m <einkommen__aus_vermietung_m>`.
    einkommen__bruttokapitaleinkommen_m
        See basic input variable :ref:`einkommen__bruttokapitaleinkommen_m <einkommen__bruttokapitaleinkommen_m>`.
    rente__altersrente__sum_private_gesetzl_rente_m
        See basic input variable :ref:`rente__altersrente__sum_private_gesetzl_rente_m
        <rente__altersrente__sum_private_gesetzl_rente_m>`.
    arbeitslosengeld__betrag_m
        See :func:`arbeitslosengeld__betrag_m`.
    elterngeld__betrag_m
        See :func:`elterngeld__betrag_m`.

    Returns
    -------
    Income by unemployment insurance before tax.

    """
    out = (
        einkommen__bruttolohn_m
        + einkommen__sonstige_m
        + einkommen__aus_selbstständigkeit_m
        + einkommen__aus_vermietung_m
        + einkommen__bruttokapitaleinkommen_m
        + rente__altersrente__sum_private_gesetzl_rente_m
        + arbeitslosengeld__betrag_m
        + elterngeld__betrag_m
    )

    return out


@policy_function(end_date="2005-09-30")
def nettoquote_m(  # noqa: PLR0913
    einkommen__bruttolohn_m: float,
    eink_st_m_sn: float,
    soli_st_m_sn: float,
    demographic_vars__anzahl_personen_sn: int,
    sozialversicherungsbeitraege__betrag_arbeitnehmer_m: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate share of net to gross wage.

    Quotienten von bereinigtem Nettoeinkommen und Bruttoeinkommen. § 3 Abs. 2 Alg II-V.

    Parameters
    ----------
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.
    eink_st_m_sn
        See :func:`eink_st_m_sn`.
    soli_st_m_sn
        See :func:`soli_st_m_sn`.
    demographic_vars__anzahl_personen_sn
        See :func:`demographic_vars__anzahl_personen_sn`.
    sozialversicherungsbeitraege__betrag_arbeitnehmer_m
        See :func:`sozialversicherungsbeitraege__betrag_arbeitnehmer_m`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    # Bereinigtes monatliches Einkommen aus Erwerbstätigkeit nach § 11 Abs. 2 Nr. 1-5.
    alg2_2005_bne = max(
        (
            einkommen__bruttolohn_m
            - (eink_st_m_sn / demographic_vars__anzahl_personen_sn)
            - (soli_st_m_sn / demographic_vars__anzahl_personen_sn)
            - sozialversicherungsbeitraege__betrag_arbeitnehmer_m
            - arbeitsl_geld_2_params["abzugsfähige_pausch"]["werbung"]
            - arbeitsl_geld_2_params["abzugsfähige_pausch"]["versicherung"]
        ),
        0,
    )

    return alg2_2005_bne / einkommen__bruttolohn_m


@policy_function(
    end_date="2005-09-30",
    leaf_name="anrechnungsfreies_einkommen_m",
)
def anrechnungsfreies_einkommen_m_basierend_auf_nettoquote(
    einkommen__bruttolohn_m: float,
    nettoquote_m: float,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Share of income which remains to the individual.

    Parameters
    ----------
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.
    nettoquote_m
        See :func:`nettoquote_m`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    out = piecewise_polynomial(
        x=einkommen__bruttolohn_m,
        thresholds=arbeitsl_geld_2_params["eink_anr_frei"]["thresholds"],
        rates=arbeitsl_geld_2_params["eink_anr_frei"]["rates"],
        intercepts_at_lower_thresholds=arbeitsl_geld_2_params["eink_anr_frei"][
            "intercepts_at_lower_thresholds"
        ],
        rates_multiplier=nettoquote_m,
    )
    return out


@policy_function(start_date="2005-10-01")
def anrechnungsfreies_einkommen_m(
    einkommen__bruttolohn_m: float,
    einkommen__aus_selbstständigkeit_m: float,
    demographic_vars__anzahl_kinder_bis_17_bg: int,
    einkommensteuer__freibetraege__kinderfreibetrag_anzahl_ansprüche: int,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate share of income, which remains to the individual since 10/2005.

    Note: Since 2023, Arbeitslosengeld 2 is referred to as Bürgergeld.
    Sozialgesetzbuch (SGB) Zweites Buch (II) - Bürgergeld, Grundsicherung für
    Arbeitsuchende. SGB II §11b Abs 3
    https://www.gesetze-im-internet.de/sgb_2/__11b.html

    Parameters
    ----------
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.
    einkommen__aus_selbstständigkeit_m
        See basic input variable :ref:`einkommen__aus_selbstständigkeit_m <einkommen__aus_selbstständigkeit_m>`.
    demographic_vars__anzahl_kinder_bis_17_bg
        See :func:`demographic_vars__anzahl_kinder_bis_17_bg`.
    einkommensteuer__freibetraege__kinderfreibetrag_anzahl_ansprüche
        See :func:
        `einkommensteuer__freibetraege__kinderfreibetrag_anzahl_ansprüche`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    # Beneficiaries who live with a minor child in a group home or who have a minor
    # child have slightly different thresholds. We currently do not consider the second
    # condition.
    eink_erwerbstätigkeit = einkommen__bruttolohn_m + einkommen__aus_selbstständigkeit_m

    if (
        demographic_vars__anzahl_kinder_bis_17_bg > 0
        or einkommensteuer__freibetraege__kinderfreibetrag_anzahl_ansprüche > 0
    ):
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
