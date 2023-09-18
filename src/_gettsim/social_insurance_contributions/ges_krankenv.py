from _gettsim.shared import dates_active


@dates_active(end="2003-03-31", change_name="ges_krankenv_beitr_m")
def ges_krankenv_beitr_m_vor_midijob(
    geringfügig_beschäftigt: bool,
    ges_krankenv_beitr_rente_m: float,
    ges_krankenv_beitr_selbst_m: float,
    _ges_krankenv_beitr_reg_beschäftigt_m: float,
    selbstständig: bool,
) -> float:
    """Employee's public health insurance contribution.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    ges_krankenv_beitr_rente_m
        See :func:`ges_krankenv_beitr_rente_m`.
    ges_krankenv_beitr_selbst_m
        See :func:`ges_krankenv_beitr_selbst_m`.
    _ges_krankenv_beitr_reg_beschäftigt_m
        See :func:`_ges_krankenv_beitr_reg_beschäftigt_m`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.


    Returns
    -------

    """

    if selbstständig:
        out = ges_krankenv_beitr_selbst_m
    elif geringfügig_beschäftigt:
        out = 0.0
    else:
        out = _ges_krankenv_beitr_reg_beschäftigt_m

    # Add the health insurance contribution for pensions
    return out + ges_krankenv_beitr_rente_m


@dates_active(start="2003-04-01", change_name="ges_krankenv_beitr_m")
def ges_krankenv_beitr_m_mit_midijob(  # noqa: PLR0913
    geringfügig_beschäftigt: bool,
    ges_krankenv_beitr_rente_m: float,
    ges_krankenv_beitr_selbst_m: float,
    in_gleitzone: bool,
    _ges_krankenv_beitr_midijob_arbeitn_m: float,
    _ges_krankenv_beitr_reg_beschäftigt_m: float,
    selbstständig: bool,
) -> float:
    """Employee's public health insurance contribution.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    ges_krankenv_beitr_rente_m
        See :func:`ges_krankenv_beitr_rente_m`.
    ges_krankenv_beitr_selbst_m
        See :func:`ges_krankenv_beitr_selbst_m`.
    _ges_krankenv_beitr_midijob_arbeitn_m
        See :func:`_ges_krankenv_beitr_midijob_arbeitn_m`.
    _ges_krankenv_beitr_reg_beschäftigt_m
        See :func:`_ges_krankenv_beitr_reg_beschäftigt_m`.
    in_gleitzone
        See :func:`in_gleitzone`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.


    Returns
    -------

    """

    if selbstständig:
        out = ges_krankenv_beitr_selbst_m
    elif geringfügig_beschäftigt:
        out = 0.0
    elif in_gleitzone:
        out = _ges_krankenv_beitr_midijob_arbeitn_m
    else:
        out = _ges_krankenv_beitr_reg_beschäftigt_m

    # Add the health insurance contribution for pensions
    return out + ges_krankenv_beitr_rente_m


@dates_active(end="2003-03-31", change_name="ges_krankenv_beitr_arbeitg_m")
def ges_krankenv_beitr_arbeitg_m_vor_midijob(
    geringfügig_beschäftigt: bool,
    bruttolohn_m: float,
    _ges_krankenv_bruttolohn_m: float,
    selbstständig: bool,
    sozialv_beitr_params: dict,
    _ges_krankenv_beitr_satz_arbeitg: float,
) -> float:
    """Employer's public health insurance contribution.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    _ges_krankenv_bruttolohn_m
        See :func:`_ges_krankenv_bruttolohn_m`.
    _ges_krankenv_beitr_satz_arbeitg
        See :func:`_ges_krankenv_beitr_satz_arbeitg`.
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
        out = _ges_krankenv_bruttolohn_m * _ges_krankenv_beitr_satz_arbeitg

    return out


@dates_active(start="2003-04-01", change_name="ges_krankenv_beitr_arbeitg_m")
def ges_krankenv_beitr_arbeitg_m_mit_midijob(
    geringfügig_beschäftigt: bool,
    in_gleitzone: bool,
    bruttolohn_m: float,
    _ges_krankenv_beitr_midijob_arbeitg_m: float,
    _ges_krankenv_bruttolohn_m: float,
    selbstständig: bool,
    sozialv_beitr_params: dict,
    _ges_krankenv_beitr_satz_arbeitg: float,
) -> float:
    """Employer's public health insurance contribution.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    _ges_krankenv_beitr_midijob_arbeitg_m
        See :func:`_ges_krankenv_beitr_midijob_arbeitg_m`.
    _ges_krankenv_bruttolohn_m
        See :func:`_ges_krankenv_bruttolohn_m`.
    _ges_krankenv_beitr_satz_arbeitg
        See :func:`_ges_krankenv_beitr_satz_arbeitg`.
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
        out = _ges_krankenv_beitr_midijob_arbeitg_m
    else:
        out = _ges_krankenv_bruttolohn_m * _ges_krankenv_beitr_satz_arbeitg

    return out


