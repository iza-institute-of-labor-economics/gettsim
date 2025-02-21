"""Public health insurance contributions."""

from _gettsim.shared import policy_info


@policy_info(end_date="2003-03-31", name_in_dag="betrag_arbeitnehmer_m")
def betrag_arbeitnehmer_vor_midijob_m(
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    betrag_rentner_m: float,
    betrag_selbständig_m: float,
    betrag_arbeitnehmer_regulär_beschäftigt_m: float,
    selbstständig: bool,
) -> float:
    """Employee's public health insurance contribution.

    Before Midijob introduction in April 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    betrag_rentner_m
        See :func:`betrag_rentner_m`.
    betrag_selbständig_m
        See :func:`betrag_selbständig_m`.
    betrag_arbeitnehmer_regulär_beschäftigt_m
        See :func:`betrag_arbeitnehmer_regulär_beschäftigt_m`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.


    Returns
    -------

    """
    if selbstständig:
        out = betrag_selbständig_m
    elif einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = betrag_arbeitnehmer_regulär_beschäftigt_m

    # Add the health insurance contribution for pensions
    return out + betrag_rentner_m


@policy_info(start_date="2003-04-01", name_in_dag="betrag_arbeitnehmer_m")
def betrag_arbeitnehmer_mit_midijob_m(  # noqa: PLR0913
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    betrag_rentner_m: float,
    betrag_selbständig_m: float,
    einkommensgrenzen__in_gleitzone: bool,
    betrag_arbeitnehmer_midijob_m: float,
    betrag_arbeitnehmer_regulär_beschäftigt_m: float,
    selbstständig: bool,
) -> float:
    """Employee's public health insurance contribution.

    After Midijob introduction in April 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    betrag_rentner_m
        See :func:`betrag_rentner_m`.
    betrag_selbständig_m
        See :func:`betrag_selbständig_m`.
    betrag_arbeitnehmer_midijob_m
        See :func:`betrag_arbeitnehmer_midijob_m`.
    betrag_arbeitnehmer_regulär_beschäftigt_m
        See :func:`betrag_arbeitnehmer_regulär_beschäftigt_m`.
    einkommensgrenzen__in_gleitzone
        See :func:`einkommensgrenzen__in_gleitzone`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.


    Returns
    -------

    """
    if selbstständig:
        out = betrag_selbständig_m
    elif einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    elif einkommensgrenzen__in_gleitzone:
        out = betrag_arbeitnehmer_midijob_m
    else:
        out = betrag_arbeitnehmer_regulär_beschäftigt_m

    # Add the health insurance contribution for pensions
    return out + betrag_rentner_m


@policy_info(end_date="2003-03-31", name_in_dag="betrag_arbeitgeber_m")
def betrag_arbeitgeber_vor_midijob_m(
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    bruttolohn_m: float,
    sozialversicherungsbeitraege__krankenversicherung__einkommen__betrag_m: float,
    selbstständig: bool,
    sozialv_beitr_params: dict,
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitgeber: float,
) -> float:
    """Employer's public health insurance contribution.

    Before Midijob introduction in April 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    sozialversicherungsbeitraege__krankenversicherung__einkommen__betrag_m
        See :func:`sozialversicherungsbeitraege__krankenversicherung__einkommen__betrag_m`.
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitgeber
        See :func:`sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitgeber`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.


    Returns
    -------

    """
    if selbstständig:
        out = 0.0
    elif einkommensgrenzen__geringfügig_beschäftigt:
        out = bruttolohn_m * sozialv_beitr_params["ag_abgaben_geringf"]["ges_krankenv"]
    else:
        out = (
            sozialversicherungsbeitraege__krankenversicherung__einkommen__betrag_m
            * sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitgeber
        )

    return out


@policy_info(start_date="2003-04-01", name_in_dag="betrag_arbeitgeber_m")
def betrag_arbeitgeber_mit_midijob_m(
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    einkommensgrenzen__in_gleitzone: bool,
    bruttolohn_m: float,
    betrag_arbeitgeber_midijob_m: float,
    sozialversicherungsbeitraege__krankenversicherung__einkommen__betrag_m: float,
    selbstständig: bool,
    sozialv_beitr_params: dict,
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitgeber: float,
) -> float:
    """Employer's public health insurance contribution.

    After Midijob introduction in April 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    betrag_arbeitgeber_midijob_m
        See :func:`betrag_arbeitgeber_midijob_m`.
    sozialversicherungsbeitraege__krankenversicherung__einkommen__betrag_m
        See :func:`sozialversicherungsbeitraege__krankenversicherung__einkommen__betrag_m`.
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitgeber
        See :func:`sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitgeber`.
    einkommensgrenzen__in_gleitzone
        See :func:`einkommensgrenzen__in_gleitzone`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.


    Returns
    -------

    """
    if selbstständig:
        out = 0.0
    elif einkommensgrenzen__geringfügig_beschäftigt:
        out = bruttolohn_m * sozialv_beitr_params["ag_abgaben_geringf"]["ges_krankenv"]
    elif einkommensgrenzen__in_gleitzone:
        out = betrag_arbeitgeber_midijob_m
    else:
        out = (
            sozialversicherungsbeitraege__krankenversicherung__einkommen__betrag_m
            * sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitgeber
        )

    return out


