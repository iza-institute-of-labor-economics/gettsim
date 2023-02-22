from math import trunc

from _gettsim.shared import add_rounding_spec
from _gettsim.taxes.eink_st import _eink_st_tarif


@add_rounding_spec(params_key="lohnst")
def lohnst_eink(
    bruttolohn_m: float,
    steuerklasse: int,
    eink_st_abzuege_params: dict,
    vorsorgepauschale: float,
) -> float:
    """Calculate tax base for Lohnsteuer (withholding tax on earnings).

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

    # Zu versteuerndes Einkommen / tax base for Lohnsteuer.
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
    """Calculate base for Lst for Steuerklasse 5 and 6.

    §39 b Absatz 2 Satz 7 (part 1):

        Jahreslohnsteuer die sich aus dem Zweifachen des Unterschiedsbetrags zwischen
        dem Steuerbetrag für das Eineinviertelfache und dem Steuerbetrag für das
        Dreiviertelfache des zu versteuernden Jahresbetrags nach § 32a Absatz 1 ergibt;
        die Jahreslohnsteuer beträgt jedoch mindestens 14 Prozent des zu versteuernden
        Jahresbetrags.

    Parameters
    ----------

    taxable_inc:
        Taxable Income used in function (not necessarily the same as lohnst_eink)
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


def lohnst_m(
    lohnst_eink: float,
    eink_st_params: dict,
    lohnst_params: dict,
    steuerklasse: int,
) -> float:
    """
    Calculates Lohnsteuer (withholding tax on earnings), paid monthly by the employer on
    behalf of the employee. Apply the income tax tariff, but individually and with
    different exemptions, determined by the 'Steuerklasse'. Source: §39b EStG

    Calculation is differentiated by steuerklasse:

    1,2,4: Standard tariff (§32a (1) EStG) 3: Splitting tariff (§32a (5) EStG) 5,6: Take
    twice the difference between applying the tariff on 5/4 and 3/4 of taxable income.
    Tax rate may not be lower than the starting statutory one.

    Parameters
    ----------
    lohnst_eink
        See :func:`lohnst_eink`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`
    lohnst_params
        See params documentation :ref:`lohnst_params <lohnst_params>`
    steuerklasse:
        See basic input variable :ref:`steuerklasse <steuerklasse>`.

    Returns
    -------
    Individual withholding tax on annual basis
    """

    lohnsteuer_basistarif = _eink_st_tarif(lohnst_eink, eink_st_params)
    lohnsteuer_splittingtarif = 2 * _eink_st_tarif(lohnst_eink / 2, eink_st_params)
    lohnsteuer_5_6_basis = _lohnsteuer_klasse5_6_basis(lohnst_eink, eink_st_params)

    grenze_1 = lohnst_params["lohnst_einkommensgrenzen"][0]
    grenze_2 = lohnst_params["lohnst_einkommensgrenzen"][1]
    grenze_3 = lohnst_params["lohnst_einkommensgrenzen"][2]

    lohnsteuer_grenze_1 = _lohnsteuer_klasse5_6_basis(grenze_1, eink_st_params)
    max_lohnsteuer = trunc(
        lohnsteuer_grenze_1
        + (lohnst_eink - grenze_1) * eink_st_params["eink_st_tarif"]["rates"][0][3]
    )
    lohnsteuer_grenze_2 = _lohnsteuer_klasse5_6_basis(grenze_2, eink_st_params)
    lohnsteuer_zw_grenze_2_3 = (grenze_3 - grenze_2) * eink_st_params["eink_st_tarif"][
        "rates"
    ][0][3]
    lohnsteuer_klasse5_6_tmp = trunc(lohnsteuer_grenze_2 + lohnsteuer_zw_grenze_2_3)

    if lohnst_eink < grenze_1:
        lohnsteuer_klasse5_6 = lohnsteuer_5_6_basis
    elif grenze_1 <= lohnst_eink < grenze_2:
        lohnsteuer_klasse5_6 = min(
            max_lohnsteuer, _lohnsteuer_klasse5_6_basis(lohnst_eink, eink_st_params)
        )
    elif grenze_2 <= lohnst_eink < grenze_3:
        lohnsteuer_klasse5_6 = trunc(
            lohnsteuer_grenze_2
            + (lohnst_eink - grenze_2) * eink_st_params["eink_st_tarif"]["rates"][0][3]
        )
    else:
        lohnsteuer_klasse5_6 = trunc(
            lohnsteuer_klasse5_6_tmp
            + (lohnst_eink - grenze_3) * eink_st_params["eink_st_tarif"]["rates"][0][4]
        )

    if steuerklasse in (1, 2, 4):
        out = lohnsteuer_basistarif
    elif steuerklasse == 3:
        out = lohnsteuer_splittingtarif
    else:
        out = lohnsteuer_klasse5_6

    out = out / 12

    return max(out, 0.0)


