"""Contributions to public long-term care insurance."""

from _gettsim.functions.policy_function import policy_function


@policy_function(end_date="2003-03-31", name_in_dag="betrag_arbeitnehmer_m")
def betrag_vor_midijob_m(
    betrag_arbeitnehmer_regulär_beschäftigt_m: float,
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    betrag_rentner_m: float,
    betrag_selbständig_m: float,
    selbstständig: bool,
) -> float:
    """Employee's long-term care insurance contribution until March 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    betrag_rentner_m
        See :func:`betrag_rentner_m`.
    betrag_selbständig_m
        See :func:`betrag_selbständig_m`.
    betrag_arbeitnehmer_regulär_beschäftigt_m
        See :func:`betrag_arbeitnehmer_regulär_beschäftigt_m`.
    selbstständig
        See basic input variable :ref:`selbstständig <selbstständig>`.

    Returns
    -------
    Employee's long-term care insurance contributions.

    """

    if selbstständig:
        out = betrag_selbständig_m
    elif einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = betrag_arbeitnehmer_regulär_beschäftigt_m

    # Add the care insurance contribution for pensions
    return out + betrag_rentner_m


@policy_function(start_date="2003-04-01", name_in_dag="betrag_arbeitnehmer_m")
def betrag_mit_midijob_m(  # noqa: PLR0913
    betrag_arbeitnehmer_regulär_beschäftigt_m: float,
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    betrag_rentner_m: float,
    betrag_selbständig_m: float,
    betrag_arbeitnehmer_m: float,
    einkommensgrenzen__in_gleitzone: bool,
    selbstständig: bool,
) -> float:
    """Employee's long-term care insurance contribution since April 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    betrag_rentner_m
        See :func:`betrag_rentner_m`.
    betrag_selbständig_m
        See :func:`betrag_selbständig_m`.
    betrag_arbeitnehmer_m
        See :func:`betrag_arbeitnehmer_m`.
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
        out = betrag_selbständig_m
    elif einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    elif einkommensgrenzen__in_gleitzone:
        out = betrag_arbeitnehmer_m
    else:
        out = betrag_arbeitnehmer_regulär_beschäftigt_m

    # Add the care insurance contribution for pensions
    return out + betrag_rentner_m


def betrag_arbeitnehmer_regulär_beschäftigt_m(
    sozialversicherungsbeitraege__krankenversicherung__einkommen_m: float,
    beitragssatz: float,
) -> float:
    """Employee's long-term care insurance contribution if regularly employed.

    Parameters
    ----------
    sozialversicherungsbeitraege__krankenversicherung__einkommen_m:
        See :func:`sozialversicherungsbeitraege__krankenversicherung__einkommen_m`.
    beitragssatz:
        See :func:`beitragssatz`.

    Returns
    -------
    Long-term care insurance contributions of employer and employee.

    """

    return sozialversicherungsbeitraege__krankenversicherung__einkommen_m * beitragssatz


@policy_function(end_date="2003-03-31", name_in_dag="betrag_arbeitgeber_m")
def betrag_arbeitgeber_vor_midijob_m(
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    sozialversicherungsbeitraege__krankenversicherung__einkommen_m: float,
    sozialv_beitr_params: dict,
    selbstständig: bool,
) -> float:
    """Employer's long-term care insurance contribution.

    Before Midijob introduction in April 2003.

    Parameters
    ----------
    einkommensgrenzen__geringfügig_beschäftigt
        See :func:`einkommensgrenzen__geringfügig_beschäftigt`.
    sozialversicherungsbeitraege__krankenversicherung__einkommen_m
        See :func:`sozialversicherungsbeitraege__krankenversicherung__einkommen_m`.
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
        sozialversicherungsbeitraege__krankenversicherung__einkommen_m
        * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]
    )

    if selbstständig or einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = beitr_regulär_beschäftigt_m

    return out


