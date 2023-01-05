from math import trunc

from _gettsim.shared import add_rounding_spec
from _gettsim.taxes.eink_st import _eink_st_tarif


@add_rounding_spec(params_key="lohn_st")
def lohn_st_eink(
    bruttolohn_m: float,
    steuerklasse: int,
    eink_st_abzuege_params: dict,
    vorsorgepauschale: float,
) -> float:
    """Calculates taxable income for lohnsteuer.

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
        sonderausgaben = eink_st_abzuege_params["sonderausgabenpauschbetrag"]["single"]

    # zu versteuerndes Einkommen / tax base for Lohnsteuer
    out = max(
        12 * bruttolohn_m
        - werbungskosten
        - sonderausgaben
        - entlastung_freibetrag_alleinerz
        - vorsorgepauschale,
        0.0,
    )

    return out


def _lohnsteuer_klasse5_6_basis(taxable_inc: float, eink_st_params: dict) -> float:
    """Calculates base for Lst for Steuerklasse 5 and 6.

    §39 b Absatz 2 Satz 7 (part 1):
        Jahreslohnsteuer die sich aus dem Zweifachen des Unterschiedsbetrags zwischen
    dem Steuerbetrag für das Eineinviertelfache und dem Steuerbetrag für das
    Dreiviertelfache des zu versteuernden Jahresbetrags nach § 32a Absatz 1 ergibt;
    die Jahreslohnsteuer beträgt jedoch mindestens 14 Prozent des zu versteuernden
    Jahresbetrags.

    Parameters
    ----------

    x
        Taxable Income used in function (not necessarily the same as lohn_st_eink)
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`

    Returns
    -------
    Base for Lohnsteuer for Steuerklasse 5 and 6

    """

    out = max(
        2
        * (
            trunc(_eink_st_tarif(taxable_inc * 1.25, eink_st_params))
            - trunc(_eink_st_tarif(taxable_inc * 0.75, eink_st_params))
        ),
        trunc(taxable_inc * eink_st_params["eink_st_tarif"]["rates"][0][1]),
    )

    return out


def lohn_st_m(
    lohn_st_eink: float,
    eink_st_params: dict,
    lohn_st_params: dict,
    steuerklasse: int,
) -> float:
    """
    Calculates Lohnsteuer = withholding tax on earnings,
    paid monthly by the employer on behalf of the employee.
    Apply the income tax tariff, but individually and with different
    exemptions, determined by the 'Steuerklasse'.
    Source: §39b EStG

    Caluclation is differentiated by steuerklasse

    1,2,4: Standard tariff (§32a (1) EStG)
    3: Splitting tariff (§32a (5) EStG)
    5,6: Take twice the difference between applying the tariff on 5/4 and 3/4
          of taxable income. Tax rate may not be lower than the
          starting statutory one.
    Parameters
    ----------
    lohn_st_eink
        See :func:`lohn_st_eink`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`
    lohn_st_params
        See params documentation :ref:`lohn_st_params <lohn_st_params>`
    steuerklasse:
        See :func:`steuerklasse`

    Returns
    -------
    Individual withholding tax on annual basis
    """

    lohnsteuer_basistarif = _eink_st_tarif(lohn_st_eink, eink_st_params)
    lohnsteuer_splittingtarif = 2 * _eink_st_tarif(lohn_st_eink / 2, eink_st_params)
    lohnsteuer_5_6_basis = _lohnsteuer_klasse5_6_basis(lohn_st_eink, eink_st_params)

    grenze_1 = lohn_st_params["lohn_st_einkommensgrenzen"][0]
    grenze_2 = lohn_st_params["lohn_st_einkommensgrenzen"][1]
    grenze_3 = lohn_st_params["lohn_st_einkommensgrenzen"][2]

    if lohn_st_eink < grenze_1:
        lohnsteuer_klasse5_6 = lohnsteuer_5_6_basis
    elif grenze_1 <= lohn_st_eink < grenze_2:
        lohnsteuer_grenze_1 = _lohnsteuer_klasse5_6_basis(grenze_1, eink_st_params)
        max_lohnsteuer = (
            lohnsteuer_grenze_1
            + (lohn_st_eink - grenze_1) * eink_st_params["eink_st_tarif"]["rates"][0][3]
        )
        max_lohnsteuer = trunc(max_lohnsteuer)
        lohnsteuer_klasse5_6 = min(
            max_lohnsteuer, _lohnsteuer_klasse5_6_basis(lohn_st_eink, eink_st_params)
        )
    elif grenze_2 <= lohn_st_eink < grenze_3:
        lohnsteuer_grenze_2 = _lohnsteuer_klasse5_6_basis(grenze_2, eink_st_params)
        lohnsteuer_klasse5_6 = (
            lohnsteuer_grenze_2
            + (lohn_st_eink - grenze_2) * eink_st_params["eink_st_tarif"]["rates"][0][3]
        )
        trunc(lohnsteuer_klasse5_6)
    else:
        lohnsteuer_grenze_2 = _lohnsteuer_klasse5_6_basis(grenze_2, eink_st_params)
        lohnsteuer_zw_grenze_2_3 = (grenze_3 - grenze_2) * eink_st_params[
            "eink_st_tarif"
        ]["rates"][0][3]
        lohnsteuer_klasse5_6 = lohnsteuer_grenze_2 + lohnsteuer_zw_grenze_2_3
        lohnsteuer_klasse5_6 = trunc(lohnsteuer_klasse5_6)
        lohnsteuer_klasse5_6 = (
            lohnsteuer_klasse5_6
            + (lohn_st_eink - grenze_3) * eink_st_params["eink_st_tarif"]["rates"][0][4]
        )
        lohnsteuer_klasse5_6 = trunc(lohnsteuer_klasse5_6)

    if steuerklasse in (1, 2, 4):
        out = lohnsteuer_basistarif
    elif steuerklasse == 3:
        out = lohnsteuer_splittingtarif
    else:
        out = lohnsteuer_klasse5_6

    out = trunc(out / 12)

    return max(out, 0.0)


@add_rounding_spec(params_key="lohn_st")
def vorsorgepauschale_ab_2010(
    bruttolohn_m: float,
    steuerklasse: int,
    eink_st_abzuege_params: dict,
    soz_vers_beitr_params: dict,
    wohnort_ost: bool,
    ges_krankenv_zusatzbeitrag: float,
) -> float:
    """Calculates Vorsorgepauschale for Lohnsteuer valid since 2010 Those are deducted
    from gross earnings. Idea is similar, but not identical, to Vorsorgeaufwendungen
    used when calculating Einkommensteuer.

    Parameters
    ----------
    bruttolohn_m:
      See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    steuerklasse:
      See :func:`steuerklasse`
    eink_st_abzuege_params:
      See params documentation :ref:`eink_st_abzuege_params`
    soz_vers_beitr_params:
        See params documentation :ref:`soz_vers_beitr_params`
    wohnort_ost:
      See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
    ges_krankenv_zusatzbeitrag
        See :func:ges_krankenv_zusatzbeitrag`.


    Returns
    -------
    Individual Vorsorgepauschale on annual basis

    """

    # 1. Rentenversicherungsbeiträge, §39b (2) Nr. 3a EStG.
    if wohnort_ost:
        bruttolohn_rente = min(12 * bruttolohn_m, 81000)
    else:
        bruttolohn_rente = min(12 * bruttolohn_m, 84600)

    vorsorg_rv = (
        bruttolohn_rente
        * soz_vers_beitr_params["beitr_satz"]["ges_rentenv"]
        * eink_st_abzuege_params["vorsorge_pauschale_rv_anteil"]
    )

    # 2. Krankenversicherungsbeiträge, §39b (2) Nr. 3b EStG.
    # For health care deductions, there are two ways to calculate.
    # a) at least 12% of earnings of earnings can be deducted,
    #    but only up to a certain threshold

    bruttolohn_kv = min(12 * bruttolohn_m, 58050)
    vorsorg_kv_option_a_basis = (
        eink_st_abzuege_params["vorsorgepauschale_mindestanteil"] * bruttolohn_kv
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

    vorsorg_kv_option_b = bruttolohn_kv * (
        soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["ermäßigt"] / 2
        + ges_krankenv_zusatzbeitrag / 2 / 100
        + soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    # add both RV and KV deductions. For KV, take the larger amount.
    out = vorsorg_rv + max(vorsorg_kv_option_a, vorsorg_kv_option_b)
    return out


def vorsorgepauschale_2005_2010() -> float:
    """vorsorg_rv and vorsorg_kv_option_a are identical to after 2010."""

    out = 0
    return out


# Possible ToDo: Determine Steuerklasse endogenously.
# Right now, Steuerklasse is an input variable

# def steuerklasse_tu(
#     gemeinsam_veranlagt_tu: bool,
#     alleinerz_tu: bool,
#     bruttolohn_m: float,
#     eink_st_params: dict,
#     eink_st_abzuege_params: dict,
# ) -> int:
#     """Determine Lohnsteuerklassen (also called 'tax brackets')
#     if not delivered by the user.
#     They determine the basic allowance for the withholding tax.

#     Tax brackets are predetermined for singles and single parents.
#     Married couples can choose between the combinations 4/4, 3/5 and 5/3.
#     We assume the following:
#         -  If one of the spouses earns less than the income tax allowance,
#            this is essentially a single-earner couple. The spouse with the higher
#            income is assigned tax bracket 3, the other spouse tax bracket 5.
#         - In all other cases, we assign tax bracket 4 to both spouses.

#     1: Single
#     2: Single Parent
#     3: One spouse in married couple who receives allowance of both partners.
#        Makes sense primarily for Single-Earner Households
#     4: Both spouses receive their individual allowance
#     5: If one spouse chooses 3, the other has to choose 5,
#        which means no allowance.
#     6: Additional Job...not modelled yet, as we do not
#     distinguish between different jobs

#     Parameters
#     ----------
#     gemeinsam_veranlagt_tu: bool
#         Return of :func:`gemeinsam_veranlagt_tu`.
#     alleinerz_tu: bool
#         See basic input variable :ref:`alleinerz_tu <alleinerz_tu>`.
#     bruttolohn_m: float
#         See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
#     eink_st_params:
#         See params documentation :ref:`eink_st_params <eink_st_params>`
#     eink_st_abzuege_params:
#      See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`

