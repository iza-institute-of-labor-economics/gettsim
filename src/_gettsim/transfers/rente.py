from _gettsim.shared import policy_info


def sum_ges_rente_priv_rente_m(priv_rente_m: float, ges_rente_m: float) -> float:
    """Calculate total individual pension as sum of private and public pension.

    Parameters
    ----------
    priv_rente_m
        See basic input variable :ref:`priv_rente_m <priv_rente_m>`.
    ges_rente_m
        See :func:`ges_rente_m`.

    Returns
    -------

    """
    out = priv_rente_m + ges_rente_m
    return out


@policy_info(end_date="2020-12-31")
def ges_rente_m(bruttorente_m: float, rentner: bool) -> float:
    return bruttorente_m if rentner else 0.0


@policy_info(
    start_date="2021-01-01",
    params_key_for_rounding="ges_rente",
    name_in_dag="ges_rente_m",
)
def ges_rente_mit_grundrente_m(
    bruttorente_m: float,
    grundr_zuschlag_m: float,
    rentner: bool,
) -> float:
    """Calculate total individual public pension including Grundrentenzuschlag.

    Parameters
    ----------
    bruttorente_m
        See :func:`bruttorente_m`.
    grundr_zuschlag_m
        See :func:`grundr_zuschlag_m`.
    rentner
        See basic input variable :ref:`rentner <rentner>`.

    Returns
    -------

    """
    out = bruttorente_m + grundr_zuschlag_m if rentner else 0.0
    return out


@policy_info(
    end_date="2016-12-31",
    name_in_dag="bruttorente_m",
    params_key_for_rounding="ges_rente",
)
def bruttorente_mit_harter_hinzuverdienstgrenze_m(
    alter: int,
    ges_rente_regelaltersgrenze: float,
    bruttolohn_y: float,
    bruttorente_basisbetrag_m: float,
    ges_rente_params: dict,
) -> float:
    """Pension benefits after earnings test for early retirees.

    If earnings are above an earnings limit, the pension is fully deducted.

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    bruttolohn_y
        See basic input variable :ref:`bruttolohn_y <bruttolohn_y>`.
    bruttorente_basisbetrag_m
        See :func:`bruttorente_basisbetrag_m`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """
    # TODO (@MImmesberger): Use age with monthly precision.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/781
    if (alter >= ges_rente_regelaltersgrenze) or (
        bruttolohn_y <= ges_rente_params["hinzuverdienstgrenze"]
    ):
        out = bruttorente_basisbetrag_m
    else:
        out = 0.0

    return out


@policy_info(
    start_date="2017-01-01",
    end_date="2022-12-31",
    name_in_dag="bruttorente_m",
    params_key_for_rounding="ges_rente",
)
def bruttorente_mit_hinzuverdienstdeckel_m(
    alter: int,
    ges_rente_regelaltersgrenze: float,
    bruttolohn_y: float,
    _differenz_bruttolohn_hinzuverdienstdeckel_m: float,
    _ges_rente_zahlbetrag_ohne_deckel_m: float,
) -> float:
    """Pension benefits after earnings test for early retirees.

    If sum of earnings and pension is larger than the highest income in the last 15
    years, the pension is fully deducted (Hinzuverdienstdeckel).

    Parameters
    ----------
    alter
        See basic input variable :ref:`alter <alter>`.
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    bruttolohn_y
        See basic input variable :ref:`bruttolohn_y <bruttolohn_y>`.
    _differenz_bruttolohn_hinzuverdienstdeckel_m
        See :func:`_differenz_bruttolohn_hinzuverdienstdeckel_m`.
    _ges_rente_zahlbetrag_ohne_deckel_m
        See :func:`_ges_rente_zahlbetrag_ohne_deckel_m`.

    Returns
    -------

    """
    # TODO (@MImmesberger): Use age with monthly precision.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/781
    if (
        _differenz_bruttolohn_hinzuverdienstdeckel_m > 0
        and alter <= ges_rente_regelaltersgrenze
        and bruttolohn_y > 0
    ):
        out = max(
            _ges_rente_zahlbetrag_ohne_deckel_m
            - _differenz_bruttolohn_hinzuverdienstdeckel_m,
            0.0,
        )
    else:
        out = _ges_rente_zahlbetrag_ohne_deckel_m

    return out


@policy_info(
    start_date="2017-01-01",
    end_date="2022-12-31",
)
def _ges_rente_zahlbetrag_ohne_deckel_m(
    bruttolohn_y: float,
    alter: int,
    ges_rente_regelaltersgrenze: float,
    bruttorente_basisbetrag_m: float,
    _differenz_bruttolohn_hinzuverdienstgrenze_m: float,
    ges_rente_params: dict,
) -> float:
    """Pension benefits after earnings test without accounting for the earnings cap
    (Hinzuverdienstdeckel).

    Parameters
    ----------
    bruttolohn_y
        See basic input variable :ref:`bruttolohn_y <bruttolohn_y>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    bruttorente_basisbetrag_m
        See :func:`bruttorente_basisbetrag_m`.
    _differenz_bruttolohn_hinzuverdienstgrenze_m
        See :func:`_differenz_bruttolohn_hinzuverdienstgrenze_m`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """
    # TODO (@MImmesberger): Use age with monthly precision.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/781
    # No deduction because of age or low earnings
    if (alter >= ges_rente_regelaltersgrenze) or (
        bruttolohn_y <= ges_rente_params["hinzuverdienstgrenze"]
    ):
        out = bruttorente_basisbetrag_m
    # Basis deduction of 40%
    else:
        out = max(
            bruttorente_basisbetrag_m
            - ges_rente_params["abzugsrate_hinzuverdienst"]
            * _differenz_bruttolohn_hinzuverdienstgrenze_m,
            0.0,
        )

    return out


@policy_info(
    end_date="2016-12-31", name_in_dag="_differenz_bruttolohn_hinzuverdienstgrenze_y"
)
def _differenz_bruttolohn_monatliche_hinzuverdienstgrenze_y(
    bruttolohn_y: float,
    ges_rente_params: dict,
) -> float:
    """Earnings that are subject to pension deductions.

    Earnings cap is denoted in law in terms of monthly wage.

    Parameters
    ----------
    bruttolohn_y
        See basic input variable :ref:`bruttolohn_y <bruttolohn_y>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """
    return max(bruttolohn_y - ges_rente_params["hinzuverdienstgrenze"] * 12, 0.0)


@policy_info(
    start_date="2017-01-01",
    end_date="2022-12-31",
    name_in_dag="_differenz_bruttolohn_hinzuverdienstgrenze_y",
)
def _differenz_bruttolohn_jährliche_hinzuverdienstgrenze_y(
    bruttolohn_y: float,
    ges_rente_params: dict,
) -> float:
    """Earnings that are subject to pension deductions.

    Earnings cap is denoted in law in terms of yearly wage.

    Parameters
    ----------
    bruttolohn_y
        See basic input variable :ref:`bruttolohn_y <bruttolohn_y>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """
    return max(bruttolohn_y - ges_rente_params["hinzuverdienstgrenze"], 0.0)


@policy_info(
    start_date="2017-01-01",
    end_date="2022-12-31",
)
def _differenz_bruttolohn_hinzuverdienstdeckel_y(
    bruttolohn_y: float,
    _ges_rente_zahlbetrag_ohne_deckel_y: float,
    höchster_bruttolohn_letzte_15_jahre_vor_rente_y: float,
) -> float:
    """Income above the earnings cap (Hinzuverdienstdeckel).

    Parameters
    ----------
    bruttolohn_y
        See basic input variable :ref:`bruttolohn_y <bruttolohn_y>`.
    _ges_rente_zahlbetrag_ohne_deckel_y
        See :func:`_ges_rente_zahlbetrag_ohne_deckel_y`.
    höchster_bruttolohn_letzte_15_jahre_vor_rente_y
        See basic input variable :ref:`höchster_bruttolohn_letzte_15_jahre_vor_rente_y
        <höchster_bruttolohn_letzte_15_jahre_vor_rente_y>`.

    Returns
    -------

    """
    return max(
        _ges_rente_zahlbetrag_ohne_deckel_y
        + bruttolohn_y
        - höchster_bruttolohn_letzte_15_jahre_vor_rente_y,
        0.0,
    )


@policy_info(
    start_date="2023-01-01",
    name_in_dag="bruttorente_m",
    params_key_for_rounding="ges_rente",
)
def bruttorente_ohne_einkommensanrechnung_m(
    bruttorente_basisbetrag_m: float,
) -> float:
    """Public pension claim before Grundrentenzuschlag.

    Parameters
    ----------
    bruttorente_basisbetrag_m
        See :func:`bruttorente_basisbetrag_m`.

    Returns
    -------

    """
    return bruttorente_basisbetrag_m


