"""Contributions to the unemployment insurance."""

from _gettsim.function_types import policy_function


@policy_function(end_date="2003-03-31", leaf_name="betrag_versicherter_m")
def betrag_versicherter_vor_midijob_m(
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__rente__beitrag__einkommen_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Unemployment insurance contributions paid by the insured person.

    Parameters
    ----------
    sozialversicherung__geringfügig_beschäftigt
        See :func:`sozialversicherung__geringfügig_beschäftigt`.
    sozialversicherung__rente__beitrag__einkommen_m
        See :func:`sozialversicherung__rente__beitrag__einkommen_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    betrag_arbeitgeber_regulär_beschäftigt_m = (
        sozialversicherung__rente__beitrag__einkommen_m
        * sozialv_beitr_params["beitr_satz"]["arbeitslosenversicherung"]
    )

    # Set to 0 for minijobs
    if sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = betrag_arbeitgeber_regulär_beschäftigt_m

    return out


@policy_function(start_date="2003-04-01", leaf_name="betrag_versicherter_m")
def betrag_versicherter_mit_midijob_m(
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__in_gleitzone: bool,
    betrag_versicherter_midijob_m: float,
    sozialversicherung__rente__beitrag__einkommen_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Unemployment insurance contributions paid by the insured person.

    Parameters
    ----------
    sozialversicherung__geringfügig_beschäftigt
        See :func:`sozialversicherung__geringfügig_beschäftigt`.
    sozialversicherung__in_gleitzone
        See :func:`sozialversicherung__in_gleitzone`.
    betrag_versicherter_midijob_m
        See :func:`betrag_versicherter_midijob_m`.
    sozialversicherung__rente__beitrag__einkommen_m
        See :func:`sozialversicherung__rente__beitrag__einkommen_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    betrag_arbeitgeber_regulär_beschäftigt_m = (
        sozialversicherung__rente__beitrag__einkommen_m
        * sozialv_beitr_params["beitr_satz"]["arbeitslosenversicherung"]
    )

    # Set to 0 for minijobs
    if sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    elif sozialversicherung__in_gleitzone:
        out = betrag_versicherter_midijob_m
    else:
        out = betrag_arbeitgeber_regulär_beschäftigt_m

    return out


@policy_function(end_date="2003-03-31", leaf_name="betrag_arbeitgeber_m")
def betrag_arbeitgeber_vor_midijob_m(
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__rente__beitrag__einkommen_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employer's unemployment insurance contribution until March 2003.

    Parameters
    ----------
    sozialversicherung__geringfügig_beschäftigt
        See :func:`sozialversicherung__geringfügig_beschäftigt`.
    sozialversicherung__rente__beitrag__einkommen_m
        See :func:`sozialversicherung__rente__beitrag__einkommen_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    betrag_arbeitgeber_regulär_beschäftigt_m = (
        sozialversicherung__rente__beitrag__einkommen_m
        * sozialv_beitr_params["beitr_satz"]["arbeitslosenversicherung"]
    )

    # Set to 0 for minijobs
    if sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = betrag_arbeitgeber_regulär_beschäftigt_m

    return out


@policy_function(start_date="2003-04-01", leaf_name="betrag_arbeitgeber_m")
def betrag_arbeitgeber_m_mit_midijob(
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__in_gleitzone: bool,
    betrag_arbeitgeber_midijob_m: float,
    sozialversicherung__rente__beitrag__einkommen_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employer's unemployment insurance contribution since April 2003.

    Parameters
    ----------
    sozialversicherung__geringfügig_beschäftigt
        See :func:`sozialversicherung__geringfügig_beschäftigt`.
    sozialversicherung__in_gleitzone
        See :func:`sozialversicherung__in_gleitzone`.
    betrag_arbeitgeber_midijob_m
        See :func:`betrag_arbeitgeber_midijob_m`.
    sozialversicherung__rente__beitrag__einkommen_m
        See :func:`sozialversicherung__rente__beitrag__einkommen_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    betrag_arbeitgeber_regulär_beschäftigt_m = (
        sozialversicherung__rente__beitrag__einkommen_m
        * sozialv_beitr_params["beitr_satz"]["arbeitslosenversicherung"]
    )

    # Set to 0 for minijobs
    if sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    elif sozialversicherung__in_gleitzone:
        out = betrag_arbeitgeber_midijob_m
    else:
        out = betrag_arbeitgeber_regulär_beschäftigt_m

    return out


@policy_function(start_date="2003-04-01")
def betrag_gesamt_midijob_m(
    sozialversicherung__midijob_bemessungsentgelt_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Sum of employee's and employer's unemployment insurance contribution
    for midijobs.

    Parameters
    ----------
    sozialversicherung__midijob_bemessungsentgelt_m
        See :func:`sozialversicherung__midijob_bemessungsentgelt_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    return (
        sozialversicherung__midijob_bemessungsentgelt_m
        * 2
        * sozialv_beitr_params["beitr_satz"]["arbeitslosenversicherung"]
    )


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="betrag_arbeitgeber_midijob_m",
)
def betrag_arbeitgeber_midijob_m_anteil_bruttolohn(
    einnahmen__bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employers' unemployment insurance contribution for Midijobs until September
    2022.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    einnahmen__bruttolohn_m
        See basic input variable :ref:`einnahmen__bruttolohn_m <einnahmen__bruttolohn_m>`.

    Returns
    -------

    """
    return (
        einnahmen__bruttolohn_m
        * sozialv_beitr_params["beitr_satz"]["arbeitslosenversicherung"]
    )


@policy_function(start_date="2022-10-01", leaf_name="betrag_arbeitgeber_midijob_m")
def betrag_arbeitgeber_midijob_m_residuum(
    betrag_gesamt_midijob_m: float,
    betrag_versicherter_midijob_m: float,
) -> float:
    """Employer's unemployment insurance contribution since October 2022.

    Parameters
    ----------
    betrag_gesamt_midijob_m
        See :func:`betrag_gesamt_midijob_m`.
    betrag_versicherter_midijob_m
        See :func:`betrag_versicherter_midijob_m`.

    Returns
    -------

    """
    return betrag_gesamt_midijob_m - betrag_versicherter_midijob_m


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="betrag_versicherter_midijob_m",
)
def betrag_versicherter_midijob_m_residuum(
    betrag_gesamt_midijob_m: float,
    betrag_arbeitgeber_midijob_m: float,
) -> float:
    """Employee's unemployment insurance contribution for Midijobs until September
    2022.

    Parameters
    ----------
    betrag_gesamt_midijob_m
        See :func:`betrag_gesamt_midijob_m`.
    betrag_arbeitgeber_midijob_m
        See :func:`betrag_arbeitgeber_midijob_m`.

    Returns
    -------

    """
    return betrag_gesamt_midijob_m - betrag_arbeitgeber_midijob_m


@policy_function(start_date="2022-10-01", leaf_name="betrag_versicherter_midijob_m")
def betrag_versicherter_midijob_m_anteil_beitragspflichtiger_einnahmen(
    sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's unemployment insurance contribution since October 2022.

    Parameters
    ----------
    sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m
        See :func:`sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    return (
        sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m
        * sozialv_beitr_params["beitr_satz"]["arbeitslosenversicherung"]
    )
