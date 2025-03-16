"""Withholding tax on earnings (Lohnsteuer)."""

from _gettsim.function_types import policy_function
from _gettsim.taxes.einkommensteuer.einkommensteuer import einkommensteuer_tarif
from _gettsim.taxes.solidaritätszuschlag.solidaritätszuschlag import (
    solidaritätszuschlag_tarif,
)


@policy_function()
def betrag_m(
    einkommen_y: float,
    eink_st_params: dict,
    steuerklasse: int,
    lohnst_params: dict,
) -> float:
    """
    Withholding tax on earnings (Lohnsteuer).

    Parameters
    ----------
    einkommen_y
        See :func:`einkommen_y`.
    steuerklasse
        See :func:`steuerklasse`.
    eink_st_params
        See params documentation :ref:`eink_st_params`.
    lohnst_params
        See params documentation :ref:`lohnst_params`.

    """
    return lohnsteuerformel(einkommen_y, eink_st_params, lohnst_params, steuerklasse)


@policy_function()
def betrag_mit_kinderfreibetrag_m(
    einkommen_y: float,
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
    einkommen_y
        See :func:`einkommen_y`.
    kinderfreibetrag_soli_y
        See :func:`kinderfreibetrag_soli_y`.
    steuerklasse
        See :func:`steuerklasse`.
    eink_st_params
        See params documentation :ref:`eink_st_params`.
    lohnst_params
        See params documentation :ref:`lohnst_params`.
    """

    eink = max(einkommen_y - kinderfreibetrag_soli_y, 0)

    return lohnsteuerformel(eink, eink_st_params, lohnst_params, steuerklasse)


@policy_function()
def betrag_soli_y(betrag_mit_kinderfreibetrag_y: float, soli_st_params: dict) -> float:
    """Solidarity surcharge on Lohnsteuer (withholding tax on earnings).

    Parameters
    ----------
    betrag_mit_kinderfreibetrag_y
        See :func:`betrag_mit_kinderfreibetrag_y`.
    soli_st_params
        See params documentation :ref:`soli_st_params <soli_st_params>`.

    Returns
        Solidarity Surcharge on Lohnsteuer
    -------

    """

    return solidaritätszuschlag_tarif(betrag_mit_kinderfreibetrag_y, soli_st_params)


@policy_function()
def kinderfreibetrag_soli_y(
    steuerklasse: int,
    einkommensteuer__anzahl_kinderfreibeträge: int,
    eink_st_abzuege_params: dict,
) -> float:
    """Child Allowance (Kinderfreibetrag) for Lohnsteuer-Soli.

    For the purpose of Soli on Lohnsteuer, the child allowance not only depends on the
    number of children, but also on the steuerklasse

    Parameters
    ----------
    steuerklasse
        See :func:`steuerklasse`.
    einkommensteuer__anzahl_kinderfreibeträge
        See :func:`einkommensteuer__anzahl_kinderfreibeträge`.
    eink_st_abzuege_params
        See params documenation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------
    Kinderfreibetrag for Lohnsteuer-Soli.
    """

    kinderfreibetrag_basis = (
        eink_st_abzuege_params["kinderfreib"]["sächl_existenzmin"]
        + eink_st_abzuege_params["kinderfreib"]["beitr_erz_ausb"]
    )

    # For certain tax brackets, twice the child allowance can be deducted
    if steuerklasse in {1, 2, 3}:
        out = kinderfreibetrag_basis * 2 * einkommensteuer__anzahl_kinderfreibeträge
    elif steuerklasse == 4:
        out = kinderfreibetrag_basis * einkommensteuer__anzahl_kinderfreibeträge
    else:
        out = 0
    return out


def lohnsteuerformel(
    einkommen_y: float,
    eink_st_params: dict,
    lohnst_params: dict,
    steuerklasse: int,
) -> float:
    """
    Calculates Lohnsteuer (withholding tax on earnings), paid monthly by the employer on
    behalf of the employee. Apply the income tax tariff, but individually and with
    different exemptions, determined by the 'steuerklasse'. Source: §39b EStG

    Calculation is differentiated by steuerklasse

    1,2,4: Standard tariff (§32a (1) EStG) 3: Splitting tariff (§32a (5) EStG) 5,6: Take
    twice the difference between applying the tariff on 5/4 and 3/4 of taxable income.
    Tax rate may not be lower than the starting statutory one.

    Parameters
    ----------
    einkommen_y
        See :func:`einkommen_y`.
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

    lohnsteuer_basistarif = einkommensteuer_tarif(einkommen_y, eink_st_params)
    lohnsteuer_splittingtarif = 2 * einkommensteuer_tarif(
        einkommen_y / 2, eink_st_params
    )
    lohnsteuer_5_6_basis = basis_für_klassen_5_6(
        einkommen_y=einkommen_y, eink_st_params=eink_st_params
    )

    grenze_1 = lohnst_params["lohnst_einkommensgrenzen"][0]
    grenze_2 = lohnst_params["lohnst_einkommensgrenzen"][1]
    grenze_3 = lohnst_params["lohnst_einkommensgrenzen"][2]

    lohnsteuer_grenze_1 = basis_für_klassen_5_6(
        einkommen_y=grenze_1, eink_st_params=eink_st_params
    )
    max_lohnsteuer = (
        lohnsteuer_grenze_1
        + (einkommen_y - grenze_1) * eink_st_params["eink_st_tarif"]["rates"][0][3]
    )
    lohnsteuer_grenze_2 = basis_für_klassen_5_6(
        einkommen_y=grenze_2, eink_st_params=eink_st_params
    )
    lohnsteuer_zw_grenze_2_3 = (grenze_3 - grenze_2) * eink_st_params["eink_st_tarif"][
        "rates"
    ][0][3]
    lohnsteuer_klasse5_6_tmp = lohnsteuer_grenze_2 + lohnsteuer_zw_grenze_2_3

    if einkommen_y < grenze_1:
        lohnsteuer_klasse5_6 = lohnsteuer_5_6_basis
    elif grenze_1 <= einkommen_y < grenze_2:
        lohnsteuer_klasse5_6 = min(
            max_lohnsteuer,
            basis_für_klassen_5_6(
                einkommen_y=einkommen_y, eink_st_params=eink_st_params
            ),
        )
    elif grenze_2 <= einkommen_y < grenze_3:
        lohnsteuer_klasse5_6 = (
            lohnsteuer_grenze_2
            + (einkommen_y - grenze_2) * eink_st_params["eink_st_tarif"]["rates"][0][3]
        )
    else:
        lohnsteuer_klasse5_6 = (
            lohnsteuer_klasse5_6_tmp
            + (einkommen_y - grenze_3) * eink_st_params["eink_st_tarif"]["rates"][0][4]
        )

    if steuerklasse in {1, 2, 4}:
        out = lohnsteuer_basistarif
    elif steuerklasse == 3:
        out = lohnsteuer_splittingtarif
    else:
        out = lohnsteuer_klasse5_6

    out = out / 12

    return max(out, 0.0)


def basis_für_klassen_5_6(einkommen_y: float, eink_st_params: dict) -> float:
    """Calculate base for Lohnsteuer for steuerklasse 5 and 6, by applying
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

    einkommen_y:
        Taxable Income.
    eink_st_params
        See params documentation :ref:`eink_st_params <eink_st_params>`

    Returns
    -------
    Base for Lohnsteuer for steuerklasse 5 and 6

    """

    out = max(
        2
        * (
            einkommensteuer_tarif(einkommen_y * 1.25, eink_st_params)
            - einkommensteuer_tarif(einkommen_y * 0.75, eink_st_params)
        ),
        einkommen_y * eink_st_params["eink_st_tarif"]["rates"][0][1],
    )

    return out
