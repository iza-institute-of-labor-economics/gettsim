"""Income relevant for calculation of Kinderzuschlag."""

from _gettsim.aggregation import AggregateByGroupSpec
from _gettsim.function_types import policy_function

aggregation_specs = {
    "arbeitslosengeld_2__anzahl_kinder_bg": AggregateByGroupSpec(
        source_col="kindergeld__anzahl_ansprüche",
        aggr="sum",
    ),
}


@policy_function()
def bruttoeinkommen_eltern_m(
    arbeitslosengeld_2__bruttoeinkommen_m: float,
    kindergeld__grundsätzlich_anspruchsberechtigt: bool,
    demographics__erwachsen: bool,
) -> float:
    """Calculate parental gross income for calculation of child benefit.

    This variable is used to check whether the minimum income threshold for child
    benefit is met.

    Parameters
    ----------
    arbeitslosengeld_2__bruttoeinkommen_m
        See :func:`arbeitslosengeld_2__bruttoeinkommen_m`.
    kindergeld__grundsätzlich_anspruchsberechtigt
        See :func:`kindergeld__grundsätzlich_anspruchsberechtigt`.
    demographics__erwachsen
        See :func:`demographics__erwachsen`.


    Returns
    -------

    """
    # TODO(@MImmesberger): Redesign the conditions in this function: False for adults
    # who do not have Kindergeld claims.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/704
    if demographics__erwachsen and (not kindergeld__grundsätzlich_anspruchsberechtigt):
        out = arbeitslosengeld_2__bruttoeinkommen_m
    else:
        out = 0.0

    return out


@policy_function(params_key_for_rounding="kinderzuschl_eink")
def nettoeinkommen_eltern_m(
    arbeitslosengeld_2__nettoeinkommen_nach_abzug_freibetrag_m: float,
    kindergeld__grundsätzlich_anspruchsberechtigt: bool,
    demographics__erwachsen: bool,
) -> float:
    """Parental income (after deduction of taxes, social insurance contributions, and
    other deductions) for calculation of child benefit.

    Parameters
    ----------
    arbeitslosengeld_2__nettoeinkommen_nach_abzug_freibetrag_m
        See :func:`arbeitslosengeld_2__nettoeinkommen_nach_abzug_freibetrag_m`.
    kindergeld__grundsätzlich_anspruchsberechtigt
        See :func:`kindergeld__grundsätzlich_anspruchsberechtigt`.
    demographics__erwachsen
        See :func:`demographics__erwachsen`.

    Returns
    -------

    """
    # TODO(@MImmesberger): Redesign the conditions in this function: False for adults
    # who do not have Kindergeld claims.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/704
    if demographics__erwachsen and (not kindergeld__grundsätzlich_anspruchsberechtigt):
        out = arbeitslosengeld_2__nettoeinkommen_nach_abzug_freibetrag_m
    else:
        out = 0.0
    return out