def betrag_arbeitnehmer_regulär_beschäftigt_m(
    sozialversicherungsbeitraege__krankenversicherung__einkommen__betrag_m: float,
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitnehmer: float,
) -> float:
    """Employee's health insurance contributions for regular jobs.

    Parameters
    ----------
    sozialversicherungsbeitraege__krankenversicherung__einkommen__betrag_m
        See :func:`sozialversicherungsbeitraege__krankenversicherung__einkommen__betrag_m`.
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitnehmer
        See :func:`sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitnehmer`.
    Returns
    -------

    """
    return (
        sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitnehmer
        * sozialversicherungsbeitraege__krankenversicherung__einkommen__betrag_m
    )


def betrag_selbständig_m(
    sozialversicherungsbeitraege__krankenversicherung__einkommen__bemessungsgrundlage_selbständig_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Health insurance contributions for self-employed's income. The self-employed
    pay the full reduced contribution.

    Parameters
    ----------
    sozialversicherungsbeitraege__krankenversicherung__einkommen__bemessungsgrundlage_selbständig_m
        See :func:`sozialversicherungsbeitraege__krankenversicherung__einkommen__bemessungsgrundlage_selbständig_m`.
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

    return (
        ges_krankenv_beitr_satz_selbst
        * sozialversicherungsbeitraege__krankenversicherung__einkommen__bemessungsgrundlage_selbständig_m
    )


def betrag_rentner_m(
    sozialversicherungsbeitraege__krankenversicherung__einkommen__bemessungsgrundlage_rente_m: float,
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitnehmer: float,
) -> float:
    """Health insurance contributions for pension incomes.

    Parameters
    ----------
    sozialversicherungsbeitraege__krankenversicherung__einkommen__bemessungsgrundlage_rente_m
        See :func:`sozialversicherungsbeitraege__krankenversicherung__einkommen__bemessungsgrundlage_rente_m`.
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitnehmer
        See :func:`sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitnehmer`.
    Returns
    -------

    """

    return (
        sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitnehmer
        * sozialversicherungsbeitraege__krankenversicherung__einkommen__bemessungsgrundlage_rente_m
    )


@policy_info(start_date="2003-04-01")
def betrag_gesamt_midijob_m(
    einkommensgrenzen__midijob_bemessungsentgelt_m: float,
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitnehmer: float,
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitgeber: float,
) -> float:
    """Sum of employee and employer health insurance contribution for midijobs.

    Midijobs were introduced in April 2003.

    Parameters
    ----------
    einkommensgrenzen__midijob_bemessungsentgelt_m
        See :func:`einkommensgrenzen__midijob_bemessungsentgelt_m`.
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitnehmer
        See :func:`sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitnehmer`.
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitgeber
        See :func:`sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitgeber`.

    Returns
    -------

    """
    return (
        sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitnehmer
        + sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitgeber
    ) * einkommensgrenzen__midijob_bemessungsentgelt_m


@policy_info(
    start_date="2003-04-01",
    end_date="2022-09-30",
    name_in_dag="betrag_arbeitgeber_midijob_m",
)
def betrag_arbeitgeber_midijob_anteil_bruttolohn_m(
    bruttolohn_m: float,
    einkommensgrenzen__in_gleitzone: bool,
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitgeber: float,
) -> float:
    """Employers' health insurance contribution for midijobs until September 2022.

    Midijobs were introduced in April 2003.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    einkommensgrenzen__in_gleitzone
        See :func:`einkommensgrenzen__in_gleitzone`.
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitgeber
        See :func:`sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitgeber`.
    Returns
    -------

    """
    if einkommensgrenzen__in_gleitzone:
        out = (
            sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitgeber
            * bruttolohn_m
        )
    else:
        out = 0.0

    return out


@policy_info(start_date="2022-10-01", name_in_dag="betrag_arbeitgeber_midijob_m")
def betrag_arbeitgeber_midijob_residuum_m(
    betrag_gesamt_midijob_m: float,
    betrag_arbeitnehmer_midijob_m: float,
    einkommensgrenzen__in_gleitzone: bool,
) -> float:
    """Employer's health insurance contribution for midijobs since October
    2022.

    Parameters
    ----------
    betrag_gesamt_midijob_m
        See :func:`betrag_gesamt_midijob_m`.
    betrag_arbeitnehmer_midijob_m
        See :func:`betrag_arbeitnehmer_midijob_m`.
    einkommensgrenzen__in_gleitzone
        See :func:`einkommensgrenzen__in_gleitzone`.
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitgeber
        See :func:`sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitgeber`.
    Returns
    -------

    """
    if einkommensgrenzen__in_gleitzone:
        out = betrag_gesamt_midijob_m - betrag_arbeitnehmer_midijob_m
    else:
        out = 0.0

    return out


@policy_info(
    start_date="2003-04-01",
    end_date="2022-09-30",
    name_in_dag="betrag_arbeitnehmer_midijob_m",
)
def betrag_arbeitnehmer_midijob_residuum_m(
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


@policy_info(start_date="2022-10-01", name_in_dag="betrag_arbeitnehmer_midijob_m")
def betrag_arbeitnehmer_midijob_anteil_beitragspfl_einnahme_m(
    einkommensgrenzen__beitragspfl_einnahmen_arbeitnehmer_m: float,
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitnehmer: float,
) -> float:
    """Employee's health insurance contribution for midijobs since October 2022.

    Parameters
    ----------
    einkommensgrenzen__beitragspfl_einnahmen_arbeitnehmer_m
        See :func:`einkommensgrenzen__beitragspfl_einnahmen_arbeitnehmer_m`.
    sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitnehmer
        See :func:`sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitnehmer`.
    Returns
    -------

    """
    return (
        einkommensgrenzen__beitragspfl_einnahmen_arbeitnehmer_m
        * sozialversicherungsbeitraege__krankenversicherung__beitragssatz__betrag_arbeitnehmer
    )
