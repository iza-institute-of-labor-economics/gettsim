from _gettsim.shared import dates_active


@dates_active(start="2005-01-01")
def ges_pflegev_zusatz_kinderlos(
    hat_kinder: bool,
    alter: int,
    sozialv_beitr_params: dict,
) -> bool:
    """Whether additional care insurance contribution for childless individuals applies.

    Parameters
    ----------
    hat_kinder
        See basic input variable :ref:`hat_kinder <hat_kinder>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    sozialv_beitr_params: dict,
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    mindestalter = sozialv_beitr_params["ges_pflegev_zusatz_kinderlos_mindestalter"]
    return (not hat_kinder) and alter >= mindestalter


@dates_active(
    start="1995-01-01", end="2004-12-31", change_name="ges_pflegev_beitr_satz"
)
def ges_pflegev_beitr_satz_ohne_zusatz_fuer_kinderlose(
    sozialv_beitr_params: dict,
) -> float:
    """Long-term care insurance contribution rate.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """

    return sozialv_beitr_params["beitr_satz"]["ges_pflegev"]


@dates_active(
    start="2005-01-01", end="2023-06-30", change_name="ges_pflegev_beitr_satz"
)
def ges_pflegev_beitr_satz_zusatz_kinderlos_dummy(
    ges_pflegev_zusatz_kinderlos: bool,
    sozialv_beitr_params: dict,
) -> float:
    """Long-term care insurance contribution rate.

    Parameters
    ----------
    ges_pflegev_zusatz_kinderlos
        See :func:`ges_pflegev_zusatz_kinderlos`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    out = sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]

    # Add additional contribution for childless individuals
    if ges_pflegev_zusatz_kinderlos:
        out += sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]

    return out