@policy_info(start_date="1992-01-01")
def bruttorente_basisbetrag_m(
    ges_rente_zugangsfaktor: float,
    entgeltp_ost: float,
    entgeltp_west: float,
    rentner: bool,
    ges_rente_params: dict,
) -> float:
    """Old-Age Pensions claim. The function follows the following equation:

    .. math::

        R = EP * ZF * Rw

    models 'Rentenformel':
    https://de.wikipedia.org/wiki/Rentenformel
    https://de.wikipedia.org/wiki/Rentenanpassungsformel


    Parameters
    ----------
    ges_rente_zugangsfaktor
        See :func:`ges_rente_zugangsfaktor`.
    entgeltp_ost
        See :func:`entgeltp_ost`.
    entgeltp_west
        See :func:`entgeltp_west`.
    rentner
        See basic input variable :ref:`rentner <rentner>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """

    if rentner:
        out = (
            entgeltp_west * ges_rente_params["rentenwert"]["west"]
            + entgeltp_ost * ges_rente_params["rentenwert"]["ost"]
        ) * ges_rente_zugangsfaktor
    else:
        out = 0.0

    return out


def rentenwert(wohnort_ost: bool, ges_rente_params: dict) -> float:
    """Select the rentenwert depending on place of living.

    Parameters
    ----------
    wohnort_ost
        See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """
    params = ges_rente_params["rentenwert"]

    out = params["ost"] if wohnort_ost else params["west"]

    return float(out)


def entgeltp_west_updated(
    wohnort_ost: bool, entgeltp_west: float, entgeltp_update_lohn: float
) -> float:
    """Update western earning points.

    Given earnings, social insurance rules, average
    earnings in a particular year and potentially other
    variables (e.g., benefits for raising children,
    informal care), return the new earnings points.

    Parameters
    ----------
    wohnort_ost
        See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
    entgeltp_west
        See basic input variable :ref:`ententgeltp_westgeltp <entgeltp_west>`.
    entgeltp_update_lohn
        See :func:`entgeltp_update_lohn`.

    Returns
    -------

    """
    if wohnort_ost:
        out = entgeltp_west
    else:
        out = entgeltp_west + entgeltp_update_lohn
    return out


def entgeltp_ost_updated(
    wohnort_ost: bool, entgeltp_ost: float, entgeltp_update_lohn: float
) -> float:
    """Update eastern earning points.

    Given earnings, social insurance rules, average
    earnings in a particular year and potentially other
    variables (e.g., benefits for raising children,
    informal care), return the new earnings points.

    Parameters
    ----------
    wohnort_ost
        See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
    entgeltp_ost
        See basic input variable :ref:`entgeltp_ost <entgeltp_ost>`.
    entgeltp_update_lohn
        See :func:`entgeltp_update_lohn`.

    Returns
    -------

    """
    if wohnort_ost:
        out = entgeltp_ost + entgeltp_update_lohn
    else:
        out = entgeltp_ost
    return out


def entgeltp_update_lohn(
    bruttolohn_m: float,
    wohnort_ost: bool,
    _ges_rentenv_beitr_bemess_grenze_m: float,
    ges_rente_params: dict,
) -> float:
    """Return earning points for the wages earned in the last year.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    wohnort_ost
        See :func:`wohnort_ost`.
    _ges_rentenv_beitr_bemess_grenze_m
        See :func:`_ges_rentenv_beitr_bemess_grenze_m`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.
    Returns
    -------

    """

    # Scale bruttolohn up if earned in eastern Germany
    if wohnort_ost:
        bruttolohn_scaled_east = (
            bruttolohn_m * ges_rente_params["umrechnung_entgeltp_beitrittsgebiet"]
        )
    else:
        bruttolohn_scaled_east = bruttolohn_m

    # Calculate the (scaled) wage, which is subject to pension contributions.
    if bruttolohn_scaled_east > _ges_rentenv_beitr_bemess_grenze_m:
        bruttolohn_scaled_rentenv = _ges_rentenv_beitr_bemess_grenze_m
    else:
        bruttolohn_scaled_rentenv = bruttolohn_scaled_east

    # Calculate monthly mean wage in Germany
    durchschnittslohn_m = (1 / 12) * ges_rente_params[
        "beitragspflichtiges_durchschnittsentgelt"
    ]

    out = bruttolohn_scaled_rentenv / durchschnittslohn_m
    return out


def ges_rente_zugangsfaktor(  # noqa: PLR0913
    age_of_retirement: float,
    ges_rente_regelaltersgrenze: float,
    referenzalter_abschlag: float,
    _ges_rente_altersgrenze_abschlagsfrei: float,
    _ges_rente_altersgrenze_vorzeitig: float,
    ges_rente_vorauss_vorzeitig: bool,
    ges_rente_vorauss_regelrente: bool,
    ges_rente_params: dict,
) -> float:
    """Zugangsfaktor (pension adjustment factor).

    Factor by which the pension claim is multiplied to calculate the pension payment.
    The Zugangsfaktor is larger than 1 if the agent retires after the normal retirement
    age (NRA) and smaller than 1 if the agent retires earlier than the full retirement
    age (FRA).

    At the regelaltersgrenze - normal retirement age (NRA), the agent is allowed to get
    pensions with his full claim. In general, if the agent retires earlier or later, the
    Zugangsfaktor and therefore the pension claim is higher or lower. The Zugangsfaktor
    is 1.0 in [FRA, NRA].

    Legal reference: § 77 Abs. 2 Nr. 2 SGB VI

    Since pension payments of the GRV always start at 1st day of month, day of birth
    within month does not matter. The eligibility always starts in the month after
    reaching the required age.

    Returns 0 of the person is not eligible for receiving pension benefits because
    either i) the person is younger than the earliest possible retirement age or ii) the
    person is not eligible for pension benefits because `ges_rente_vorauss_regelrente`
    is False.

    Parameters
    ----------
    age_of_retirement
        See :func:`age_of_retirement`.
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    referenzalter_abschlag
        See :func:`referenzalter_abschlag`.
    _ges_rente_altersgrenze_abschlagsfrei
        See :func:`_ges_rente_altersgrenze_abschlagsfrei`.
    _ges_rente_altersgrenze_vorzeitig
        See :func:`_ges_rente_altersgrenze_vorzeitig`.
    ges_rente_vorauss_vorzeitig
        See :func:`ges_rente_vorauss_vorzeitig`.
    ges_rente_vorauss_regelrente
        See :func:`ges_rente_vorauss_regelrente`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Zugangsfaktor

    """

    if ges_rente_vorauss_regelrente:
        # Early retirement (before full retirement age): Zugangsfaktor < 1
        if age_of_retirement < _ges_rente_altersgrenze_abschlagsfrei:  # [ERA,FRA)
            if ges_rente_vorauss_vorzeitig and (
                age_of_retirement >= _ges_rente_altersgrenze_vorzeitig
            ):
                # Calc difference to FRA of pensions with early retirement options
                # (Altersgrenze langjährig Versicherte, Altersrente für Frauen
                # /Arbeitslose).
                # checks whether older than possible era
                out = (
                    1
                    + (age_of_retirement - referenzalter_abschlag)
                    * ges_rente_params["zugangsfaktor_veränderung_pro_jahr"][
                        "vorzeitiger_renteneintritt"
                    ]
                )
            else:
                # Early retirement although not eligible to do so.
                out = 0.0

        # Late retirement (after normal retirement age/Regelaltersgrenze):
        # Zugangsfaktor > 1
        elif age_of_retirement > ges_rente_regelaltersgrenze:
            out = (
                1
                + (age_of_retirement - ges_rente_regelaltersgrenze)
                * ges_rente_params["zugangsfaktor_veränderung_pro_jahr"][
                    "späterer_renteneintritt"
                ]
            )

        # Retirement between full retirement age and normal retirement age:
        else:  # [FRA,NRA]
            out = 1.0

    # Claiming pension is not possible if ges_rente_vorauss_regelrente is 'False'.
    # Return 0 in this case. Then, the pension payment is 0 as well.
    else:
        out = 0.0

    out = max(out, 0.0)

    return out


