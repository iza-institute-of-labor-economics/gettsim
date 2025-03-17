"""Income relevant for public health insurance contributions."""

from _gettsim.function_types import policy_function


@policy_function()
def einkommen_m(
    einkommen_regulär_beschäftigt_m: float,
    sozialversicherung__regulär_beschäftigt: bool,
) -> float:
    """Wage subject to public health insurance contributions.

    This affects marginally employed persons and high wages for above the assessment
    ceiling.

    Parameters
    ----------
    einnahmen__bruttolohn_m
        See :func:`einnahmen__bruttolohn_m`.
    sozialversicherung__regulär_beschäftigt
        See :func:`sozialversicherung__regulär_beschäftigt`.
    beitragsbemessungsgrenze_m
        See :func:`beitragsbemessungsgrenze_m`.


    Returns
    -------

    """
    if sozialversicherung__regulär_beschäftigt:
        out = einkommen_regulär_beschäftigt_m
    else:
        out = 0.0
    return out


@policy_function()
def einkommen_regulär_beschäftigt_m(
    einnahmen__bruttolohn_m: float,
    beitragsbemessungsgrenze_m: float,
) -> float:
    """Income subject to public health insurance contributions.

    This does not consider reduced contributions for Mini- and Midijobs. Relevant for
    the computation of payroll taxes.

    Parameters
    ----------
    einnahmen__bruttolohn_m
        See :func:`einnahmen__bruttolohn_m`.
    beitragsbemessungsgrenze_m
        See :func:`beitragsbemessungsgrenze_m`.

    Returns
    -------
    Income subject to public health insurance contributions.
    """

    return min(einnahmen__bruttolohn_m, beitragsbemessungsgrenze_m)


@policy_function()
def bemessungsgrundlage_selbstständig_m(  # noqa: PLR0913
    einkünfte__aus_selbstständiger_arbeit_m: float,
    bezugsgröße_selbstständig_m: float,
    einkünfte__ist_selbstständig: bool,
    privat_versichert: bool,
    beitragsbemessungsgrenze_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Self-employed income which is subject to health insurance contributions.

    The value is bounded from below and from above. Only affects those self-employed who
    voluntarily contribute to the public health system.

    Reference: §240 SGB V Abs. 4

    Parameters
    ----------
    einkünfte__aus_selbstständiger_arbeit_m
        See basic input variable :ref:`einkünfte__aus_selbstständiger_arbeit_m <einkünfte__aus_selbstständiger_arbeit_m>`.
    bezugsgröße_selbstständig_m
        See :func:`bezugsgröße_selbstständig_m`.
    einkünfte__ist_selbstständig
        See basic input variable :ref:`einkünfte__ist_selbstständig <einkünfte__ist_selbstständig>`.
    privat_versichert
        See basic input variable :ref:`privat_versichert <privat_versichert>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    beitragsbemessungsgrenze_m
        See :func:`beitragsbemessungsgrenze_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    # Calculate if self employed insures via public health insurance.
    if einkünfte__ist_selbstständig and not privat_versichert:
        out = min(
            beitragsbemessungsgrenze_m,
            max(
                bezugsgröße_selbstständig_m
                * sozialv_beitr_params[
                    "mindestanteil_bezugsgröße_beitragspf_einnahme_selbst"
                ],
                einkünfte__aus_selbstständiger_arbeit_m,
            ),
        )
    else:
        out = 0.0

    return out


@policy_function()
def beitragsbemessungsgrenze_m(
    demographics__wohnort_ost: bool, sozialv_beitr_params: dict
) -> float:
    """Income threshold up to which health insurance payments apply.

    Parameters
    ----------
    demographics__wohnort_ost
        See :func:`demographics__wohnort_ost`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    The income threshold up to which the rate of health insurance contributions apply.

    """
    params = sozialv_beitr_params["beitr_bemess_grenze_m"]["ges_krankenv"]

    out = params["ost"] if demographics__wohnort_ost else params["west"]

    return float(out)


@policy_function()
def bezugsgröße_selbstständig_m(
    demographics__wohnort_ost: bool, sozialv_beitr_params: dict
) -> float:
    """Threshold for self employment income subject to health insurance.

    Selecting by place of living the income threshold for self employed up to which the
    rate of health insurance contributions apply.

    Parameters
    ----------
    demographics__wohnort_ost
        See basic input variable :ref:`demographics__wohnort_ost <demographics__wohnort_ost>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    out = (
        sozialv_beitr_params["bezugsgröße_selbst_m"]["ost"]
        if demographics__wohnort_ost
        else sozialv_beitr_params["bezugsgröße_selbst_m"]["west"]
    )

    return float(out)


@policy_function()
def bemessungsgrundlage_rente_m(
    sozialversicherung__rente__altersrente__betrag_m: float,
    sozialversicherung__rente__private_rente_betrag_m: float,
    beitragsbemessungsgrenze_m: float,
) -> float:
    """Pension income which is subject to health insurance contribution.

    Parameters
    ----------
    sozialversicherung__rente__altersrente__betrag_m: float,
        See :func:`sozialversicherung__rente__altersrente__betrag_m`.
    sozialversicherung__rente__private_rente_betrag_m: float,
        See :func:`sozialversicherung__rente__private_rente_betrag_m`.
    beitragsbemessungsgrenze_m
        See :func:`beitragsbemessungsgrenze_m`.

    Returns
    -------

    """
    return min(
        sozialversicherung__rente__altersrente__betrag_m
        + sozialversicherung__rente__private_rente_betrag_m,
        beitragsbemessungsgrenze_m,
    )
