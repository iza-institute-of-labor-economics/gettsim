"""Income relevant for public health insurance contributions."""


def betrag_m(
    betrag_regulär_beschäftigt_m: float,
    einkommensgrenzen__regulär_beschäftigt: bool,
) -> float:
    """Wage subject to public health insurance contributions.

    This affects marginally employed persons and high wages for above the assessment
    ceiling.

    Parameters
    ----------
    bruttolohn_m
        See :func:`bruttolohn_m`.
    einkommensgrenzen__regulär_beschäftigt
        See :func:`einkommensgrenzen__regulär_beschäftigt`.
    beitragsbemessungsgrenze_m
        See :func:`beitragsbemessungsgrenze_m`.


    Returns
    -------

    """
    if einkommensgrenzen__regulär_beschäftigt:
        out = betrag_regulär_beschäftigt_m
    else:
        out = 0.0
    return out


def betrag_regulär_beschäftigt_m(
    bruttolohn_m: float,
    beitragsbemessungsgrenze_m: float,
) -> float:
    """Income subject to public health insurance contributions.

    This does not consider reduced contributions for Mini- and Midijobs. Relevant for
    the computation of payroll taxes.

    Parameters
    ----------
    bruttolohn_m
        See :func:`bruttolohn_m`.
    beitragsbemessungsgrenze_m
        See :func:`beitragsbemessungsgrenze_m`.

    Returns
    -------
    Income subject to public health insurance contributions.
    """

    return min(bruttolohn_m, beitragsbemessungsgrenze_m)


def bemessungsgrundlage_selbständig_m(
    eink_selbst_m: float,
    bezugsgröße_selbständig_m: float,
    selbstständig: bool,
    in_priv_krankenv: bool,
    beitragsbemessungsgrenze_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Self-employed income which is subject to health insurance contributions.

    The value is bounded from below and from above. Only affects those self-employed who
    voluntarily contribute to the public health system.

    Reference: §240 SGB V Abs. 4

    Parameters
    ----------
    eink_selbst_m
        See basic input variable :ref:`eink_selbst_m <eink_selbst_m>`.
    bezugsgröße_selbständig_m
        See :func:`bezugsgröße_selbständig_m`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.
    in_priv_krankenv
        See basic input variable :ref:`in_priv_krankenv <in_priv_krankenv>`.
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
    if selbstständig and not in_priv_krankenv:
        out = min(
            beitragsbemessungsgrenze_m,
            max(
                bezugsgröße_selbständig_m
                * sozialv_beitr_params[
                    "mindestanteil_bezugsgröße_beitragspf_einnahme_selbst"
                ],
                eink_selbst_m,
            ),
        )
    else:
        out = 0.0

    return out


def beitragsbemessungsgrenze_m(wohnort_ost: bool, sozialv_beitr_params: dict) -> float:
    """Income threshold up to which health insurance payments apply.

    Parameters
    ----------
    wohnort_ost
        See :func:`wohnort_ost`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    The income threshold up to which the rate of health insurance contributions apply.

    """
    params = sozialv_beitr_params["beitr_bemess_grenze_m"]["ges_krankenv"]

    out = params["ost"] if wohnort_ost else params["west"]

    return float(out)


def bezugsgröße_selbständig_m(wohnort_ost: bool, sozialv_beitr_params: dict) -> float:
    """Threshold for self employment income subject to health insurance.

    Selecting by place of living the income threshold for self employed up to which the
    rate of health insurance contributions apply.

    Parameters
    ----------
    wohnort_ost
        See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    out = (
        sozialv_beitr_params["bezugsgröße_selbst_m"]["ost"]
        if wohnort_ost
        else sozialv_beitr_params["bezugsgröße_selbst_m"]["west"]
    )

    return float(out)


def bemessungsgrundlage_rente_m(
    sum_ges_rente_priv_rente_m: float,
    beitragsbemessungsgrenze_m: float,
) -> float:
    """Pension income which is subject to health insurance contribution.

    Parameters
    ----------
    sum_ges_rente_priv_rente_m
        See :func:`sum_ges_rente_priv_rente_m`.
    beitragsbemessungsgrenze_m
        See :func:`beitragsbemessungsgrenze_m`.

    Returns
    -------

    """
    return min(sum_ges_rente_priv_rente_m, beitragsbemessungsgrenze_m)