def age_of_retirement(
    jahr_renteneintr: int,
    monat_renteneintr: int,
    geburtsjahr: int,
    geburtsmonat: int,
) -> float:
    """Age at retirement in monthly precision.

    Calculates the age of person's retirement in monthly precision.
    As retirement is only possible at first day of month and as
    persons eligible for pension at first of month after reaching the
    age threshold (§ 99 SGB VI) persons who retire in same month will
    be considered a month too young: Substraction of 1/12.


    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    jahr_renteneintr
        See basic input variable :ref:`jahr_renteneintr <jahr_renteneintr>`.
    monat_renteneintr
        See basic input variable :ref:`monat_renteneintr <monat_renteneintr>`.

    Returns
    -------
    Age at retirement.

    """
    return jahr_renteneintr - geburtsjahr + (monat_renteneintr - geburtsmonat - 1) / 12


@policy_info(end_date="2011-12-31", name_in_dag="_ges_rente_altersgrenze_abschlagsfrei")
def _ges_rente_altersgrenze_abschlagsfrei_ohne_besond_langj(
    ges_rente_regelaltersgrenze: float,
    _ges_rente_frauen_altersgrenze: float,
    _ges_rente_langj_altersgrenze: float,
    _ges_rente_arbeitsl_altersgrenze: float,
    ges_rente_vorauss_frauen: bool,
    ges_rente_vorauss_langj: bool,
    ges_rente_vorauss_arbeitsl: bool,
) -> float:
    """Full retirement age after eligibility checks, assuming eligibility for
    Regelaltersrente.

    Age at which pension can be claimed without deductions. This age is smaller or equal
    to the normal retirement age (FRA<=NRA) and depends on personal characteristics as
    gender, insurance duration, health/disability, employment status.

    Parameters
    ----------
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    _ges_rente_frauen_altersgrenze
        See :func:`_ges_rente_frauen_altersgrenze`.
    _ges_rente_langj_altersgrenze
        See :func:`_ges_rente_langj_altersgrenze`.
    _ges_rente_arbeitsl_altersgrenze
         See :func:`_ges_rente_arbeitsl_altersgrenze`.
    ges_rente_vorauss_frauen
        See :func:`ges_rente_vorauss_frauen`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    ges_rente_vorauss_arbeitsl:
        See :func:`ges_rente_vorauss_arbeitsl`.
    Returns
    -------
    Full retirement age.

    """

    out = ges_rente_regelaltersgrenze
    if ges_rente_vorauss_frauen:
        out = min([out, _ges_rente_frauen_altersgrenze])
    if ges_rente_vorauss_arbeitsl:
        out = min([out, _ges_rente_arbeitsl_altersgrenze])
    if ges_rente_vorauss_langj:
        out = min([out, _ges_rente_langj_altersgrenze])

    return out


@policy_info(
    start_date="2012-01-01",
    end_date="2017-12-31",
    name_in_dag="_ges_rente_altersgrenze_abschlagsfrei",
)
def _ges_rente_altersgrenze_abschlagsfrei_mit_besond_langj(
    ges_rente_regelaltersgrenze: float,
    _ges_rente_frauen_altersgrenze: float,
    _ges_rente_langj_altersgrenze: float,
    _ges_rente_besond_langj_altersgrenze: float,
    _ges_rente_arbeitsl_altersgrenze: float,
    ges_rente_vorauss_frauen: bool,
    ges_rente_vorauss_langj: bool,
    ges_rente_vorauss_besond_langj: bool,
    ges_rente_vorauss_arbeitsl: bool,
) -> float:
    """Full retirement age after eligibility checks, assuming eligibility for
    Regelaltersrente.

    Age at which pension can be claimed without deductions. This age is smaller or equal
    to the normal retirement age (FRA<=NRA) and depends on personal characteristics as
    gender, insurance duration, health/disability, employment status.

    Starting in 2012, the pension for the very long term insured (Altersrente für
    besonders langjährig Versicherte) is introduced. Policy becomes inactive in 2018
    because then all potential beneficiaries of the Rente wg. Arbeitslosigkeit and
    Rente für Frauen have reached the normal retirement age.

    Parameters
    ----------
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    _ges_rente_frauen_altersgrenze
        See :func:`_ges_rente_frauen_altersgrenze`.
    _ges_rente_langj_altersgrenze
        See :func:`_ges_rente_langj_altersgrenze`.
    _ges_rente_besond_langj_altersgrenze
        See :func:`_ges_rente_besond_langj_altersgrenze`.
    _ges_rente_arbeitsl_altersgrenze
        See :func:`_ges_rente_arbeitsl_altersgrenze`.
    ges_rente_vorauss_frauen
        See :func:`ges_rente_vorauss_frauen`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    ges_rente_vorauss_besond_langj
        See :func:`ges_rente_vorauss_besond_langj`.
    ges_rente_vorauss_arbeitsl
        See :func:`ges_rente_vorauss_arbeitsl`.

    Returns
    -------
    Full retirement age.

    """

    out = ges_rente_regelaltersgrenze
    if ges_rente_vorauss_frauen:
        out = min([out, _ges_rente_frauen_altersgrenze])
    if ges_rente_vorauss_arbeitsl:
        out = min([out, _ges_rente_arbeitsl_altersgrenze])
    if ges_rente_vorauss_langj:
        out = min([out, _ges_rente_langj_altersgrenze])
    if ges_rente_vorauss_besond_langj:
        out = min([out, _ges_rente_besond_langj_altersgrenze])

    return out


@policy_info(
    start_date="2018-01-01", name_in_dag="_ges_rente_altersgrenze_abschlagsfrei"
)
def _ges_rente_altersgrenze_abschlagsfrei_ohne_arbeitsl_frauen(
    ges_rente_regelaltersgrenze: float,
    _ges_rente_langj_altersgrenze: float,
    _ges_rente_besond_langj_altersgrenze: float,
    ges_rente_vorauss_langj: bool,
    ges_rente_vorauss_besond_langj: bool,
) -> float:
    """Full retirement age after eligibility checks, assuming eligibility for
    Regelaltersrente.

    Age at which pension can be claimed without deductions. This age is smaller or equal
    to the normal retirement age (FRA<=NRA) and depends on personal characteristics as
    gender, insurance duration, health/disability, employment status.

    Parameters
    ----------
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    _ges_rente_langj_altersgrenze
        See :func:`_ges_rente_langj_altersgrenze`.
    _ges_rente_besond_langj_altersgrenze
        See :func:`_ges_rente_besond_langj_altersgrenze`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    ges_rente_vorauss_besond_langj
        See :func:`ges_rente_vorauss_besond_langj`.

    Returns
    -------
    Full retirement age.

    """

    out = ges_rente_regelaltersgrenze
    if ges_rente_vorauss_langj:
        out = min([out, _ges_rente_langj_altersgrenze])
    if ges_rente_vorauss_besond_langj:
        out = min([out, _ges_rente_besond_langj_altersgrenze])

    return out


@policy_info(end_date="2017-12-31", name_in_dag="referenzalter_abschlag")
def _referenzalter_abschlag_mit_rente_arbeitsl_frauen(
    ges_rente_regelaltersgrenze: float,
    _ges_rente_frauen_altersgrenze: float,
    _ges_rente_langj_altersgrenze: float,
    _ges_rente_arbeitsl_altersgrenze: float,
    ges_rente_vorauss_frauen: bool,
    ges_rente_vorauss_langj: bool,
    ges_rente_vorauss_arbeitsl: bool,
) -> float:
    """Reference age for deduction calculation in case of early retirement
    (Zugangsfaktor).

    Normal retirement age if not eligible for early retirement. Policy becomes inactive
    in 2018 because then all potential beneficiaries of the Rente wg. Arbeitslosigkeit
    and Rente für Frauen have reached the normal retirement age.

    Parameters
    ----------
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    _ges_rente_frauen_altersgrenze
        See :func:`_ges_rente_frauen_altersgrenze`.
    _ges_rente_langj_altersgrenze
        See :func:`_ges_rente_langj_altersgrenze`.
    _ges_rente_arbeitsl_altersgrenze
        See :func:`_ges_rente_arbeitsl_altersgrenze`.
    ges_rente_vorauss_frauen
        See :func:`ges_rente_vorauss_frauen`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    ges_rente_vorauss_arbeitsl
        See :func:`ges_rente_vorauss_arbeitsl`.

     Returns
    -------
    Reference age for deduction calculation.

    """
    if (
        ges_rente_vorauss_langj
        and ges_rente_vorauss_frauen
        and ges_rente_vorauss_arbeitsl
    ):
        out = min(
            [
                _ges_rente_frauen_altersgrenze,
                _ges_rente_langj_altersgrenze,
                _ges_rente_arbeitsl_altersgrenze,
            ]
        )
    elif ges_rente_vorauss_langj and ges_rente_vorauss_frauen:
        out = min([_ges_rente_frauen_altersgrenze, _ges_rente_langj_altersgrenze])
    elif ges_rente_vorauss_langj and ges_rente_vorauss_arbeitsl:
        out = min([_ges_rente_langj_altersgrenze, _ges_rente_arbeitsl_altersgrenze])
    elif ges_rente_vorauss_langj:
        out = _ges_rente_langj_altersgrenze
    elif ges_rente_vorauss_frauen:
        out = _ges_rente_frauen_altersgrenze
    elif ges_rente_vorauss_arbeitsl:
        out = _ges_rente_arbeitsl_altersgrenze
    else:
        out = ges_rente_regelaltersgrenze

    return out


