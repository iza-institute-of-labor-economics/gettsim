"""Relevant income for parental leave benefits."""

from _gettsim.function_types import policy_function


@policy_function(start_date="2007-01-01")
def anzurechnendes_nettoeinkommen_m(
    einkommensteuer__einnahmen__bruttolohn_m: float,
    lohnsteuer__betrag_m: float,
    lohnsteuer__betrag_soli_m: float,
) -> float:
    """Income that reduces the Elterngeld claim.

    Parameters
    ----------
    einkommensteuer__einnahmen__bruttolohn_m
        See basic input variable :ref:`einkommensteuer__einnahmen__bruttolohn_m <einkommensteuer__einnahmen__bruttolohn_m>`.
    lohnsteuer__betrag_m
        See :func:`lohnsteuer__betrag_m`.
    lohnsteuer__betrag_soli_m
        See :func:`lohnsteuer__betrag_soli_m`.

    Returns
    -------

    """
    # TODO(@MImmesberger): In this case, lohnsteuer__betrag_m should be calculated
    # without taking into account adaptions to the standard care insurance rate.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/792
    return (
        einkommensteuer__einnahmen__bruttolohn_m
        - lohnsteuer__betrag_m
        - lohnsteuer__betrag_soli_m
    )


@policy_function(start_date="2007-01-01", params_key_for_rounding="elterngeld")
def lohnersatzanteil_einkommen_untere_grenze(
    nettoeinkommen_vorjahr_m: float,
    elterngeld_params: dict,
) -> float:
    """Lower threshold for replacement rate adjustment minus net income.

    Parameters
    ----------
    nettoeinkommen_vorjahr_m
        See basic input variable :ref:`nettoeinkommen_vorjahr_m<nettoeinkommen_vorjahr_m>`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return (
        elterngeld_params["nettoeinkommen_stufen"]["lower_threshold"]
        - nettoeinkommen_vorjahr_m
    )


@policy_function(start_date="2007-01-01", params_key_for_rounding="elterngeld")
def lohnersatzanteil_einkommen_obere_grenze(
    nettoeinkommen_vorjahr_m: float,
    elterngeld_params: dict,
) -> float:
    """Net income minus upper threshold for replacement rate adjustment.

    Parameters
    ----------
    nettoeinkommen_vorjahr_m
        See basic input variable
        :ref:`nettoeinkommen_vorjahr_m<nettoeinkommen_vorjahr_m>`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return (
        nettoeinkommen_vorjahr_m
        - elterngeld_params["nettoeinkommen_stufen"]["upper_threshold"]
    )


@policy_function(
    start_date="2007-01-01",
    end_date="2024-03-31",
    leaf_name="einkommen_vorjahr_unter_bezugsgrenze",
)
def einkommen_vorjahr_unter_bezugsgrenze_mit_unterscheidung_single_paar(
    demographics__alleinerziehend: bool,
    zu_versteuerndes_einkommen_vorjahr_y_sn: float,
    elterngeld_params: dict,
) -> bool:
    """Income before birth is below income threshold for Elterngeld.

    Parameters
    ----------
    demographics__alleinerziehend
        See basic input variable :ref:`demographics__alleinerziehend <demographics__alleinerziehend>`.
    zu_versteuerndes_einkommen_vorjahr_y_sn
        See :func:`zu_versteuerndes_einkommen_vorjahr_y_sn`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    if demographics__alleinerziehend:
        out = (
            zu_versteuerndes_einkommen_vorjahr_y_sn
            <= elterngeld_params["max_eink_vorj"]["single"]
        )
    else:
        out = (
            zu_versteuerndes_einkommen_vorjahr_y_sn
            <= elterngeld_params["max_eink_vorj"]["paar"]
        )
    return out


@policy_function(
    start_date="2024-04-01", leaf_name="einkommen_vorjahr_unter_bezugsgrenze"
)
def einkommen_vorjahr_unter_bezugsgrenze_ohne_unterscheidung_single_paar(
    zu_versteuerndes_einkommen_vorjahr_y_sn: float,
    elterngeld_params: dict,
) -> bool:
    """Income before birth is below income threshold for Elterngeld.

    Parameters
    ----------
    zu_versteuerndes_einkommen_vorjahr_y_sn
        See :func:`zu_versteuerndes_einkommen_vorjahr_y_sn`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return zu_versteuerndes_einkommen_vorjahr_y_sn <= elterngeld_params["max_eink_vorj"]


@policy_function(start_date="2006-01-01", params_key_for_rounding="elterngeld")
def nettoeinkommen_approximation_m(
    einkommensteuer__einnahmen__bruttolohn_m: float,
    lohnsteuer__betrag_m: float,
    lohnsteuer__betrag_soli_m: float,
    elterngeld_params: dict,
) -> float:
    """Approximation of net wage used to calculate Elterngeld.

    This target can be used as an input in another GETTSIM call to compute Elterngeld.
    In principle, the relevant gross wage for this target is the sum of the gross wages
    in the 12 months before the birth of the child. For most datasets, except those with
    monthly income date (IAB, DRV data), the best approximation will likely be the gross
    wage in the calendar year before the birth of the child.

    Parameters
    ----------
    einkommensteuer__einnahmen__bruttolohn_m
        See basic input variable :ref:`einkommensteuer__einnahmen__bruttolohn_m <einkommensteuer__einnahmen__bruttolohn_m>`.
    lohnsteuer__betrag_m
        See :func:`lohnsteuer__betrag_m`.
    lohnsteuer__betrag_soli_m
        See :func:`lohnsteuer__betrag_soli_m`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
    """
    prox_ssc = (
        elterngeld_params["sozialv_pausch"] * einkommensteuer__einnahmen__bruttolohn_m
    )
    return (
        einkommensteuer__einnahmen__bruttolohn_m
        - prox_ssc
        - lohnsteuer__betrag_m
        - lohnsteuer__betrag_soli_m
    )
