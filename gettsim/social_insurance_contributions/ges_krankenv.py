import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def ges_krankenv_beitr_m(
    geringfügig_beschäftigt: BoolSeries,
    ges_krankenv_beitr_rente: FloatSeries,
    ges_krankenv_beitr_selbst: FloatSeries,
    _ges_krankenv_beitr_reg_beschäftigt: FloatSeries,
    an_beitr_ges_krankenv_midi_job: FloatSeries,
) -> FloatSeries:
    """Contribution for each individual to the public health insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    ges_krankenv_beitr_rente
        See :func:`ges_krankenv_beitr_rente`.
    ges_krankenv_beitr_selbst
        See :func:`ges_krankenv_beitr_selbst`.
    _ges_krankenv_beitr_reg_beschäftigt
        See :func:`_ges_krankenv_beitr_reg_beschäftigt`.
    an_beitr_ges_krankenv_midi_job
        See :func:`an_beitr_ges_krankenv_midi_job`.

    Returns
    -------

    """

    out = geringfügig_beschäftigt.astype(float) * np.nan

    # Set to 0 for minijobs
    out.loc[geringfügig_beschäftigt] = 0

    # Assign calculated contributions
    out.loc[an_beitr_ges_krankenv_midi_job.index] = an_beitr_ges_krankenv_midi_job
    out.loc[
        _ges_krankenv_beitr_reg_beschäftigt.index
    ] = _ges_krankenv_beitr_reg_beschäftigt
    out.loc[ges_krankenv_beitr_selbst.index] = ges_krankenv_beitr_selbst

    # Add the health insurance contribution for pensions
    return out + ges_krankenv_beitr_rente


def ges_krankenv_beitr_m_tu(
    ges_krankenv_beitr_m: FloatSeries, tu_id: IntSeries
) -> FloatSeries:
    """Contribution for each tax unit to the public health insurance.

    Parameters
    ----------
    ges_krankenv_beitr_m
        See :func:`ges_krankenv_beitr_m`.
    tu_id
        See basic input variable :ref:`tu_id <tu_id>`.

    Returns
    -------

    """
    return ges_krankenv_beitr_m.groupby(tu_id).sum()