@policy_function(end_date="2019-06-30")
def maximales_nettoeinkommen_m_bg(
    erwachsenenbedarf_m_bg: float,
    arbeitslosengeld_2__anzahl_kinder_bg: int,
    kinderzuschl_params: dict,
) -> float:
    """Calculate maximum income to be eligible for additional child benefit
    (Kinderzuschlag).

    There is a maximum income threshold, depending on the need, plus the potential kiz
    receipt (§6a (1) Nr. 3 BKGG).

    Parameters
    ----------
    erwachsenenbedarf_m_bg
        See :func:`erwachsenenbedarf_m_bg`.
    arbeitslosengeld_2__anzahl_kinder_bg
        See :func:`arbeitslosengeld_2__anzahl_kinder_bg`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    out = (
        erwachsenenbedarf_m_bg
        + kinderzuschl_params["maximum"] * arbeitslosengeld_2__anzahl_kinder_bg
    )

    kindersofortzuschl = kinderzuschl_params.get("kindersofortzuschl", 0.0)
    out += kindersofortzuschl * arbeitslosengeld_2__anzahl_kinder_bg

    return out


@policy_function()
def mindestbruttoeinkommen_m_bg(
    arbeitslosengeld_2__anzahl_kinder_bg: int,
    arbeitslosengeld_2__alleinerziehend_bg: bool,
    kinderzuschl_params: dict,
) -> float:
    """Calculate minimal claim of child benefit (kinderzuschlag).

    Min income to be eligible for KIZ (different for singles and couples) (§6a (1) Nr. 2
    BKGG).

    Parameters
    ----------
    arbeitslosengeld_2__anzahl_kinder_bg
        See :func:`arbeitslosengeld_2__anzahl_kinder_bg
        <arbeitslosengeld_2__anzahl_kinder_bg>`.
    arbeitslosengeld_2__alleinerziehend_bg
        See :func:`arbeitslosengeld_2__alleinerziehend_bg`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    if arbeitslosengeld_2__anzahl_kinder_bg == 0:
        out = 0.0
    elif arbeitslosengeld_2__alleinerziehend_bg:
        out = kinderzuschl_params["min_eink_alleinerz"]
    else:
        out = kinderzuschl_params["min_eink_paare"]

    return out


@policy_function()
def anzurechnendes_einkommen_eltern_m_bg(
    nettoeinkommen_eltern_m_bg: float,
    erwachsenenbedarf_m_bg: float,
    kinderzuschl_params: dict,
) -> float:
    """Calculate parental income subtracted from child benefit.

    (§6a (6) S. 3 BKGG)

    Parameters
    ----------
    nettoeinkommen_eltern_m_bg
        See :func:`nettoeinkommen_eltern_m_bg`.
    erwachsenenbedarf_m_bg
        See :func:`erwachsenenbedarf_m_bg`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    out = kinderzuschl_params["entzugsrate_eltern"] * (
        nettoeinkommen_eltern_m_bg - erwachsenenbedarf_m_bg
    )

    return max(out, 0.0)


@policy_function()
def kosten_der_unterkunft_m_bg(
    wohnbedarf_anteil_eltern_bg: float,
    arbeitslosengeld_2__bruttokaltmiete_m_bg: float,
    arbeitslosengeld_2__heizkosten_m_bg: float,
) -> float:
    """Calculate costs of living eligible to claim.

    Unlike ALG2, there is no check on whether living costs are "appropriate".

    Parameters
    ----------
    wohnbedarf_anteil_eltern_bg
        See :func:`wohnbedarf_anteil_eltern_bg`.
    arbeitslosengeld_2__bruttokaltmiete_m_bg
        See :func:`arbeitslosengeld_2__bruttokaltmiete_m_bg`.
    arbeitslosengeld_2__heizkosten_m_bg
        See :func:`arbeitslosengeld_2__heizkosten_m_bg`.

    Returns
    -------

    """
    warmmiete_m_bg = (
        arbeitslosengeld_2__bruttokaltmiete_m_bg + arbeitslosengeld_2__heizkosten_m_bg
    )

    out = wohnbedarf_anteil_eltern_bg * warmmiete_m_bg

    return out


@policy_function()
def wohnbedarf_anteil_eltern_bg(
    arbeitslosengeld_2__anzahl_kinder_bg: int,
    arbeitslosengeld_2__anzahl_erwachsene_bg: int,
    kinderzuschl_params: dict,
) -> float:
    """Calculate living needs broken down to the parents. Defined as parents'
    subsistence level on housing, divided by sum of subsistence level from parents and
    children.

    Reference: § 6a Abs. 5 S. 3 BKGG

    Parameters
    ----------
    arbeitslosengeld_2__anzahl_kinder_bg
        See :func:`arbeitslosengeld_2__anzahl_kinder_bg`.
    arbeitslosengeld_2__anzahl_erwachsene_bg
        See :func:`arbeitslosengeld_2__anzahl_erwachsene_bg`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    ex_min = kinderzuschl_params["existenzminimum"]

    # Up to 10 children are considered
    considered_children = min(arbeitslosengeld_2__anzahl_kinder_bg, 10)
    single_oder_paar = (
        "single" if arbeitslosengeld_2__anzahl_erwachsene_bg == 1 else "paare"
    )

    out = (
        ex_min["kosten_der_unterkunft"][single_oder_paar]
        + ex_min["heizkosten"][single_oder_paar]
    ) / (
        ex_min["kosten_der_unterkunft"][single_oder_paar]
        + ex_min["heizkosten"][single_oder_paar]
        + (
            considered_children
            * (
                ex_min["kosten_der_unterkunft"]["kinder"]
                + ex_min["heizkosten"]["kinder"]
            )
        )
    )

    return out


