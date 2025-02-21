"""Relevant income for parental leave benefits."""

from _gettsim.functions.policy_function import policy_function


def elterngeld_anrechenbares_nettoeinkommen_m(
    bruttolohn_m: float,
    lohnsteuer__betrag_m: float,
    lohnsteuer__betrag_soli_m: float,
) -> float:
    """Income that reduces the Elterngeld claim.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
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
    return bruttolohn_m - lohnsteuer__betrag_m - lohnsteuer__betrag_soli_m


@policy_function(params_key_for_rounding="elterngeld")
def _untere_lohnersatzanteil_grenze_minus_nettoeinkommen(
    elterngeld_nettoeinkommen_vorjahr_m: float,
    elterngeld_params: dict,
) -> float:
    """Lower threshold for replacement rate adjustment minus net income.

    Parameters
    ----------
    elterngeld_nettoeinkommen_vorjahr_m
        See basic input variable
        :ref:`elterngeld_nettoeinkommen_vorjahr_m<elterngeld_nettoeinkommen_vorjahr_m>`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return (
        elterngeld_params["nettoeinkommen_stufen"]["lower_threshold"]
        - elterngeld_nettoeinkommen_vorjahr_m
    )


@policy_function(params_key_for_rounding="elterngeld")
def _nettoeinkommen_minus_obere_lohnersatzanteil_grenze(
    elterngeld_nettoeinkommen_vorjahr_m: float,
    elterngeld_params: dict,
) -> float:
    """Net income minus upper threshold for replacement rate adjustment.

    Parameters
    ----------
    elterngeld_nettoeinkommen_vorjahr_m
        See basic input variable
        :ref:`elterngeld_nettoeinkommen_vorjahr_m<elterngeld_nettoeinkommen_vorjahr_m>`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return (
        elterngeld_nettoeinkommen_vorjahr_m
        - elterngeld_params["nettoeinkommen_stufen"]["upper_threshold"]
    )


@policy_function(
    end_date="2024-03-31", name_in_dag="vorjahr_einkommen_unter_bezugsgrenze"
)
def vorjahr_einkommen_unter_bezugsgrenze_mit_unterscheidung_single_paar(
    alleinerz: bool,
    elterngeld_zu_verst_eink_vorjahr_y_sn: float,
    elterngeld_params: dict,
) -> bool:
    """Income before birth is below income threshold for Elterngeld.

    Parameters
    ----------
    alleinerz
        See basic input variable :ref:`alleinerz <alleinerz>`.
    elterngeld_zu_verst_eink_vorjahr_y_sn
        See :func:`elterngeld_zu_verst_eink_vorjahr_y_sn`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    if alleinerz:
        out = (
            elterngeld_zu_verst_eink_vorjahr_y_sn
            <= elterngeld_params["max_eink_vorj"]["single"]
        )
    else:
        out = (
            elterngeld_zu_verst_eink_vorjahr_y_sn
            <= elterngeld_params["max_eink_vorj"]["paar"]
        )
    return out


@policy_function(
    start_date="2024-04-01", name_in_dag="vorjahr_einkommen_unter_bezugsgrenze"
)
def vorjahr_einkommen_unter_bezugsgrenze_ohne_unterscheidung_single_paar(
    elterngeld_zu_verst_eink_vorjahr_y_sn: float,
    elterngeld_params: dict,
) -> bool:
    """Income before birth is below income threshold for Elterngeld.

    Parameters
    ----------
    elterngeld_zu_verst_eink_vorjahr_y_sn
        See :func:`elterngeld_zu_verst_eink_vorjahr_y_sn`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.

    Returns
    -------

    """
    return elterngeld_zu_verst_eink_vorjahr_y_sn <= elterngeld_params["max_eink_vorj"]


@policy_function(params_key_for_rounding="elterngeld")
def elterngeld_nettolohn_approximation_m(
    bruttolohn_m: float,
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
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    lohnsteuer__betrag_m
        See :func:`lohnsteuer__betrag_m`.
    lohnsteuer__betrag_soli_m
        See :func:`lohnsteuer__betrag_soli_m`.
    elterngeld_params
        See params documentation :ref:`elterngeld_params <elterngeld_params>`.
    """
    prox_ssc = elterngeld_params["sozialv_pausch"] * bruttolohn_m
    return bruttolohn_m - prox_ssc - lohnsteuer__betrag_m - lohnsteuer__betrag_soli_m
