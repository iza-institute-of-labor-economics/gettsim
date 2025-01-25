from _gettsim.functions.policy_function import policy_function


@policy_function(end_date="2003-03-31", leaf_name="ges_krankenv_beitr_arbeitnehmer_m")
def ges_krankenv_beitr_arbeitnehmer_m_vor_midijob(
    geringfügig_beschäftigt: bool,
    ges_krankenv_beitr_rentner_m: float,
    ges_krankenv_beitr_selbstständig_m: float,
    _ges_krankenv_beitr_arbeitnehmer_reg_beschäftigt_m: float,
    selbstständig: bool,
) -> float:
    """Employee's public health insurance contribution.

    Before Midijob introduction in April 2003.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    ges_krankenv_beitr_rentner_m
        See :func:`ges_krankenv_beitr_rentner_m`.
    ges_krankenv_beitr_selbstständig_m
        See :func:`ges_krankenv_beitr_selbstständig_m`.
    _ges_krankenv_beitr_arbeitnehmer_reg_beschäftigt_m
        See :func:`_ges_krankenv_beitr_arbeitnehmer_reg_beschäftigt_m`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.


    Returns
    -------

    """

    if selbstständig:
        out = ges_krankenv_beitr_selbstständig_m
    elif geringfügig_beschäftigt:
        out = 0.0
    else:
        out = _ges_krankenv_beitr_arbeitnehmer_reg_beschäftigt_m

    # Add the health insurance contribution for pensions
    return out + ges_krankenv_beitr_rentner_m


@policy_function(start_date="2003-04-01", leaf_name="ges_krankenv_beitr_arbeitnehmer_m")
def ges_krankenv_beitr_arbeitnehmer_m_mit_midijob(  # noqa: PLR0913
    geringfügig_beschäftigt: bool,
    ges_krankenv_beitr_rentner_m: float,
    ges_krankenv_beitr_selbstständig_m: float,
    in_gleitzone: bool,
    _ges_krankenv_beitr_midijob_arbeitnehmer_m: float,
    _ges_krankenv_beitr_arbeitnehmer_reg_beschäftigt_m: float,
    selbstständig: bool,
) -> float:
    """Employee's public health insurance contribution.

    After Midijob introduction in April 2003.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    ges_krankenv_beitr_rentner_m
        See :func:`ges_krankenv_beitr_rentner_m`.
    ges_krankenv_beitr_selbstständig_m
        See :func:`ges_krankenv_beitr_selbstständig_m`.
    _ges_krankenv_beitr_midijob_arbeitnehmer_m
        See :func:`_ges_krankenv_beitr_midijob_arbeitnehmer_m`.
    _ges_krankenv_beitr_arbeitnehmer_reg_beschäftigt_m
        See :func:`_ges_krankenv_beitr_arbeitnehmer_reg_beschäftigt_m`.
    in_gleitzone
        See :func:`in_gleitzone`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.


    Returns
    -------

    """

    if selbstständig:
        out = ges_krankenv_beitr_selbstständig_m
    elif geringfügig_beschäftigt:
        out = 0.0
    elif in_gleitzone:
        out = _ges_krankenv_beitr_midijob_arbeitnehmer_m
    else:
        out = _ges_krankenv_beitr_arbeitnehmer_reg_beschäftigt_m

    # Add the health insurance contribution for pensions
    return out + ges_krankenv_beitr_rentner_m


