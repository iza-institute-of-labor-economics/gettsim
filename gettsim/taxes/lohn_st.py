from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.taxes.eink_st import _eink_st_tarif


def lohn_st_eink(
    bruttolohn_m: float,
    steuerklasse: int,
    eink_st_abzuege_params: dict,
    vorsorgepauschale: float,
) -> float:
    """Calculates taxable income for lohnsteuer

    Parameters
    ----------
    bruttolohn_m:
      See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    steuerklasse:
      See :func:`steuerklasse`
    eink_st_abzuege_params:
      See :func:`eink_st_abzuege_params`
    vorsorgepauschale
        See :func:`vorsorgepauschale`

    Returns
    -------

    """
    # WHY IS THIS 1908??
    entlastung_freibetrag_alleinerz = (steuerklasse == 2) * eink_st_abzuege_params[
        "alleinerz_freibetrag"
    ]

    if steuerklasse == 6:
        werbungskosten = 0
    else:
        werbungskosten = eink_st_abzuege_params["werbungskostenpauschale"]

    if steuerklasse == 6:
        sonderausgaben = 0
    else:
        sonderausgaben = eink_st_abzuege_params["sonderausgabenpauschbetrag"]

    # zu versteuerndes Einkommen / tax base for Lohnsteuer
    out = max(
        12 * bruttolohn_m
        - werbungskosten
        - sonderausgaben
        - entlastung_freibetrag_alleinerz
        - vorsorgepauschale,
        0,
    )

    return out


def lohn_st(lohn_st_eink: float, eink_st_params: dict, steuerklasse: int) -> float:
    """
    Calculates Lohnsteuer = withholding tax on earnings,
    paid monthly by the employer on behalf of the employee.
    Apply the income tax tariff, but individually and with different
    exemptions, determined by the 'Steuerklasse'.
    Source: §39b EStG

    Caluclation is differentiated by steuerklasse

    1,2,4: Standard tariff (§32a (1) EStG)
    3: Splitting tariff (§32a (5) EStG)
    5,6,: Take twice the difference between applying the tariff on 5/4 and 3/4
          of taxable income. Tax rate may not be lower than the
          starting statutory one.
    Parameters
    ----------
    lohn_st_eink
        See :func:`lohn_st_eink`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`
    steuerklasse


    Returns
    -------
    Individual withdrawal tax on annual basis
    """
    lohnsteuer_basistarif = _eink_st_tarif(lohn_st_eink, eink_st_params)
    lohnsteuer_splittingtarif = 2 * _eink_st_tarif(lohn_st_eink / 2, eink_st_params)
    lohnsteuer_klasse5_6 = max(
        2
        * (
            _eink_st_tarif(lohn_st_eink * 1.25, eink_st_params)
            - _eink_st_tarif(lohn_st_eink * 0.75, eink_st_params)
        ),
        lohn_st_eink * eink_st_params["eink_st_tarif"]["rates"][0][1],
    )

    if (steuerklasse == 1) | (steuerklasse == 2) | (steuerklasse == 4):
        out = lohnsteuer_basistarif
    elif steuerklasse == 3:
        out = lohnsteuer_splittingtarif
    else:
        out = lohnsteuer_klasse5_6

    return out


def vorsorgepauschale_ab_2010(
    bruttolohn_m: float,
    steuerklasse: int,
    vorsorg_rv_anteil: float,
    eink_st_abzuege_params: dict,
    krankenv_beitr_lohnsteuer: float,
    soz_vers_beitr_params: dict,
) -> float:
    """
    Calculates Vorsorgepauschale for Lohnsteuer valid since 2010
    Those are deducted from gross earnings.
    Idea is similar, but not identical, to Vorsorgeaufwendungen
    used when calculating Einkommensteuer.

    Parameters
    ----------
    bruttolohn_m:
      See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    steuerklasse:
      See :func:`steuerklasse`
    eink_st_abzuege_params:
      See params documentation :ref:`eink_st_abzuege_params`


    Returns
    -------
    Individual Vorsorgepauschale on annual basis
    """

    # 1. Rentenversicherungsbeiträge, §39b (2) Nr. 3a EStG.
    vorsorg_rv = (
        12
        * (bruttolohn_m * soz_vers_beitr_params["beitr_satz"]["ges_rentenv"])
        * vorsorg_rv_anteil
        * float(vorsorg_rv_anteil(eink_st_abzuege_params))
    )

    # 2. Krankenversicherungsbeiträge, §39b (2) Nr. 3b EStG.
    # For health care deductions, there are two ways to calculate.
    # a) at least 12% of earnings of earnings can be deducted,
    #    but only up to a certain threshold
    vorsorg_kv_option_a_basis = (
        eink_st_abzuege_params["vorsorgepauschale_mindestanteil"] * bruttolohn_m * 12
    )

    if steuerklasse == 3:
        vorsorg_kv_option_a_max = eink_st_abzuege_params["vorsorgepauschale_kv_max"][
            "stkl3"
        ]
    else:
        vorsorg_kv_option_a_max = eink_st_abzuege_params["vorsorgepauschale_kv_max"][
            "stkl_nicht3"
        ]

    vorsorg_kv_option_a = min(vorsorg_kv_option_a_max, vorsorg_kv_option_a_basis)
    # b) Take the actual contributions (usually the better option),
    #   but apply the reduced rate!
    vorsorg_kv_option_b = krankenv_beitr_lohnsteuer
    vorsorg_kv_option_b += (
        bruttolohn_m * soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )
    # add both RV and KV deductions. For KV, take the larger amount.
    out = vorsorg_rv + max(vorsorg_kv_option_a, vorsorg_kv_option_b * 12)

    return out


