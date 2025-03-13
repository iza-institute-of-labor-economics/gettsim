"""Contributions to public long-term care insurance."""

from _gettsim.function_types import policy_function


@policy_function(end_date="2003-03-31", leaf_name="betrag_arbeitnehmer_m")
def betrag_vor_midijob_m(
    betrag_arbeitnehmer_regulär_beschäftigt_m: float,
    sozialversicherung__geringfügig_beschäftigt: bool,
    betrag_rentner_m: float,
    betrag_selbständig_m: float,
    einkommen__ist_selbstständig: bool,
) -> float:
    """Employee's long-term care insurance contribution until March 2003.

    Parameters
    ----------
    sozialversicherung__geringfügig_beschäftigt
        See :func:`sozialversicherung__geringfügig_beschäftigt`.
    betrag_rentner_m
        See :func:`betrag_rentner_m`.
    betrag_selbständig_m
        See :func:`betrag_selbständig_m`.
    betrag_arbeitnehmer_regulär_beschäftigt_m
        See :func:`betrag_arbeitnehmer_regulär_beschäftigt_m`.
    einkommen__ist_selbstständig
        See basic input variable :ref:`einkommen__ist_selbstständig <einkommen__ist_selbstständig>`.

    Returns
    -------
    Employee's long-term care insurance contributions.

    """

    if einkommen__ist_selbstständig:
        out = betrag_selbständig_m
    elif sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = betrag_arbeitnehmer_regulär_beschäftigt_m

    # Add the care insurance contribution for pensions
    return out + betrag_rentner_m


@policy_function(start_date="2003-04-01", leaf_name="betrag_arbeitnehmer_m")
def betrag_mit_midijob_m(  # noqa: PLR0913
    betrag_arbeitnehmer_regulär_beschäftigt_m: float,
    sozialversicherung__geringfügig_beschäftigt: bool,
    betrag_rentner_m: float,
    betrag_selbständig_m: float,
    betrag_arbeitnehmer_m: float,
    sozialversicherung__in_gleitzone: bool,
    einkommen__ist_selbstständig: bool,
) -> float:
    """Employee's long-term care insurance contribution since April 2003.

    Parameters
    ----------
    betrag_arbeitnehmer_regulär_beschäftigt_m
        See :func:`betrag_arbeitnehmer_regulär_beschäftigt_m`.
    sozialversicherung__geringfügig_beschäftigt
        See :func:`sozialversicherung__geringfügig_beschäftigt`.
    betrag_rentner_m
        See :func:`betrag_rentner_m`.
    betrag_selbständig_m
        See :func:`betrag_selbständig_m`.
    betrag_arbeitnehmer_m
        See :func:`betrag_arbeitnehmer_m`.
    sozialversicherung__in_gleitzone
        See :func:`sozialversicherung__in_gleitzone`.
    einkommen__ist_selbstständig
        See basic input variable :ref:`einkommen__ist_selbstständig <einkommen__ist_selbstständig>`.

    Returns
    -------
    Employee's long-term care insurance contributions.

    """

    if einkommen__ist_selbstständig:
        out = betrag_selbständig_m
    elif sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    elif sozialversicherung__in_gleitzone:
        out = betrag_arbeitnehmer_m
    else:
        out = betrag_arbeitnehmer_regulär_beschäftigt_m

    # Add the care insurance contribution for pensions
    return out + betrag_rentner_m


@policy_function()
def betrag_arbeitnehmer_regulär_beschäftigt_m(
    sozialversicherung__kranken__beitrag__einkommen_m: float,
    beitragssatz: float,
) -> float:
    """Employee's long-term care insurance contribution if regularly employed.

    Parameters
    ----------
    sozialversicherung__kranken__beitrag__einkommen_m:
        See :func:`sozialversicherung__kranken__beitrag__einkommen_m`.
    beitragssatz:
        See :func:`beitragssatz`.

    Returns
    -------
    Long-term care insurance contributions of employer and employee.

    """

    return sozialversicherung__kranken__beitrag__einkommen_m * beitragssatz


