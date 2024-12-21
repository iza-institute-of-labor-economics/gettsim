"""Contribution rate for health insurance."""

from _gettsim.shared import policy_info


@policy_info(
    end_date="2005-06-30",
)
def betrag_arbeitnehmer(
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


@policy_info(
    end_date="2005-06-30",
)
def betrag_arbeitnehmer_jahresanfang(
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


@policy_info(
    start_date="2005-07-01",
    end_date="2008-12-31",
    name_in_dag="betrag_arbeitnehmer",
)
def satz_mean_kassenspezifisch_zusatzbeitrag_nur_arbeitnehmer(
    zusatzbeitrag_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's health insurance contribution rate.

    From July 2005 until December 2008. The contribution rates consists of a general
    rate (split equally between employers and employees, differs across sickness funds)
    and a top-up rate, which is fully paid by employees.

    Parameters
    ----------
    zusatzbeitrag_satz
        See :func:`zusatzbeitrag_satz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Beitragssatz for statutory health insurance.

    """

    mean_allgemein = sozialv_beitr_params["beitr_satz"]["ges_krankenv"][
        "mean_allgemein"
    ]

    return mean_allgemein / 2 + zusatzbeitrag_satz


@policy_info(
    start_date="2005-07-01",
    end_date="2008-12-31",
    name_in_dag="betrag_arbeitnehmer_jahresanfang",
)
def satz_mean_kassenspezifisch_zusatzbeitrag_nur_arbeitnehmer_jahresanfang(
    zusatzbeitrag_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's health insurance contribution rate at the beginning of the year.

    From July 2005 until December 2008. The contribution rates consists of a general
    rate (split equally between employers and employees, differs across sickness funds)
    and a top-up rate, which is fully paid by employees.

    Parameters
    ----------
    zusatzbeitrag_satz
        See :func:`zusatzbeitrag_satz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Beitragssatz for statutory health insurance at the beginning of the year.

    """

    mean_allgemein = sozialv_beitr_params["beitr_satz_jahresanfang"]["ges_krankenv"][
        "mean_allgemein"
    ]

    return mean_allgemein / 2 + zusatzbeitrag_satz


@policy_info(
    start_date="2009-01-01",
    end_date="2018-12-31",
    name_in_dag="betrag_arbeitnehmer",
)
def satz_einheitlich_zusatzbeitrag_nur_arbeitnehmer(
    zusatzbeitrag_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's health insurance contribution rate.

    From January 2009 until December 2018. The contribution rates consists of a general
    rate (split equally between employers and employees, same for all sickness funds)
    and a top-up rate, which is fully paid by employees.

    Parameters
    ----------
    zusatzbeitrag_satz
        See :func:`zusatzbeitrag_satz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Beitragssatz for statutory health insurance.

    """

    allgemein = sozialv_beitr_params["beitr_satz"]["ges_krankenv"]["allgemein"]

    return allgemein / 2 + zusatzbeitrag_satz


@policy_info(
    start_date="2009-01-01",
    end_date="2018-12-31",
    name_in_dag="betrag_arbeitnehmer_jahresanfang",
)
def satz_einheitlich_zusatzbeitrag_nur_arbeitnehmer_jahresanfang(
    zusatzbeitrag_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's health insurance contribution rate at the beginning of the year.

    From January 2009 until December 2018. The contribution rates consists of a general
    rate (split equally between employers and employees, same for all sickness funds)
    and a top-up rate, which is fully paid by employees.

    Parameters
    ----------
    zusatzbeitrag_satz
        See :func:`zusatzbeitrag_satz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Beitragssatz for statutory health insurance at the beginning of the year.

    """

    allgemein = sozialv_beitr_params["beitr_satz_jahresanfang"]["ges_krankenv"][
        "allgemein"
    ]

    return allgemein / 2 + zusatzbeitrag_satz


@policy_info(
    start_date="2019-01-01",
    name_in_dag="betrag_arbeitnehmer",
)
def satz_zusatzbeitrag_arbeitnehmer_paritätisch(
    zusatzbeitrag_satz: float,
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
    return (allgemeiner_beitr_satz + zusatzbeitrag_satz) / 2


@policy_info(
    start_date="2019-01-01",
    name_in_dag="betrag_arbeitnehmer_jahresanfang",
)
def satz_zusatzbeitrag_arbeitnehmer_paritätisch_jahresanfang(
    zusatzbeitrag_satz: float,
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
    return (allgemeiner_beitr_satz + zusatzbeitrag_satz) / 2


@policy_info(
    end_date="2008-12-31",
    name_in_dag="betrag_arbeitgeber",
)
def satz_arbeitgeber_mean_kassenspezifisch_zusatzbeitrag_nur_arbeitnehmer(
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


@policy_info(
    end_date="2008-12-31",
    name_in_dag="betrag_arbeitgeber_jahresanfang",
)
def satz_arbeitgeber_mean_kassenspezifisch_zusatzbeitrag_nur_arbeitnehmer_jahresanfang(
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


@policy_info(
    start_date="2009-01-01",
    end_date="2018-12-31",
    name_in_dag="betrag_arbeitgeber",
)
def satz_arbeitgeber_einheitlich_zusatzbeitrag_nur_arbeitnehmer(
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


@policy_info(
    start_date="2009-01-01",
    end_date="2018-12-31",
    name_in_dag="betrag_arbeitgeber_jahresanfang",
)
def satz_arbeitgeber_einheitlich_zusatzbeitrag_nur_arbeitnehmer_jahresanfang(
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


@policy_info(
    start_date="2019-01-01",
    name_in_dag="betrag_arbeitgeber",
)
def satz_arbeitgeber_zusatzbeitrag_paritätisch(
    betrag_arbeitnehmer: float,
) -> float:
    """Employer's health insurance contribution rate.

    Since 2019, the full contribution rate is now split equally between employers and
    employees.

    Parameters
    ----------
    betrag_arbeitnehmer
        See :func:`betrag_arbeitnehmer`.

    Returns
    -------

    """
    return betrag_arbeitnehmer


@policy_info(
    start_date="2019-01-01",
    name_in_dag="betrag_arbeitgeber_jahresanfang",
)
def satz_arbeitgeber_zusatzbeitrag_paritätisch_jahresanfang(
    betrag_arbeitnehmer_jahresanfang: float,
) -> float:
    """Employer's health insurance contribution rate at the beginning of the year.

    Since 2019, the full contribution rate is now split equally between employers and
    employees.

    Parameters
    ----------
    betrag_arbeitnehmer
        See :func:`betrag_arbeitnehmer`.

    Returns
    -------

    """
    return betrag_arbeitnehmer_jahresanfang


@policy_info(
    start_date="2005-07-01",
    end_date="2014-12-31",
    name_in_dag="zusatzbeitrag_satz",
)
def satz_from_sonderbeitr_satz(
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


@policy_info(
    start_date="2015-01-01",
    name_in_dag="zusatzbeitrag_satz",
)
def zusatzbeitrag_satz_from_mean_zusatzbeitrag(
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