#     Returns
#     ----------
#     steuerklasse: int
#         The steuerklasse for each person in the tax unit
#     """

#     bruttolohn_max = max(bruttolohn_m)
#     bruttolohn_min = min(bruttolohn_m)

#     einkommensgrenze_zweitverdiener = (
#         eink_st_params["eink_st_tarif"]["thresholds"][1]
#         + eink_st_abzuege_params["werbungskostenpauschale"]
#     )
#     alleinverdiener_paar = (
#         (bruttolohn_min <= einkommensgrenze_zweitverdiener / 12)
#         & (bruttolohn_max > 0)
#         & (gemeinsam_veranlagt_tu)
#     )
#     cond_steuerklasse1 = (~gemeinsam_veranlagt_tu) & ~alleinerz_tu
#     cond_steuerklasse2 = alleinerz_tu
#     cond_steuerklasse3 = alleinverdiener_paar & (
#         bruttolohn_m > einkommensgrenze_zweitverdiener / 12
#     )
#     cond_steuerklasse4 = (gemeinsam_veranlagt_tu) & (~alleinverdiener_paar)
#     cond_steuerklasse5 = alleinverdiener_paar & (
#         bruttolohn_m <= einkommensgrenze_zweitverdiener / 12
#     )
#     steuerklasse = (
#         1 * cond_steuerklasse1
#         + 2 * cond_steuerklasse2
#         + 3 * cond_steuerklasse3
#         + 4 * cond_steuerklasse4
#         + 5 * cond_steuerklasse5
#     )

#     return steuerklasse
