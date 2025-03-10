"""Income relevant for calculation of Kinderzuschlag."""

from _gettsim.aggregation import AggregateByGroupSpec
from _gettsim.functions.policy_function import policy_function

aggregation_specs = {
    "anzahl_kinder_bg": AggregateByGroupSpec(
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
    bedarf_m_bg: float,
    anzahl_kinder_bg: int,
    kinderzuschl_params: dict,
) -> float:
    """Calculate maximum income to be eligible for additional child benefit
    (Kinderzuschlag).

    There is a maximum income threshold, depending on the need, plus the potential kiz
    receipt (§6a (1) Nr. 3 BKGG).

    Parameters
    ----------
    bedarf_m_bg
        See :func:`bedarf_m_bg`.
    anzahl_kinder_bg
        See :func:`anzahl_kinder_bg`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    out = bedarf_m_bg + kinderzuschl_params["maximum"] * anzahl_kinder_bg

    kindersofortzuschl = kinderzuschl_params.get("kindersofortzuschl", 0.0)
    out += kindersofortzuschl * anzahl_kinder_bg

    return out


@policy_function()
def mindestbruttoeinkommen_m_bg(
    anzahl_kinder_bg: int,
    demographics__alleinerziehend_bg: bool,
    kinderzuschl_params: dict,
) -> float:
    """Calculate minimal claim of child benefit (kinderzuschlag).

    Min income to be eligible for KIZ (different for singles and couples) (§6a (1) Nr. 2
    BKGG).

    Parameters
    ----------
    anzahl_kinder_bg
        See :func:`anzahl_kinder_bg
        <anzahl_kinder_bg>`.
    demographics__alleinerziehend_bg
        See :func:`demographics__alleinerziehend_bg`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    if anzahl_kinder_bg == 0:
        out = 0.0
    elif demographics__alleinerziehend_bg:
        out = kinderzuschl_params["min_eink_alleinerz"]
    else:
        out = kinderzuschl_params["min_eink_paare"]

    return out


@policy_function()
def anzurechnendes_einkommen_eltern_m_bg(
    nettoeinkommen_eltern_m_bg: float,
    bedarf_m_bg: float,
    kinderzuschl_params: dict,
) -> float:
    """Calculate parental income subtracted from child benefit.

    (§6a (6) S. 3 BKGG)

    Parameters
    ----------
    nettoeinkommen_eltern_m_bg
        See :func:`nettoeinkommen_eltern_m_bg`.
    bedarf_m_bg
        See :func:`bedarf_m_bg`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    out = kinderzuschl_params["entzugsrate_eltern"] * (
        nettoeinkommen_eltern_m_bg - bedarf_m_bg
    )

    return max(out, 0.0)
