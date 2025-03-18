"""Public health insurance contributions."""

from _gettsim.function_types import policy_function


@policy_function(end_date="2003-03-31", leaf_name="betrag_versicherter_m")
def betrag_versicherter_vor_midijob_m(
    sozialversicherung__geringfügig_beschäftigt: bool,
    betrag_rentner_m: float,
    betrag_selbstständig_m: float,
    betrag_versicherter_regulär_beschäftigt_m: float,
    einkommensteuer__einkünfte__ist_selbstständig: bool,
) -> float:
    """Public health insurance contributions paid by the insured person.

    Before Midijob introduction in April 2003.

    Parameters
    ----------
    sozialversicherung__geringfügig_beschäftigt
        See :func:`sozialversicherung__geringfügig_beschäftigt`.
    betrag_rentner_m
        See :func:`betrag_rentner_m`.
    betrag_selbstständig_m
        See :func:`betrag_selbstständig_m`.
    betrag_versicherter_regulär_beschäftigt_m
        See :func:`betrag_versicherter_regulär_beschäftigt_m`.
    einkommensteuer__einkünfte__ist_selbstständig
        See basic input variable :ref:`einkommensteuer__einkünfte__ist_selbstständig <einkommensteuer__einkünfte__ist_selbstständig>`.


    Returns
    -------

    """
    if einkommensteuer__einkünfte__ist_selbstständig:
        out = betrag_selbstständig_m
    elif sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = betrag_versicherter_regulär_beschäftigt_m

    # Add the health insurance contribution for pensions
    return out + betrag_rentner_m


@policy_function(start_date="2003-04-01", leaf_name="betrag_versicherter_m")
def betrag_versicherter_mit_midijob_m(  # noqa: PLR0913
    sozialversicherung__geringfügig_beschäftigt: bool,
    betrag_rentner_m: float,
    betrag_selbstständig_m: float,
    sozialversicherung__in_gleitzone: bool,
    betrag_versicherter_midijob_m: float,
    betrag_versicherter_regulär_beschäftigt_m: float,
    einkommensteuer__einkünfte__ist_selbstständig: bool,
) -> float:
    """Public health insurance contributions paid by the insured person.

    After Midijob introduction in April 2003.

    Parameters
    ----------
    sozialversicherung__geringfügig_beschäftigt
        See :func:`sozialversicherung__geringfügig_beschäftigt`.
    betrag_rentner_m
        See :func:`betrag_rentner_m`.
    betrag_selbstständig_m
        See :func:`betrag_selbstständig_m`.
    betrag_versicherter_midijob_m
        See :func:`betrag_versicherter_midijob_m`.
    betrag_versicherter_regulär_beschäftigt_m
        See :func:`betrag_versicherter_regulär_beschäftigt_m`.
    sozialversicherung__in_gleitzone
        See :func:`sozialversicherung__in_gleitzone`.
    einkommensteuer__einkünfte__ist_selbstständig
        See basic input variable :ref:`einkommensteuer__einkünfte__ist_selbstständig <einkommensteuer__einkünfte__ist_selbstständig>`.


    Returns
    -------

    """
    if einkommensteuer__einkünfte__ist_selbstständig:
        out = betrag_selbstständig_m
    elif sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    elif sozialversicherung__in_gleitzone:
        out = betrag_versicherter_midijob_m
    else:
        out = betrag_versicherter_regulär_beschäftigt_m

    # Add the health insurance contribution for pensions
    return out + betrag_rentner_m


