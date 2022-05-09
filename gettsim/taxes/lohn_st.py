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
        "alleinerziehenden_freibetrag"
    ]

    werbungskosten = [
        eink_st_abzuege_params["werbungskostenpauschale"] if stkl != 6 else 0
        for stkl in steuerklasse
    ]
    sonderausgaben = [
        eink_st_abzuege_params["sonderausgabenpauschbetrag"] if stkl != 6 else 0
        for stkl in steuerklasse
    ]
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

    out = (
        (lohnsteuer_splittingtarif * (steuerklasse == 3))
        + (lohnsteuer_basistarif * (steuerklasse.isin([1, 2, 4])))
        + (lohnsteuer_klasse5_6 * (steuerklasse.isin([5, 6])))
    )

    return out


def vorsorgepauschale_ab_2010(
    bruttolohn_m: float,
    steuerklasse: int,
    vorsorg_rv_anteil: float,
    eink_st_abzuege_params: dict,
    ges_rentenv_beitr_regular_job: float,
    krankenv_beitr_lohnsteuer: float,
    _ges_pflegev_beitr_reg_beschäftigt: float,
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
    ges_rentenv_beitr_reg_beschäftigt:
      See :func:`ges_rentenv_beitr_regular_job`.
    _ges_pflegev_beitr_reg_beschäftigt
      See :func:`_ges_pflegev_beitr_reg_beschäftigt`.

    Returns
    -------
    Individual Vorsorgepauschale on annual basis
    """

    # 1. Rentenversicherungsbeiträge, §39b (2) Nr. 3a EStG.
    vorsorg_rv = 12 * ges_rentenv_beitr_regular_job * vorsorg_rv_anteil

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
    vorsorg_kv_option_b += _ges_pflegev_beitr_reg_beschäftigt
    # add both RV and KV deductions. For KV, take the larger amount.
    out = vorsorg_rv + max(vorsorg_kv_option_a, vorsorg_kv_option_b * 12)

    return out


def vorsorgepauschale_2005_2010() -> float:
    """
    vorsorg_rv and vorsorg_kv_option_a are identical to after 2010
    """

    out = 0
    return out


def vorsorg_rv_anteil(eink_st_abzuege_params: dict, year: int):
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
        x=year,
        thresholds=eink_st_abzuege_params["vorsorge_pauschale_rv_anteil"]["thresholds"],
        rates=eink_st_abzuege_params["vorsorge_pauschale_rv_anteil"]["rates"],
        intercepts_at_lower_thresholds=eink_st_abzuege_params[
            "vorsorge_pauschale_rv_anteil"
        ]["intercepts_at_lower_thresholds"],
    )

    return out
