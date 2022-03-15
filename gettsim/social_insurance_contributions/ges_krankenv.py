from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def ges_krankenv_beitr_m(
    geringfügig_beschäftigt: BoolSeries,
    ges_krankenv_beitr_rente_m: FloatSeries,
    ges_krankenv_beitr_selbst_m: FloatSeries,
    in_gleitzone: BoolSeries,
    _ges_krankenv_beitr_midi_job_m: FloatSeries,
    _ges_krankenv_beitr_bruttolohn_m: FloatSeries,
    soz_vers_beitr_params: dict,
    selbständig: BoolSeries,
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
    in_gleitzone
        See :func:`in_gleitzone`.
    _ges_krankenv_beitr_bruttolohn_m
        See :func:`_ges_krankenv_beitr_bruttolohn_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    selbständig
        See basic input variable :ref:`selbständig <selbständig>`.


    Returns
    -------

    """
    beitr_regulär_beschäftigt_m = (
        soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["an"]
        * _ges_krankenv_beitr_bruttolohn_m
    )

    if geringfügig_beschäftigt:
        out = 0
    elif in_gleitzone:
        out = _ges_krankenv_beitr_midi_job_m
    elif selbständig:
        out = ges_krankenv_beitr_selbst_m
    else:
        out = beitr_regulär_beschäftigt_m

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
    regulär_beschäftigt: BoolSeries,
) -> FloatSeries:
    """Calculate the wage subject to public health insurance contributions.


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
        bruttolohn_m_regulär_beschäftigt = bruttolohn_m
        bemess_grenze = _ges_krankenv_beitr_bemess_grenze_m
    else:
        bruttolohn_m_regulär_beschäftigt = 0

    if bruttolohn_m_regulär_beschäftigt > bemess_grenze:
        return bemess_grenze
    else:
        return bruttolohn_m_regulär_beschäftigt


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
    if selbstständig and not in_priv_krankenv:
        bezugsgröße_selbstv_m = _ges_krankenv_bezugsgröße_selbst_m
        eink_selbst_selbstv_m = eink_selbst_m
    else:
        bezugsgröße_selbstv_m = 0
        eink_selbst_selbstv_m = 0

    anteil_ges_krankenv_bezugsgröße_selbst_m = (
        soz_vers_beitr_params["bezugsgröße_selbst_anteil"] * bezugsgröße_selbstv_m
    )

    if eink_selbst_selbstv_m > anteil_ges_krankenv_bezugsgröße_selbst_m:
        return anteil_ges_krankenv_bezugsgröße_selbst_m
    else:
        return eink_selbst_selbstv_m


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
    soz_vers_beitr_params: dict,
) -> FloatSeries:
    """Calculating the employer health insurance contribution.

    Parameters
    ----------
    _ges_rentenv_beitr_bruttolohn_m
        See :func:`_ges_rentenv_beitr_bruttolohn_m`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
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
        bruttolohn_m * soz_vers_beitr_params["soz_vers_beitr"]["ges_krankenv"]["ag"]
    )
    return ges_beitr_midi_job_m - ag_beitr_midi_job_m