def _ges_krankenv_beitr_reg_beschäftigt_until2005(
    bruttolohn_ges_krankenv_beitr_m: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates health insurance contributions for regular jobs until 2008.

    As contribution rates differ between insurance entities until 2008, we rely on
    average contribution rate ('durchschnitt').

    Parameters
    ----------
    bruttolohn_ges_krankenv_beitr_m
        See :func:`bruttolohn_ges_krankenv_beitr_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """

    return (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["durchschnitt"] / 2
    ) * bruttolohn_ges_krankenv_beitr_m


def _ges_krankenv_beitr_reg_beschäftigt_2005_2008(
    bruttolohn_ges_krankenv_beitr_m: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates health insurance contributions for regular jobs

    Between 07/2005 and 12/2019,
    contributions were not equally split between employer and employee. Until
    2008, there was no statutory contribution rate. We hence apply the average
    rate.

    Parameters
    ----------
    bruttolohn_ges_krankenv_beitr_m
        See :func:`bruttolohn_ges_krankenv_beitr_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    return (
        (soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["durchschnitt"] / 2)
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["zusatz"]
    ) * bruttolohn_ges_krankenv_beitr_m


def _ges_krankenv_beitr_reg_beschäftigt_2009_2018(
    bruttolohn_ges_krankenv_beitr_m: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates health insurance contributions for regular jobs

    Between 07/2005 and 12/2019,
    contributions were not equally split between employer and employee. Until
    2008, there was no statutory contribution rate. We hence apply the average
    rate.

    Parameters
    ----------
    bruttolohn_ges_krankenv_beitr_m
        See :func:`bruttolohn_ges_krankenv_beitr_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    return (
        (soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["allgemein"] / 2)
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["zusatz"]
    ) * bruttolohn_ges_krankenv_beitr_m


def _ges_krankenv_beitr_reg_beschäftigt_after2019(
    bruttolohn_ges_krankenv_beitr_m: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates health insurance contributions for regular jobs

    Since 2019, contributions are split equally between employee and employer,
    taking into account the top-up rate (we assume the average) and the statutory
    contribution rate.

    Parameters
    ----------
    bruttolohn_ges_krankenv_beitr_m
        See :func:`bruttolohn_ges_krankenv_beitr_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """

    return (
        (
            soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["allgemein"]
            + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["zusatz"]
        )
        / 2
    ) * bruttolohn_ges_krankenv_beitr_m


def bruttolohn_ges_krankenv_beitr_m(
    bruttolohn_m: FloatSeries,
    ges_krankenv_beitr_bemess_grenze: FloatSeries,
    reg_beschäftigt: BoolSeries,
) -> FloatSeries:
    """Calculate the wage subject to public health insurance contributions.


    Parameters
    ----------
    bruttolohn_m
        See :func:`bruttolohn_m`.
    reg_beschäftigt
        See :func:`reg_beschäftigt`.
    ges_krankenv_beitr_bemess_grenze
        See :func:`ges_krankenv_beitr_bemess_grenze`.


    Returns
    -------

    """
    bruttolohn_m_reg_beschäftigt = bruttolohn_m.loc[reg_beschäftigt]
    bemess_grenze = ges_krankenv_beitr_bemess_grenze.loc[reg_beschäftigt]
    return bruttolohn_m_reg_beschäftigt.clip(upper=bemess_grenze)


def _ges_krankenv_beitr_selbst_before2005(
    ges_krankenv_eink_selbst: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates health insurance contributions.
    Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'.

    Parameters
    ----------
    ges_krankenv_eink_selbst
        See :func:`ges_krankenv_eink_selbst`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    beitr_satz = soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["durchschnitt"]
    return ges_krankenv_eink_selbst * beitr_satz


def _ges_krankenv_beitr_selbst_2005_2008(
    ges_krankenv_eink_selbst: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates health insurance contributions.
    Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'.

    Parameters
    ----------
    ges_krankenv_eink_selbst
        See :func:`ges_krankenv_eink_selbst`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    beitr_satz = (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["durchschnitt"]
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["zusatz"]
    )
    return ges_krankenv_eink_selbst * beitr_satz


def _ges_krankenv_beitr_selbst_ab_2009(
    ges_krankenv_eink_selbst: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates health insurance contributions.
    Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'.

    Parameters
    ----------
    ges_krankenv_eink_selbst
        See :func:`ges_krankenv_eink_selbst`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    beitr_satz = (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["allgemein"]
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["zusatz"]
    )
    return ges_krankenv_eink_selbst * beitr_satz


def ges_krankenv_eink_selbst(
    eink_selbst_m: FloatSeries,
    bezugsgröße: FloatSeries,
    selbstständig_ges_krankenv: BoolSeries,
    soz_vers_beitr_params: dict,
) -> FloatSeries:
    """Choose the amount selfemployed income which is subject to health insurance
    contribution.

    Parameters
    ----------
    eink_selbst_m
        See basic input variable :ref:`eink_selbst_m <eink_selbst_m>`.
    bezugsgröße
        See :func:`bezugsgröße`.
    selbstständig_ges_krankenv
        See :func:`selbstständig_ges_krankenv`.

    Returns
    -------

    """
    bezugsgröße_selbstv = bezugsgröße.loc[selbstständig_ges_krankenv]
    eink_selbst_m_selbstv = eink_selbst_m.loc[selbstständig_ges_krankenv]
    anteil_bezugsgröße = (
        soz_vers_beitr_params["bezugsgröße_selbst_anteil"] * bezugsgröße_selbstv
    )
    return eink_selbst_m_selbstv.clip(upper=anteil_bezugsgröße)


def ges_krankenv_rente(
    summe_ges_priv_rente_m: FloatSeries, ges_krankenv_beitr_bemess_grenze: FloatSeries
) -> FloatSeries:
    """Choose the amount pension which is subject to health insurance contribution.

    Parameters
    ----------
    summe_ges_priv_rente_m
        See :func:`summe_ges_priv_rente_m`.
    ges_krankenv_beitr_bemess_grenze
        See :func:`ges_krankenv_beitr_bemess_grenze`.

    Returns
    -------

    """
    return summe_ges_priv_rente_m.clip(upper=ges_krankenv_beitr_bemess_grenze)


def _ges_krankenv_beitr_rente_until2005(
    ges_krankenv_rente: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates health insurance contributions for pension incomes until 2008.

    As contribution rates differ between insurance entities until 2008, we rely on
    average contribution rate ('durchschnitt').

    Parameters
    ----------
    ges_krankenv_rente
        See :func:`ges_krankenv_rente`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions on pension income
    income.
    """

    return (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["durchschnitt"] / 2
    ) * ges_krankenv_rente


def _ges_krankenv_beitr_rente_2005_2008(
    ges_krankenv_rente: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates health insurance contributions for pension incomes

    Between 07/2005 and 12/2019,
    contributions were not equally split between employer and employee. Until
    2008, there was no statutory contribution rate. We hence apply the average
    rate.

    Parameters
    ----------
    ges_krankenv_rente
        See :func:`ges_krankenv_rente`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    return (
        (soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["durchschnitt"] / 2)
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["zusatz"]
    ) * ges_krankenv_rente


def _ges_krankenv_beitr_rente_2009_2018(
    ges_krankenv_rente: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates health insurance contributions for pension incomes

    Between 07/2005 and 12/2019,
    contributions were not equally split between employer and employee. Until
    2008, there was no statutory contribution rate. We hence apply the average
    rate.

    Parameters
    ----------
    ges_krankenv_rente
        See :func:`ges_krankenv_rente`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    return (
        (soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["allgemein"] / 2)
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["zusatz"]
    ) * ges_krankenv_rente


def _ges_krankenv_beitr_rente_after2019(
    ges_krankenv_rente: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculates health insurance contributions for pension incomes

    Since 2019, contributions are split equally between employee and employer,
    taking into account the top-up rate (we assume the average) and the statutory
    contribution rate.

    Parameters
    ----------
    ges_krankenv_rente
        See :func:`ges_krankenv_rente`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """

    return (
        (
            soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["allgemein"]
            + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["zusatz"]
        )
        / 2
    ) * ges_krankenv_rente


def _ges_beitr_ges_krankenv_midi_job_ab_2003_bis_2008(
    midi_job_bemessungsentgelt: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the sum of employee and employer health insurance contribution.


    Parameters
    ----------
    midi_job_bemessungsentgelt
        See :func:`midi_job_bemessungsentgelt`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    return (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["durchschnitt"]
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["zusatz"]
    ) * midi_job_bemessungsentgelt


def _ges_beitr_ges_krankenv_midi_job_ab_2009(
    midi_job_bemessungsentgelt: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the sum of employee and employer health insurance contribution.


    Parameters
    ----------
    midi_job_bemessungsentgelt
        See :func:`midi_job_bemessungsentgelt`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    return (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["allgemein"]
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["zusatz"]
    ) * midi_job_bemessungsentgelt


def _ag_beitr_ges_krankenv_midi_job_ab_2003_bis_2008(
    bruttolohn_m: FloatSeries, in_gleitzone: BoolSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the employer health insurance contribution.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    in_gleitzone
        See :func:`in_gleitzone`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    bruttolohn_m_in_gleitzone = bruttolohn_m.loc[in_gleitzone]
    return (
        bruttolohn_m_in_gleitzone
        * soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["durchschnitt"]
        / 2
    )


def _ag_beitr_ges_krankenv_midi_job_ab_2009(
    bruttolohn_m: FloatSeries, in_gleitzone: BoolSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the employer health insurance contribution.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    in_gleitzone
        See :func:`in_gleitzone`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    bruttolohn_m_in_gleitzone = bruttolohn_m.loc[in_gleitzone]
    return (
        bruttolohn_m_in_gleitzone
        * soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["allgemein"]
        / 2
    )


def an_beitr_ges_krankenv_midi_job(
    ges_beitr_ges_krankenv_midi_job: FloatSeries,
    ag_beitr_ges_krankenv_midi_job: FloatSeries,
) -> FloatSeries:
    """Calculating the employer health insurance contribution.


    Parameters
    ----------
    ges_beitr_ges_krankenv_midi_job
        See :func:`ges_beitr_ges_krankenv_midi_job`.
    ag_beitr_ges_krankenv_midi_job
        See :func:`ag_beitr_ges_krankenv_midi_job`.
    Returns
    -------

    """
    return ges_beitr_ges_krankenv_midi_job - ag_beitr_ges_krankenv_midi_job


def selbstständig_ges_krankenv(
    selbstständig: BoolSeries, in_priv_krankenv: BoolSeries
) -> BoolSeries:
    """
    Create boolean Series indicating selfemployed insures via public health insurance.

    Parameters
    ----------
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.
    in_priv_krankenv
        See basic input variable :ref:`in_priv_krankenv <in_priv_krankenv>`.

    Returns
    -------

    """
    return selbstständig & ~in_priv_krankenv