@policy_function(end_date="2003-03-31", leaf_name="betrag_arbeitgeber_m")
def betrag_arbeitgeber_vor_midijob_m(  # noqa: PLR0913
    sozialversicherung__geringfügig_beschäftigt: bool,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m: float,
    einkommen_m: float,
    einkommensteuer__einkünfte__ist_selbstständig: bool,
    sozialv_beitr_params: dict,
    beitragssatz_arbeitgeber: float,
) -> float:
    """Employer's public health insurance contribution.

    Before Midijob introduction in April 2003.

    Parameters
    ----------
    sozialversicherung__geringfügig_beschäftigt
        See :func:`sozialversicherung__geringfügig_beschäftigt`.
    einkommen_m
        See :func:`einkommen_m`.
    beitragssatz_arbeitgeber
        See :func:`beitragssatz_arbeitgeber`.
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m
        See basic input variable :ref:`einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m <einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m>`.
    einkommensteuer__einkünfte__ist_selbstständig
        See basic input variable :ref:`einkommensteuer__einkünfte__ist_selbstständig <einkommensteuer__einkünfte__ist_selbstständig>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.


    Returns
    -------

    """
    if einkommensteuer__einkünfte__ist_selbstständig:
        out = 0.0
    elif sozialversicherung__geringfügig_beschäftigt:
        out = (
            einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m
            * sozialv_beitr_params["ag_abgaben_geringf"]["ges_krankenv"]
        )
    else:
        out = einkommen_m * beitragssatz_arbeitgeber

    return out


@policy_function(start_date="2003-04-01", leaf_name="betrag_arbeitgeber_m")
def betrag_arbeitgeber_mit_midijob_m(  # noqa: PLR0913
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__in_gleitzone: bool,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m: float,
    betrag_arbeitgeber_midijob_m: float,
    einkommen_m: float,
    einkommensteuer__einkünfte__ist_selbstständig: bool,
    sozialv_beitr_params: dict,
    beitragssatz_arbeitgeber: float,
) -> float:
    """Employer's public health insurance contribution.

    After Midijob introduction in April 2003.

    Parameters
    ----------
    sozialversicherung__geringfügig_beschäftigt
        See :func:`sozialversicherung__geringfügig_beschäftigt`.
    betrag_arbeitgeber_midijob_m
        See :func:`betrag_arbeitgeber_midijob_m`.
    einkommen_m
        See :func:`einkommen_m`.
    beitragssatz_arbeitgeber
        See :func:`beitragssatz_arbeitgeber`.
    sozialversicherung__in_gleitzone
        See :func:`sozialversicherung__in_gleitzone`.
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m
        See basic input variable :ref:`einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m <einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m>`.
    einkommensteuer__einkünfte__ist_selbstständig
        See basic input variable :ref:`einkommensteuer__einkünfte__ist_selbstständig <einkommensteuer__einkünfte__ist_selbstständig>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.


    Returns
    -------

    """
    if einkommensteuer__einkünfte__ist_selbstständig:
        out = 0.0
    elif sozialversicherung__geringfügig_beschäftigt:
        out = (
            einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m
            * sozialv_beitr_params["ag_abgaben_geringf"]["ges_krankenv"]
        )
    elif sozialversicherung__in_gleitzone:
        out = betrag_arbeitgeber_midijob_m
    else:
        out = einkommen_m * beitragssatz_arbeitgeber

    return out


@policy_function()
def betrag_versicherter_regulär_beschäftigt_m(
    einkommen_m: float,
    beitragssatz_arbeitnehmer: float,
) -> float:
    """Employee's health insurance contributions for regular jobs.

    Parameters
    ----------
    einkommen_m
        See :func:`einkommen_m`.
    beitragssatz_arbeitnehmer
        See :func:`beitragssatz_arbeitnehmer`.
    Returns
    -------

    """
    return beitragssatz_arbeitnehmer * einkommen_m


