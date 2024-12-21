"""Contributions to public long-term care insurance."""

from _gettsim.shared import policy_info


@policy_info(end_date="2003-03-31", name_in_dag="ges_pflegev_beitr_arbeitnehmer_m")
def ges_pflegev_beitr_arbeitnehmer_m_vor_midijob(
    _ges_pflegev_beitr_arbeitnehmer_reg_beschäftigt_m: float,
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    ges_pflegev_beitr_rentner_m: float,
    ges_pflegev_beitr_selbstständig_m: float,
    selbstständig: bool,
) -> float:
    """Employee's long-term care insurance contribution until March 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    ges_pflegev_beitr_rentner_m
        See :func:`ges_pflegev_beitr_rentner_m`.
    ges_pflegev_beitr_selbstständig_m
        See :func:`ges_pflegev_beitr_selbstständig_m`.
    ges_pflegev_beitr_regulär_besch_m
        See :func:`ges_pflegev_beitr_regulär_besch_m`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.

    Returns
    -------
    Employee's long-term care insurance contributions.

    """

    if selbstständig:
        out = ges_pflegev_beitr_selbstständig_m
    elif einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = _ges_pflegev_beitr_arbeitnehmer_reg_beschäftigt_m

    # Add the care insurance contribution for pensions
    return out + ges_pflegev_beitr_rentner_m


@policy_info(start_date="2003-04-01", name_in_dag="ges_pflegev_beitr_arbeitnehmer_m")
def ges_pflegev_beitr_arbeitnehmer_m_mit_midijob(  # noqa: PLR0913
    _ges_pflegev_beitr_arbeitnehmer_reg_beschäftigt_m: float,
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    ges_pflegev_beitr_rentner_m: float,
    ges_pflegev_beitr_selbstständig_m: float,
    _ges_pflegev_beitr_midijob_arbeitnehmer_m: float,
    einkommensgrenzen__in_gleitzone: bool,
    selbstständig: bool,
) -> float:
    """Employee's long-term care insurance contribution since April 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    ges_pflegev_beitr_rentner_m
        See :func:`ges_pflegev_beitr_rentner_m`.
    ges_pflegev_beitr_selbstständig_m
        See :func:`ges_pflegev_beitr_selbstständig_m`.
    _ges_pflegev_beitr_midijob_arbeitnehmer_m
        See :func:`_ges_pflegev_beitr_midijob_arbeitnehmer_m`.
    ges_pflegev_beitr_regulär_besch_m
        See :func:`ges_pflegev_beitr_regulär_besch_m`.
    einkommensgrenzen__in_gleitzone
        See :func:`einkommensgrenzen__in_gleitzone`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.

    Returns
    -------
    Employee's long-term care insurance contributions.

    """

    if selbstständig:
        out = ges_pflegev_beitr_selbstständig_m
    elif einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    elif einkommensgrenzen__in_gleitzone:
        out = _ges_pflegev_beitr_midijob_arbeitnehmer_m
    else:
        out = _ges_pflegev_beitr_arbeitnehmer_reg_beschäftigt_m

    # Add the care insurance contribution for pensions
    return out + ges_pflegev_beitr_rentner_m


def _ges_pflegev_beitr_arbeitnehmer_reg_beschäftigt_m(
    _ges_krankenv_bruttolohn_m: float,
    ges_pflegev_beitr_satz_arbeitnehmer: float,
) -> float:
    """Employee's long-term care insurance contribution if regularly employed.

    Parameters
    ----------
    _ges_krankenv_bruttolohn_m:
        See :func:`_ges_krankenv_bruttolohn_m`.
    ges_pflegev_beitr_satz_arbeitnehmer:
        See :func:`ges_pflegev_beitr_satz_arbeitnehmer`.

    Returns
    -------
    Long-term care insurance contributions of employer and employee.

    """

    beitr_regulär_beschäftigt_m = (
        _ges_krankenv_bruttolohn_m * ges_pflegev_beitr_satz_arbeitnehmer
    )

    return beitr_regulär_beschäftigt_m