@dates_active(start="2023-07-01", change_name="ges_pflegev_beitr_satz")
def ges_pflegev_beitr_satz_mit_kinder_abschlag(
    anz_eig_kind_bis_24: int,
    ges_pflegev_zusatz_kinderlos: bool,
    sozialv_beitr_params: dict,
) -> float:
    """Care insurance contribution rate.
    For individuals with children younger than 25 rates are reduced.

    Parameters
    ----------
    anz_eig_kind_bis_24: int,
        See basic input variable :ref:`anz_eig_kind_bis_24 <anz_eig_kind_bis_24>`.
    ges_pflegev_zusatz_kinderlos
        See :func:`ges_pflegev_zusatz_kinderlos`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    out = sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]

    # Add additional contribution for childless individuals
    if ges_pflegev_zusatz_kinderlos:
        out += sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]

    # Reduced contribution for individuals with two or more children under 25
    if anz_eig_kind_bis_24 >= 2:
        out -= sozialv_beitr_params["beitr_satz"]["ges_pflegev"][
            "abschlag_kinder"
        ] * min(anz_eig_kind_bis_24 - 1, 4)

    return out


@dates_active(end="2003-03-31", change_name="ges_pflegev_beitr_m")
def ges_pflegev_beitr_m_vor_midijob(
    _ges_pflegev_beitr_reg_beschäftigt_m: float,
    geringfügig_beschäftigt: bool,
    ges_pflegev_beitr_rente_m: float,
    ges_pflegev_beitr_selbst_m: float,
    selbstständig: bool,
) -> float:
    """Contribution for each individual to the public care insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    ges_pflegev_beitr_rente_m
        See :func:`ges_pflegev_beitr_rente_m`.
    ges_pflegev_beitr_selbst_m
        See :func:`ges_pflegev_beitr_selbst_m`.
    ges_pflegev_beitr_regulär_besch_m
        See :func:`ges_pflegev_beitr_regulär_besch_m`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.

    Returns
    -------

    """

    if selbstständig:
        out = ges_pflegev_beitr_selbst_m
    elif geringfügig_beschäftigt:
        out = 0.0
    else:
        out = _ges_pflegev_beitr_reg_beschäftigt_m

    # Add the care insurance contribution for pensions
    return out + ges_pflegev_beitr_rente_m


@dates_active(start="2003-04-01", change_name="ges_pflegev_beitr_m")
def ges_pflegev_beitr_m_mit_midijob(  # noqa: PLR0913
    _ges_pflegev_beitr_reg_beschäftigt_m: float,
    geringfügig_beschäftigt: bool,
    ges_pflegev_beitr_rente_m: float,
    ges_pflegev_beitr_selbst_m: float,
    _ges_pflegev_beitr_midijob_arbeitn_m: float,
    in_gleitzone: bool,
    selbstständig: bool,
) -> float:
    """Contribution for each individual to the public care insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    ges_pflegev_beitr_rente_m
        See :func:`ges_pflegev_beitr_rente_m`.
    ges_pflegev_beitr_selbst_m
        See :func:`ges_pflegev_beitr_selbst_m`.
    _ges_pflegev_beitr_midijob_arbeitn_m
        See :func:`_ges_pflegev_beitr_midijob_arbeitn_m`.
    ges_pflegev_beitr_regulär_besch_m
        See :func:`ges_pflegev_beitr_regulär_besch_m`.
    in_gleitzone
        See :func:`in_gleitzone`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.

    Returns
    -------

    """

    if selbstständig:
        out = ges_pflegev_beitr_selbst_m
    elif geringfügig_beschäftigt:
        out = 0.0
    elif in_gleitzone:
        out = _ges_pflegev_beitr_midijob_arbeitn_m
    else:
        out = _ges_pflegev_beitr_reg_beschäftigt_m

    # Add the care insurance contribution for pensions
    return out + ges_pflegev_beitr_rente_m


def _ges_pflegev_beitr_reg_beschäftigt_m(
    _ges_krankenv_bruttolohn_m: float,
    ges_pflegev_beitr_satz: float,
) -> float:
    """Contribution to the public care insurance for people with regular jobs.

    Parameters
    ----------
    _ges_krankenv_bruttolohn_m:
        See :func:`_ges_krankenv_bruttolohn_m`.
    ges_pflegev_beitr_satz:
        See :func:`ges_pflegev_beitr_satz`.

    Returns
    -------

    """

    beitr_regulär_beschäftigt_m = _ges_krankenv_bruttolohn_m * ges_pflegev_beitr_satz

    return beitr_regulär_beschäftigt_m


@dates_active(end="2003-03-31", change_name="ges_pflegev_beitr_arbeitg_m")
def ges_pflegev_beitr_arbeitg_m_vor_midijob(
    geringfügig_beschäftigt: bool,
    _ges_krankenv_bruttolohn_m: float,
    sozialv_beitr_params: dict,
    selbstständig: bool,
) -> float:
    """Contribution of the respective employer to the public care insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    _ges_krankenv_bruttolohn_m
        See :func:`_ges_krankenv_bruttolohn_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.

    Returns
    -------

    """
    # Calculate care insurance contributions for regular jobs.
    beitr_regulär_beschäftigt_m = (
        _ges_krankenv_bruttolohn_m * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]
    )

    if selbstständig or geringfügig_beschäftigt:
        out = 0.0
    else:
        out = beitr_regulär_beschäftigt_m

    return out


@dates_active(start="2003-04-01", change_name="ges_pflegev_beitr_arbeitg_m")
def ges_pflegev_beitr_arbeitg_m_mit_midijob(
    geringfügig_beschäftigt: bool,
    _ges_pflegev_beitr_midijob_arbeitg_m: float,
    _ges_krankenv_bruttolohn_m: float,
    sozialv_beitr_params: dict,
    in_gleitzone: bool,
    selbstständig: bool,
) -> float:
    """Contribution of the respective employer to the public care insurance.

    Parameters
    ----------
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.
    _ges_pflegev_beitr_midijob_arbeitg_m
        See :func:`_ges_pflegev_beitr_midijob_arbeitg_m`.
    _ges_krankenv_bruttolohn_m
        See :func:`_ges_krankenv_bruttolohn_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    in_gleitzone
        See :func:`in_gleitzone`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.

    Returns
    -------

    """
    # Calculate care insurance contributions for regular jobs.
    beitr_regulär_beschäftigt_m = (
        _ges_krankenv_bruttolohn_m
        * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    if selbstständig or geringfügig_beschäftigt:
        out = 0.0
    elif in_gleitzone:
        out = _ges_pflegev_beitr_midijob_arbeitg_m
    else:
        out = beitr_regulär_beschäftigt_m

    return out


@dates_active(
    start="1995-01-01", end="2004-12-31", change_name="ges_pflegev_beitr_selbst_m"
)
def ges_pflegev_beitr_selbst_m_ohne_zusatz_fuer_kinderlose(
    _ges_krankenv_bemessungsgrundlage_eink_selbst: float,
    ges_pflegev_beitr_satz: float,
) -> float:
    """Calculate care insurance contributions for self-employed individuals.

    Self-employed pay the full contribution (employer + employee), which is either
    assessed on their self-employement income or 3/4 of the 'Bezugsgröße'

    Parameters
    ----------

    _ges_krankenv_bemessungsgrundlage_eink_selbst
        See :func:`_ges_krankenv_bemessungsgrundlage_eink_selbst`.

    ges_pflegev_beitr_satz
        See :func:`ges_pflegev_beitr_satz`.

    Returns
    -------
    Monthly care insurance contributions for self employed income.

    """
    out = _ges_krankenv_bemessungsgrundlage_eink_selbst * (ges_pflegev_beitr_satz * 2)

    return out


@dates_active(start="2005-01-01", change_name="ges_pflegev_beitr_selbst_m")
def ges_pflegev_beitr_selbst_m_zusatz_kinderlos_dummy(
    _ges_krankenv_bemessungsgrundlage_eink_selbst: float,
    ges_pflegev_beitr_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Calculate care insurance contributions for self-employed individuals.

    Self-employed pay the full contribution (employer + employee), which is either
    assessed on their self-employement income or 3/4 of the 'Bezugsgröße'

    Parameters
    ----------

    _ges_krankenv_bemessungsgrundlage_eink_selbst
        See :func:`_ges_krankenv_bemessungsgrundlage_eink_selbst`.

    ges_pflegev_beitr_satz
        See :func:`ges_pflegev_beitr_satz`.

    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Monthly care insurance contributions for self employed income.

    """
    out = _ges_krankenv_bemessungsgrundlage_eink_selbst * (
        ges_pflegev_beitr_satz
        + sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    return out


@dates_active(
    start="1995-01-01", end="2004-12-31", change_name="ges_pflegev_beitr_rente_m"
)
def ges_pflegev_beitr_rente_m_ohne_zusatz_fuer_kinderlose(
    _ges_krankenv_bemessungsgrundlage_rente_m: float,
    ges_pflegev_beitr_satz: float,
) -> float:
    """Calculating the contribution to health insurance for pension income.

    Pensioners pay twice the contribution of employees.

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_rente_m
        See :func:`_ges_krankenv_bemessungsgrundlage_rente_m`.
    ges_pflegev_beitr_satz
        See :func:`ges_pflegev_beitr_satz`.

    Returns
    -------
    Monthly health insurance contributions for pension income.

    """
    out = _ges_krankenv_bemessungsgrundlage_rente_m * (ges_pflegev_beitr_satz * 2)

    return out


@dates_active(start="2005-01-01", change_name="ges_pflegev_beitr_rente_m")
def ges_pflegev_beitr_rente_m_zusatz_kinderlos_dummy(
    _ges_krankenv_bemessungsgrundlage_rente_m: float,
    ges_pflegev_beitr_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Calculating the contribution to health insurance for pension income.

    Pensioners pay twice the contribution of employees, but only once the additional
    charge for childless individuals.

    Parameters
    ----------
    _ges_krankenv_bemessungsgrundlage_rente_m
        See :func:`_ges_krankenv_bemessungsgrundlage_rente_m`.
    ges_pflegev_beitr_satz
        See :func:`ges_pflegev_beitr_satz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Monthly health insurance contributions for pension income.

    """
    out = _ges_krankenv_bemessungsgrundlage_rente_m * (
        ges_pflegev_beitr_satz
        + sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    return out


@dates_active(
    start="2003-04-01",
    end="2004-12-31",
    change_name="_ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m",
)
def _ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m_bis_2004(
    midijob_bemessungsentgelt_m: float,
    ges_pflegev_beitr_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Sum of employee and employer long-term care insurance contributions.

    Parameters
    ----------
    midijob_bemessungsentgelt_m
        See :func:`midijob_bemessungsentgelt_m`.
    ges_pflegev_beitr_satz
        See :func:`ges_pflegev_beitr_satz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """

    gesamtbeitrag_midijob_m = midijob_bemessungsentgelt_m * (
        ges_pflegev_beitr_satz + sozialv_beitr_params["beitr_satz"]["ges_pflegev"]
    )

    return gesamtbeitrag_midijob_m


@dates_active(
    start="2005-01-01",
    change_name="_ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m",
)
def _ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m_ab_2005(
    midijob_bemessungsentgelt_m: float,
    ges_pflegev_beitr_satz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Sum of employee and employer long-term care insurance contributions.

    Parameters
    ----------
    midijob_bemessungsentgelt_m
        See :func:`midijob_bemessungsentgelt_m`.
    ges_pflegev_beitr_satz
        See :func:`ges_pflegev_beitr_satz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """

    gesamtbeitrag_midijob_m = midijob_bemessungsentgelt_m * (
        ges_pflegev_beitr_satz
        + sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    return gesamtbeitrag_midijob_m


@dates_active(
    end="2004-12-31",
    change_name="_ges_pflegev_beitr_midijob_arbeitg_m",
)
def _ges_pflegev_beitr_midijob_arbeitg_m_anteil_bruttolohn_bis_2004(
    bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Calculating the employer care insurance contribution until September 2022.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.


    Returns
    -------

    """

    out = bruttolohn_m * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]

    return out


@dates_active(
    start="2005-01-01",
    end="2022-09-30",
    change_name="_ges_pflegev_beitr_midijob_arbeitg_m",
)
def _ges_pflegev_beitr_midijob_arbeitg_m_anteil_bruttolohn_ab_2005(
    bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Calculating the employer care insurance contribution until September 2022.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.


    Returns
    -------

    """
    if isinstance(sozialv_beitr_params["beitr_satz"]["ges_pflegev"], dict):
        out = (
            bruttolohn_m * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
        )
    else:
        out = bruttolohn_m * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]
    return out


@dates_active(start="2022-10-01", change_name="_ges_pflegev_beitr_midijob_arbeitg_m")
def _ges_pflegev_beitr_midijob_arbeitg_m_residuum(
    _ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m: float,
    _ges_pflegev_beitr_midijob_arbeitn_m: float,
) -> float:
    """Calculating the employer care insurance contribution since October 2022.

    Parameters
    ----------
    _ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m
        See :func:`_ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m`.
    _ges_pflegev_beitr_midijob_arbeitn_m
        See :func:`_ges_pflegev_beitr_midijob_arbeitn_m`.


    Returns
    -------

    """
    out = (
        _ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m
        - _ges_pflegev_beitr_midijob_arbeitn_m
    )
    return out


@dates_active(
    end="2022-09-30",
    change_name="_ges_pflegev_beitr_midijob_arbeitn_m",
)
def _ges_pflegev_beitr_midijob_arbeitn_m_residuum(
    _ges_pflegev_beitr_midijob_arbeitg_m: float,
    _ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m: float,
) -> float:
    """Calculating the employee care insurance contribution until September 2022.

    Parameters
    ----------
    _ges_pflegev_beitr_midijob_arbeitg_m
        See :func:`_ges_pflegev_beitr_midijob_arbeitg_m`.
    _ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m
        See :func:`_ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m`.

    Returns
    -------

    """
    out = (
        _ges_pflegev_beitr_midijob_sum_arbeitn_arbeitg_m
        - _ges_pflegev_beitr_midijob_arbeitg_m
    )

    return out


@dates_active(
    start="2022-10-01",
    end="2023-06-30",
    change_name="_ges_pflegev_beitr_midijob_arbeitn_m",
)
def _ges_pflegev_beitr_midijob_arbeitn_m_anteil_beitragspfl_einnahme(
    ges_pflegev_zusatz_kinderlos: bool,
    _midijob_beitragspfl_einnahme_arbeitn_m: float,
    midijob_bemessungsentgelt_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Calculating the employee care insurance contribution since October 2022.

    Parameters
    ----------
    ges_pflegev_zusatz_kinderlos
        See :func:`ges_pflegev_zusatz_kinderlos`.
    midijob_bemessungsentgelt_m
        See :func:`midijob_bemessungsentgelt_m`.
    _midijob_beitragspfl_einnahme_arbeitn_m
        See :func:`_midijob_beitragspfl_einnahme_arbeitn_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    # Calculate the employee care insurance contribution
    an_beitr_midijob_m = (
        _midijob_beitragspfl_einnahme_arbeitn_m
        * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    # Add additional contribution for childless individuals
    if ges_pflegev_zusatz_kinderlos:
        an_beitr_midijob_m += (
            midijob_bemessungsentgelt_m
            * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    return an_beitr_midijob_m


@dates_active(start="2023-07-01", change_name="_ges_pflegev_beitr_midijob_arbeitn_m")
def _ges_pflegev_beitr_midijob_arbeitn_m_anteil_mit_kinder_abschlag(
    anz_eig_kind_bis_24: int,
    ges_pflegev_zusatz_kinderlos: bool,
    _midijob_beitragspfl_einnahme_arbeitn_m: float,
    midijob_bemessungsentgelt_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Calculating the employee care insurance contribution since October 2022.

    Parameters
    ----------
    anz_eig_kind_bis_24
        See basic input variable :ref:`anz_eig_kind_bis_24 <anz_eig_kind_bis_24>`.
    ges_pflegev_zusatz_kinderlos
        See :func:`ges_pflegev_zusatz_kinderlos`.
    midijob_bemessungsentgelt_m
        See :func:`midijob_bemessungsentgelt_m`.
    _midijob_beitragspfl_einnahme_arbeitn_m
        See :func:`_midijob_beitragspfl_einnahme_arbeitn_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------

    """
    # Calculate the employee care insurance rate
    ges_pflegev_rate = sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]

    # Reduced contribution for individuals with two or more children under 25
    if anz_eig_kind_bis_24 >= 2:
        ges_pflegev_rate -= sozialv_beitr_params["beitr_satz"]["ges_pflegev"][
            "abschlag_kinder"
        ] * min(anz_eig_kind_bis_24 - 1, 4)

    # Calculate the employee care insurance contribution
    an_beitr_midijob_m = _midijob_beitragspfl_einnahme_arbeitn_m * ges_pflegev_rate

    # Add additional contribution for childless individuals
    if ges_pflegev_zusatz_kinderlos:
        an_beitr_midijob_m += (
            midijob_bemessungsentgelt_m
            * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    return an_beitr_midijob_m