@policy_function(end_date="2003-03-31", leaf_name="ges_krankenv_beitr_arbeitgeber_m")
def ges_krankenv_beitr_arbeitgeber_m_vor_midijob(
    geringfügig_beschäftigt: bool,
    bruttolohn_m: float,
    _ges_krankenv_bruttolohn_m: float,
    selbstständig: bool,
    sozialv_beitr_params: dict,
    _ges_krankenv_beitr_satz_arbeitgeber: float,
) -> float:
    """Employer's public health insurance contribution.

    Before Midijob introduction in April 2003.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    _ges_krankenv_bruttolohn_m
        See :func:`_ges_krankenv_bruttolohn_m`.
    _ges_krankenv_beitr_satz_arbeitgeber
        See :func:`_ges_krankenv_beitr_satz_arbeitgeber`.
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
    elif geringfügig_beschäftigt:
        out = bruttolohn_m * sozialv_beitr_params["ag_abgaben_geringf"]["ges_krankenv"]
    else:
        out = _ges_krankenv_bruttolohn_m * _ges_krankenv_beitr_satz_arbeitgeber

    return out


@policy_function(start_date="2003-04-01", leaf_name="ges_krankenv_beitr_arbeitgeber_m")
def ges_krankenv_beitr_arbeitgeber_m_mit_midijob(
    geringfügig_beschäftigt: bool,
    in_gleitzone: bool,
    bruttolohn_m: float,
    _ges_krankenv_beitr_midijob_arbeitgeber_m: float,
    _ges_krankenv_bruttolohn_m: float,
    selbstständig: bool,
    sozialv_beitr_params: dict,
    _ges_krankenv_beitr_satz_arbeitgeber: float,
) -> float:
    """Employer's public health insurance contribution.

    After Midijob introduction in April 2003.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    _ges_krankenv_beitr_midijob_arbeitgeber_m
        See :func:`_ges_krankenv_beitr_midijob_arbeitgeber_m`.
    _ges_krankenv_bruttolohn_m
        See :func:`_ges_krankenv_bruttolohn_m`.
    _ges_krankenv_beitr_satz_arbeitgeber
        See :func:`_ges_krankenv_beitr_satz_arbeitgeber`.
    in_gleitzone
        See :func:`in_gleitzone`.
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
    elif geringfügig_beschäftigt:
        out = bruttolohn_m * sozialv_beitr_params["ag_abgaben_geringf"]["ges_krankenv"]
    elif in_gleitzone:
        out = _ges_krankenv_beitr_midijob_arbeitgeber_m
    else:
        out = _ges_krankenv_bruttolohn_m * _ges_krankenv_beitr_satz_arbeitgeber

    return out


@policy_function(
    start_date="2005-07-01",
    end_date="2014-12-31",
    leaf_name="ges_krankenv_zusatzbeitr_satz",
)
def ges_krankenv_zusatzbeitr_satz_from_sonderbeitr_satz(
    sozialv_beitr_params: dict,
) -> float:
    """Health insurance top-up (Zusatzbeitrag) rate until December 2014.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Zusatzbeitragssatz (based on Sonderbeitrag)

    """

    return sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["sonderbeitrag"]


@policy_function(
    start_date="2015-01-01",
    leaf_name="ges_krankenv_zusatzbeitr_satz",
)
def ges_krankenv_zusatzbeitr_satz_from_mean_zusatzbeitrag(
    sozialv_beitr_params: dict,
) -> float:
    """Health insurance top-up rate (Zusatzbeitrag) since January 2015.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Zusatzbeitragssatz (based on mean value of Zusatzbeitragssatz)

    """

    return sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["mean_zusatzbeitrag"]


@policy_function(
    end_date="2005-06-30",
)
def ges_krankenv_beitr_satz_arbeitnehmer(
    sozialv_beitr_params: dict,
) -> float:
    """Employee's health insurance contribution rate until June 2005.

    Basic split between employees and employers.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Beitragssatz for statutory health insurance.

    """

    return sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["mean_allgemein"] / 2


@policy_function(
    end_date="2005-06-30",
)
def _ges_krankenv_beitr_satz_arbeitnehmer_jahresanfang(
    sozialv_beitr_params: dict,
) -> float:
    """Employee's health insurance contribution rate for the beginning of the year until
    June 2005.

    Basic split between employees and employers.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Beitragssatz for statutory health insurance at the begging of the year.

    """
    return (
        sozialv_beitr_params["beitr_satz_jahresanfang"]["ges_krankenv"][
            "mean_allgemein"
        ]
        / 2
    )