@policy_function(end_date="2003-03-31", leaf_name="betrag_arbeitgeber_m")
def betrag_arbeitgeber_vor_midijob_m(
    sozialversicherung__geringfügig_beschäftigt: bool,
    sozialversicherung__kranken__beitrag__einkommen_m: float,
    sozialv_beitr_params: dict,
    einkommen__ist_selbstständig: bool,
) -> float:
    """Employer's long-term care insurance contribution.

    Before Midijob introduction in April 2003.

    Parameters
    ----------
    sozialversicherung__geringfügig_beschäftigt
        See :func:`sozialversicherung__geringfügig_beschäftigt`.
    sozialversicherung__kranken__beitrag__einkommen_m
        See :func:`sozialversicherung__kranken__beitrag__einkommen_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    einkommen__ist_selbstständig
        See basic input variable :ref:`einkommen__ist_selbstständig <einkommen__ist_selbstständig>`.

    Returns
    -------
    Employer's long-term care insurance contributions.

    """
    # Calculate care insurance contributions for regular jobs.
    beitr_regulär_beschäftigt_m = (
        sozialversicherung__kranken__beitrag__einkommen_m
        * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]
    )

    if einkommen__ist_selbstständig or sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    else:
        out = beitr_regulär_beschäftigt_m

    return out


