"""Priority checks of transfers against each other."""

from _gettsim.aggregation import AggregateByGroupSpec
from _gettsim.function_types import policy_function

aggregation_specs = {
    "wohngeld_vorrang_wthh": AggregateByGroupSpec(
        source_col="wohngeld_vorrang_vor_arbeitslosengeld_2_bg",
        aggr="any",
    ),
    "wohngeld_kinderzuschlag_vorrang_wthh": AggregateByGroupSpec(
        source_col="wohngeld_und_kinderzuschlag_vorrang_vor_arbeitslosengeld_2_bg",
        aggr="any",
    ),
}


@policy_function()
def wohngeld_vorrang_vor_arbeitslosengeld_2_bg(
    arbeitslosengeld_2__regelbedarf_m_bg: float,
    arbeitslosengeld_2__nettoeinkommen_m_bg: float,
    wohngeld__anspruchshöhe_m_bg: float,
) -> bool:
    """Check if housing benefit has priority.

    Housing benefit has priority if the sum of housing benefit and income covers the
    needs according to SGB II of the Bedarfsgemeinschaft.

    Parameters
    ----------
    arbeitslosengeld_2__regelbedarf_m_bg
        See :func:`arbeitslosengeld_2__regelbedarf_m_bg`.
    arbeitslosengeld_2__nettoeinkommen_m_bg
        See :func:`arbeitslosengeld_2__nettoeinkommen_m_bg`.
    wohngeld__anspruchshöhe_m_bg
        See :func:`wohngeld__anspruchshöhe_m_bg`.

    Returns
    -------

    """
    return (
        arbeitslosengeld_2__nettoeinkommen_m_bg + wohngeld__anspruchshöhe_m_bg
        >= arbeitslosengeld_2__regelbedarf_m_bg
    )


@policy_function()
def kinderzuschlag_vorrang_vor_arbeitslosengeld_2_bg(
    arbeitslosengeld_2__regelbedarf_m_bg: float,
    arbeitslosengeld_2__nettoeinkommen_m_bg: float,
    kinderzuschlag__anspruchshöhe_m_bg: float,
) -> bool:
    """Check if child benefit has priority.

    Parameters
    ----------
    arbeitslosengeld_2__regelbedarf_m_bg
        See :func:`arbeitslosengeld_2__regelbedarf_m_bg`.
    arbeitslosengeld_2__nettoeinkommen_m_bg
        See :func:`arbeitslosengeld_2__nettoeinkommen_m_bg`.
    kinderzuschlag__anspruchshöhe_m_bg
        See :func:`kinderzuschlag__anspruchshöhe_m_bg`.

    Returns
    -------

    """
    return (
        arbeitslosengeld_2__nettoeinkommen_m_bg + kinderzuschlag__anspruchshöhe_m_bg
        >= arbeitslosengeld_2__regelbedarf_m_bg
    )


@policy_function()
def wohngeld_und_kinderzuschlag_vorrang_vor_arbeitslosengeld_2_bg(
    arbeitslosengeld_2__regelbedarf_m_bg: float,
    arbeitslosengeld_2__nettoeinkommen_m_bg: float,
    kinderzuschlag__anspruchshöhe_m_bg: float,
    wohngeld__anspruchshöhe_m_bg: float,
) -> bool:
    """Check if housing and child benefit have priority.

    Parameters
    ----------
    arbeitslosengeld_2__regelbedarf_m_bg
        See :func:`arbeitslosengeld_2__regelbedarf_m_bg`.
    arbeitslosengeld_2__nettoeinkommen_m_bg
        See :func:`arbeitslosengeld_2__nettoeinkommen_m_bg`.
    kinderzuschlag__anspruchshöhe_m_bg
        See :func:`kinderzuschlag__anspruchshöhe_m_bg`.
    wohngeld__anspruchshöhe_m_bg
        See :func:`wohngeld__anspruchshöhe_m_bg`.

    Returns
    -------

    """

    return (
        arbeitslosengeld_2__nettoeinkommen_m_bg
        + wohngeld__anspruchshöhe_m_bg
        + kinderzuschlag__anspruchshöhe_m_bg
        >= arbeitslosengeld_2__regelbedarf_m_bg
    )
