"""Public pension insurance contributions."""

from _gettsim.functions.policy_function import policy_function


@policy_function(end_date="2003-03-31", leaf_name="betrag_arbeitnehmer_m")
def betrag_arbeitnehmer_m_vor_midijob(
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    einkommen_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's public pension insurance contribution.

    Before Midijob introduction in April 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    einkommen_m
        See :func:`einkommen_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    ges_rentenv_beitr_regular_job_m = (
        einkommen_m * sozialv_beitr_params["beitr_satz"]["ges_rentenv"]
    )

    if einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = ges_rentenv_beitr_regular_job_m

    return out


@policy_function(start_date="2003-04-01", leaf_name="betrag_arbeitnehmer_m")
def betrag_arbeitnehmer_m_mit_midijob(
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    betrag_midijob_arbeitnehmer_m: float,
    einkommen_m: float,
    sozialv_beitr_params: dict,
    einkommensgrenzen__in_gleitzone: bool,
) -> float:
    """Employee's public pension insurance contribution.

    After Midijob introduction in April 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    betrag_midijob_arbeitnehmer_m
        See :func:`betrag_midijob_arbeitnehmer_m`.
    einkommen_m
        See :func:`einkommen_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    einkommensgrenzen__in_gleitzone
        See :func:`einkommensgrenzen__in_gleitzone`.

    Returns
    -------

    """
    ges_rentenv_beitr_regular_job_m = (
        einkommen_m * sozialv_beitr_params["beitr_satz"]["ges_rentenv"]
    )

    if einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    elif einkommensgrenzen__in_gleitzone:
        out = betrag_midijob_arbeitnehmer_m
    else:
        out = ges_rentenv_beitr_regular_job_m

    return out


@policy_function(end_date="2003-03-31", leaf_name="betrag_arbeitgeber_m")
def betrag_arbeitgeber_m_vor_midijob(
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    einkommen_m: float,
    sozialv_beitr_params: dict,
    einkommen__bruttolohn_m: float,
) -> float:
    """Employer's public pension insurance contribution.

    Before Midijob introduction in April 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    einkommen_m
        See :func:`einkommen_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.

    Returns
    -------

    """
    ges_rentenv_beitr_regular_job_m = (
        einkommen_m * sozialv_beitr_params["beitr_satz"]["ges_rentenv"]
    )

    if einkommensgrenzen__geringfügig_beschäftigt:
        out = (
            einkommen__bruttolohn_m
            * sozialv_beitr_params["ag_abgaben_geringf"]["ges_rentenv"]
        )
    else:
        out = ges_rentenv_beitr_regular_job_m

    return out


@policy_function(start_date="2003-04-01", leaf_name="betrag_arbeitgeber_m")
def betrag_arbeitgeber_m_mit_midijob(  # noqa: PLR0913
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    betrag_midijob_arbeitgeber_m: float,
    einkommen_m: float,
    sozialv_beitr_params: dict,
    einkommensgrenzen__in_gleitzone: bool,
    einkommen__bruttolohn_m: float,
) -> float:
    """Employer's public pension insurance contribution.

    After Midijob introduction in April 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    betrag_midijob_arbeitgeber_m
        See :func:`betrag_midijob_arbeitgeber_m`.
    einkommen_m
        See :func:`einkommen_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    einkommensgrenzen__in_gleitzone
        See :func:`einkommensgrenzen__in_gleitzone`.
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.

    Returns
    -------

    """
    ges_rentenv_beitr_regular_job_m = (
        einkommen_m * sozialv_beitr_params["beitr_satz"]["ges_rentenv"]
    )

    if einkommensgrenzen__geringfügig_beschäftigt:
        out = (
            einkommen__bruttolohn_m
            * sozialv_beitr_params["ag_abgaben_geringf"]["ges_rentenv"]
        )
    elif einkommensgrenzen__in_gleitzone:
        out = betrag_midijob_arbeitgeber_m
    else:
        out = ges_rentenv_beitr_regular_job_m

    return out


@policy_function()
def einkommen_m(
    einkommen__bruttolohn_m: float,
    beitragsbemessungsgrenze_m: float,
) -> float:
    """Wage subject to pension and unemployment insurance contributions.

    Parameters
    ----------
    einkommen__bruttolohn_m
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    beitragsbemessungsgrenze_m
        See :func:`beitragsbemessungsgrenze_m`.


    Returns
    -------

    """
    return min(einkommen__bruttolohn_m, beitragsbemessungsgrenze_m)


@policy_function()
def beitragsbemessungsgrenze_m(
    demographics__wohnort_ost: bool, sozialv_beitr_params: dict
) -> float:
    """Income threshold up to which pension insurance payments apply.

    Parameters
    ----------
    demographics__wohnort_ost
        See :func:`demographics__wohnort_ost`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    params = sozialv_beitr_params["beitr_bemess_grenze_m"]["ges_rentenv"]
    out = params["ost"] if demographics__wohnort_ost else params["west"]

    return float(out)


@policy_function(start_date="2003-04-01")
def betrag_midijob_gesamt_m(
    einkommensgrenzen__midijob_bemessungsentgelt_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Sum of employer and employee pension insurance contribution for midijobs.
    Midijobs were introduced in April 2003.

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
        * sozialv_beitr_params["beitr_satz"]["ges_rentenv"]
    )


@policy_function(
    end_date="2022-09-30",
    leaf_name="betrag_midijob_arbeitgeber_m",
)
def betrag_midijob_arbeitgeber_m_anteil_bruttolohn(
    einkommen__bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employer's unemployment insurance contribution until September 2022.

    Parameters
    ----------
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    return einkommen__bruttolohn_m * sozialv_beitr_params["beitr_satz"]["ges_rentenv"]


@policy_function(start_date="2022-10-01", leaf_name="betrag_midijob_arbeitgeber_m")
def betrag_midijob_arbeitgeber_m_residuum(
    betrag_midijob_gesamt_m: float,
    betrag_midijob_arbeitnehmer_m: float,
) -> float:
    """Employer's unemployment insurance contribution since October 2022.

    Parameters
    ----------
    betrag_midijob_gesamt_m
        See :func:`betrag_midijob_gesamt_m`.
    betrag_midijob_arbeitnehmer_m
        See :func:`betrag_midijob_arbeitnehmer_m`.

    Returns
    -------

    """
    return betrag_midijob_gesamt_m - betrag_midijob_arbeitnehmer_m


@policy_function(
    end_date="2022-09-30",
    leaf_name="betrag_midijob_arbeitnehmer_m",
)
def betrag_midijob_arbeitnehmer_m_residuum(
    betrag_midijob_arbeitgeber_m: float,
    betrag_midijob_gesamt_m: float,
) -> float:
    """Employee's unemployment insurance contribution for midijobs until September 2022.

    Parameters
    ----------
    betrag_midijob_arbeitgeber_m
        See :func:`betrag_midijob_arbeitgeber_m`.
    betrag_midijob_gesamt_m
        See :func:`betrag_midijob_gesamt_m`.

    Returns
    -------

    """
    return betrag_midijob_gesamt_m - betrag_midijob_arbeitgeber_m


@policy_function(start_date="2022-10-01", leaf_name="betrag_midijob_arbeitnehmer_m")
def betrag_midijob_arbeitnehmer_m_anteil_beitragspfl_einnahme(
    einkommensgrenzen__beitragspflichtige_einnahmen_arbeitnehmer_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's unemployment insurance contribution for midijobs since October 2022.

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
        * sozialv_beitr_params["beitr_satz"]["ges_rentenv"]
    )