@policy_function(
    start_date="2005-07-01",
    end_date="2008-12-31",
    leaf_name="ges_krankenv_beitr_satz_arbeitnehmer",
)
def ges_krankenv_beitr_satz_mean_kassenspezifisch_zusatzbeitrag_nur_arbeitnehmer(
    ges_krankenv_zusatzbeitr_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's health insurance contribution rate.

    From July 2005 until December 2008. The contribution rates consists of a general
    rate (split equally between employers and employees, differs across sickness funds)
    and a top-up rate, which is fully paid by employees.

    Parameters
    ----------
    ges_krankenv_zusatzbeitr_satz
        See :func:`ges_krankenv_zusatzbeitr_satz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Beitragssatz for statutory health insurance.

    """

    mean_allgemein = sozialv_beitr_params["beitr_satz"]["ges_krankenv"][
        "mean_allgemein"
    ]

    return mean_allgemein / 2 + ges_krankenv_zusatzbeitr_satz


@policy_function(
    start_date="2005-07-01",
    end_date="2008-12-31",
    leaf_name="_ges_krankenv_beitr_satz_arbeitnehmer_jahresanfang",
)
def ges_krankenv_beitr_satz_mean_kassenspezifisch_zusatzbeitrag_nur_arbeitnehmer_jahresanfang(  # noqa: E501
    ges_krankenv_zusatzbeitr_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's health insurance contribution rate at the beginning of the year.

    From July 2005 until December 2008. The contribution rates consists of a general
    rate (split equally between employers and employees, differs across sickness funds)
    and a top-up rate, which is fully paid by employees.

    Parameters
    ----------
    ges_krankenv_zusatzbeitr_satz
        See :func:`ges_krankenv_zusatzbeitr_satz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Beitragssatz for statutory health insurance at the beginning of the year.

    """

    mean_allgemein = sozialv_beitr_params["beitr_satz_jahresanfang"]["ges_krankenv"][
        "mean_allgemein"
    ]

    return mean_allgemein / 2 + ges_krankenv_zusatzbeitr_satz


@policy_function(
    start_date="2009-01-01",
    end_date="2018-12-31",
    leaf_name="ges_krankenv_beitr_satz_arbeitnehmer",
)
def ges_krankenv_beitr_satz_einheitlich_zusatzbeitrag_nur_arbeitnehmer(
    ges_krankenv_zusatzbeitr_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's health insurance contribution rate.

    From January 2009 until December 2018. The contribution rates consists of a general
    rate (split equally between employers and employees, same for all sickness funds)
    and a top-up rate, which is fully paid by employees.

    Parameters
    ----------
    ges_krankenv_zusatzbeitr_satz
        See :func:`ges_krankenv_zusatzbeitr_satz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Beitragssatz for statutory health insurance.

    """

    allgemein = sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["allgemein"]

    return allgemein / 2 + ges_krankenv_zusatzbeitr_satz


@policy_function(
    start_date="2009-01-01",
    end_date="2018-12-31",
    leaf_name="_ges_krankenv_beitr_satz_arbeitnehmer_jahresanfang",
)
def ges_krankenv_beitr_satz_einheitlich_zusatzbeitrag_nur_arbeitnehmer_jahresanfang(
    ges_krankenv_zusatzbeitr_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's health insurance contribution rate at the beginning of the year.

    From January 2009 until December 2018. The contribution rates consists of a general
    rate (split equally between employers and employees, same for all sickness funds)
    and a top-up rate, which is fully paid by employees.

    Parameters
    ----------
    ges_krankenv_zusatzbeitr_satz
        See :func:`ges_krankenv_zusatzbeitr_satz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Beitragssatz for statutory health insurance at the beginning of the year.

    """

    allgemein = sozialv_beitr_params["beitr_satz_jahresanfang"]["ges_krankenv"][
        "allgemein"
    ]

    return allgemein / 2 + ges_krankenv_zusatzbeitr_satz


@policy_function(
    start_date="2019-01-01",
    leaf_name="ges_krankenv_beitr_satz_arbeitnehmer",
)
def ges_krankenv_beitr_satz_zusatzbeitrag_arbeitnehmer_paritätisch(
    ges_krankenv_zusatzbeitr_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's health insurance contribution rate.

    Since 2019. Zusatzbeitrag is split equally between employers and employees.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    allgemeiner_beitr_satz = sozialv_beitr_params["beitr_satz"]["ges_krankenv"][
        "allgemein"
    ]
    return (allgemeiner_beitr_satz + ges_krankenv_zusatzbeitr_satz) / 2


@policy_function(
    start_date="2019-01-01",
    leaf_name="_ges_krankenv_beitr_satz_arbeitnehmer_jahresanfang",
)
def ges_krankenv_beitr_satz_zusatzbeitrag_arbeitnehmer_paritätisch_jahresanfang(
    ges_krankenv_zusatzbeitr_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's health insurance contribution rate at the beginning of the year.

    Zusatzbeitrag is now split equally between employers and employees.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    allgemeiner_beitr_satz = sozialv_beitr_params["beitr_satz_jahresanfang"][
        "ges_krankenv"
    ]["allgemein"]
    return (allgemeiner_beitr_satz + ges_krankenv_zusatzbeitr_satz) / 2


@policy_function(
    end_date="2008-12-31",
    leaf_name="_ges_krankenv_beitr_satz_arbeitgeber",
)
def ges_krankenv_beitr_satz_arbeitgeber_mean_kassenspezifisch_zusatzbeitrag_nur_arbeitnehmer(  # noqa: E501
    sozialv_beitr_params: dict,
) -> float:
    """Employer's health insurance contribution rate.

    Until 2008, the top-up contribution rate (Zusatzbeitrag) was not considered.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """

    return sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["mean_allgemein"] / 2


@policy_function(
    end_date="2008-12-31",
    leaf_name="_ges_krankenv_beitr_satz_arbeitgeber_jahresanfang",
)
def ges_krankenv_beitr_satz_arbeitgeber_mean_kassenspezifisch_zusatzbeitrag_nur_arbeitnehmer_jahresanfang(  # noqa: E501
    sozialv_beitr_params: dict,
) -> float:
    """Employer's health insurance contribution rate at the begging of the year.

    Until 2008, the top-up contribution rate (Zusatzbeitrag) was not considered.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """

    return (
        sozialv_beitr_params["beitr_satz_jahresanfang"]["ges_krankenv"][
            "mean_allgemein"
        ]
        / 2
    )


@policy_function(
    start_date="2009-01-01",
    end_date="2018-12-31",
    leaf_name="_ges_krankenv_beitr_satz_arbeitgeber",
)
def ges_krankenv_beitr_satz_arbeitgeber_einheitlich_zusatzbeitrag_nur_arbeitnehmer(
    sozialv_beitr_params: dict,
) -> float:
    """Employer's health insurance contribution rate.

    From 2009 until 2018, the contribution rate was uniform for all health insurers,
    Zusatzbeitrag irrelevant.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """

    return sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["allgemein"] / 2


@policy_function(
    start_date="2009-01-01",
    end_date="2018-12-31",
    leaf_name="_ges_krankenv_beitr_satz_arbeitgeber_jahresanfang",
)
def ges_krankenv_beitr_satz_arbeitgeber_einheitlich_zusatzbeitrag_nur_arbeitnehmer_jahresanfang(  # noqa: E501
    sozialv_beitr_params: dict,
) -> float:
    """Employer's health insurance contribution rate at the beginning of the year.

    From 2009 until 2018, the contribution rate was uniform for all health insurers,
    Zusatzbeitrag irrelevant.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """

    return (
        sozialv_beitr_params["beitr_satz_jahresanfang"]["ges_krankenv"]["allgemein"] / 2
    )


@policy_function(
    start_date="2019-01-01",
    leaf_name="_ges_krankenv_beitr_satz_arbeitgeber",
)
def _ges_krankenv_beitr_satz_arbeitgeber_zusatzbeitrag_paritätisch(
    ges_krankenv_beitr_satz_arbeitnehmer: float,
) -> float:
    """Employer's health insurance contribution rate.

    Since 2019, the full contribution rate is now split equally between employers and
    employees.

    Parameters
    ----------
    ges_krankenv_beitr_satz_arbeitnehmer
        See :func:`ges_krankenv_beitr_satz_arbeitnehmer`.

    Returns
    -------

    """
    return ges_krankenv_beitr_satz_arbeitnehmer


@policy_function(
    start_date="2019-01-01",
    leaf_name="_ges_krankenv_beitr_satz_arbeitgeber_jahresanfang",
)
def _ges_krankenv_beitr_satz_arbeitgeber_zusatzbeitrag_paritätisch_jahresanfang(
    _ges_krankenv_beitr_satz_arbeitnehmer_jahresanfang: float,
) -> float:
    """Employer's health insurance contribution rate at the beginning of the year.

    Since 2019, the full contribution rate is now split equally between employers and
    employees.

    Parameters
    ----------
    ges_krankenv_beitr_satz_arbeitnehmer
        See :func:`ges_krankenv_beitr_satz_arbeitnehmer`.

    Returns
    -------

    """
    return _ges_krankenv_beitr_satz_arbeitnehmer_jahresanfang


def _ges_krankenv_bruttolohn_reg_beschäftigt_m(
    bruttolohn_m: float,
    _ges_krankenv_beitr_bemess_grenze_m: float,
) -> float:
    """Income subject to public health insurance contributions.

    This does not consider reduced contributions for Mini- and Midijobs. Relevant for
    the computation of payroll taxes.

    Parameters
    ----------
    bruttolohn_m
        See :func:`bruttolohn_m`.
    _ges_krankenv_beitr_bemess_grenze_m
        See :func:`_ges_krankenv_beitr_bemess_grenze_m`.

    Returns
    -------
    Income subject to public health insurance contributions.
    """

    return min(bruttolohn_m, _ges_krankenv_beitr_bemess_grenze_m)


def _ges_krankenv_bruttolohn_m(
    _ges_krankenv_bruttolohn_reg_beschäftigt_m: float,
    regulär_beschäftigt: bool,
) -> float:
    """Wage subject to public health insurance contributions.

    This affects marginally employed persons and high wages for above the assessment
    ceiling.

    Parameters
    ----------
    bruttolohn_m
        See :func:`bruttolohn_m`.
    regulär_beschäftigt
        See :func:`regulär_beschäftigt`.
    _ges_krankenv_beitr_bemess_grenze_m
        See :func:`_ges_krankenv_beitr_bemess_grenze_m`.


    Returns
    -------

    """
    if regulär_beschäftigt:
        out = _ges_krankenv_bruttolohn_reg_beschäftigt_m
    else:
        out = 0.0
    return out


def _ges_krankenv_beitr_arbeitnehmer_reg_beschäftigt_m(
    _ges_krankenv_bruttolohn_m: float, ges_krankenv_beitr_satz_arbeitnehmer: float
) -> float:
    """Employee's health insurance contributions for regular jobs.

    Parameters
    ----------
    _ges_krankenv_bruttolohn_m
        See :func:`_ges_krankenv_bruttolohn_m`.
    ges_krankenv_beitr_satz_arbeitnehmer
        See :func:`ges_krankenv_beitr_satz_arbeitnehmer`.
    Returns
    -------

    """

    return ges_krankenv_beitr_satz_arbeitnehmer * _ges_krankenv_bruttolohn_m


def _ges_krankenv_bemessungsgrundlage_eink_selbständig(
    eink_selbst_m: float,
    _ges_krankenv_bezugsgröße_selbst_m: float,
    selbstständig: bool,
    in_priv_krankenv: bool,
    _ges_krankenv_beitr_bemess_grenze_m: float,
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
    _ges_krankenv_bezugsgröße_selbst_m
        See :func:`_ges_krankenv_bezugsgröße_selbst_m`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.
    in_priv_krankenv
        See basic input variable :ref:`in_priv_krankenv <in_priv_krankenv>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    _ges_krankenv_beitr_bemess_grenze_m
        See :func:`_ges_krankenv_beitr_bemess_grenze_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    # Calculate if self employed insures via public health insurance.
    if selbstständig and not in_priv_krankenv:
        out = min(
            _ges_krankenv_beitr_bemess_grenze_m,
            max(
                _ges_krankenv_bezugsgröße_selbst_m
                * sozialv_beitr_params[
                    "mindestanteil_bezugsgröße_beitragspf_einnahme_selbst"
                ],
                eink_selbst_m,
            ),
        )
    else:
        out = 0.0

    return out


def ges_krankenv_beitr_selbstständig_m(
    _ges_krankenv_bemessungsgrundlage_eink_selbständig: float,
    sozialv_beitr_params: dict,
) -> float:
    """Health insurance contributions for self-employed's income. The self-employed
    pay the full reduced contribution.

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_eink_selbständig
        See :func:`_ges_krankenv_bemessungsgrundlage_eink_selbständig`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """

    params = sozialv_beitr_params["beitr_satz"]["ges_krankenv"]
    ermäßigter_beitrag = (
        params["ermäßigt"] if ("ermäßigt" in params) else params["mean_allgemein"]
    )
    zusatzbeitrag = (
        params["mean_zusatzbeitrag"] if "mean_zusatzbeitrag" in params else 0.0
    )
    ges_krankenv_beitr_satz_selbst = ermäßigter_beitrag + zusatzbeitrag

    out = (
        ges_krankenv_beitr_satz_selbst
        * _ges_krankenv_bemessungsgrundlage_eink_selbständig
    )
    return out


def _ges_krankenv_bemessungsgrundlage_rente_m(
    sum_ges_rente_priv_rente_m: float,
    _ges_krankenv_beitr_bemess_grenze_m: float,
) -> float:
    """Pension income which is subject to health insurance contribution.

    Parameters
    ----------
    sum_ges_rente_priv_rente_m
        See :func:`sum_ges_rente_priv_rente_m`.
    _ges_krankenv_beitr_bemess_grenze_m
        See :func:`_ges_krankenv_beitr_bemess_grenze_m`.

    Returns
    -------

    """
    return min(sum_ges_rente_priv_rente_m, _ges_krankenv_beitr_bemess_grenze_m)


def ges_krankenv_beitr_rentner_m(
    _ges_krankenv_bemessungsgrundlage_rente_m: float,
    ges_krankenv_beitr_satz_arbeitnehmer: float,
) -> float:
    """Health insurance contributions for pension incomes.

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_rente_m
        See :func:`_ges_krankenv_bemessungsgrundlage_rente_m`.
    ges_krankenv_beitr_satz_arbeitnehmer
        See :func:`ges_krankenv_beitr_satz_arbeitnehmer`.
    Returns
    -------

    """

    return (
        ges_krankenv_beitr_satz_arbeitnehmer * _ges_krankenv_bemessungsgrundlage_rente_m
    )


@policy_function(start_date="2003-04-01")
def _ges_krankenv_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m(
    midijob_bemessungsentgelt_m: float,
    ges_krankenv_beitr_satz_arbeitnehmer: float,
    _ges_krankenv_beitr_satz_arbeitgeber: float,
) -> float:
    """Sum of employee and employer health insurance contribution for midijobs.

    Midijobs were introduced in April 2003.

    Parameters
    ----------
    midijob_bemessungsentgelt_m
        See :func:`midijob_bemessungsentgelt_m`.
    ges_krankenv_beitr_satz_arbeitnehmer
        See :func:`ges_krankenv_beitr_satz_arbeitnehmer`.
    _ges_krankenv_beitr_satz_arbeitgeber
        See :func:`_ges_krankenv_beitr_satz_arbeitgeber`.

    Returns
    -------

    """
    out = (
        ges_krankenv_beitr_satz_arbeitnehmer + _ges_krankenv_beitr_satz_arbeitgeber
    ) * midijob_bemessungsentgelt_m
    return out


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="_ges_krankenv_beitr_midijob_arbeitgeber_m",
)
def _ges_krankenv_beitr_midijob_arbeitgeber_m_anteil_bruttolohn(
    bruttolohn_m: float, in_gleitzone: bool, _ges_krankenv_beitr_satz_arbeitgeber: float
) -> float:
    """Employers' health insurance contribution for midijobs until September 2022.

    Midijobs were introduced in April 2003.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    in_gleitzone
        See :func:`in_gleitzone`.
    _ges_krankenv_beitr_satz_arbeitgeber
        See :func:`_ges_krankenv_beitr_satz_arbeitgeber`.
    Returns
    -------

    """
    if in_gleitzone:
        out = _ges_krankenv_beitr_satz_arbeitgeber * bruttolohn_m
    else:
        out = 0.0

    return out


@policy_function(
    start_date="2022-10-01", leaf_name="_ges_krankenv_beitr_midijob_arbeitgeber_m"
)
def _ges_krankenv_beitr_midijob_arbeitgeber_m_residuum(
    _ges_krankenv_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m: float,
    _ges_krankenv_beitr_midijob_arbeitnehmer_m: float,
    in_gleitzone: bool,
) -> float:
    """Employer's health insurance contribution for midijobs since October
    2022.

    Parameters
    ----------
    _ges_krankenv_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m
        See :func:`_ges_krankenv_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m`.
    _ges_krankenv_beitr_midijob_arbeitnehmer_m
        See :func:`_ges_krankenv_beitr_midijob_arbeitnehmer_m`.
    in_gleitzone
        See :func:`in_gleitzone`.
    _ges_krankenv_beitr_satz_arbeitgeber
        See :func:`_ges_krankenv_beitr_satz_arbeitgeber`.
    Returns
    -------

    """
    if in_gleitzone:
        out = (
            _ges_krankenv_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m
            - _ges_krankenv_beitr_midijob_arbeitnehmer_m
        )
    else:
        out = 0.0

    return out


@policy_function(
    start_date="2003-04-01",
    end_date="2022-09-30",
    leaf_name="_ges_krankenv_beitr_midijob_arbeitnehmer_m",
)
def _ges_krankenv_beitr_midijob_arbeitnehmer_m_residuum(
    _ges_krankenv_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m: float,
    _ges_krankenv_beitr_midijob_arbeitgeber_m: float,
) -> float:
    """Employee's health insurance contribution for midijobs until September 2022.

    Parameters
    ----------
    _ges_krankenv_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m
        See :func:`_ges_krankenv_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m`.
    _ges_krankenv_beitr_midijob_arbeitgeber_m
        See :func:`_ges_krankenv_beitr_midijob_arbeitgeber_m`.
    Returns
    -------

    """
    return (
        _ges_krankenv_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m
        - _ges_krankenv_beitr_midijob_arbeitgeber_m
    )


@policy_function(
    start_date="2022-10-01", leaf_name="_ges_krankenv_beitr_midijob_arbeitnehmer_m"
)
def _ges_krankenv_beitr_midijob_arbeitnehmer_m_anteil_beitragspfl_einnahme(
    _midijob_beitragspfl_einnahme_arbeitnehmer_m: float,
    ges_krankenv_beitr_satz_arbeitnehmer: float,
) -> float:
    """Employee's health insurance contribution for midijobs since October 2022.

    Parameters
    ----------
    _midijob_beitragspfl_einnahme_arbeitnehmer_m
        See :func:`_midijob_beitragspfl_einnahme_arbeitnehmer_m`.
    ges_krankenv_beitr_satz_arbeitnehmer
        See :func:`ges_krankenv_beitr_satz_arbeitnehmer`.
    Returns
    -------

    """
    return (
        _midijob_beitragspfl_einnahme_arbeitnehmer_m
        * ges_krankenv_beitr_satz_arbeitnehmer
    )