@policy_info(start_date="2018-01-01", name_in_dag="referenzalter_abschlag")
def _referenzalter_abschlag_ohne_rente_arbeitsl_frauen(
    ges_rente_regelaltersgrenze: float,
    _ges_rente_langj_altersgrenze: float,
    ges_rente_vorauss_langj: bool,
) -> float:
    """Reference age for deduction calculation in case of early retirement
    (Zugangsfaktor).

    Normal retirement age if not eligible for early retirement.

    Parameters
    ----------
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    _ges_rente_langj_altersgrenze
        See :func:`_ges_rente_langj_altersgrenze`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.

     Returns
    -------
    Reference age for deduction calculation.

    """
    if ges_rente_vorauss_langj:
        out = _ges_rente_langj_altersgrenze
    else:
        out = ges_rente_regelaltersgrenze

    return out


@policy_info(end_date="2007-04-19", name_in_dag="ges_rente_regelaltersgrenze")
def ges_rente_regelaltersgrenze_ohne_staffelung(
    geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """Normal retirement age (NRA).

    NRA is the same for every birth cohort.

    The Regelaltersrente cannot be claimed earlier than at the NRA, i.e. the NRA does
    not serve as reference for calculating deductions. However, it serves as reference
    for calculating gains in the Zugangsfakor in case of later retirement.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.


    Returns
    -------
    Normal retirement age (NRA).

    """
    # TODO(@MImmesberger): Remove fake dependency (geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["regelaltersgrenze"]


@policy_info(start_date="2007-04-20", name_in_dag="ges_rente_regelaltersgrenze")
def ges_rente_regelaltersgrenze_mit_staffelung(
    geburtsjahr: int, ges_rente_params: dict
) -> float:
    """Normal retirement age (NRA).

    NRA differs by birth cohort.

    The Regelaltersrente cannot be claimed earlier than at the NRA, i.e. the NRA does
    not serve as reference for calculating deductions. However, it serves as reference
    for calculating gains in the Zugangsfakor in case of later retirement.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.


    Returns
    -------
    Normal retirement age (NRA).

    """
    if geburtsjahr <= ges_rente_params["regelaltersgrenze"]["max_birthyear_old_regime"]:
        out = ges_rente_params["regelaltersgrenze"]["entry_age_old_regime"]
    elif (
        geburtsjahr >= ges_rente_params["regelaltersgrenze"]["min_birthyear_new_regime"]
    ):
        out = ges_rente_params["regelaltersgrenze"]["entry_age_new_regime"]
    else:
        out = ges_rente_params["regelaltersgrenze"][geburtsjahr]

    return out


@policy_info(end_date="1989-12-17", name_in_dag="_ges_rente_frauen_altersgrenze")
def ges_rente_frauen_altersgrenze_ohne_staffelung(
    geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """Full retirement age (FRA) for women.

    FRA is the same for each birth cohort.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age for women.

    """
    # TODO(@MImmesberger): Remove fake dependency (geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_für_frauen_abschlagsfrei"]


@policy_info(start_date="1989-12-18", name_in_dag="_ges_rente_frauen_altersgrenze")
def ges_rente_frauen_altersgrenze_mit_staffelung(
    geburtsjahr: int,
    geburtsmonat: int,
    ges_rente_params: dict,
) -> float:
    """Full retirement age (FRA) for women.

    FRA differs by birth cohort.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age for women.

    """
    if (
        geburtsjahr
        <= ges_rente_params["altersgrenze_für_frauen_abschlagsfrei"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_für_frauen_abschlagsfrei"][
            "entry_age_old_regime"
        ]
    elif (
        geburtsjahr
        >= ges_rente_params["altersgrenze_für_frauen_abschlagsfrei"][
            "min_birthyear_new_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_für_frauen_abschlagsfrei"][
            "entry_age_new_regime"
        ]
    else:
        out = ges_rente_params["altersgrenze_für_frauen_abschlagsfrei"][geburtsjahr][
            geburtsmonat
        ]

    return out


@policy_info(end_date="2017-12-31")
def _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung(
    geburtsjahr: int,
    geburtsmonat: int,
    ges_rente_params: dict,
) -> float:
    """Full retirement age for unemployed without Vertrauensschutz.

    Full retirement age depends on birth year and month.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    ges_rente_params
        See params documentation
        :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age for unemployed.

    """
    if (
        geburtsjahr
        <= ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            "entry_age_old_regime"
        ]
    elif (
        geburtsjahr
        >= ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            "min_birthyear_new_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            "entry_age_new_regime"
        ]
    else:
        out = ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][geburtsjahr][
            geburtsmonat
        ]

    return out


@policy_info(end_date="1989-12-17", name_in_dag="_ges_rente_arbeitsl_altersgrenze")
def _ges_rente_arbeitsl_altersgrenze_ohne_staffelung(
    geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """Full retirement age for unemployed.

    Before the WFG (Gesetz für Wachstum und Beschäftigung) was implemented in 1997 the
    full retirement age was the same for every birth cohort.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    ges_rente_params
        See params documentation
        :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    lowest full retirement age for unemployed.

    """
    # TODO(@MImmesberger): Remove fake dependency (geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"]


@policy_info(
    start_date="1989-12-18",
    end_date="1996-07-28",
    name_in_dag="_ges_rente_arbeitsl_altersgrenze",
)
def _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung_bis_1996(
    _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung: float,
) -> float:
    """Full retirement age for unemployed without Vertrauensschutz.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung
        See :func:`_ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung`.

    Returns
    -------
    Full retirement age for unemployed.

    """
    return _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung


@policy_info(
    start_date="1996-07-29",
    end_date="2009-12-31",
    name_in_dag="_ges_rente_arbeitsl_altersgrenze",
)
def _ges_rente_arbeitsl_altersgrenze_mit_vertrauensschutzprüfung(
    geburtsjahr: int,
    geburtsmonat: int,
    vertra_arbeitsl_1997: bool,
    _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung: float,
    ges_rente_params: dict,
) -> float:
    """Full retirement age for unemployed with Vertrauensschutz.

    Full retirement age depends on birth year and month. Policy becomes inactive in 2010
    because then all potential beneficiaries have reached the normal retirement age.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    vertra_arbeitsl_1997
        See basic input variable :ref:`vertra_arbeitsl_1997 <vertra_arbeitsl_1997>`.
    _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung
        See :func:`_ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age for unemployed.

    """
    if (
        vertra_arbeitsl_1997
        and geburtsjahr
        <= ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"]["vertrauensschutz"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            "vertrauensschutz"
        ]["entry_age_old_regime"]

    elif vertra_arbeitsl_1997:
        out = ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
            "vertrauensschutz"
        ][geburtsjahr][geburtsmonat]
    else:
        out = _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung

    return out


@policy_info(
    start_date="2010-01-01",
    end_date="2017-12-31",
    name_in_dag="_ges_rente_arbeitsl_altersgrenze",
)
def _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung_ab_2010(
    _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung: float,
) -> float:
    """Full retirement age for unemployed without Vertrauensschutz.

    Full retirement age depends on birth year and month. Policy becomes inactive in 2017
    because then all potential beneficiaries have reached the normal retirement age.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung
        See :func:`_ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung`.

    Returns
    -------
    Full retirement age for unemployed.

    """
    return _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutzprüfung


@policy_info(end_date="1989-12-17", name_in_dag="_ges_rente_langj_altersgrenze")
def _ges_rente_langj_altersgrenze_ohne_staffelung(
    geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """
    Full retirement age (FRA) for long term insured.

    FRA is the same for each birth year.

    Calculate the age, at which a long term insured person (at least 35 years) is
    eligible to claim the full pension (without deductions). This pension scheme allows
    for early retirement (e.g. age 63) with deductions. Hence this threshold is needed
    as reference for calculating the zugangsfaktor.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age for long term insured.

    """
    # TODO(@MImmesberger): Remove fake dependency (geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"]


@policy_info(
    start_date="1989-12-18",
    end_date="2007-04-19",
    name_in_dag="_ges_rente_langj_altersgrenze",
)
def _ges_rente_langj_altersgrenze_mit_staffelung_nach_geburtsmonat(
    geburtsjahr: int,
    geburtsmonat: int,
    ges_rente_params: dict,
) -> float:
    """
    Full retirement age (FRA) for long term insured.

    FRA depends on birth year and month.

    Calculate the age, at which a long term insured person (at least 35 years) is
    eligible to claim the full pension (without deductions). This pension scheme allows
    for early retirement (e.g. age 63) with deductions. Hence this threshold is needed
    as reference for calculating the zugangsfaktor.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age (without deductions) for long term insured.
    """
    if (
        geburtsjahr
        <= ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            "entry_age_old_regime"
        ]
    elif (
        geburtsjahr
        >= ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            "min_birthyear_new_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            "entry_age_new_regime"
        ]
    else:
        out = ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            geburtsjahr
        ][geburtsmonat]

    return out


@policy_info(start_date="2007-04-20", name_in_dag="_ges_rente_langj_altersgrenze")
def _ges_rente_langj_altersgrenze_mit_staffelung_nach_geburtsjahr(
    geburtsjahr: int,
    geburtsmonat: int,
    ges_rente_params: dict,
) -> float:
    """
    Full retirement age (FRA) for long term insured.

    FRA depends on birth year.

    Calculate the age, at which a long term insured person (at least 35 years) is
    eligible to claim the full pension (without deductions). This pension scheme allows
    for early retirement (e.g. age 63) with deductions. Hence this threshold is needed
    as reference for calculating the zugangsfaktor.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age (without deductions) for long term insured.
    """
    if (
        geburtsjahr
        <= ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            "entry_age_old_regime"
        ]
    elif (
        geburtsjahr
        >= ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            "min_birthyear_new_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            "entry_age_new_regime"
        ]
    else:
        out = ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
            geburtsjahr
        ][geburtsmonat]

    return out


@policy_info(
    start_date="2012-01-01",
    end_date="2014-06-22",
    name_in_dag="_ges_rente_besond_langj_altersgrenze",
)
def _ges_rente_besond_langj_altersgrenze_ohne_staffelung(
    geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """
    Full retirement age (FRA) for very long term insured.

    FRA is the same for each birth year.

    Calculate the threshold from which very long term insured people (at least 45
    years) can claim their full pension without deductions.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age (without deductions) for very long term insured.

    """
    # TODO(@MImmesberger): Remove fake dependency (geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_besond_langj_versicherte"]


@policy_info(
    start_date="2014-06-23", name_in_dag="_ges_rente_besond_langj_altersgrenze"
)
def _ges_rente_besond_langj_altersgrenze_mit_staffelung(
    geburtsjahr: int,
    ges_rente_params: dict,
) -> float:
    """
    Full retirement age (FRA) for very long term insured.

    FRA depends on birth year and month.

    Calculate the threshold from which very long term insured people (at least 45
    years) can claim their full pension without deductions.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age (without deductions) for very long term insured.

    """
    if (
        geburtsjahr
        <= ges_rente_params["altersgrenze_besond_langj_versicherte"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_besond_langj_versicherte"][
            "entry_age_old_regime"
        ]
    elif (
        geburtsjahr
        >= ges_rente_params["altersgrenze_besond_langj_versicherte"][
            "min_birthyear_new_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_besond_langj_versicherte"][
            "entry_age_new_regime"
        ]
    else:
        out = ges_rente_params["altersgrenze_besond_langj_versicherte"][geburtsjahr]

    return out


@policy_info(end_date="2017-12-31", name_in_dag="_ges_rente_altersgrenze_vorzeitig")
def _ges_rente_altersgrenze_vorzeitig_mit_rente_arbeitsl_frauen(
    ges_rente_vorauss_frauen: bool,
    ges_rente_vorauss_langj: bool,
    ges_rente_vorauss_arbeitsl: bool,
    ges_rente_regelaltersgrenze: float,
    _ges_rente_frauen_altersgrenze_vorzeitig: float,
    _ges_rente_arbeitsl_vorzeitig: float,
    _ges_rente_langj_vorzeitig: float,
) -> float:
    """Earliest possible retirement age after checking for eligibility.

    Early retirement age depends on personal characteristics as gender, insurance
    duration, health/disability, employment status. Policy becomes inactive in 2018
    because then all potential beneficiaries of the Rente wg. Arbeitslosigkeit and Rente
    für Frauen have reached the normal retirement age.

    Parameters
    ----------
    ges_rente_vorauss_frauen
        See :func:`ges_rente_vorauss_frauen`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    ges_rente_vorauss_arbeitsl:
        See :func:`ges_rente_vorauss_arbeitsl`.
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    _ges_rente_frauen_altersgrenze_vorzeitig
        See :func:`_ges_rente_frauen_altersgrenze_vorzeitig`.
    _ges_rente_arbeitsl_vorzeitig
        See :func:`_ges_rente_arbeitsl_vorzeitig`.
    _ges_rente_langj_vorzeitig
        See :func:`_ges_rente_langj_vorzeitig`.

     Returns
    -------
    Early retirement age (potentially with deductions).

    """
    frauen_vorzeitig = _ges_rente_frauen_altersgrenze_vorzeitig

    arbeitsl_vorzeitig = _ges_rente_arbeitsl_vorzeitig

    langjährig_vorzeitig = _ges_rente_langj_vorzeitig

    out = ges_rente_regelaltersgrenze

    if ges_rente_vorauss_langj:
        out = langjährig_vorzeitig
    if ges_rente_vorauss_frauen:
        out = min([out, frauen_vorzeitig])
    if ges_rente_vorauss_arbeitsl:
        out = min([out, arbeitsl_vorzeitig])

    return out


@policy_info(start_date="2018-01-01", name_in_dag="_ges_rente_altersgrenze_vorzeitig")
def _ges_rente_altersgrenze_vorzeitig_ohne_rente_arbeitsl_frauen(
    ges_rente_vorauss_langj: bool,
    ges_rente_regelaltersgrenze: float,
    _ges_rente_langj_vorzeitig: float,
) -> float:
    """Earliest possible retirement age after checking for eligibility.

    Early retirement age depends on personal characteristics as gender, insurance
    duration, health/disability, employment status.

    Parameters
    ----------
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    _ges_rente_langj_vorzeitig
        See :func:`_ges_rente_langj_vorzeitig`.

     Returns
    -------
    Early retirement age (potentially with deductions).

    """

    out = ges_rente_regelaltersgrenze

    if ges_rente_vorauss_langj:
        out = _ges_rente_langj_vorzeitig
    else:
        out = ges_rente_regelaltersgrenze

    return out


@policy_info(
    end_date="1989-12-17", name_in_dag="_ges_rente_frauen_altersgrenze_vorzeitig"
)
def _ges_rente_frauen_altersgrenze_vorzeitig_ohne_staffelung(
    geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """Early retirement age (ERA) for Renten für Frauen.

    ERA does not depend on birth year and month.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age

    """

    # TODO(@MImmesberger): Remove fake dependency (geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_für_frauen_vorzeitig"]


@policy_info(
    start_date="1989-12-18",
    end_date="1996-09-26",
    name_in_dag="_ges_rente_frauen_altersgrenze_vorzeitig",
)
def _ges_rente_frauen_altersgrenze_vorzeitig_mit_staffelung(
    geburtsjahr: int,
    geburtsmonat: int,
    ges_rente_params: dict,
) -> float:
    """Early retirement age (ERA) for Renten für Frauen.

    ERA depends on birth year and month.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age

    """
    if (
        geburtsjahr
        <= ges_rente_params["altersgrenze_für_frauen_vorzeitig"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_für_frauen_vorzeitig"][
            "entry_age_old_regime"
        ]
    elif (
        geburtsjahr
        >= ges_rente_params["altersgrenze_für_frauen_vorzeitig"][
            "min_birthyear_new_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_für_frauen_vorzeitig"][
            "entry_age_new_regime"
        ]
    else:
        out = ges_rente_params["altersgrenze_für_frauen_vorzeitig"][geburtsjahr][
            geburtsmonat
        ]

    return out


@policy_info(
    start_date="1996-09-27", name_in_dag="_ges_rente_frauen_altersgrenze_vorzeitig"
)
def _ges_rente_frauen_altersgrenze_vorzeitig_ohne_staffelung_nach_96(
    geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """Early retirement age (ERA) for Renten für Frauen.

    ERA does not depend on birth year and month.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age

    """

    # TODO(@MImmesberger): Remove fake dependency (geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_für_frauen_vorzeitig"]


@policy_info(end_date="1989-12-17", name_in_dag="_ges_rente_langj_vorzeitig")
def _ges_rente_langj_vorzeitig_ohne_staffelung(
    geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """Early retirement age (ERA) for Rente für langjährig Versicherte.

    ERA does not depend on birth year and month.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age

    """

    # TODO(@MImmesberger): Remove fake dependency (geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_langj_versicherte_vorzeitig"]


@policy_info(
    start_date="1989-12-18",
    end_date="1996-09-26",
    name_in_dag="_ges_rente_langj_vorzeitig",
)
def _ges_rente_langj_vorzeitig_mit_staffelung(
    geburtsjahr: int,
    ges_rente_params: dict,
) -> float:
    """Early retirement age (ERA) for Renten für Frauen.

    ERA depends on birth year and month.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age

    """
    if (
        geburtsjahr
        <= ges_rente_params["altersgrenze_langj_versicherte_vorzeitig"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_langj_versicherte_vorzeitig"][
            "entry_age_old_regime"
        ]
    else:
        out = ges_rente_params["altersgrenze_langj_versicherte_vorzeitig"][
            "entry_age_new_regime"
        ]

    return out


@policy_info(start_date="1996-09-27", name_in_dag="_ges_rente_langj_vorzeitig")
def _ges_rente_langj_vorzeitig_ohne_staffelung_nach_96(
    geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """Early retirement age (ERA) for Rente für langjährig Versicherte.

    ERA does not depend on birth year and month.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age
    """

    # TODO(@MImmesberger): Remove fake dependency (geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_langj_versicherte_vorzeitig"]


@policy_info(end_date="1989-12-17", name_in_dag="_ges_rente_arbeitsl_vorzeitig")
def _ges_rente_arbeitsl_vorzeitig_ohne_staffelung(
    geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """Early retirement age of pension for unemployed.

    Early retirement age does not depend on birth year and month.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    ges_rente_params
        See params documentation
        :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age for unemployed.

    """

    # TODO(@MImmesberger): Remove fake dependency (geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_arbeitsl_vorzeitig"]


@policy_info(end_date="2017-12-31")
def _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss(
    geburtsjahr: int,
    geburtsmonat: int,
    ges_rente_params: dict,
) -> float:
    """Early retirement age of pension for unemployed without Vertrauensschutz.

    Relevant if the early retirement age depends on birth year and month.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age for unemployed.
    """

    if (
        geburtsjahr
        <= ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            "max_birthyear_old_regime"
        ]
    ):
        arbeitsl_vorzeitig = ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            "entry_age_old_regime"
        ]
    elif (
        geburtsjahr
        >= ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            "min_birthyear_new_regime"
        ]
    ):
        arbeitsl_vorzeitig = ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            "entry_age_new_regime"
        ]
    else:
        arbeitsl_vorzeitig = ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            geburtsjahr
        ][geburtsmonat]

    return arbeitsl_vorzeitig


@policy_info(
    start_date="1989-12-18",
    end_date="1996-07-28",
    name_in_dag="_ges_rente_arbeitsl_vorzeitig",
)
def ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss_vor_1996(
    _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss: float,
) -> float:
    """Early retirement age of pension for unemployed.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss
        See :func:`_ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss`.

    Returns
    -------
    Early retirement age for unemployed.
    """

    return _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss


@policy_info(
    start_date="1996-07-29",
    end_date="1996-09-26",
    name_in_dag="_ges_rente_arbeitsl_vorzeitig",
)
def ges_rente_arbeitsl_vorzeitig_mit_vertrauenss_1996(
    vertra_arbeitsl_1997: bool,
    _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss: float,
    ges_rente_params: dict,
) -> float:
    """Early retirement age of pension for unemployed.

    Includes Vertrauensschutz rules implemented from July to September 1996.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------

    vertra_arbeitsl_2006
        See basic input variable :ref:`vertra_arbeitsl_2006 <vertra_arbeitsl_2006>`.
    _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss
        See :func:`_ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age for unemployed.
    """

    if vertra_arbeitsl_1997:
        arbeitsl_vorzeitig = ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            "vertrauensschutz"
        ]
    else:
        arbeitsl_vorzeitig = _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss

    return arbeitsl_vorzeitig


@policy_info(
    start_date="1996-09-27",
    end_date="2004-07-25",
    name_in_dag="_ges_rente_arbeitsl_vorzeitig",
)
def _ges_rente_arbeitsl_vorzeitig_ohne_staffelung_nach_1997(
    geburtsjahr: int,  # noqa: ARG001
    ges_rente_params: dict,
) -> float:
    """Early retirement age of pension for unemployed.

    Early retirement age does not depend on birth year and month.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    ges_rente_params
        See params documentation
        :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age for unemployed.

    """

    # TODO(@MImmesberger): Remove fake dependency (geburtsjahr).
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/666

    return ges_rente_params["altersgrenze_arbeitsl_vorzeitig"]


@policy_info(
    start_date="2004-07-26",
    end_date="2017-12-31",
    name_in_dag="_ges_rente_arbeitsl_vorzeitig",
)
def ges_rente_arbeitsl_vorzeitig_mit_vertrauenss_ab_2006(
    vertra_arbeitsl_2006: bool,
    _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss: float,
    ges_rente_params: dict,
) -> float:
    """Early retirement age of pension for unemployed.

    Includes Vertrauensschutz rules implemented in 2006. Policy becomes inactive in 2018
    because then all potential beneficiaries have reached the normal retirement age.

    Does not check for eligibility for this pathway into retirement.

    Parameters
    ----------
    vertra_arbeitsl_2006
        See basic input variable :ref:`vertra_arbeitsl_2006
        <vertra_arbeitsl_2006>`.
    _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss
        See :func:`_ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Early retirement age for unemployed.
    """

    if vertra_arbeitsl_2006:
        arbeitsl_vorzeitig = ges_rente_params["altersgrenze_arbeitsl_vorzeitig"][
            "vertrauensschutz"
        ]
    else:
        arbeitsl_vorzeitig = _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss

    return arbeitsl_vorzeitig


@policy_info(end_date="2017-12-31", name_in_dag="ges_rente_vorauss_vorzeitig")
def ges_rente_vorauss_vorzeitig_mit_rente_arbeitsl_frauen(
    ges_rente_vorauss_frauen: bool,
    ges_rente_vorauss_langj: bool,
    ges_rente_vorauss_arbeitsl: bool,
) -> bool:
    """Eligibility for early retirement.

    Can only be claimed if eligible for "Rente für langjährig Versicherte" or "Rente für
    Frauen" or "Rente für Arbeitslose" (or -not yet implemented - for disabled). Policy
    becomes inactive in 2018 because then all potential beneficiaries of the Rente wg.
    Arbeitslosigkeit and Rente für Frauen have reached the normal retirement age.

    Parameters
    ----------
    ges_rente_vorauss_frauen
        See :func:`ges_rente_vorauss_frauen`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    ges_rente_vorauss_arbeitsl
        See :func:`ges_rente_vorauss_arbeitsl`.


    Returns
    -------
    Eligibility as bool.

    """

    out = (
        ges_rente_vorauss_frauen
        or ges_rente_vorauss_langj
        or ges_rente_vorauss_arbeitsl
    )

    return out


@policy_info(start_date="2018-01-01", name_in_dag="ges_rente_vorauss_vorzeitig")
def ges_rente_vorauss_vorzeitig_ohne_rente_arbeitsl_frauen(
    ges_rente_vorauss_langj: bool,
) -> bool:
    """Eligibility for early retirement.

    Can only be claimed if eligible for "Rente für langjährig Versicherte".

    Parameters
    ----------
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.

    Returns
    -------
    Eligibility as bool.

    """

    return ges_rente_vorauss_langj


def ges_rente_vorauss_regelrente(ges_rente_wartezeit_5: bool) -> bool:
    """Determining the eligibility for the Regelaltersrente.

    Parameters
    ----------
    ges_rente_wartezeit_5
        See :func:`ges_rente_wartezeit_5`.

    Returns
    -------
    Eligibility as bool.

    """

    return ges_rente_wartezeit_5


@policy_info(end_date="1997-12-15", name_in_dag="ges_rente_vorauss_frauen")
def ges_rente_vorauss_frauen_ohne_prüfung_geburtsjahr(
    weiblich: bool,
    ges_rente_wartezeit_15: bool,
    y_pflichtbeitr_ab_40: float,
    ges_rente_params: dict,
) -> bool:
    """Eligibility for Altersrente für Frauen (pension for women).

    Eligibility does not depend on birth year.

    Wartezeit 15 years, contributions for 10 years after age 40, being a woman. Policy
    becomes inactive in 2018 because then all potential beneficiaries have reached the
    normal retirement age.

    Parameters
    ----------
    weiblich
        See basic input variable :ref:`weiblich <weiblich>`.
    ges_rente_wartezeit_15
        See :func:`ges_rente_wartezeit_15`
    y_pflichtbeitr_ab_40
        See basic input variable :ref:`y_pflichtbeitr_ab_40 <y_pflichtbeitr_ab_40>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Eligibility as bool.

    """

    out = (
        weiblich
        and ges_rente_wartezeit_15
        and y_pflichtbeitr_ab_40 > ges_rente_params["rente_für_frauen_pflichtbeitr_y"]
    )

    return out


@policy_info(
    start_date="1997-12-16",
    end_date="2017-12-31",
    name_in_dag="ges_rente_vorauss_frauen",
)
def ges_rente_vorauss_frauen_mit_geburtsjahr_prüfung(
    weiblich: bool,
    ges_rente_wartezeit_15: bool,
    y_pflichtbeitr_ab_40: float,
    geburtsjahr: int,
    ges_rente_params: dict,
) -> bool:
    """Eligibility for Altersrente für Frauen (pension for women).

    Only individuals born before a certain year are eligible.

    Wartezeit 15 years, contributions for 10 years after age 40, being a woman. Policy
    becomes inactive in 2018 because then all potential beneficiaries have reached the
    normal retirement age.

    Parameters
    ----------
    weiblich
        See basic input variable :ref:`weiblich <weiblich>`.
    ges_rente_wartezeit_15
        See :func:`ges_rente_wartezeit_15`
    y_pflichtbeitr_ab_40
        See basic input variable :ref:`y_pflichtbeitr_ab_40 <y_pflichtbeitr_ab_40>`.
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Eligibility as bool.

    """

    out = (
        weiblich
        and ges_rente_wartezeit_15
        and y_pflichtbeitr_ab_40 > ges_rente_params["rente_für_frauen_pflichtbeitr_y"]
        and geburtsjahr < ges_rente_params["first_birthyear_without_rente_für_frauen"]
    )

    return out


@policy_info(end_date="2007-04-29", name_in_dag="ges_rente_vorauss_arbeitsl")
def _ges_rente_vorauss_arbeitsl_ohne_2007_reform(
    arbeitsl_1y_past_585: bool,
    ges_rente_wartezeit_15: bool,
    pflichtbeitr_8_in_10: bool,
) -> bool:
    """Eligibility for Altersrente für Arbeitslose (pension for unemployed).

    Wartezeit 15 years, 8 contribution years past 10 years, being unemployed for at
    least 1 year after age 58 and 6 months. The person is also required to be
    unemployed at the time of claiming the pension. As there are no restrictions
    regarding voluntary unemployment this requirement may be viewed as always satisfied
    and is therefore not included when checking for eligibility.

    Parameters
    ----------
    arbeitsl_1y_past_585
        See basic input variable
        :ref:`arbeitsl_1y_past_585 <arbeitsl_1y_past_585>`.
    ges_rente_wartezeit_15
        See :func:`ges_rente_wartezeit_15`
    pflichtbeitr_8_in_10
        See basic input variable :ref:`pflichtbeitr_8_in_10 <pflichtbeitr_8_in_10>`.

    Returns
    -------
    Eligibility as bool.

    """

    out = arbeitsl_1y_past_585 and ges_rente_wartezeit_15 and pflichtbeitr_8_in_10

    return out


@policy_info(
    start_date="2007-04-30",
    end_date="2017-12-31",
    name_in_dag="ges_rente_vorauss_arbeitsl",
)
def _ges_rente_vorauss_arbeitsl_mit_2007_reform(
    arbeitsl_1y_past_585: bool,
    ges_rente_wartezeit_15: bool,
    pflichtbeitr_8_in_10: bool,
    geburtsjahr: int,
    ges_rente_params: dict,
) -> bool:
    """Eligibility for Altersrente für Arbeitslose (pension for unemployed).

    Wartezeit 15 years, 8 contributionyears past 10 years, being at least 1 year
    unemployed after age 58 and 6 months and being born before 1952. The person is also
    required to be unemployed at the time of claiming the pension. As there are no
    restrictions regarding voluntary unemployment this requirement may be viewed as
    always satisfied and is therefore not included when checking for eligibility. Policy
    becomes inactive in 2018 because then all potential beneficiaries have reached the
    normal retirement age.

    Parameters
    ----------
    arbeitsl_1y_past_585
        See basic input variable :ref:`arbeitsl_1y_past_585 <arbeitsl_1y_past_585>`.
    ges_rente_wartezeit_15
        See :func:`ges_rente_wartezeit_15`
    pflichtbeitr_8_in_10
        See basic input variable :ref:`pflichtbeitr_8_in_10 <pflichtbeitr_8_in_10>`.
    geburtsjahr
        See :func:`geburtsjahr`
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Eligibility as bool.

    """

    out = (
        arbeitsl_1y_past_585
        and ges_rente_wartezeit_15
        and pflichtbeitr_8_in_10
        and geburtsjahr < ges_rente_params["first_birthyear_without_rente_für_arbeitsl"]
    )

    return out


def ges_rente_vorauss_langj(
    ges_rente_wartezeit_35: bool,
) -> bool:
    """Determining the eligibility for Altersrente für langjährig
    Versicherte (pension for long-term insured). Wartezeit 35 years and
    crossing the age threshold.

    Parameters
    ----------
    ges_rente_wartezeit_35
        See :func:`ges_rente_wartezeit_35`.

    Returns
    -------
    Eligibility as bool.

    """

    return ges_rente_wartezeit_35


@policy_info(start_date="2012-01-01")
def ges_rente_vorauss_besond_langj(
    ges_rente_wartezeit_45: bool,
) -> bool:
    """Determining the eligibility for Altersrente für besonders langjährig Versicherte
    (pension for very long-term insured). Wartezeit 45 years. aka "Rente mit 63".

    Parameters
    ----------
    ges_rente_wartezeit_45
        See :func:`ges_rente_wartezeit_45`


    Returns
    -------
    Eligibility as bool.

    """

    return ges_rente_wartezeit_45


def ges_rente_wartezeit_5(
    m_pflichtbeitrag: float,
    m_freiw_beitrag: float,
    m_ersatzzeit: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Allgemeine Wartezeit has been completed. Aggregates time
    periods that are relevant for the general eligibility of the
    regular pension (regelaltersrente). "Allgemeine Wartezeit".

    Parameters
    ----------
    m_pflichtbeitrag
        See basic input variable :ref:`m_pflichtbeitrag <m_pflichtbeitrag>`.
    m_freiw_beitrag
        See basic input variable :ref:`m_freiw_beitrag <m_freiw_beitrag>`.
    m_ersatzzeit
        See basic input variable :ref:`m_ersatzzeit <m_ersatzzeit>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 5 Jahren.

    """
    m_zeiten = (m_pflichtbeitrag + m_freiw_beitrag + m_ersatzzeit) / 12

    out = m_zeiten >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_5"]

    return out


def ges_rente_wartezeit_15(
    m_pflichtbeitrag: float,
    m_freiw_beitrag: float,
    m_ersatzzeit: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Wartezeit von 15 Jahren Wartezeit has been completed.
    Aggregates time periods that are relevant for the Altersrente für Frauen
    and Leistungen zur Teilhabe. Wartezeit von 15 Jahren.

    Parameters
    ----------
    m_pflichtbeitrag
        See basic input variable :ref:`m_pflichtbeitrag <m_pflichtbeitrag>`.
    m_freiw_beitrag
        See basic input variable :ref:`m_freiw_beitrag <m_freiw_beitrag>`.
    m_ersatzzeit
        See basic input variable :ref:`m_ersatzzeit <m_ersatzzeit>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 15 Jahren

    """
    m_zeiten = (m_pflichtbeitrag + m_freiw_beitrag + m_ersatzzeit) / 12

    out = m_zeiten >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_15"]

    return out


def ges_rente_wartezeit_35(  # noqa: PLR0913
    m_pflichtbeitrag: float,
    m_freiw_beitrag: float,
    ges_rente_anrechnungszeit: float,
    m_ersatzzeit: float,
    m_kind_berücks_zeit: float,
    m_pfleg_berücks_zeit: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Wartezeit von 35 Jahren Wartezeit has been completed.
    Aggregates time periods that are relevant for the eligibility of Altersrente für
    langjährig Versicherte (pension for long-term insured). Wartezeit von 35 Jahren. All
    "rentenrechtliche Zeiten" are considered.

    Parameters
    ----------
    m_pflichtbeitrag
        See basic input variable :ref:`m_pflichtbeitrag <m_pflichtbeitrag>`.
    m_freiw_beitrag
        See basic input variable :ref:`m_freiw_beitrag <m_freiw_beitrag>`.
    m_ersatzzeit
        See basic input variable :ref:`m_ersatzzeit <m_ersatzzeit>`.
    ges_rente_anrechnungszeit
        See :func:`ges_rente_anrechnungszeit`
    m_kind_berücks_zeit
        See basic input variable :ref:`m_kind_berücks_zeit <m_kind_berücks_zeit>`.
    m_pfleg_berücks_zeit
        See basic input variable :ref:`m_pfleg_berücks_zeit <m_pfleg_berücks_zeit>`
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 35 Jahren

    """
    m_zeiten = (
        m_pflichtbeitrag
        + m_freiw_beitrag
        + ges_rente_anrechnungszeit
        + m_ersatzzeit
        + m_pfleg_berücks_zeit
        + m_kind_berücks_zeit
    ) / 12
    out = m_zeiten >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_35"]

    return out


@policy_info(start_date="2012-01-01")
def ges_rente_wartezeit_45(  # noqa: PLR0913
    m_pflichtbeitrag: float,
    m_freiw_beitrag: float,
    ges_rente_anrechnungszeit_45: float,
    m_ersatzzeit: float,
    m_kind_berücks_zeit: float,
    m_pfleg_berücks_zeit: float,
    ges_rente_params: dict,
) -> bool:
    """Whether Wartezeit von 45 Jahren Wartezeit has been completed.
    Aggregates time periods that are relevant for the eligibility of Altersrente für
    besonders langjährig Versicherte (pension for very long-term insured). Wartezeit von
    45 Jahren. Not all "rentenrechtliche Zeiten" are considered. Years with voluntary
    contributions are only considered if at least 18 years of mandatory contributions
    (m_pflichtbeitrag). Not all ges_rente_anrechnungszeiten are considered, but only
    specific ones (e.g. ALG I, Kurzarbeit but not ALG II).

    Parameters
    ----------
    m_pflichtbeitrag
        See basic input variable :ref:`m_pflichtbeitrag <m_pflichtbeitrag>`.
    m_freiw_beitrag
        See basic input variable :ref:`m_freiw_beitrag <m_freiw_beitrag>`.
    ges_rente_anrechnungszeit_45
        See :func:`ges_rente_anrechnungszeit_45`.
    m_ersatzzeit
        See basic input variable :ref:`m_ersatzzeit <m_ersatzzeit>`.
    m_kind_berücks_zeit
        See basic input variable :ref:`m_kind_berücks_zeit <m_kind_berücks_zeit>`.
    m_pfleg_berücks_zeit
        See basic input variable :ref:`m_pfleg_berücks_zeit <m_pfleg_berücks_zeit>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Fulfilled Wartezeit von 45 Jahren

    """
    if m_pflichtbeitrag >= ges_rente_params["wartezeit_45_pflichtbeitragsmonate"]:
        freiwilligbeitr = m_freiw_beitrag
    else:
        freiwilligbeitr = 0

    m_zeiten = (
        m_pflichtbeitrag
        + freiwilligbeitr
        + ges_rente_anrechnungszeit_45
        + m_ersatzzeit
        + m_pfleg_berücks_zeit
        + m_kind_berücks_zeit
    ) / 12
    out = m_zeiten >= ges_rente_params["thresholds_wartezeiten"]["wartezeit_45"]

    return out


def ges_rente_anrechnungszeit(  # noqa: PLR0913
    m_arbeitsunfähig: float,
    m_krank_ab_16_bis_24: float,
    m_mutterschutz: float,
    m_arbeitsl: float,
    m_ausbild_suche: float,
    m_schul_ausbild: float,
) -> float:
    """Adds up all times that are accounted for in "Anrechnungszeiten"
    relevant for "Wartezeit von 35 Jahren" i.e. for Altersrente für
    langjährig Versicherte (pension for long term insured).
    (Ref: Studientext der Deutschen Rentenversicherung, Nr. 19,
    Wartezeiten, Ausgabe 2021, S. 24.)


    Parameters
    ----------
    m_arbeitsunfähig
        See basic input variable :ref:`m_arbeitsunfähig <m_arbeitsunfähig>`.
    m_krank_ab_16_bis_24
        See basic input variable :ref:`m_krank_ab_16_bis_24 <m_krank_ab_16_bis_24>`.
    m_mutterschutz
        See basic input variable :ref:`m_mutterschutz <m_mutterschutz>`.
    m_arbeitsl
        See basic input variable :ref:`m_arbeitsl <m_arbeitsl>`.
    m_ausbild_suche
        See basic input variable :ref:`m_ausbild_suche <m_ausbild_suche>`.
    m_schul_ausbild
        See basic input variable :ref:`m_schul_ausbild <m_schul_ausbild>`.

    Returns
    -------
    Anrechnungszeit in months
    """
    out = (
        m_arbeitsunfähig
        + m_krank_ab_16_bis_24
        + m_mutterschutz
        + m_arbeitsl
        + m_ausbild_suche
        + m_schul_ausbild
    )
    return out


@policy_info(start_date="2012-01-01")
def ges_rente_anrechnungszeit_45(
    m_arbeitsunfähig: float,
    m_alg1_übergang: float,
    m_geringf_beschäft: float,
) -> float:
    """Adds up all times NOT included in Beitragszeiten, Berücksichtigungszeiten,
    Ersatzzeiten (a variant of Anrechnungszeiten) that are accounted for in "Wartezeit
    von 45 Jahren" i.e. for Altersrente für besonders langjährig Versicherte (pension
    for very long term insured). "nur Anrechnungszeiten mit Bezug von
    Entgeltersatzleistungen der Arbeitsförderung, Leistungen bei Krankheit und
    Übergangsgeld". (Ref: Studientext der Deutschen Rentenversicherung, Nr. 19,
    Wartezeiten, Ausgabe 2021, S. 24)

    Parameters
    ----------
    m_arbeitsunfähig
        See basic input variable :ref:`m_arbeitsunfähig <m_arbeitsunfähig>`.
    m_alg1_übergang
        See basic input variable :ref:`m_alg1_übergang <m_alg1_übergang>`.
    m_geringf_beschäft
        See basic input variable :ref:`m_geringf_beschäft <m_geringf_beschäft>`.
    Returns
    -------
    Anrechnungszeit in months.

    """
    out = m_arbeitsunfähig + m_alg1_übergang + m_geringf_beschäft

    return out


def anteil_entgeltp_ost(
    entgeltp_west: float,
    entgeltp_ost: float,
) -> float:
    """Proportion of Entgeltpunkte accumulated in East Germany

    Parameters
    ----------
    entgeltp_west
        See basic input variable :ref:`entgeltp_west <entgeltp_west>
    entgeltp_ost
        See basic input variable :ref:`entgeltp_ost <entgeltp_ost>

    Returns
    -------
    Proportion of Entgeltpunkte accumulated in East Germany

    """
    if entgeltp_west == entgeltp_ost == 0.0:
        out = 0.0
    else:
        out = entgeltp_ost / (entgeltp_west + entgeltp_ost)

    return out


def durchschn_entgeltp(
    entgeltp_west: float,
    entgeltp_ost: float,
    age_of_retirement: float,
    erwerbsm_rente_params: dict,
) -> float:
    """Average earning points as part of the "Grundbewertung".
    Earnings points are divided by "belegungsfähige Gesamtzeitraum" which is
    the period from the age of 17 until the start of the pension.

    Legal reference: SGB VI § 72: Grundbewertung

    Parameters
    ----------
    entgeltp_west
        See basic input variable :ref:`entgeltp_west <entgeltp_west>
    entgeltp_ost
        See basic input variable :ref:`entgeltp_ost <entgeltp_ost>
    age_of_retirement
        See :func:`age_of_retirement`.
    erwerbsm_rente_params
        See params documentation :ref:`erwerbsm_rente_params <erwerbsm_rente_params>.

    Returns
    -------
    average entgeltp
    """

    beleg_gesamtzeitr = (
        age_of_retirement - erwerbsm_rente_params["altersgrenze_grundbewertung"]
    )

    durchschn_entgeltp = (entgeltp_west + entgeltp_ost) / beleg_gesamtzeitr

    return durchschn_entgeltp
