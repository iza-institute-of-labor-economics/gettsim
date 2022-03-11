from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries


def ges_beitr_ges_rentenv_midi_job_m(
    midi_job_bemessungsentgelt_m: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the sum of employee and employer pension insurance contribution.

    Parameters
    ----------
    midi_job_bemessungsentgelt_m
        See :func:`midi_job_bemessungsentgelt_m`.

    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    return (
        midi_job_bemessungsentgelt_m
        * 2
        * soz_vers_beitr_params["soz_vers_beitr"]["ges_rentenv"]
    )


def _ges_rentenv_beitr_bemess_grenze_m(
    wohnort_ost: BoolSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the income threshold up to which pension insurance payments apply.

    Parameters
    ----------
    wohnort_ost
    soz_vers_beitr_params

    Returns
    -------

    """
    out = wohnort_ost.replace(
        {
            True: soz_vers_beitr_params["beitr_bemess_grenze_m"]["ges_rentenv"]["ost"],
            False: soz_vers_beitr_params["beitr_bemess_grenze_m"]["ges_rentenv"][
                "west"
            ],
        }
    )
    return out.astype(float)


def _ges_krankenv_beitr_bemess_grenze_m(
    wohnort_ost: BoolSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the income threshold up to which health insurance payments apply.

    Parameters
    ----------
    wohnort_ost
        See :func:`wohnort_ost`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Pandas Series containing the income threshold up to which the rate of health
    insurance contributions apply.

    """
    out = wohnort_ost.replace(
        {
            True: soz_vers_beitr_params["beitr_bemess_grenze_m"]["ges_krankenv"]["ost"],
            False: soz_vers_beitr_params["beitr_bemess_grenze_m"]["ges_krankenv"][
                "west"
            ],
        }
    )
    return out.astype(float)


def _ges_krankenv_bezugsgröße_selbst_m(
    wohnort_ost: BoolSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Threshold for self employment income subject to health insurance.

    Selecting by place of living the income threshold for self employed up to which the
    rate of health insurance contributions apply.

    Parameters
    ----------
    wohnort_ost
        See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    """
    return wohnort_ost.replace(
        {
            True: soz_vers_beitr_params["bezugsgröße_selbst_m"]["ost"],
            False: soz_vers_beitr_params["bezugsgröße_selbst_m"]["west"],
        }
    ).astype(float)