# TODO(@MImmesberger): The regelsatz is already calculated in the ALG2 modules. We
# should remove this function.
# https://github.com/iza-institute-of-labor-economics/gettsim/issues/826
@policy_function(end_date="2010-12-31", leaf_name="regelsatz_m_bg")
def regelsatz_m_bg_arbeitsl_geld_2_params_bis_2010(
    arbeitslosengeld_2__mehrbedarf_alleinerziehend_m_bg: float,
    arbeitslosengeld_2__alleinerziehend_bg: bool,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate income relevant for calculation of child benefit until 2010.

    Parameters
    ----------
    arbeitslosengeld_2__mehrbedarf_alleinerziehend_m_bg
        See :func:`arbeitslosengeld_2__mehrbedarf_alleinerziehend_m_bg`.
    arbeitslosengeld_2__alleinerziehend_bg
        See :func:`arbeitslosengeld_2__alleinerziehend_bg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    if arbeitslosengeld_2__alleinerziehend_bg:
        out = arbeitsl_geld_2_params["regelsatz"] * (
            1 + arbeitslosengeld_2__mehrbedarf_alleinerziehend_m_bg
        )
    else:
        out = (
            arbeitsl_geld_2_params["regelsatz"]
            * arbeitsl_geld_2_params["anteil_regelsatz_erwachsene"]["zwei_erwachsene"]
            * 2
        )

    return float(out)


# TODO(@MImmesberger): The regelsatz is already calculated in the ALG2 modules. We
# should remove this function.
# https://github.com/iza-institute-of-labor-economics/gettsim/issues/826
@policy_function(start_date="2011-01-01")
def regelsatz_m_bg(
    arbeitslosengeld_2__mehrbedarf_alleinerziehend_m_bg: float,
    arbeitslosengeld_2__alleinerziehend_bg: bool,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate income relevant for calculation of child benefit since 2011.

    Parameters
    ----------
    arbeitslosengeld_2__mehrbedarf_alleinerziehend_m_bg
        See :func:`arbeitslosengeld_2__mehrbedarf_alleinerziehend_m_bg`.
    arbeitslosengeld_2__alleinerziehend_bg
        See :func:`arbeitslosengeld_2__alleinerziehend_bg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    if arbeitslosengeld_2__alleinerziehend_bg:
        out = arbeitsl_geld_2_params["regelsatz"][1] * (
            1 + arbeitslosengeld_2__mehrbedarf_alleinerziehend_m_bg
        )
    else:
        out = arbeitsl_geld_2_params["regelsatz"][2] * 2

    return float(out)


@policy_function()
def erwachsenenbedarf_m_bg(
    regelsatz_m_bg: float, kosten_der_unterkunft_m_bg: float
) -> float:
    """Aggregate relevant income and rental costs.

    Parameters
    ----------
    regelsatz_m_bg
        See :func:`regelsatz_m_bg`.
    kosten_der_unterkunft_m_bg
        See :func:`kosten_der_unterkunft_m_bg`.

    Returns
    -------

    """
    return regelsatz_m_bg + kosten_der_unterkunft_m_bg