@dates_active(
    start="2005-07-01",
    end="2014-12-31",
    change_name="ges_krankenv_zusatzbeitr_satz",
)
def ges_krankenv_zusatzbeitr_satz_from_sonderbeitr_satz(
    sozialv_beitr_params: dict,
) -> float:
    """Health insurance top-up rate until December 2014.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Zusatzbeitragssatz (based on Sonderbeitrag)

    """

    return sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["sonderbeitrag"]


@dates_active(
    start="2015-01-01",
    change_name="ges_krankenv_zusatzbeitr_satz",
)
def ges_krankenv_zusatzbeitr_satz_from_mean_zusatzbeitrag(
    sozialv_beitr_params: dict,
) -> float:
    """Calculate the top-up rate of the health care insurance since January 2015.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Zusatzbeitragssatz (based on mean value of Zusatzbeitragssatz)

    """

    return sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["mean_zusatzbeitrag"]


@dates_active(
    end="2005-06-30",
)
def ges_krankenv_beitr_satz(
    sozialv_beitr_params: dict,
) -> float:
    """Contribution rates of employees for health insurance, just a basic split
    between employees and employers. Incorporates regime changes regarding different
    values across insurers (pick "official" mean) and same contribution rate for all.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Beitragssatz for statutory health insurance.

    """

    return sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["mean_allgemein"] / 2


@dates_active(
    end="2005-06-30",
)
def _ges_krankenv_beitr_satz_jahresanfang(
    sozialv_beitr_params: dict,
) -> float:
    """Contribution rates of employees for health insurance for the beginning
    of a year, just a basic split between employees and employers. Incorporates
    regime changes regarding different values across insurers (pick "official" mean)
    and same contribution rate for all.

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


@dates_active(
    start="2005-07-01",
    end="2008-12-31",
    change_name="ges_krankenv_beitr_satz",
)
def ges_krankenv_beitr_satz_mean_kassenspezifisch_zusatzbeitrag_nur_arbeitn(
    ges_krankenv_zusatzbeitr_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Contribution rates of employees for health insurance.

    The contribution rates consists of a general rate (split equally between employers
    and employees, differs across sickness funds) and a top-up rate, which is fully paid
    by employees.

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


@dates_active(
    start="2005-07-01",
    end="2008-12-31",
    change_name="_ges_krankenv_beitr_satz_jahresanfang",
)
def ges_krankenv_beitr_satz_mean_kassenspezifisch_zusatzbeitrag_nur_arbeitn_jahresanfang(  # noqa: E501
    ges_krankenv_zusatzbeitr_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Contribution rates of employees for health insurance at the beginning of the
    year.

    The contribution rates consists of a general rate (split equally between employers
    and employees, differs across sickness funds) and a top-up rate, which is fully paid
    by employees.

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


@dates_active(
    start="2009-01-01",
    end="2018-12-31",
    change_name="ges_krankenv_beitr_satz",
)
def ges_krankenv_beitr_satz_einheitlich_zusatzbeitrag_nur_arbeitn(
    ges_krankenv_zusatzbeitr_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Contribution rates of employees for health insurance.

    The contribution rates consists of a general rate (split equally between employers
    and employees, same for all sickness funds) and a top-up rate, which is fully paid
    by employees.

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


@dates_active(
    start="2009-01-01",
    end="2018-12-31",
    change_name="_ges_krankenv_beitr_satz_jahresanfang",
)
def ges_krankenv_beitr_satz_einheitlich_zusatzbeitrag_nur_arbeitn_jahresanfang(
    ges_krankenv_zusatzbeitr_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Contribution rates of employees for health insurance at the beginning of the
    year.

    The contribution rates consists of a general rate (split equally between employers
    and employees, same for all sickness funds) and a top-up rate, which is fully paid
    by employees.

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


@dates_active(
    start="2019-01-01",
    change_name="ges_krankenv_beitr_satz",
)
def ges_krankenv_beitr_satz_zusatzbeitrag_paritätisch(
    ges_krankenv_zusatzbeitr_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Contribution rates of employees for health insurance.

    Zusatzbeitrag is split equally between employers and employees.

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


@dates_active(
    start="2019-01-01",
    change_name="_ges_krankenv_beitr_satz_jahresanfang",
)
def ges_krankenv_beitr_satz_zusatzbeitrag_paritätisch_jahresanfang(
    ges_krankenv_zusatzbeitr_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Contribution rates of employees for health insurance at the beginning of the
    year.

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


@dates_active(
    end="2008-12-31",
    change_name="_ges_krankenv_beitr_satz_arbeitg",
)
def ges_krankenv_beitr_satz_arbeitg_mean_kassenspezifisch_zusatzbeitrag_nur_arbeitn(
    sozialv_beitr_params: dict,
) -> float:
    """Contribution rates of employers for health insurance. Zusatzbeitrag irrelevant.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """

    return sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["mean_allgemein"] / 2


@dates_active(
    end="2008-12-31",
    change_name="_ges_krankenv_beitr_satz_arbeitg_jahresanfang",
)
def ges_krankenv_beitr_satz_arbeitg_mean_kassenspezifisch_zusatzbeitrag_nur_arbeitn_jahresanfang(  # noqa: E501
    sozialv_beitr_params: dict,
) -> float:
    """Contribution rates of employers for health insurance. Zusatzbeitrag irrelevant.

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