@policy_function(start_date="2003-04-01", leaf_name="betrag_arbeitgeber_m")
def betrag_arbeitgeber_mit_midijob_m(  # noqa: PLR0913
    sozialversicherung__geringfügig_beschäftigt: bool,
    betrag_arbeitgeber_midijob_m: float,
    sozialversicherung__kranken__beitrag__einkommen_m: float,
    sozialv_beitr_params: dict,
    sozialversicherung__in_gleitzone: bool,
    einkommen__ist_selbstständig: bool,
) -> float:
    """Employer's long-term care insurance contribution.

    After Midijob introduction in April 2003.

    Parameters
    ----------
    sozialversicherung__geringfügig_beschäftigt
        See :func:`sozialversicherung__geringfügig_beschäftigt`.
    betrag_arbeitgeber_midijob_m
        See :func:`betrag_arbeitgeber_midijob_m`.
    sozialversicherung__kranken__beitrag__einkommen_m
        See         :func:`sozialversicherung__kranken__beitrag__einkommen_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    sozialversicherung__in_gleitzone
        See :func:`sozialversicherung__in_gleitzone`.
    einkommen__ist_selbstständig
        See basic input variable :ref:`einkommen__ist_selbstständig <einkommen__ist_selbstständig>`.

    Returns
    -------
    Employer's long-term care insurance contributions.

    """
    # Calculate care insurance contributions for regular jobs.
    beitr_regulär_beschäftigt_m = (
        sozialversicherung__kranken__beitrag__einkommen_m
        * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    if einkommen__ist_selbstständig or sozialversicherung__geringfügig_beschäftigt:
        out = 0.0
    elif sozialversicherung__in_gleitzone:
        out = betrag_arbeitgeber_midijob_m
    else:
        out = beitr_regulär_beschäftigt_m

    return out


@policy_function(
    start_date="1995-01-01",
    end_date="2004-12-31",
    leaf_name="betrag_selbständig_m",
)
def betrag_selbständig_ohne_zusatz_fuer_kinderlose_m(
    sozialversicherung__kranken__beitrag__bemessungsgrundlage_selbständig_m: float,
    beitragssatz: float,
) -> float:
    """Self-employed individuals' long-term care insurance contribution until 2004.

    Self-employed pay the full contribution (employer + employee), which is either
    assessed on their self-employement income or 3/4 of the 'Bezugsgröße'

    Parameters
    ----------

    sozialversicherung__kranken__beitrag__bemessungsgrundlage_selbständig_m
        See :func: `sozialversicherung__kranken__beitrag__bemessungsgrundlage_selbständig_m`.

    beitragssatz
        See :func: `beitragssatz`.

    Returns
    -------
    Self-employed long-term care insurance contributions.

    """
    return sozialversicherung__kranken__beitrag__bemessungsgrundlage_selbständig_m * (
        beitragssatz * 2
    )


@policy_function(start_date="2005-01-01", leaf_name="betrag_selbständig_m")
def betrag_selbständig_zusatz_kinderlos_dummy_m(
    sozialversicherung__kranken__beitrag__bemessungsgrundlage_selbständig_m: float,
    beitragssatz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Self-employed individuals' long-term care insurance contribution since 2005.

    Self-employed pay the full contribution (employer + employee), which is either
    assessed on their self-employement income or 3/4 of the 'Bezugsgröße'

    Parameters
    ----------

    sozialversicherung__kranken__beitrag__bemessungsgrundlage_selbständig_m
        See         :func:`sozialversicherung__kranken__beitrag__bemessungsgrundlage_selbständig_m`.

    beitragssatz
        See :func:`beitragssatz`.

    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Self-employed long-term care insurance contributions.

    """
    return sozialversicherung__kranken__beitrag__bemessungsgrundlage_selbständig_m * (
        beitragssatz + sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )


@policy_function(
    start_date="1995-01-01",
    end_date="2004-03-31",
    leaf_name="betrag_rentner_m",
)
def betrag_rentner_reduz_beitrag_m(
    sozialversicherung__kranken__beitrag__bemessungsgrundlage_rente_m: float,
    beitragssatz: float,
) -> float:
    """Long-term care insurance contribution from pension income from 1995 until March
    2004.

    Pensioners pay the same contribution as employees.

    Parameters
    ----------
    sozialversicherung__kranken__beitrag__bemessungsgrundlage_rente_m
        See :func:`sozialversicherung__kranken__beitrag__bemessungsgrundlage_rente_m`.
    beitragssatz
        See :func:`beitragssatz`.

    Returns
    -------
    Retiree's long-term care insurance contributions.

    """
    return (
        sozialversicherung__kranken__beitrag__bemessungsgrundlage_rente_m * beitragssatz
    )


@policy_function(
    start_date="2004-04-01",
    end_date="2004-12-31",
    leaf_name="betrag_rentner_m",
)
def betrag_rentner_ohne_zusatz_für_kinderlose_m(
    sozialversicherung__kranken__beitrag__bemessungsgrundlage_rente_m: float,
    beitragssatz: float,
) -> float:
    """Health insurance contribution from pension income from April until December 2004.

    Pensioners pay twice the contribution of employees.

    Parameters
    ----------
    sozialversicherung__kranken__beitrag__bemessungsgrundlage_rente_m
        See :func:`sozialversicherung__kranken__beitrag__bemessungsgrundlage_rente_m`.
    beitragssatz
        See :func:`beitragssatz`.

    Returns
    -------
    Retiree's long-term care insurance contributions.

    """
    return sozialversicherung__kranken__beitrag__bemessungsgrundlage_rente_m * (
        beitragssatz * 2
    )


@policy_function(start_date="2005-01-01", leaf_name="betrag_rentner_m")
def betrag_rentner_zusatz_kinderlos_dummy_m(
    sozialversicherung__kranken__beitrag__bemessungsgrundlage_rente_m: float,
    beitragssatz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Health insurance contribution from pension income since 2005.

    Pensioners pay twice the contribution of employees, but only once the additional
    charge for childless individuals.

    Parameters
    ----------
    sozialversicherung__kranken__beitrag__bemessungsgrundlage_rente_m
        See :func:`sozialversicherung__kranken__beitrag__bemessungsgrundlage_rente_m`.
    beitragssatz
        See :func:`beitragssatz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Retiree's long-term care insurance contributions.

    """
    return sozialversicherung__kranken__beitrag__bemessungsgrundlage_rente_m * (
        beitragssatz + sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )


@policy_function(
    start_date="2003-04-01",
    end_date="2004-12-31",
    leaf_name="betrag_gesamt_m",
)
def betrag_gesamt_bis_2004_m(
    sozialversicherung__midijob_bemessungsentgelt_m: float,
    beitragssatz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Sum of employee and employer long-term care insurance contributions until 2004.

    Parameters
    ----------
    sozialversicherung__midijob_bemessungsentgelt_m
        See :func:`sozialversicherung__midijob_bemessungsentgelt_m`.
    beitragssatz
        See :func:`beitragssatz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Long-term care insurance contributions of employer and employee.


    """

    return sozialversicherung__midijob_bemessungsentgelt_m * (
        beitragssatz + sozialv_beitr_params["beitr_satz"]["ges_pflegev"]
    )


@policy_function(
    start_date="2005-01-01",
    leaf_name="betrag_gesamt_m",
)
def betrag_gesamty_ab_2005_m(
    sozialversicherung__midijob_bemessungsentgelt_m: float,
    beitragssatz: float,
    sozialv_beitr_params: dict,
) -> float:
    """Sum of employee and employer long-term care insurance contributions since 2005.

    Parameters
    ----------
    sozialversicherung__midijob_bemessungsentgelt_m
        See :func:`sozialversicherung__midijob_bemessungsentgelt_m`.
    beitragssatz
        See         :func:`beitragssatz`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Long-term care insurance contributions of employer and employee.

    """

    return sozialversicherung__midijob_bemessungsentgelt_m * (
        beitragssatz + sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )


@policy_function(
    end_date="2004-12-31",
    leaf_name="betrag_arbeitgeber_midijob_m",
)
def betrag_arbeitgeber_midijob_anteil_bruttolohn_bis_2004_m(
    einkommen__bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employer's long-term care insurance contribution until December 2004.

    Parameters
    ----------
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.


    Returns
    -------
    Employer's long-term care insurance contributions.


    """

    out = einkommen__bruttolohn_m * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]

    return out


@policy_function(
    start_date="2005-01-01",
    end_date="2022-09-30",
    leaf_name="betrag_arbeitgeber_midijob_m",
)
def betrag_arbeitgeber_midijob_anteil_bruttolohn_ab_2005_m(
    einkommen__bruttolohn_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employers' contribution to long-term care insurance between 2005 and September
    2022.

    Parameters
    ----------
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.


    Returns
    -------
    Employer's long-term care insurance contributions.

    """
    out = (
        einkommen__bruttolohn_m
        * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )
    return out


@policy_function(start_date="2022-10-01", leaf_name="betrag_arbeitgeber_midijob_m")
def betrag_arbeitgeber_midijob_residuum_m(
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
    leaf_name="betrag_arbeitnehmer_midijob_m",
)
def betrag_arbeitnehmer_midijob_residuum_m(
    betrag_arbeitgeber_midijob_m: float,
    betrag_gesamt_m: float,
) -> float:
    """Employee's long-term care insurance contribution for Midijobs
    until September 2022.

    Parameters
    ----------
    betrag_arbeitgeber_midijob_m
        See :func:`betrag_arbeitgeber_midijob_m`.
    betrag_gesamt_m
        See :func:`betrag_gesamt_m`.

    Returns
    -------
    Employee's long-term care insurance contributions.

    """
    out = betrag_gesamt_m - betrag_arbeitgeber_midijob_m

    return out


@policy_function(
    start_date="2022-10-01",
    end_date="2023-06-30",
    leaf_name="betrag_arbeitnehmer_midijob_m",
)
def betrag_arbeitnehmer_midijob_anteil_beitragspflichtiger_einnahmen_m(
    beitragssatz__zusatzbetrag_kinderlos: bool,
    sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m: float,
    sozialversicherung__midijob_bemessungsentgelt_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's long-term care insurance contribution between October 2022 and
    June 2023.

    Parameters
    ----------
    beitragssatz__zusatzbetrag_kinderlos
        See         :func:`beitragssatz__zusatzbetrag_kinderlos`.
    sozialversicherung__midijob_bemessungsentgelt_m
        See :func:`sozialversicherung__midijob_bemessungsentgelt_m`.
    sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m
        See :func:`sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Employee's long-term care insurance contributions.

    """
    # Calculate the employee care insurance contribution
    an_beitr_midijob_m = (
        sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m
        * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]
    )

    # Add additional contribution for childless individuals
    if beitragssatz__zusatzbetrag_kinderlos:
        an_beitr_midijob_m += (
            sozialversicherung__midijob_bemessungsentgelt_m
            * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    return an_beitr_midijob_m


@policy_function(start_date="2023-07-01", leaf_name="betrag_arbeitnehmer_midijob_m")
def betrag_arbeitnehmer_midijob_anteil_mit_kinder_abschlag_m(
    anzahl_kinder_bis_24: int,
    beitragssatz__zusatzbetrag_kinderlos: bool,
    sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m: float,
    sozialversicherung__midijob_bemessungsentgelt_m: float,
    sozialv_beitr_params: dict,
) -> float:
    """Employee's long-term care insurance contribution since July 2023.

    Parameters
    ----------
    anzahl_kinder_bis_24
        See :func:`anzahl_kinder_bis_24`.
    beitragssatz__zusatzbetrag_kinderlos
        See :func:`beitragssatz__zusatzbetrag_kinderlos`.
    sozialversicherung__midijob_bemessungsentgelt_m
        See :func:`sozialversicherung__midijob_bemessungsentgelt_m`.
    sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m
        See :func:`sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Employee's long-term care insurance contributions.

    """
    # Calculate the employee care insurance rate
    ges_pflegev_rate = sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["standard"]

    # Reduced contribution for individuals with two or more children under 25
    if anzahl_kinder_bis_24 >= 2:
        ges_pflegev_rate -= sozialv_beitr_params["beitr_satz"]["ges_pflegev"][
            "abschlag_kinder"
        ] * min(anzahl_kinder_bis_24 - 1, 4)

    # Calculate the employee care insurance contribution
    an_beitr_midijob_m = (
        sozialversicherung__beitragspflichtige_einnahmen_aus_midijob_arbeitnehmer_m
        * ges_pflegev_rate
    )

    # Add additional contribution for childless individuals
    if beitragssatz__zusatzbetrag_kinderlos:
        an_beitr_midijob_m += (
            sozialversicherung__midijob_bemessungsentgelt_m
            * sozialv_beitr_params["beitr_satz"]["ges_pflegev"]["zusatz_kinderlos"]
        )

    return an_beitr_midijob_m
