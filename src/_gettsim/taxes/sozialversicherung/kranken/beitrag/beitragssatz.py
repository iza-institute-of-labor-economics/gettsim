"""Contribution rate for health insurance."""

from _gettsim.function_types import policy_function


@policy_function(
    end_date="2005-06-30",
)
def beitragssatz_arbeitnehmer(
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
def beitragssatz_arbeitnehmer_jahresanfang(
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
    leaf_name="beitragssatz_arbeitnehmer",
)
def beitragssatz_arbeitnehmer_mittlerer_kassenspezifischer_zusatzbeitrag(
    zusatzbeitragssatz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's health insurance contribution rate.

    From July 2005 until December 2008. The contribution rates consists of a general
    rate (split equally between employers and employees, differs across sickness funds)
    and a top-up rate, which is fully paid by employees.

    Parameters
    ----------
    zusatzbeitragssatz
        See :func:`zusatzbeitragssatz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Beitragssatz for statutory health insurance.

    """

    mean_allgemein = sozialv_beitr_params["beitr_satz"]["ges_krankenv"][
        "mean_allgemein"
    ]

    return mean_allgemein / 2 + zusatzbeitragssatz


@policy_function(
    start_date="2005-07-01",
    end_date="2008-12-31",
    leaf_name="beitragssatz_arbeitnehmer_jahresanfang",
)
def beitragssatz_arbeitnehmer_jahresanfang_mittlerer_kassenspezifischer_zusatzbeitrag(
    zusatzbeitragssatz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's health insurance contribution rate at the beginning of the year.

    From July 2005 until December 2008. The contribution rates consists of a general
    rate (split equally between employers and employees, differs across sickness funds)
    and a top-up rate, which is fully paid by employees.

    Parameters
    ----------
    zusatzbeitragssatz
        See :func:`zusatzbeitragssatz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Beitragssatz for statutory health insurance at the beginning of the year.

    """

    mean_allgemein = sozialv_beitr_params["beitr_satz_jahresanfang"]["ges_krankenv"][
        "mean_allgemein"
    ]

    return mean_allgemein / 2 + zusatzbeitragssatz


@policy_function(
    start_date="2009-01-01",
    end_date="2018-12-31",
    leaf_name="beitragssatz_arbeitnehmer",
)
def beitragssatz_arbeitnehmer_einheitlicher_zusatzbeitrag(
    zusatzbeitragssatz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's health insurance contribution rate.

    From January 2009 until December 2018. The contribution rates consists of a general
    rate (split equally between employers and employees, same for all sickness funds)
    and a top-up rate, which is fully paid by employees.

    Parameters
    ----------
    zusatzbeitragssatz
        See :func:`zusatzbeitragssatz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Beitragssatz for statutory health insurance.

    """

    allgemein = sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["allgemein"]

    return allgemein / 2 + zusatzbeitragssatz


@policy_function(
    start_date="2009-01-01",
    end_date="2018-12-31",
    leaf_name="beitragssatz_arbeitnehmer_jahresanfang",
)
def beitragssatz_arbeitnehmer_jahresanfang_einheitlicher_zusatzbeitrag(
    zusatzbeitragssatz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's health insurance contribution rate at the beginning of the year.

    From January 2009 until December 2018. The contribution rates consists of a general
    rate (split equally between employers and employees, same for all sickness funds)
    and a top-up rate, which is fully paid by employees.

    Parameters
    ----------
    zusatzbeitragssatz
        See :func:`zusatzbeitragssatz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Beitragssatz for statutory health insurance at the beginning of the year.

    """

    allgemein = sozialv_beitr_params["beitr_satz_jahresanfang"]["ges_krankenv"][
        "allgemein"
    ]

    return allgemein / 2 + zusatzbeitragssatz


@policy_function(
    start_date="2019-01-01",
    leaf_name="beitragssatz_arbeitnehmer",
)
def beitragssatz_arbeitnehmer_paritätischer_zusatzbeitrag(
    zusatzbeitragssatz: float,
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
    return (allgemeiner_beitr_satz + zusatzbeitragssatz) / 2


@policy_function(
    start_date="2019-01-01",
    leaf_name="beitragssatz_arbeitnehmer_jahresanfang",
)
def beitragssatz_arbeitnehmer_jahresanfang_paritätischer_zusatzbeitrag(
    zusatzbeitragssatz: float,
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
    return (allgemeiner_beitr_satz + zusatzbeitragssatz) / 2


@policy_function(
    end_date="2008-12-31",
    leaf_name="beitragssatz_arbeitgeber",
)
def beitragssatz_arbeitgeber_mittlerer_kassenspezifischer(
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
    leaf_name="beitragssatz_arbeitgeber_jahresanfang",
)
def beitragssatz_arbeitgeber_jahresanfang_mittlerer_kassenspezifischer(
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
    leaf_name="beitragssatz_arbeitgeber",
)
def beitragssatz_arbeitgeber_einheitlicher_zusatzbeitrag(
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
    leaf_name="beitragssatz_arbeitgeber_jahresanfang",
)
def beitragssatz_arbeitgeber_jahresanfang_einheitlicher_zusatzbeitrag(
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
    leaf_name="beitragssatz_arbeitgeber",
)
def beitragssatz_arbeitgeber_paritätischer_zusatzbeitrag(
    beitragssatz_arbeitnehmer: float,
) -> float:
    """Employer's health insurance contribution rate.

    Since 2019, the full contribution rate is now split equally between employers and
    employees.

    Parameters
    ----------
    beitragssatz_arbeitnehmer
        See :func:`beitragssatz_arbeitnehmer`.

    Returns
    -------

    """
    return beitragssatz_arbeitnehmer


@policy_function(
    start_date="2019-01-01",
    leaf_name="beitragssatz_arbeitgeber_jahresanfang",
)
def beitragssatz_arbeitgeber_jahresanfang_paritätischer_zusatzbeitrag(
    beitragssatz_arbeitnehmer_jahresanfang: float,
) -> float:
    """Employer's health insurance contribution rate at the beginning of the year.

    Since 2019, the full contribution rate is now split equally between employers and
    employees.

    Parameters
    ----------
    beitragssatz_arbeitnehmer
        See :func:`beitragssatz_arbeitnehmer`.

    Returns
    -------

    """
    return beitragssatz_arbeitnehmer_jahresanfang


@policy_function(
    start_date="2005-07-01",
    end_date="2014-12-31",
    leaf_name="zusatzbeitragssatz",
)
def zusatzbeitragssatz_von_sonderbeitrag(
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
    leaf_name="zusatzbeitragssatz",
)
def zusatzbeitragssatz_von_mean_zusatzbeitrag(
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