def vorsorgepauschale_2005_2010() -> float:
    """
    vorsorg_rv and vorsorg_kv_option_a are identical to after 2010
    """

    out = 0
    return out


def vorsorg_rv_anteil(eink_st_abzuege_params: dict, jahr: int):
    """
    Calculates the share of pension contributions to be deducted for Lohnsteuer
    increases by year

    Parameters
    ----------
    eink_st_abzuege_params

    Returns
    -------
    out: float
    """

    out = piecewise_polynomial(
        x=jahr,      
        thresholds=eink_st_abzuege_params["vorsorge_pauschale_rv_anteil"]["thresholds"],
        rates=eink_st_abzuege_params["vorsorge_pauschale_rv_anteil"]["rates"],
        intercepts_at_lower_thresholds=eink_st_abzuege_params[
            "vorsorge_pauschale_rv_anteil"
        ]["intercepts_at_lower_thresholds"],
    )

    return out


def steuerklasse(
    tu_id: int,
    gemeinsam_veranlagt: bool,
    alleinerziehend: bool,
    bruttolohn_m: float,
    eink_st_params: dict,
    eink_st_abzuege_params: dict,
) -> int:
    """Determine Lohnsteuerklassen (also called 'tax brackets')
    They determine the basic allowance for the withdrawal tax

    1: Single
    2: Single Parent
    3: One spouse in married couple who receives allowance of both partners.
       Makes sense primarily for Single-Earner Households
    4: Both spouses receive their individual allowance
    5: If one spouse chooses 3, the other has to choose 5,
       which means no allowance.
    6: Additional Job...not modelled yet, as we do not
    distinguish between different jobs

    Parameters
    ----------
    tu_id: int
        See basic input variable :ref:`tu_id <tu_id>`.
    gemeinsam_veranlagt: bool
        Return of :func:`gemeinsam_veranlagt`.
    alleinerziehend: bool
        See basic input variable :ref:`alleinerziehend <alleinerziehend>`.
    bruttolohn_m: float
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    eink_st_params:
        See params documentation :ref:`eink_st_params <eink_st_params>`
    eink_st_abzuege_params:
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`

    Returns
    ----------
    steuerklasse: int
        The steuerklasse for each person in the tax unit
    """

    bruttolohn_max = bruttolohn_m.groupby(tu_id).max()
    bruttolohn_min = bruttolohn_m.groupby(tu_id).min()
    # Determine Single Earner Couple:
    # If one of the spouses earns tax-free income, assume Single Earner Couple
    einkommensgrenze_zweitverdiener = (
        eink_st_params["eink_st_tarif"]["thresholds"][1]
        + eink_st_abzuege_params["werbungskostenpauschale"]
    )
    alleinverdiener_paar = (
        (bruttolohn_min <= einkommensgrenze_zweitverdiener / 12)
        & (bruttolohn_max > 0)
        & (gemeinsam_veranlagt)
    )
    cond_steuerklasse1 = (~gemeinsam_veranlagt) & ~alleinerziehend
    cond_steuerklasse2 = alleinerziehend
    cond_steuerklasse3 = alleinverdiener_paar & (
        bruttolohn_m > einkommensgrenze_zweitverdiener / 12
    )
    cond_steuerklasse4 = (gemeinsam_veranlagt) & (~alleinverdiener_paar)
    cond_steuerklasse5 = alleinverdiener_paar & (
        bruttolohn_m <= einkommensgrenze_zweitverdiener / 12
    )
    steuerklasse = (
        1 * cond_steuerklasse1
        + 2 * cond_steuerklasse2
        + 3 * cond_steuerklasse3
        + 4 * cond_steuerklasse4
        + 5 * cond_steuerklasse5
    )

    return steuerklasse