@dates_active(
    start="2009-01-01",
    end="2018-12-31",
    change_name="_ges_krankenv_beitr_satz_arbeitg",
)
def ges_krankenv_beitr_satz_arbeitg_einheitlich_zusatzbeitrag_nur_arbeitn(
    sozialv_beitr_params: dict,
) -> float:
    """Contribution rates of employers for health insurance. Uniform contribution rate
    for all health insurers, Zusatzbeitrag irrelevant.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """

    return sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["allgemein"] / 2


@dates_active(
    start="2009-01-01",
    end="2018-12-31",
    change_name="_ges_krankenv_beitr_satz_arbeitg_jahresanfang",
)
def ges_krankenv_beitr_satz_arbeitg_einheitlich_zusatzbeitrag_nur_arbeitn_jahresanfang(
    sozialv_beitr_params: dict,
) -> float:
    """Contribution rates of employers for health insurance at the beginning of the
    year. Uniform contribution rate for all health insurers, Zusatzbeitrag irrelevant.

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


@dates_active(
    start="2019-01-01",
    change_name="_ges_krankenv_beitr_satz_arbeitg",
)
def _ges_krankenv_beitr_satz_arbeitg_zusatzbeitrag_paritätisch(
    ges_krankenv_beitr_satz: float,
) -> float:
    """Contribution rates of employers for health insurance since 2019.

    The full contribution rate is now split equally between employers and employees.

    Parameters
    ----------
    ges_krankenv_beitr_satz
        See :func:`ges_krankenv_beitr_satz`.

    Returns
    -------

    """
    return ges_krankenv_beitr_satz


@dates_active(
    start="2019-01-01",
    change_name="_ges_krankenv_beitr_satz_arbeitg_jahresanfang",
)
def _ges_krankenv_beitr_satz_arbeitg_zusatzbeitrag_paritätisch_jahresanfang(
    _ges_krankenv_beitr_satz_jahresanfang: float,
) -> float:
    """Contribution rates of employers for health insurance for the beginning
    of a year since 2019.

    The full contribution rate is now split equally between employers and employees.

    Parameters
    ----------
    ges_krankenv_beitr_satz
        See :func:`ges_krankenv_beitr_satz`.

    Returns
    -------

    """
    return _ges_krankenv_beitr_satz_jahresanfang


def _ges_krankenv_bruttolohn_m(
    bruttolohn_m: float,
    _ges_krankenv_beitr_bemess_grenze_m: float,
    regulär_beschäftigt: bool,
) -> float:
    """Calculate the wage subject to public health insurance contributions. This affects
    marginally employed persons and high wages for above the assessment ceiling.

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
        out = min(bruttolohn_m, _ges_krankenv_beitr_bemess_grenze_m)
    else:
        out = 0.0
    return out


