"""Contributions to the unemployment insurance."""

from _gettsim.functions.policy_function import policy_function


@policy_function(end_date="2003-03-31", name_in_dag="betrag_arbeitnehmer_m")
def betrag_arbeitnehmer_vor_midijob_m(
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    sozialversicherungsbeitraege__rentenversicherung__einkommen_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's unemployment insurance contribution.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    sozialversicherungsbeitraege__rentenversicherung__einkommen_m
        See :func:`sozialversicherungsbeitraege__rentenversicherung__einkommen_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    arbeitsl_v_regulär_beschäftigt_m = (
        sozialversicherungsbeitraege__rentenversicherung__einkommen_m
        * sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]
    )

    # Set to 0 for minijobs
    if einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = arbeitsl_v_regulär_beschäftigt_m

    return out


@policy_function(start_date="2003-04-01", name_in_dag="betrag_arbeitnehmer_m")
def betrag_arbeitnehmer_mit_midijob_m(
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    einkommensgrenzen__in_gleitzone: bool,
    betrag_arbeitnehmer_midijob_m: float,
    sozialversicherungsbeitraege__rentenversicherung__einkommen_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's unemployment insurance contribution.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    einkommensgrenzen__in_gleitzone
        See :func:`einkommensgrenzen__in_gleitzone`.
    betrag_arbeitnehmer_midijob_m
        See :func:`betrag_arbeitnehmer_midijob_m`.
    sozialversicherungsbeitraege__rentenversicherung__einkommen_m
        See :func:`sozialversicherungsbeitraege__rentenversicherung__einkommen_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    arbeitsl_v_regulär_beschäftigt_m = (
        sozialversicherungsbeitraege__rentenversicherung__einkommen_m
        * sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]
    )

    # Set to 0 for minijobs
    if einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    elif einkommensgrenzen__in_gleitzone:
        out = betrag_arbeitnehmer_midijob_m
    else:
        out = arbeitsl_v_regulär_beschäftigt_m

    return out


@policy_function(end_date="2003-03-31", name_in_dag="betrag_arbeitgeber_m")
def betrag_arbeitgeber_vor_midijob_m(
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    sozialversicherungsbeitraege__rentenversicherung__einkommen_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employer's unemployment insurance contribution until March 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    sozialversicherungsbeitraege__rentenversicherung__einkommen_m
        See :func:`sozialversicherungsbeitraege__rentenversicherung__einkommen_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    arbeitsl_v_regulär_beschäftigt_m = (
        sozialversicherungsbeitraege__rentenversicherung__einkommen_m
        * sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]
    )

    # Set to 0 for minijobs
    if einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = arbeitsl_v_regulär_beschäftigt_m

    return out


@policy_function(start_date="2003-04-01", name_in_dag="betrag_arbeitgeber_m")
def betrag_arbeitgeber_m_mit_midijob(
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    einkommensgrenzen__in_gleitzone: bool,
    betrag_arbeitgeber_midijob_m: float,
    sozialversicherungsbeitraege__rentenversicherung__einkommen_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employer's unemployment insurance contribution since April 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    einkommensgrenzen__in_gleitzone
        See :func:`einkommensgrenzen__in_gleitzone`.
    betrag_arbeitgeber_midijob_m
        See :func:`betrag_arbeitgeber_midijob_m`.
    sozialversicherungsbeitraege__rentenversicherung__einkommen_m
        See :func:`sozialversicherungsbeitraege__rentenversicherung__einkommen_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    arbeitsl_v_regulär_beschäftigt_m = (
        sozialversicherungsbeitraege__rentenversicherung__einkommen_m
        * sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]
    )

    # Set to 0 for minijobs
    if einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    elif einkommensgrenzen__in_gleitzone:
        out = betrag_arbeitgeber_midijob_m
    else:
        out = arbeitsl_v_regulär_beschäftigt_m

    return out


@policy_function(start_date="2003-04-01")
def betrag_gesamt_midijob_m(
    einkommensgrenzen__midijob_bemessungsentgelt_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Sum of employee's and employer's unemployment insurance contribution
    for midijobs.

    Parameters
    ----------
    einkommensgrenzen__midijob_bemessungsentgelt_m
        See :func:`einkommensgrenzen__midijob_bemessungsentgelt_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    return (
        einkommensgrenzen__midijob_bemessungsentgelt_m
        * 2
        * sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]
    )


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    name_in_dag="betrag_arbeitgeber_midijob_m",
)
def betrag_arbeitgeber_midijob_m_anteil_bruttolohn(
    einkommen__bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employers' unemployment insurance contribution for Midijobs until September
    2022.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.

    Returns
    -------

    """
    return einkommen__bruttolohn_m * sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]


@policy_function(start_date="2022-10-01", name_in_dag="betrag_arbeitgeber_midijob_m")
def betrag_arbeitgeber_midijob_m_residuum(
    betrag_gesamt_midijob_m: float,
    betrag_arbeitnehmer_midijob_m: float,
) -> float:
    """Employer's unemployment insurance contribution since October 2022.

    Parameters
    ----------
    betrag_gesamt_midijob_m
        See :func:`betrag_gesamt_midijob_m`.
    betrag_arbeitnehmer_midijob_m
        See :func:`betrag_arbeitnehmer_midijob_m`.

    Returns
    -------

    """
    return betrag_gesamt_midijob_m - betrag_arbeitnehmer_midijob_m


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    name_in_dag="betrag_arbeitnehmer_midijob_m",
)
def betrag_arbeitnehmer_midijob_m_residuum(
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


@policy_function(start_date="2022-10-01", name_in_dag="betrag_arbeitnehmer_midijob_m")
def betrag_arbeitnehmer_midijob_m_anteil_beitragspfl_einnahme(
    einkommensgrenzen__beitragspflichtige_einnahmen_arbeitnehmer_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's unemployment insurance contribution since October 2022.

    Parameters
    ----------
    einkommensgrenzen__beitragspflichtige_einnahmen_arbeitnehmer_m
        See :func:`einkommensgrenzen__beitragspflichtige_einnahmen_arbeitnehmer_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    return (
        einkommensgrenzen__beitragspflichtige_einnahmen_arbeitnehmer_m
        * sozialv_beitr_params["beitr_satz"]["arbeitsl_v"]
    )
