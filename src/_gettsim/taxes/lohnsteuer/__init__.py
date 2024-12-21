"""Withholding tax on earnings (Lohnsteuer)."""

from _gettsim.taxes.einkommensteuer import einkommensteuer_tarif


def lohnst_m(
    lohnst_eink_y: float,
    eink_st_params: dict,
    lohnst_params: dict,
    steuerklasse: int,
) -> float:
    """
    Calls _lohnst_m with individual income
    """
    return _lohnst_m(lohnst_eink_y, eink_st_params, lohnst_params, steuerklasse)


def lohnst_mit_kinderfreib_m(
    lohnst_eink_y: float,
    kinderfreib_für_soli_st_lohnst_y: float,
    eink_st_params: dict,
    lohnst_params: dict,
    steuerklasse: int,
) -> float:
    """
    Same as lohnst_m, but with an alternative income definition that
    takes child allowance into account. Important only for calculation
    of soli on Lohnsteuer!
    """

    eink = max(lohnst_eink_y - kinderfreib_für_soli_st_lohnst_y, 0)

    return _lohnst_m(eink, eink_st_params, lohnst_params, steuerklasse)


def _lohnst_m(
    lohnst_eink_y: float, eink_st_params: dict, lohnst_params: dict, steuerklasse: int
) -> float:
    """
    Calculates Lohnsteuer (withholding tax on earnings), paid monthly by the employer on
    behalf of the employee. Apply the income tax tariff, but individually and with
    different exemptions, determined by the 'Steuerklasse'. Source: §39b EStG

    Calculation is differentiated by steuerklasse

    1,2,4: Standard tariff (§32a (1) EStG) 3: Splitting tariff (§32a (5) EStG) 5,6: Take
    twice the difference between applying the tariff on 5/4 and 3/4 of taxable income.
    Tax rate may not be lower than the starting statutory one.

    Parameters
    ----------
    lohnst_eink_y
        See :func:`lohnst_eink_y`.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`
    lohnst_params
        See params documentation :ref:`lohnst_params <lohnst_params>`
    steuerklasse:
        See basic input variable :ref:`steuerklasse <steuerklasse>`.


    Returns
    -------
    Individual withholding tax on monthly basis

    """

    lohnsteuer_basistarif = einkommensteuer_tarif(lohnst_eink_y, eink_st_params)
    lohnsteuer_splittingtarif = 2 * einkommensteuer_tarif(
        lohnst_eink_y / 2, eink_st_params
    )
    lohnsteuer_5_6_basis = _lohnsteuer_klasse5_6_basis_y(lohnst_eink_y, eink_st_params)

    grenze_1 = lohnst_params["lohnst_einkommensgrenzen"][0]
    grenze_2 = lohnst_params["lohnst_einkommensgrenzen"][1]
    grenze_3 = lohnst_params["lohnst_einkommensgrenzen"][2]

    lohnsteuer_grenze_1 = _lohnsteuer_klasse5_6_basis_y(grenze_1, eink_st_params)
    max_lohnsteuer = (
        lohnsteuer_grenze_1
        + (lohnst_eink_y - grenze_1) * eink_st_params["eink_st_tarif"]["rates"][0][3]
    )
    lohnsteuer_grenze_2 = _lohnsteuer_klasse5_6_basis_y(grenze_2, eink_st_params)
    lohnsteuer_zw_grenze_2_3 = (grenze_3 - grenze_2) * eink_st_params["eink_st_tarif"][
        "rates"
    ][0][3]
    lohnsteuer_klasse5_6_tmp = lohnsteuer_grenze_2 + lohnsteuer_zw_grenze_2_3

    if lohnst_eink_y < grenze_1:
        lohnsteuer_klasse5_6 = lohnsteuer_5_6_basis
    elif grenze_1 <= lohnst_eink_y < grenze_2:
        lohnsteuer_klasse5_6 = min(
            max_lohnsteuer, _lohnsteuer_klasse5_6_basis_y(lohnst_eink_y, eink_st_params)
        )
    elif grenze_2 <= lohnst_eink_y < grenze_3:
        lohnsteuer_klasse5_6 = (
            lohnsteuer_grenze_2
            + (lohnst_eink_y - grenze_2)
            * eink_st_params["eink_st_tarif"]["rates"][0][3]
        )
    else:
        lohnsteuer_klasse5_6 = (
            lohnsteuer_klasse5_6_tmp
            + (lohnst_eink_y - grenze_3)
            * eink_st_params["eink_st_tarif"]["rates"][0][4]
        )

    if steuerklasse in {1, 2, 4}:
        out = lohnsteuer_basistarif
    elif steuerklasse == 3:
        out = lohnsteuer_splittingtarif
    else:
        out = lohnsteuer_klasse5_6

    out = out / 12

    return max(out, 0.0)


def _lohnsteuer_klasse5_6_basis_y(taxable_inc: float, eink_st_params: dict) -> float:
    """Calculate base for Lohnsteuer for Steuerklasse 5 and 6, by applying
    obtaining twice the difference between applying the factors 1.25 and 0.75
    to the lohnsteuer payment. There is a also a minimum amount, which is checked
    afterwards.

    §39 b Absatz 2 Satz 7 (part 1):

        Jahreslohnsteuer die sich aus dem Zweifachen des Unterschiedsbetrags zwischen
        dem Steuerbetrag für das Eineinviertelfache und dem Steuerbetrag für das
        Dreiviertelfache des zu versteuernden Jahresbetrags nach § 32a Absatz 1 ergibt;
        die Jahreslohnsteuer beträgt jedoch mindestens 14 Prozent des zu versteuernden
        Jahresbetrags.

    Parameters
    ----------

    taxable_inc:
        Taxable Income used in function (not necessarily the same as lohnst_eink_y)
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`

    Returns
    -------
    Base for Lohnsteuer for Steuerklasse 5 and 6

    """

    out = max(
        2
        * (
            einkommensteuer_tarif(taxable_inc * 1.25, eink_st_params)
            - einkommensteuer_tarif(taxable_inc * 0.75, eink_st_params)
        ),
        taxable_inc * eink_st_params["eink_st_tarif"]["rates"][0][1],
    )

    return out