def _ges_krankenv_beitr_reg_beschäftigt_m(
    _ges_krankenv_bruttolohn_m: float, ges_krankenv_beitr_satz: float
) -> float:
    """Calculate health insurance contributions for regular jobs.

    Parameters
    ----------
    _ges_krankenv_bruttolohn_m
        See :func:`_ges_krankenv_bruttolohn_m`.
    ges_krankenv_beitr_satz
        See :func:`ges_krankenv_beitr_satz`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions for regularly
    employed income.

    """

    return ges_krankenv_beitr_satz * _ges_krankenv_bruttolohn_m


def _ges_krankenv_bemessungsgrundlage_eink_selbst(
    eink_selbst_m: float,
    _ges_krankenv_bezugsgröße_selbst_m: float,
    selbstständig: bool,
    in_priv_krankenv: bool,
    _ges_krankenv_beitr_bemess_grenze_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Choose the amount of self-employed income which is subject to health insurance
    contributions. The value is bounded from below and from above. Only affects those
    self-employed who voluntarily contribute to the public health system.

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


def ges_krankenv_beitr_selbst_m(
    _ges_krankenv_bemessungsgrundlage_eink_selbst: float, sozialv_beitr_params: dict
) -> float:
    """Health insurance contributions for self-employed's income. The self-employed
    pay the full reduced contribution.

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_eink_selbst
        See :func:`_ges_krankenv_bemessungsgrundlage_eink_selbst`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Monthly health insurance contributions for self-employed's income.

    """

    params = sozialv_beitr_params["beitr_satz"]["ges_krankenv"]
    ermäßigter_beitrag = (
        params["ermäßigt"] if ("ermäßigt" in params) else params["mean_allgemein"]
    )
    zusatzbeitrag = (
        params["mean_zusatzbeitrag"] if "mean_zusatzbeitrag" in params else 0.0
    )
    ges_krankenv_beitr_satz_selbst = ermäßigter_beitrag + zusatzbeitrag

    out = ges_krankenv_beitr_satz_selbst * _ges_krankenv_bemessungsgrundlage_eink_selbst
    return out


def _ges_krankenv_bemessungsgrundlage_rente_m(
    sum_ges_rente_priv_rente_m: float,
    _ges_krankenv_beitr_bemess_grenze_m: float,
) -> float:
    """Choose the amount of pension which is subject to health insurance contribution.

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


def ges_krankenv_beitr_rente_m(
    _ges_krankenv_bemessungsgrundlage_rente_m: float, ges_krankenv_beitr_satz: float
) -> float:
    """Calculate health insurance contributions for pension incomes.

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_rente_m
        See :func:`_ges_krankenv_bemessungsgrundlage_rente_m`.
    ges_krankenv_beitr_satz
        See :func:`ges_krankenv_beitr_satz`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions on pension income
    income.

    """

    return ges_krankenv_beitr_satz * _ges_krankenv_bemessungsgrundlage_rente_m


@dates_active(start="2003-04-01")
def _ges_krankenv_beitr_midijob_sum_arbeitn_arbeitg_m(
    midijob_bemessungsentgelt_m: float,
    ges_krankenv_beitr_satz: float,
    _ges_krankenv_beitr_satz_arbeitg: float,
) -> float:
    """Calculating the sum of employee and employer health insurance contribution for
    midijobs.

    Parameters
    ----------
    midijob_bemessungsentgelt_m
        See :func:`midijob_bemessungsentgelt_m`.
    ges_krankenv_beitr_satz
        See :func:`ges_krankenv_beitr_satz`.
    _ges_krankenv_beitr_satz_arbeitg
        See :func:`_ges_krankenv_beitr_satz_arbeitg`.

    Returns
    -------

    """
    out = (
        ges_krankenv_beitr_satz + _ges_krankenv_beitr_satz_arbeitg
    ) * midijob_bemessungsentgelt_m
    return out


@dates_active(
    start="2003-04-01",
    end="2022-09-30",
    change_name="_ges_krankenv_beitr_midijob_arbeitg_m",
)
def _ges_krankenv_beitr_midijob_arbeitg_m_anteil_bruttolohn(
    bruttolohn_m: float, in_gleitzone: bool, _ges_krankenv_beitr_satz_arbeitg: float
) -> float:
    """Employers' health insurance contribution for midijobs until September 2022.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    in_gleitzone
        See :func:`in_gleitzone`.
    _ges_krankenv_beitr_satz_arbeitg
        See :func:`_ges_krankenv_beitr_satz_arbeitg`.
    Returns
    -------

    """
    if in_gleitzone:
        out = _ges_krankenv_beitr_satz_arbeitg * bruttolohn_m
    else:
        out = 0.0

    return out


@dates_active(start="2022-10-01", change_name="_ges_krankenv_beitr_midijob_arbeitg_m")
def _ges_krankenv_beitr_midijob_arbeitg_m_residuum(
    _ges_krankenv_beitr_midijob_sum_arbeitn_arbeitg_m: float,
    _ges_krankenv_beitr_midijob_arbeitn_m: float,
    in_gleitzone: bool,
) -> float:
    """Calculating the employer health insurance contribution for midijobs since October
    2022.

    Parameters
    ----------
    _ges_krankenv_beitr_midijob_sum_arbeitn_arbeitg_m
        See :func:`_ges_krankenv_beitr_midijob_sum_arbeitn_arbeitg_m`.
    _ges_krankenv_beitr_midijob_arbeitn_m
        See :func:`_ges_krankenv_beitr_midijob_arbeitn_m`.
    in_gleitzone
        See :func:`in_gleitzone`.
    _ges_krankenv_beitr_satz_arbeitg
        See :func:`_ges_krankenv_beitr_satz_arbeitg`.
    Returns
    -------

    """
    if in_gleitzone:
        out = (
            _ges_krankenv_beitr_midijob_sum_arbeitn_arbeitg_m
            - _ges_krankenv_beitr_midijob_arbeitn_m
        )
    else:
        out = 0.0

    return out


@dates_active(
    start="2003-04-01",
    end="2022-09-30",
    change_name="_ges_krankenv_beitr_midijob_arbeitn_m",
)
def _ges_krankenv_beitr_midijob_arbeitn_m_residuum(
    _ges_krankenv_beitr_midijob_sum_arbeitn_arbeitg_m: float,
    _ges_krankenv_beitr_midijob_arbeitg_m: float,
) -> float:
    """Employee's health insurance contribution for midijobs until September 2022.

    Parameters
    ----------
    _ges_krankenv_beitr_midijob_sum_arbeitn_arbeitg_m
        See :func:`_ges_krankenv_beitr_midijob_sum_arbeitn_arbeitg_m`.
    _ges_krankenv_beitr_midijob_arbeitg_m
        See :func:`_ges_krankenv_beitr_midijob_arbeitg_m`.
    Returns
    -------

    """
    return (
        _ges_krankenv_beitr_midijob_sum_arbeitn_arbeitg_m
        - _ges_krankenv_beitr_midijob_arbeitg_m
    )


@dates_active(start="2022-10-01", change_name="_ges_krankenv_beitr_midijob_arbeitn_m")
def _ges_krankenv_beitr_midijob_arbeitn_m_anteil_beitragspfl_einnahme(
    _midijob_beitragspfl_einnahme_arbeitn_m: float,
    ges_krankenv_beitr_satz: float,
) -> float:
    """Calculating the employee health insurance contribution for midijobs since October
    2022.

    Parameters
    ----------
    _midijob_beitragspfl_einnahme_arbeitn_m
        See :func:`_midijob_beitragspfl_einnahme_arbeitn_m`.
    ges_krankenv_beitr_satz
        See :func:`ges_krankenv_beitr_satz`.
    Returns
    -------

    """
    return _midijob_beitragspfl_einnahme_arbeitn_m * ges_krankenv_beitr_satz
