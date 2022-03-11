import numpy as np

from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def ges_krankenv_beitr_m(
    geringfügig_beschäftigt: BoolSeries,
    ges_krankenv_beitr_rente_m: FloatSeries,
    ges_krankenv_beitr_selbst_m: FloatSeries,
    _ges_krankenv_beitr_midi_job_m: FloatSeries,
    _ges_krankenv_beitr_bruttolohn_m: FloatSeries,
    soz_vers_beitr_params: dict,
) -> FloatSeries:
    """Contribution for each individual to the public health insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    ges_krankenv_beitr_rente_m
        See :func:`ges_krankenv_beitr_rente_m`.
    ges_krankenv_beitr_selbst_m
        See :func:`ges_krankenv_beitr_selbst_m`.
    _ges_krankenv_beitr_midi_job_m
        See :func:`_ges_krankenv_beitr_midi_job_m`.
    _ges_krankenv_beitr_bruttolohn_m
        See :func:`_ges_krankenv_beitr_bruttolohn_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    beitr_reg_beschäftigt_m = (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
        * _ges_krankenv_beitr_bruttolohn_m
    )
    out = geringfügig_beschäftigt.astype(float) * np.nan

    # Set to 0 for minijobs
    out.loc[geringfügig_beschäftigt] = 0

    # Assign calculated contributions
    out.loc[_ges_krankenv_beitr_midi_job_m.index] = _ges_krankenv_beitr_midi_job_m
    out.loc[beitr_reg_beschäftigt_m.index] = beitr_reg_beschäftigt_m
    out.loc[ges_krankenv_beitr_selbst_m.index] = ges_krankenv_beitr_selbst_m

    # Add the health insurance contribution for pensions
    return out + ges_krankenv_beitr_rente_m


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


def _ges_krankenv_beitr_bruttolohn_m(
    bruttolohn_m: FloatSeries,
    _ges_krankenv_beitr_bemess_grenze_m: FloatSeries,
    reg_beschäftigt: BoolSeries,
) -> FloatSeries:
    """Calculate the wage subject to public health insurance contributions.


    Parameters
    ----------
    bruttolohn_m
        See :func:`bruttolohn_m`.
    reg_beschäftigt
        See :func:`reg_beschäftigt`.
    _ges_krankenv_beitr_bemess_grenze_m
        See :func:`_ges_krankenv_beitr_bemess_grenze_m`.


    Returns
    -------

    """
    bruttolohn_m_reg_beschäftigt = bruttolohn_m.loc[reg_beschäftigt]
    bemess_grenze = _ges_krankenv_beitr_bemess_grenze_m.loc[reg_beschäftigt]
    return bruttolohn_m_reg_beschäftigt.clip(upper=bemess_grenze)


def ges_krankenv_beitr_selbst_m(
    _ges_krankenv_bemessungsgrundlage_eink_selbst: FloatSeries,
    soz_vers_beitr_params: dict,
) -> FloatSeries:
    """Calculates health insurance contributions.
    Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'.

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_eink_selbst
        See :func:`_ges_krankenv_bemessungsgrundlage_eink_selbst`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Pandas Series containing monthly health insurance contributions for self employed
    income.
    """
    beitr_satz = (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["ag"]
    )
    return _ges_krankenv_bemessungsgrundlage_eink_selbst * beitr_satz


def _ges_krankenv_bemessungsgrundlage_eink_selbst(
    eink_selbst_m: FloatSeries,
    _ges_krankenv_bezugsgröße_selbst_m: FloatSeries,
    selbstständig: BoolSeries,
    in_priv_krankenv: BoolSeries,
    soz_vers_beitr_params: dict,
) -> FloatSeries:
    """Choose the amount of selfemployed income which is subject to health insurance
    contribution.

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
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    # Calculate if selfemployed insures via public health insurance.
    selbstständig_ges_krankenv = selbstständig & ~in_priv_krankenv

    bezugsgröße_selbstv_m = _ges_krankenv_bezugsgröße_selbst_m.loc[
        selbstständig_ges_krankenv
    ]
    eink_selbst_selbstv_m = eink_selbst_m.loc[selbstständig_ges_krankenv]
    anteil__ges_krankenv_bezugsgröße_selbst_m = (
        soz_vers_beitr_params["bezugsgröße_selbst_anteil"] * bezugsgröße_selbstv_m
    )
    return eink_selbst_selbstv_m.clip(upper=anteil__ges_krankenv_bezugsgröße_selbst_m)


def _ges_krankenv_bemessungsgrundlage_rente_m(
    sum_ges_rente_priv_rente_m: FloatSeries,
    _ges_krankenv_beitr_bemess_grenze_m: FloatSeries,
) -> FloatSeries:
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
    return sum_ges_rente_priv_rente_m.clip(upper=_ges_krankenv_beitr_bemess_grenze_m)


def ges_krankenv_beitr_rente_m(
    _ges_krankenv_bemessungsgrundlage_rente_m: FloatSeries, soz_vers_beitr_params: dict
) -> FloatSeries:
    """Calculating the contribution to health insurance for pension income.


    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_rente_m
        See :func:`_ges_krankenv_bemessungsgrundlage_rente_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Pandas Series containing monthly health insurance contributions for pension income.
    """

    return (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
        * _ges_krankenv_bemessungsgrundlage_rente_m
    )


def _ges_krankenv_beitr_midi_job_m(
    midi_job_bemessungsentgelt_m: FloatSeries,
    bruttolohn_m: FloatSeries,
    in_gleitzone: BoolSeries,
    soz_vers_beitr_params: dict,
) -> FloatSeries:
    """Calculating the employer health insurance contribution.

    Parameters
    ----------
    _ges_rentenv_beitr_bruttolohn_m
        See :func:`_ges_rentenv_beitr_bruttolohn_m`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    in_gleitzone
        See :func:`in_gleitzone`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------

    """
    ges_beitr_midi_job_m = (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
        + soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["ag"]
    ) * midi_job_bemessungsentgelt_m

    ag_beitr_midi_job_m = (
        bruttolohn_m.loc[in_gleitzone]
        * soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["ag"]
    )
    return ges_beitr_midi_job_m - ag_beitr_midi_job_m