@add_rounding_spec(params_key="lohnst")
def vorsorgepauschale_ab_2010(  # noqa: PLR0913
    bruttolohn_m: float,
    steuerklasse: int,
    wohnort_ost: bool,
    ges_krankenv_zusatzbeitrag: float,
    ges_pflegev_zusatz_kinderlos: bool,
    eink_st_abzuege_params: dict,
    soz_vers_beitr_params: dict,
) -> float:
    """Calculate Vorsorgepauschale for Lohnsteuer valid since 2010. Those are deducted
    from gross earnings. Idea is similar, but not identical, to Vorsorgeaufwendungen
    used when calculating Einkommensteuer.

    Parameters
    ----------
    bruttolohn_m:
      See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    steuerklasse:
      See :func:`steuerklasse`
    ges_pflegev_zusatz_kinderlos:
      See :func:`ges_pflegev_zusatz_kinderlos`
    wohnort_ost:
      See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
    ges_krankenv_zusatzbeitrag
        See :func:ges_krankenv_zusatzbeitrag`.
    eink_st_abzuege_params:
      See params documentation :ref:`eink_st_abzuege_params`
    soz_vers_beitr_params:
        See params documentation :ref:`soz_vers_beitr_params`


    Returns
    -------
    Individual Vorsorgepauschale on annual basis

    """

    # 1. Rentenversicherungsbeiträge, §39b (2) Nr. 3a EStG.
    if wohnort_ost:
        bruttolohn_rente = min(
            12 * bruttolohn_m,
            12 * soz_vers_beitr_params["beitr_bemess_grenze_m"]["ges_rentenv"]["ost"],
        )
    else:
        bruttolohn_rente = min(
            12 * bruttolohn_m,
            12 * soz_vers_beitr_params["beitr_bemess_grenze_m"]["ges_rentenv"]["west"],
        )

    vorsorg_rv = (
        bruttolohn_rente
        * soz_vers_beitr_params["beitr_satz"]["ges_rentenv"]
        * eink_st_abzuege_params["vorsorgepauschale_rv_anteil"]
    )

    # 2. Krankenversicherungsbeiträge, §39b (2) Nr. 3b EStG.
    # For health care deductions, there are two ways to calculate.
    # a) at least 12% of earnings of earnings can be deducted,
    #    but only up to a certain threshold

    bruttolohn_kv = min(
        12 * bruttolohn_m,
        12 * soz_vers_beitr_params["beitr_bemess_grenze_m"]["ges_krankenv"]["ost"],
    )
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

    if ges_pflegev_zusatz_kinderlos:
        beitr_satz_pflegev = (
            soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
            + soz_vers_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]
        )
    else:
        beitr_satz_pflegev = soz_vers_beitr_params["beitr_satz"]["ges_pflegev"][
            "standard"
        ]

    vorsorg_kv_option_b = bruttolohn_kv * (
        soz_vers_beitr_params["beitr_satz"]["ges_krankenv"]["ermäßigt"] / 2
        + ges_krankenv_zusatzbeitrag / 2 / 100
        + beitr_satz_pflegev
    )

    # add both RV and KV deductions. For KV, take the larger amount.
    out = vorsorg_rv + max(vorsorg_kv_option_a, vorsorg_kv_option_b)
    return out


@add_rounding_spec(params_key="lohnst")
def vorsorgepauschale_ab_2005_bis_2009() -> float:
    """vorsorg_rv and vorsorg_kv_option_a are identical to after 2010."""

    out = 0.0
    return out


def kinderfreib_für_soli_st_lohnst(
    steuerklasse: int,
    anz_kinder_mit_kindergeld_tu: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate Child Allowance for Lohnsteuer-Soli.

    For the purpose of Soli on Lohnsteuer, the child allowance not only depends on the
    number of children, but also on the steuerklasse.

    """

    kinderfreib_basis = (
        eink_st_abzuege_params["kinderfreib"]["sächl_existenzmin"]
        + eink_st_abzuege_params["kinderfreib"]["beitr_erz_ausb"]
    )

    # For certain tax brackets, twice the child allowance can be deducted
    if steuerklasse == 1 | steuerklasse == 2 | steuerklasse == 3:
        out = kinderfreib_basis * 2 * anz_kinder_mit_kindergeld_tu
    elif steuerklasse == 4:
        out = kinderfreib_basis * anz_kinder_mit_kindergeld_tu
    else:
        out = 0
    return out


def lohnst_mit_kinderfreib(
    lohnst_eink: float,
    kinderfreib_für_soli_st_lohnst: float,
    steuerklasse: int,
    eink_st_params: dict,
) -> float:
    """Calculate Lohnsteuer with the tax base taking child allowance into account,
    otherwise identical to :func:`lohnst_m`.

    """

    eink = max(lohnst_eink - kinderfreib_für_soli_st_lohnst, 0)
    lohnsteuer_basistarif = _eink_st_tarif(eink, eink_st_params)
    lohnsteuer_splittingtarif = 2 * _eink_st_tarif(eink / 2, eink_st_params)
    lohnsteuer_klasse5_6 = max(
        2
        * (
            _eink_st_tarif(eink * 1.25, eink_st_params)
            - _eink_st_tarif(eink * 0.75, eink_st_params)
        ),
        eink * eink_st_params["eink_st_tarif"]["rates"][0][1],
    )

    if steuerklasse in (1, 2, 4):
        out = lohnsteuer_basistarif
    elif steuerklasse == 3:
        out = lohnsteuer_splittingtarif
    else:
        out = lohnsteuer_klasse5_6

    return out


# Possible ToDo: Determine Steuerklasse endogenously.
# Right now, Steuerklasse is an input variable

# def steuerklasse(
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
#         Return of :func:`gemeinsam_veranlagt_tu`.
#         See basic input variable :ref:`alleinerz_tu <alleinerz_tu>`.
#         See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
#     eink_st_params:
#         See params documentation :ref:`eink_st_params <eink_st_params>`
#     eink_st_abzuege_params:
#      See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`

#     Returns
#     ----------
#         The steuerklasse for each person in the tax unit
#     """


#         & (bruttolohn_max > 0)
#         & (gemeinsam_veranlagt_tu)
#         bruttolohn_m > einkommensgrenze_zweitverdiener / 12
#         1 * cond_steuerklasse1
#         + 2 * cond_steuerklasse2
#         + 3 * cond_steuerklasse3
#         + 4 * cond_steuerklasse4
#         + 5 * cond_steuerklasse5
