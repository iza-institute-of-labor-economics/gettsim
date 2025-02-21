"""Withholding tax on earnings (Lohnsteuer)."""

from _gettsim.taxes.einkommensteuer import einkommensteuer_tarif
from _gettsim.taxes.einkommensteuer.solidaritaetszuschlag import (
    solidaritaetszuschlag_tarif,
)


def betrag_m(
    lohnsteuer__einkommen__betrag_y: float,
    eink_st_params: dict,
    steuerklasse: int,
    lohnst_params: dict,
) -> float:
    """
    Withholding tax on earnings (Lohnsteuer).

    Parameters
    ----------
    lohnsteuer__einkommen__betrag_y
        See :func:`lohnsteuer__einkommen__betrag_y`.
    steuerklasse
        See :func:`steuerklasse`.
    eink_st_params
        See params documentation :ref:`eink_st_params`.
    lohnst_params
        See params documentation :ref:`lohnst_params`.

    """
    return lohnsteuer_formel(
        lohnsteuer__einkommen__betrag_y, eink_st_params, lohnst_params, steuerklasse
    )


def betrag_mit_kinderfreib_m(
    lohnsteuer__einkommen__betrag_y: float,
    kinderfreibetrag_soli_y: float,
    steuerklasse: int,
    eink_st_params: dict,
    lohnst_params: dict,
) -> float:
    """Withholding tax taking child allowances into account.

    Same as betrag_m, but with an alternative income definition that
    takes child allowance into account. Important only for calculation
    of soli on Lohnsteuer!

    Parameters
    ----------
    lohnsteuer__einkommen__betrag_y
        See :func:`lohnsteuer__einkommen__betrag_y`.
    kinderfreibetrag_soli_y
        See :func:`kinderfreibetrag_soli_y`.
    steuerklasse
        See :func:`steuerklasse`.
    eink_st_params
        See params documentation :ref:`eink_st_params`.
    lohnst_params
        See params documentation :ref:`lohnst_params`.
    """

    eink = max(lohnsteuer__einkommen__betrag_y - kinderfreibetrag_soli_y, 0)

    return lohnsteuer_formel(eink, eink_st_params, lohnst_params, steuerklasse)


def betrag_soli_y(betrag_mit_kinderfreib_y: float, soli_st_params: dict) -> float:
    """Solidarity surcharge on Lohnsteuer (withholding tax on earnings).

    Parameters
    ----------
    betrag_mit_kinderfreib_y
        See :func:`betrag_mit_kinderfreib_y`.
    soli_st_params
        See params documentation :ref:`soli_st_params <soli_st_params>`.

    Returns
        Solidarity Surcharge on Lohnsteuer
    -------

    """

    return solidaritaetszuschlag_tarif(betrag_mit_kinderfreib_y, soli_st_params)


def kinderfreibetrag_soli_y(
    steuerklasse: int,
    einkommensteuer__freibetraege__kinderfreibetrag__anzahl_ansprüche: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Child Allowance (Kinderfreibetrag) for Lohnsteuer-Soli.

    For the purpose of Soli on Lohnsteuer, the child allowance not only depends on the
    number of children, but also on the steuerklasse

    Parameters
    ----------
    steuerklasse
        See :func:`steuerklasse`.
    einkommensteuer__freibetraege__kinderfreibetrag__anzahl_ansprüche
        See :func:`einkommensteuer__freibetraege__kinderfreibetrag__anzahl_ansprüche`.
    eink_st_abzuege_params
        See params documenation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------
    Kinderfreibetrag for Lohnsteuer-Soli.
    """

    kinderfreib_basis = (
        eink_st_abzuege_params["kinderfreib"]["sächl_existenzmin"]
        + eink_st_abzuege_params["kinderfreib"]["beitr_erz_ausb"]
    )

    # For certain tax brackets, twice the child allowance can be deducted
    if steuerklasse in {1, 2, 3}:
        out = (
            kinderfreib_basis
            * 2
            * einkommensteuer__freibetraege__kinderfreibetrag__anzahl_ansprüche
        )
    elif steuerklasse == 4:
        out = (
            kinderfreib_basis
            * einkommensteuer__freibetraege__kinderfreibetrag__anzahl_ansprüche
        )
    else:
        out = 0
    return out


def lohnsteuer_formel(
    lohnsteuer__einkommen__betrag_y: float,
    eink_st_params: dict,
    lohnst_params: dict,
    steuerklasse: int,
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
    lohnsteuer__einkommen__betrag_y
        See :func:`lohnsteuer__einkommen__betrag_y`.
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

    lohnsteuer_basistarif = einkommensteuer_tarif(
        lohnsteuer__einkommen__betrag_y, eink_st_params
    )
    lohnsteuer_splittingtarif = 2 * einkommensteuer_tarif(
        lohnsteuer__einkommen__betrag_y / 2, eink_st_params
    )
    lohnsteuer_5_6_basis = _lohnsteuer_klasse5_6_basis_y(
        lohnsteuer__einkommen__betrag_y, eink_st_params
    )

    grenze_1 = lohnst_params["lohnst_einkommensgrenzen"][0]
    grenze_2 = lohnst_params["lohnst_einkommensgrenzen"][1]
    grenze_3 = lohnst_params["lohnst_einkommensgrenzen"][2]

    lohnsteuer_grenze_1 = _lohnsteuer_klasse5_6_basis_y(grenze_1, eink_st_params)
    max_lohnsteuer = (
        lohnsteuer_grenze_1
        + (lohnsteuer__einkommen__betrag_y - grenze_1)
        * eink_st_params["eink_st_tarif"]["rates"][0][3]
    )
    lohnsteuer_grenze_2 = _lohnsteuer_klasse5_6_basis_y(grenze_2, eink_st_params)
    lohnsteuer_zw_grenze_2_3 = (grenze_3 - grenze_2) * eink_st_params["eink_st_tarif"][
        "rates"
    ][0][3]
    lohnsteuer_klasse5_6_tmp = lohnsteuer_grenze_2 + lohnsteuer_zw_grenze_2_3

    if lohnsteuer__einkommen__betrag_y < grenze_1:
        lohnsteuer_klasse5_6 = lohnsteuer_5_6_basis
    elif grenze_1 <= lohnsteuer__einkommen__betrag_y < grenze_2:
        lohnsteuer_klasse5_6 = min(
            max_lohnsteuer,
            _lohnsteuer_klasse5_6_basis_y(
                lohnsteuer__einkommen__betrag_y, eink_st_params
            ),
        )
    elif grenze_2 <= lohnsteuer__einkommen__betrag_y < grenze_3:
        lohnsteuer_klasse5_6 = (
            lohnsteuer_grenze_2
            + (lohnsteuer__einkommen__betrag_y - grenze_2)
            * eink_st_params["eink_st_tarif"]["rates"][0][3]
        )
    else:
        lohnsteuer_klasse5_6 = (
            lohnsteuer_klasse5_6_tmp
            + (lohnsteuer__einkommen__betrag_y - grenze_3)
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
        Taxable Income.
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
