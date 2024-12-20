"""Public health insurance contributions."""

from _gettsim.shared import policy_info


@policy_info(end_date="2003-03-31", name_in_dag="ges_krankenv_beitr_arbeitnehmer_m")
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


@policy_info(start_date="2003-04-01", name_in_dag="ges_krankenv_beitr_arbeitnehmer_m")
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


@policy_info(end_date="2003-03-31", name_in_dag="ges_krankenv_beitr_arbeitgeber_m")
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


@policy_info(start_date="2003-04-01", name_in_dag="ges_krankenv_beitr_arbeitgeber_m")
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
    zusatzbeitrag = params.get("mean_zusatzbeitrag", 0.0)
    ges_krankenv_beitr_satz_selbst = ermäßigter_beitrag + zusatzbeitrag

    return (
        ges_krankenv_beitr_satz_selbst
        * _ges_krankenv_bemessungsgrundlage_eink_selbständig
    )


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


@policy_info(start_date="2003-04-01")
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
    return (
        ges_krankenv_beitr_satz_arbeitnehmer + _ges_krankenv_beitr_satz_arbeitgeber
    ) * midijob_bemessungsentgelt_m


@policy_info(
    start_date="2003-04-01",
    end_date="2022-09-30",
    name_in_dag="_ges_krankenv_beitr_midijob_arbeitgeber_m",
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


@policy_info(
    start_date="2022-10-01", name_in_dag="_ges_krankenv_beitr_midijob_arbeitgeber_m"
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


@policy_info(
    start_date="2003-04-01",
    end_date="2022-09-30",
    name_in_dag="_ges_krankenv_beitr_midijob_arbeitnehmer_m",
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


@policy_info(
    start_date="2022-10-01", name_in_dag="_ges_krankenv_beitr_midijob_arbeitnehmer_m"
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