@policy_function(start_date="2003-04-01", name_in_dag="betrag_arbeitgeber_m")
def betrag_arbeitgeber_mit_midijob_m(  # noqa: PLR0913
    einkommensgrenzen__geringfügig_beschäftigt: bool,
    betrag_arbeitgeber_midijob: float,
    sozialversicherungsbeitraege__krankenversicherung__einkommen_m: float,
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
    betrag_arbeitgeber_midijob
        See :func:`betrag_arbeitgeber_midijob`.
    sozialversicherungsbeitraege__krankenversicherung__einkommen_m
        See         :func:`sozialversicherungsbeitraege__krankenversicherung__einkommen_m`.
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
        sozialversicherungsbeitraege__krankenversicherung__einkommen_m
        * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    if selbstständig or einkommensgrenzen__geringfügig_beschäftigt:
        out = 0.0
    elif einkommensgrenzen__in_gleitzone:
        out = betrag_arbeitgeber_midijob
    else:
        out = beitr_regulär_beschäftigt_m

    return out


@policy_function(
    start_date="1995-01-01",
    end_date="2004-12-31",
    name_in_dag="betrag_selbständig_m",
)
def betrag_selbständig_ohne_zusatz_fuer_kinderlose_m(
    sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_selbständig_m: float,
    beitragssatz: float,
) -> float:
    """Self-employed individuals' long-term care insurance contribution until 2004.

    Self-employed pay the full contribution (employer + employee), which is either
    assessed on their self-employement income or 3/4 of the 'Bezugsgröße'

    Parameters
    ----------

    sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_selbständig_m
        See         :func:`sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_selbständig_m`.

    beitragssatz
        See         :func:`beitragssatz`.

    Returns
    -------
    Self-employed long-term care insurance contributions.

    """
    return (
        sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_selbständig_m
        * (beitragssatz * 2)
    )


@policy_function(start_date="2005-01-01", name_in_dag="betrag_selbständig_m")
def betrag_selbständig_zusatz_kinderlos_dummy_m(
    sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_selbständig_m: float,
    beitragssatz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Self-employed individuals' long-term care insurance contribution since 2005.

    Self-employed pay the full contribution (employer + employee), which is either
    assessed on their self-employement income or 3/4 of the 'Bezugsgröße'

    Parameters
    ----------

    sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_selbständig_m
        See         :func:`sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_selbständig_m`.

    beitragssatz
        See :func:`beitragssatz`.

    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Self-employed long-term care insurance contributions.

    """
    return (
        sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_selbständig_m
        * (beitragssatz + sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"])
    )


@policy_function(
    start_date="1995-01-01",
    end_date="2004-03-31",
    name_in_dag="betrag_rentner_m",
)
def betrag_rentner_reduz_beitrag_m(
    sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_rente_m: float,
    beitragssatz: float,
) -> float:
    """Long-term care insurance contribution from pension income from 1995 until March
    2004.

    Pensioners pay the same contribution as employees.

    Parameters
    ----------
    sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_rente_m
        See :func:`sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_rente_m`.
    beitragssatz
        See :func:`beitragssatz`.

    Returns
    -------
    Retiree's long-term care insurance contributions.

    """
    return (
        sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_rente_m
        * beitragssatz
    )


@policy_function(
    start_date="2004-04-01",
    end_date="2004-12-31",
    name_in_dag="betrag_rentner_m",
)
def betrag_rentner_ohne_zusatz_für_kinderlose_m(
    sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_rente_m: float,
    beitragssatz: float,
) -> float:
    """Health insurance contribution from pension income from April until December 2004.

    Pensioners pay twice the contribution of employees.

    Parameters
    ----------
    sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_rente_m
        See :func:`sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_rente_m`.
    beitragssatz
        See :func:`beitragssatz`.

    Returns
    -------
    Retiree's long-term care insurance contributions.

    """
    return (
        sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_rente_m
        * (beitragssatz * 2)
    )


@policy_function(start_date="2005-01-01", name_in_dag="betrag_rentner_m")
def betrag_rentner_zusatz_kinderlos_dummy_m(
    sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_rente_m: float,
    beitragssatz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Health insurance contribution from pension income since 2005.

    Pensioners pay twice the contribution of employees, but only once the additional
    charge for childless individuals.

    Parameters
    ----------
    sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_rente_m
        See :func:`sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_rente_m`.
    beitragssatz
        See :func:`beitragssatz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Retiree's long-term care insurance contributions.

    """
    return (
        sozialversicherungsbeitraege__krankenversicherung__bemessungsgrundlage_rente_m
        * (beitragssatz + sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"])
    )


@policy_function(
    start_date="2003-04-01",
    end_date="2004-12-31",
    name_in_dag="betrag_gesamt_m",
)
def betrag_gesamt_bis_2004_m(
    einkommensgrenzen__midijob_bemessungsentgelt_m: float,
    beitragssatz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Sum of employee and employer long-term care insurance contributions until 2004.

    Parameters
    ----------
    einkommensgrenzen__midijob_bemessungsentgelt_m
        See :func:`einkommensgrenzen__midijob_bemessungsentgelt_m`.
    beitragssatz
        See :func:`beitragssatz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Long-term care insurance contributions of employer and employee.


    """

    return einkommensgrenzen__midijob_bemessungsentgelt_m * (
        beitragssatz + sozialv_beitr_params["beitr_satz"]["ges_pflegev"]
    )


@policy_function(
    start_date="2005-01-01",
    name_in_dag="betrag_gesamt_m",
)
def betrag_gesamty_ab_2005_m(
    einkommensgrenzen__midijob_bemessungsentgelt_m: float,
    beitragssatz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Sum of employee and employer long-term care insurance contributions since 2005.

    Parameters
    ----------
    einkommensgrenzen__midijob_bemessungsentgelt_m
        See :func:`einkommensgrenzen__midijob_bemessungsentgelt_m`.
    beitragssatz
        See         :func:`beitragssatz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Long-term care insurance contributions of employer and employee.

    """

    return einkommensgrenzen__midijob_bemessungsentgelt_m * (
        beitragssatz + sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )


@policy_function(
    end_date="2004-12-31",
    name_in_dag="betrag_arbeitgeber_midijob",
)
def betrag_arbeitgeber_midijob_anteil_bruttolohn_bis_2004(
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


@policy_function(
    start_date="2005-01-01",
    end_date="2022-09-30",
    name_in_dag="betrag_arbeitgeber_midijob",
)
def betrag_arbeitgeber_midijob_anteil_bruttolohn_ab_2005(
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


@policy_function(start_date="2022-10-01", name_in_dag="betrag_arbeitgeber_midijob")
def betrag_arbeitgeber_midijob_residuum(
    betrag_gesamt_m: float,
    betrag_arbeitnehmer_m: float,
) -> float:
    """Employer's long-term care insurance contribution since October 2022.

    Parameters
    ----------
    betrag_gesamt_m
        See :func:`betrag_gesamt_m`.
    betrag_arbeitnehmer_m
        See :func:`betrag_arbeitnehmer_m`.


    Returns
    -------
    Employer's long-term care insurance contributions.

    """
    out = betrag_gesamt_m - betrag_arbeitnehmer_m
    return out


@policy_function(
    end_date="2022-09-30",
    name_in_dag="betrag_arbeitnehmer_m",
)
def betrag_arbeitnehmer_residuum_m(
    betrag_arbeitgeber_midijob: float,
    betrag_gesamt_m: float,
) -> float:
    """Employee's long-term care insurance contribution for Midijobs
    until September 2022.

    Parameters
    ----------
    betrag_arbeitgeber_midijob
        See :func:`betrag_arbeitgeber_midijob`.
    betrag_gesamt_m
        See :func:`betrag_gesamt_m`.

    Returns
    -------
    Employee's long-term care insurance contributions.

    """
    out = betrag_gesamt_m - betrag_arbeitgeber_midijob

    return out


@policy_function(
    start_date="2022-10-01",
    end_date="2023-06-30",
    name_in_dag="betrag_arbeitnehmer_m",
)
def betrag_arbeitnehmer_anteil_beitragspfl_einnahme_m(
    beitragssatz__zusatzbetrag_kinderlos: bool,
    einkommensgrenzen__beitragspfl_einnahmen_arbeitnehmer_m: float,
    einkommensgrenzen__midijob_bemessungsentgelt_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's long-term care insurance contribution since between October 2022 and
    June 2023.

    Parameters
    ----------
    beitragssatz__zusatzbetrag_kinderlos
        See         :func:`beitragssatz__zusatzbetrag_kinderlos`.
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
    if beitragssatz__zusatzbetrag_kinderlos:
        an_beitr_midijob_m += (
            einkommensgrenzen__midijob_bemessungsentgelt_m
            * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    return an_beitr_midijob_m


@policy_function(start_date="2023-07-01", name_in_dag="betrag_arbeitnehmer_m")
def betrag_arbeitnehmer_m_anteil_mit_kinder_abschlag(
    ges_pflegev_anz_kinder_bis_24: int,
    beitragssatz__zusatzbetrag_kinderlos: bool,
    einkommensgrenzen__beitragspfl_einnahmen_arbeitnehmer_m: float,
    einkommensgrenzen__midijob_bemessungsentgelt_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's long-term care insurance contribution since July 2023.

    Parameters
    ----------
    ges_pflegev_anz_kinder_bis_24
        See :func:`ges_pflegev_anz_kinder_bis_24`.
    beitragssatz__zusatzbetrag_kinderlos
        See         :func:`beitragssatz__zusatzbetrag_kinderlos`.
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
    if beitragssatz__zusatzbetrag_kinderlos:
        an_beitr_midijob_m += (
            einkommensgrenzen__midijob_bemessungsentgelt_m
            * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    return an_beitr_midijob_m
