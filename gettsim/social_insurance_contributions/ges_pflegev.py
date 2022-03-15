from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


def ges_pflegev_zusatz_kinderlos(
    hat_kinder: BoolSeries, alter: IntSeries, soz_vers_beitr_params: dict,
) -> BoolSeries:
    """
    Create boolean Series indicating addtional care insurance contribution for
    childless individuals.

    Parameters
    ----------
    hat_kinder
        See basic input variable :ref:`hat_kinder <hat_kinder>`.
    alter
        See basic input variable :ref:`alter <alter>`.

    Returns
    -------

    """
    altersgrenze = soz_vers_beitr_params["ges_pflegev_zusatz_kinderlos_altersgrenze"]
    return (not hat_kinder) and alter >= altersgrenze


def ges_pflegev_beitr_m(
    geringfügig_beschäftigt: BoolSeries,
    ges_pflegev_beitr_rente_m: FloatSeries,
    ges_pflegev_beitr_selbst_m: FloatSeries,
    _ges_pflegev_beitr_midi_job_m_m: FloatSeries,
    ges_pflegev_zusatz_kinderlos: BoolSeries,
    _ges_krankenv_beitr_bruttolohn_m: FloatSeries,
    soz_vers_beitr_params: dict,
    in_gleitzone: BoolSeries,
    selbständig: BoolSeries,
) -> FloatSeries:
    """Contribution for each individual to the public care insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    ges_pflegev_beitr_rente_m
        See :func:`ges_pflegev_beitr_rente_m`.
    ges_pflegev_beitr_selbst_m
        See :func:`ges_pflegev_beitr_selbst_m`.
    _ges_pflegev_beitr_midi_job_m_m
        See :func:`_ges_pflegev_beitr_midi_job_m_m`.
    ges_pflegev_zusatz_kinderlos
        See :func:`ges_pflegev_zusatz_kinderlos`.
    _ges_krankenv_beitr_bruttolohn_m
        See :func:`_ges_krankenv_beitr_bruttolohn_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.
    in_gleitzone
        See :func:`in_gleitzone`.
    selbständig
        See basic input variable :ref:`selbständig <selbständig>`.

    Returns
    -------

    """

    # Calculate care insurance contributions for regular jobs.
    beitr_regulär_beschäftigt_m = (
        _ges_krankenv_beitr_bruttolohn_m
        * soz_vers_beitr_params["soz_vers_beitr"]["ges_pflegev"]["standard"]
    )

    # Add additional contribution for childless individuals
    if ges_pflegev_zusatz_kinderlos:
        beitr_regulär_beschäftigt_m += (
            _ges_krankenv_beitr_bruttolohn_m
            * soz_vers_beitr_params["soz_vers_beitr"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    if geringfügig_beschäftigt:
        out = 0
    elif in_gleitzone:
        out = _ges_pflegev_beitr_midi_job_m_m
    elif selbständig:
        out = ges_pflegev_beitr_selbst_m
    else:
        out = beitr_regulär_beschäftigt_m

    # Add the care insurance contribution for pensions
    return out + ges_pflegev_beitr_rente_m


def ges_pflegev_beitr_selbst_m(
    ges_pflegev_zusatz_kinderlos: BoolSeries,
    _ges_krankenv_bemessungsgrundlage_eink_selbst: FloatSeries,
    soz_vers_beitr_params: dict,
) -> FloatSeries:
    """Calculates care insurance contributions.

    Self-employed pay the full
    contribution (employer + employee), which is either assessed on their
    self-employement income or 3/4 of the 'Bezugsgröße'

    Parameters
    ----------
    ges_pflegev_zusatz_kinderlos
        See :func:`ges_pflegev_zusatz_kinderlos`.

    _ges_krankenv_bemessungsgrundlage_eink_selbst
        See :func:`_ges_krankenv_bemessungsgrundlage_eink_selbst`.

    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Pandas Series containing monthly care insurance contributions for self employed
    income.
    """
    out = (
        _ges_krankenv_bemessungsgrundlage_eink_selbst
        * 2
        * soz_vers_beitr_params["soz_vers_beitr"]["ges_pflegev"]["standard"]
    )

    # Add additional contribution for childless individuals
    if ges_pflegev_zusatz_kinderlos:
        out += (
            _ges_krankenv_bemessungsgrundlage_eink_selbst
            * soz_vers_beitr_params["soz_vers_beitr"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    return out


def ges_pflegev_beitr_rente_m(
    ges_pflegev_zusatz_kinderlos: BoolSeries,
    _ges_krankenv_bemessungsgrundlage_rente_m: FloatSeries,
    soz_vers_beitr_params: dict,
) -> FloatSeries:
    """Calculating the contribution to health insurance for pension income.


    Parameters
    ----------
    ges_pflegev_zusatz_kinderlos
        See :func:`ges_pflegev_zusatz_kinderlos`.
    _ges_krankenv_bemessungsgrundlage_rente_m
        See :func:`_ges_krankenv_bemessungsgrundlage_rente_m`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.

    Returns
    -------
    Pandas Series containing monthly health insurance contributions for pension income.
    """
    out = (
        _ges_krankenv_bemessungsgrundlage_rente_m
        * 2
        * soz_vers_beitr_params["soz_vers_beitr"]["ges_pflegev"]["standard"]
    )

    # Add additional contribution for childless individuals
    if ges_pflegev_zusatz_kinderlos:
        out += (
            _ges_krankenv_bemessungsgrundlage_rente_m
            * soz_vers_beitr_params["soz_vers_beitr"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    return out


def _ges_pflegev_beitr_midi_job_m_m(
    ges_pflegev_zusatz_kinderlos: BoolSeries,
    midi_job_bemessungsentgelt_m: FloatSeries,
    bruttolohn_m: FloatSeries,
    soz_vers_beitr_params: dict,
) -> FloatSeries:
    """Calculating the employer care insurance contribution.


    Parameters
    ----------
    ges_pflegev_zusatz_kinderlos
        See :func:`ges_pflegev_zusatz_kinderlos`.
    midi_job_bemessungsentgelt_m
        See :func:`midi_job_bemessungsentgelt_m`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    soz_vers_beitr_params
        See params documentation :ref:`soz_vers_beitr_params <soz_vers_beitr_params>`.


    Returns
    -------

    """
    # Calculate the sum of employee and employer care insurance contribution.
    ges_beitr_midi_job_m = (
        midi_job_bemessungsentgelt_m
        * 2
        * soz_vers_beitr_params["soz_vers_beitr"]["ges_pflegev"]["standard"]
    )

    # Add additional contribution for childless individuals
    if ges_pflegev_zusatz_kinderlos:
        ges_beitr_midi_job_m += (
            midi_job_bemessungsentgelt_m
            * soz_vers_beitr_params["soz_vers_beitr"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    ag_beitr_midi_job_m = (
        bruttolohn_m
        * soz_vers_beitr_params["soz_vers_beitr"]["ges_pflegev"]["standard"]
    )
    return ges_beitr_midi_job_m - ag_beitr_midi_job_m
