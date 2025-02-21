"""Public pension benefits for retirement due to age."""

from _gettsim.shared import policy_info


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
    start_date="2017-01-01",
    end_date="2022-12-31",
)
def _differenz_bruttolohn_hinzuverdienstgrenze_y(
    bruttolohn_y: float,
    ges_rente_params: dict,
) -> float:
    """Earnings that are subject to pension deductions.

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
    sozialversicherungsbeitraege__rentenversicherung__beitragsbemessungsgrenze_m: float,
    ges_rente_params: dict,
) -> float:
    """Return earning points for the wages earned in the last year.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    wohnort_ost
        See :func:`wohnort_ost`.
    sozialversicherungsbeitraege__rentenversicherung__beitragsbemessungsgrenze_m
        See :func:
        `sozialversicherungsbeitraege__rentenversicherung__beitragsbemessungsgrenze_m`.
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
    if (
        bruttolohn_scaled_east
        > sozialversicherungsbeitraege__rentenversicherung__beitragsbemessungsgrenze_m
    ):
        bruttolohn_scaled_rentenv = (
            sozialversicherungsbeitraege__rentenversicherung__beitragsbemessungsgrenze_m
        )
    else:
        bruttolohn_scaled_rentenv = bruttolohn_scaled_east

    # Calculate monthly mean wage in Germany
    durchschnittslohn_m = (1 / 12) * ges_rente_params[
        "beitragspflichtiges_durchschnittsentgelt"
    ]

    out = bruttolohn_scaled_rentenv / durchschnittslohn_m
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