@policy_info(end_date="2003-03-31", name_in_dag="ges_pflegev_beitr_arbeitgeber_m")
def ges_pflegev_beitr_arbeitgeber_m_vor_midijob(
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    _ges_krankenv_bruttolohn_m: float,
    sozialv_beitr_params: dict,
    selbstständig: bool,
) -> float:
    """Employer's long-term care insurance contribution.

    Before Midijob introduction in April 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    _ges_krankenv_bruttolohn_m
        See :func:`_ges_krankenv_bruttolohn_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.

    Returns
    -------
    Employer's long-term care insurance contributions.

    """
    # Calculate care insurance contributions for regular jobs.
    beitr_regulär_beschäftigt_m = (
        _ges_krankenv_bruttolohn_m * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]
    )

    if selbstständig or einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = beitr_regulär_beschäftigt_m

    return out


@policy_info(start_date="2003-04-01", name_in_dag="ges_pflegev_beitr_arbeitgeber_m")
def ges_pflegev_beitr_arbeitgeber_m_mit_midijob(
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    _ges_pflegev_beitr_midijob_arbeitgeber_m: float,
    _ges_krankenv_bruttolohn_m: float,
    sozialv_beitr_params: dict,
    einkommensgrenzen__in_gleitzone: bool,
    selbstständig: bool,
) -> float:
    """Employer's long-term care insurance contribution.

    After Midijob introduction in April 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    _ges_pflegev_beitr_midijob_arbeitgeber_m
        See :func:`_ges_pflegev_beitr_midijob_arbeitgeber_m`.
    _ges_krankenv_bruttolohn_m
        See :func:`_ges_krankenv_bruttolohn_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    einkommensgrenzen__in_gleitzone
        See :func:`einkommensgrenzen__in_gleitzone`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.

    Returns
    -------
    Employer's long-term care insurance contributions.

    """
    # Calculate care insurance contributions for regular jobs.
    beitr_regulär_beschäftigt_m = (
        _ges_krankenv_bruttolohn_m
        * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    if selbstständig or einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    elif einkommensgrenzen__in_gleitzone:
        out = _ges_pflegev_beitr_midijob_arbeitgeber_m
    else:
        out = beitr_regulär_beschäftigt_m

    return out


@policy_info(
    start_date="1995-01-01",
    end_date="2004-12-31",
    name_in_dag="ges_pflegev_beitr_selbstständig_m",
)
def ges_pflegev_beitr_selbstständig_m_ohne_zusatz_fuer_kinderlose(
    _ges_krankenv_bemessungsgrundlage_eink_selbständig: float,
    ges_pflegev_beitr_satz_arbeitnehmer: float,
) -> float:
    """Self-employed individuals' long-term care insurance contribution until 2004.

    Self-employed pay the full contribution (employer + employee), which is either
    assessed on their self-employement income or 3/4 of the 'Bezugsgröße'

    Parameters
    ----------

    _ges_krankenv_bemessungsgrundlage_eink_selbständig
        See :func:`_ges_krankenv_bemessungsgrundlage_eink_selbständig`.

    ges_pflegev_beitr_satz_arbeitnehmer
        See :func:`ges_pflegev_beitr_satz_arbeitnehmer`.

    Returns
    -------
    Self-employed long-term care insurance contributions.

    """
    out = _ges_krankenv_bemessungsgrundlage_eink_selbständig * (
        ges_pflegev_beitr_satz_arbeitnehmer * 2
    )

    return out


@policy_info(start_date="2005-01-01", name_in_dag="ges_pflegev_beitr_selbstständig_m")
def ges_pflegev_beitr_selbstständig_m_zusatz_kinderlos_dummy(
    _ges_krankenv_bemessungsgrundlage_eink_selbständig: float,
    ges_pflegev_beitr_satz_arbeitnehmer: float,
    sozialv_beitr_params: dict,
) -> float:
    """Self-employed individuals' long-term care insurance contribution since 2005.

    Self-employed pay the full contribution (employer + employee), which is either
    assessed on their self-employement income or 3/4 of the 'Bezugsgröße'

    Parameters
    ----------

    _ges_krankenv_bemessungsgrundlage_eink_selbständig
        See :func:`_ges_krankenv_bemessungsgrundlage_eink_selbständig`.

    ges_pflegev_beitr_satz_arbeitnehmer
        See :func:`ges_pflegev_beitr_satz_arbeitnehmer`.

    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Self-employed long-term care insurance contributions.

    """
    out = _ges_krankenv_bemessungsgrundlage_eink_selbständig * (
        ges_pflegev_beitr_satz_arbeitnehmer
        + sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    return out


@policy_info(
    start_date="1995-01-01",
    end_date="2004-03-31",
    name_in_dag="ges_pflegev_beitr_rentner_m",
)
def ges_pflegev_beitr_rentner_m_reduz_beitrag(
    _ges_krankenv_bemessungsgrundlage_rente_m: float,
    ges_pflegev_beitr_satz_arbeitnehmer: float,
) -> float:
    """Long-term care insurance contribution from pension income from 1995 until March
    2004.

    Pensioners pay the same contribution as employees.

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_rente_m
        See :func:`_ges_krankenv_bemessungsgrundlage_rente_m`.
    ges_pflegev_beitr_satz_arbeitnehmer
        See :func:`ges_pflegev_beitr_satz_arbeitnehmer`.

    Returns
    -------
    Retiree's long-term care insurance contributions.

    """
    out = (
        _ges_krankenv_bemessungsgrundlage_rente_m * ges_pflegev_beitr_satz_arbeitnehmer
    )

    return out


@policy_info(
    start_date="2004-04-01",
    end_date="2004-12-31",
    name_in_dag="ges_pflegev_beitr_rentner_m",
)
def ges_pflegev_beitr_rentner_m_ohne_zusatz_für_kinderlose(
    _ges_krankenv_bemessungsgrundlage_rente_m: float,
    ges_pflegev_beitr_satz_arbeitnehmer: float,
) -> float:
    """Health insurance contribution from pension income from April until December 2004.

    Pensioners pay twice the contribution of employees.

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_rente_m
        See :func:`_ges_krankenv_bemessungsgrundlage_rente_m`.
    ges_pflegev_beitr_satz_arbeitnehmer
        See :func:`ges_pflegev_beitr_satz_arbeitnehmer`.

    Returns
    -------
    Retiree's long-term care insurance contributions.

    """
    out = _ges_krankenv_bemessungsgrundlage_rente_m * (
        ges_pflegev_beitr_satz_arbeitnehmer * 2
    )

    return out


@policy_info(start_date="2005-01-01", name_in_dag="ges_pflegev_beitr_rentner_m")
def ges_pflegev_beitr_rentner_m_zusatz_kinderlos_dummy(
    _ges_krankenv_bemessungsgrundlage_rente_m: float,
    ges_pflegev_beitr_satz_arbeitnehmer: float,
    sozialv_beitr_params: dict,
) -> float:
    """Health insurance contribution from pension income since 2005.

    Pensioners pay twice the contribution of employees, but only once the additional
    charge for childless individuals.

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_rente_m
        See :func:`_ges_krankenv_bemessungsgrundlage_rente_m`.
    ges_pflegev_beitr_satz_arbeitnehmer
        See :func:`ges_pflegev_beitr_satz_arbeitnehmer`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Retiree's long-term care insurance contributions.

    """
    out = _ges_krankenv_bemessungsgrundlage_rente_m * (
        ges_pflegev_beitr_satz_arbeitnehmer
        + sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    return out


@policy_info(
    start_date="2003-04-01",
    end_date="2004-12-31",
    name_in_dag="_ges_pflegev_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m",
)
def _ges_pflegev_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m_bis_2004(
    einkommensgrenzen__midijob_bemessungsentgelt_m: float,
    ges_pflegev_beitr_satz_arbeitnehmer: float,
    sozialv_beitr_params: dict,
) -> float:
    """Sum of employee and employer long-term care insurance contributions until 2004.

    Parameters
    ----------
    einkommensgrenzen__midijob_bemessungsentgelt_m
        See :func:`einkommensgrenzen__midijob_bemessungsentgelt_m`.
    ges_pflegev_beitr_satz_arbeitnehmer
        See :func:`ges_pflegev_beitr_satz_arbeitnehmer`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Long-term care insurance contributions of employer and employee.


    """

    gesamtbeitrag_midijob_m = einkommensgrenzen__midijob_bemessungsentgelt_m * (
        ges_pflegev_beitr_satz_arbeitnehmer
        + sozialv_beitr_params["beitr_satz"]["ges_pflegev"]
    )

    return gesamtbeitrag_midijob_m


@policy_info(
    start_date="2005-01-01",
    name_in_dag="_ges_pflegev_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m",
)
def _ges_pflegev_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m_ab_2005(
    einkommensgrenzen__midijob_bemessungsentgelt_m: float,
    ges_pflegev_beitr_satz_arbeitnehmer: float,
    sozialv_beitr_params: dict,
) -> float:
    """Sum of employee and employer long-term care insurance contributions since 2005.

    Parameters
    ----------
    einkommensgrenzen__midijob_bemessungsentgelt_m
        See :func:`einkommensgrenzen__midijob_bemessungsentgelt_m`.
    ges_pflegev_beitr_satz_arbeitnehmer
        See :func:`ges_pflegev_beitr_satz_arbeitnehmer`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Long-term care insurance contributions of employer and employee.

    """

    gesamtbeitrag_midijob_m = einkommensgrenzen__midijob_bemessungsentgelt_m * (
        ges_pflegev_beitr_satz_arbeitnehmer
        + sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    return gesamtbeitrag_midijob_m


@policy_info(
    end_date="2004-12-31",
    name_in_dag="_ges_pflegev_beitr_midijob_arbeitgeber_m",
)
def _ges_pflegev_beitr_midijob_arbeitgeber_m_anteil_bruttolohn_bis_2004(
    bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employer's long-term care insurance contribution until December 2004.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.


    Returns
    -------
    Employer's long-term care insurance contributions.


    """

    out = bruttolohn_m * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]

    return out


@policy_info(
    start_date="2005-01-01",
    end_date="2022-09-30",
    name_in_dag="_ges_pflegev_beitr_midijob_arbeitgeber_m",
)
def _ges_pflegev_beitr_midijob_arbeitgeber_m_anteil_bruttolohn_ab_2005(
    bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employers' contribution to long-term care insurance between 2005 and September
    2022.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.


    Returns
    -------
    Employer's long-term care insurance contributions.

    """
    out = bruttolohn_m * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    return out


@policy_info(
    start_date="2022-10-01", name_in_dag="_ges_pflegev_beitr_midijob_arbeitgeber_m"
)
def _ges_pflegev_beitr_midijob_arbeitgeber_m_residuum(
    _ges_pflegev_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m: float,
    _ges_pflegev_beitr_midijob_arbeitnehmer_m: float,
) -> float:
    """Employer's long-term care insurance contribution since October 2022.

    Parameters
    ----------
    _ges_pflegev_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m
        See :func:`_ges_pflegev_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m`.
    _ges_pflegev_beitr_midijob_arbeitnehmer_m
        See :func:`_ges_pflegev_beitr_midijob_arbeitnehmer_m`.


    Returns
    -------
    Employer's long-term care insurance contributions.

    """
    out = (
        _ges_pflegev_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m
        - _ges_pflegev_beitr_midijob_arbeitnehmer_m
    )
    return out


@policy_info(
    end_date="2022-09-30",
    name_in_dag="_ges_pflegev_beitr_midijob_arbeitnehmer_m",
)
def _ges_pflegev_beitr_midijob_arbeitnehmer_m_residuum(
    _ges_pflegev_beitr_midijob_arbeitgeber_m: float,
    _ges_pflegev_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m: float,
) -> float:
    """Employee's long-term care insurance contribution for Midijobs
    until September 2022.

    Parameters
    ----------
    _ges_pflegev_beitr_midijob_arbeitgeber_m
        See :func:`_ges_pflegev_beitr_midijob_arbeitgeber_m`.
    _ges_pflegev_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m
        See :func:`_ges_pflegev_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m`.

    Returns
    -------
    Employee's long-term care insurance contributions.

    """
    out = (
        _ges_pflegev_beitr_midijob_sum_arbeitnehmer_arbeitgeber_m
        - _ges_pflegev_beitr_midijob_arbeitgeber_m
    )

    return out


@policy_info(
    start_date="2022-10-01",
    end_date="2023-06-30",
    name_in_dag="_ges_pflegev_beitr_midijob_arbeitnehmer_m",
)
def _ges_pflegev_beitr_midijob_arbeitnehmer_m_anteil_beitragspfl_einnahme(
    ges_pflegev_zusatz_kinderlos: bool,
    einkommensgrenzen__beitragspfl_einnahmen_arbeitnehmer_m: float,
    einkommensgrenzen__midijob_bemessungsentgelt_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's long-term care insurance contribution since between October 2022 and
    June 2023.

    Parameters
    ----------
    ges_pflegev_zusatz_kinderlos
        See :func:`ges_pflegev_zusatz_kinderlos`.
    einkommensgrenzen__midijob_bemessungsentgelt_m
        See :func:`einkommensgrenzen__midijob_bemessungsentgelt_m`.
    einkommensgrenzen__beitragspfl_einnahmen_arbeitnehmer_m
        See :func:`einkommensgrenzen__beitragspfl_einnahmen_arbeitnehmer_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Employee's long-term care insurance contributions.

    """
    # Calculate the employee care insurance contribution
    an_beitr_midijob_m = (
        einkommensgrenzen__beitragspfl_einnahmen_arbeitnehmer_m
        * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    # Add additional contribution for childless individuals
    if ges_pflegev_zusatz_kinderlos:
        an_beitr_midijob_m += (
            einkommensgrenzen__midijob_bemessungsentgelt_m
            * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    return an_beitr_midijob_m


@policy_info(
    start_date="2023-07-01", name_in_dag="_ges_pflegev_beitr_midijob_arbeitnehmer_m"
)
def _ges_pflegev_beitr_midijob_arbeitnehmer_m_anteil_mit_kinder_abschlag(
    ges_pflegev_anz_kinder_bis_24: int,
    ges_pflegev_zusatz_kinderlos: bool,
    einkommensgrenzen__beitragspfl_einnahmen_arbeitnehmer_m: float,
    einkommensgrenzen__midijob_bemessungsentgelt_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's long-term care insurance contribution since July 2023.

    Parameters
    ----------
    ges_pflegev_anz_kinder_bis_24
        See :func:`ges_pflegev_anz_kinder_bis_24`.
    ges_pflegev_zusatz_kinderlos
        See :func:`ges_pflegev_zusatz_kinderlos`.
    einkommensgrenzen__midijob_bemessungsentgelt_m
        See :func:`einkommensgrenzen__midijob_bemessungsentgelt_m`.
    einkommensgrenzen__beitragspfl_einnahmen_arbeitnehmer_m
        See :func:`einkommensgrenzen__beitragspfl_einnahmen_arbeitnehmer_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Employee's long-term care insurance contributions.

    """
    # Calculate the employee care insurance rate
    ges_pflegev_rate = sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]

    # Reduced contribution for individuals with two or more children under 25
    if ges_pflegev_anz_kinder_bis_24 >= 2:
        ges_pflegev_rate -= sozialv_beitr_params["beitr_satz"]["ges_pflegev"][
            "abschlag_kinder"
        ] * min(ges_pflegev_anz_kinder_bis_24 - 1, 4)

    # Calculate the employee care insurance contribution
    an_beitr_midijob_m = (
        einkommensgrenzen__beitragspfl_einnahmen_arbeitnehmer_m * ges_pflegev_rate
    )

    # Add additional contribution for childless individuals
    if ges_pflegev_zusatz_kinderlos:
        an_beitr_midijob_m += (
            einkommensgrenzen__midijob_bemessungsentgelt_m
            * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    return an_beitr_midijob_m