@policy_function()
def betrag_selbstständig_m(
    bemessungsgrundlage_selbstständig_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Health insurance contributions for self-employed's income. The self-employed
    pay the full reduced contribution.

    Parameters
    ----------
    bemessungsgrundlage_selbstständig_m
        See :func:`bemessungsgrundlage_selbstständig_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    params = sozialv_beitr_params["beitr_satz"]["ges_krankenv"]
    ermäßigter_beitrag = (
        params["ermäßigt"] if ("ermäßigt" in params) else params["mean_allgemein"]
    )
    zusatzbeitrag = params.get("mean_zusatzbeitrag", 0.0)
    ges_krankenv_beitr_satz_selbst = ermäßigter_beitrag + zusatzbeitrag

    return ges_krankenv_beitr_satz_selbst * bemessungsgrundlage_selbstständig_m


@policy_function()
def betrag_rentner_m(
    bemessungsgrundlage_rente_m: float,
    beitragssatz_arbeitnehmer: float,
) -> float:
    """Health insurance contributions for pension incomes.

    Parameters
    ----------
    bemessungsgrundlage_rente_m
        See :func:`bemessungsgrundlage_rente_m`.
    beitragssatz_arbeitnehmer
        See :func:`beitragssatz_arbeitnehmer`.
    Returns
    -------

    """

    return beitragssatz_arbeitnehmer * bemessungsgrundlage_rente_m


@policy_function(start_date="2003-04-01")
def betrag_gesamt_midijob_m(
    sozialversicherung__midijob_bemessungsentgelt_m: float,
    beitragssatz_arbeitnehmer: float,
    beitragssatz_arbeitgeber: float,
) -> float:
    """Sum of employee and employer health insurance contribution for midijobs.

    Midijobs were introduced in April 2003.

    Parameters
    ----------
    sozialversicherung__midijob_bemessungsentgelt_m
        See :func:`sozialversicherung__midijob_bemessungsentgelt_m`.
    beitragssatz_arbeitnehmer
        See
        :func:`beitragssatz_arbeitnehmer`.
    beitragssatz_arbeitgeber
        See
        :func:`beitragssatz_arbeitgeber`.

    Returns
    -------

    """
    return (
        beitragssatz_arbeitnehmer + beitragssatz_arbeitgeber
    ) * sozialversicherung__midijob_bemessungsentgelt_m


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="betrag_arbeitgeber_midijob_m",
)
def betrag_arbeitgeber_midijob_anteil_einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m(
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m: float,
    sozialversicherung__in_gleitzone: bool,
    beitragssatz_arbeitgeber: float,
) -> float:
    """Employers' health insurance contribution for midijobs until September 2022.

    Midijobs were introduced in April 2003.

    Parameters
    ----------
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m
        See basic input variable :ref:`einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m <einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m>`.
    sozialversicherung__in_gleitzone
        See :func:`sozialversicherung__in_gleitzone`.
    beitragssatz_arbeitgeber
        See
        :func:`beitragssatz_arbeitgeber`.
    Returns
    -------

    """
    if sozialversicherung__in_gleitzone:
        out = (
            beitragssatz_arbeitgeber
            * einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m
        )
    else:
        out = 0.0

    return out


@policy_function(start_date="2022-10-01", leaf_name="betrag_arbeitgeber_midijob_m")
def betrag_arbeitgeber_midijob_residuum_m(
    betrag_gesamt_midijob_m: float,
    betrag_versicherter_midijob_m: float,
    sozialversicherung__in_gleitzone: bool,
) -> float:
    """Employer's health insurance contribution for midijobs since October
    2022.

    Parameters
    ----------
    betrag_gesamt_midijob_m
        See :func:`betrag_gesamt_midijob_m`.
    betrag_versicherter_midijob_m
        See :func:`betrag_versicherter_midijob_m`.
    sozialversicherung__in_gleitzone
        See :func:`sozialversicherung__in_gleitzone`.
    beitragssatz_arbeitgeber
        See
        :func:`beitragssatz_arbeitgeber`.
    Returns
    -------

    """
    if sozialversicherung__in_gleitzone:
        out = betrag_gesamt_midijob_m - betrag_versicherter_midijob_m
    else:
        out = 0.0

    return out


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="betrag_versicherter_midijob_m",
)
def betrag_versicherter_midijob_residuum_m(
    betrag_gesamt_midijob_m: float,
    betrag_arbeitgeber_midijob_m: float,
) -> float:
    """Employee's health insurance contribution for midijobs until September 2022.

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
def betrag_versicherter_midijob_anteil_beitragspflichtiger_einnahmen_m(
    sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m: float,
    beitragssatz_arbeitnehmer: float,
) -> float:
    """Employee's health insurance contribution for midijobs since October 2022.

    Parameters
    ----------
    sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m
        See :func:`sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m`.
    beitragssatz_arbeitnehmer
        See
        :func:`beitragssatz_arbeitnehmer`.
    Returns
    -------

    """
    return (
        sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m
        * beitragssatz_arbeitnehmer
    )
