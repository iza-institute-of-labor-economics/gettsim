from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.shared import add_rounding_spec, dates_active


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


@add_rounding_spec(params_key="ges_rente")
def ges_rente_vor_grundr_m(
    ges_rente_zugangsfaktor: float,
    entgeltp_update: float,
    rentenwert: float,
    rentner: bool,
) -> float:
    """Old-Age Pensions claim without Grundrentenzuschlag. The function follows the
    following equation:

    .. math::

        R = EP * ZF * Rw

    models 'Rentenformel':
    https://de.wikipedia.org/wiki/Rentenformel
    https://de.wikipedia.org/wiki/Rentenanpassungsformel


    Parameters
    ----------
    ges_rente_zugangsfaktor
        See :func:`ges_rente_zugangsfaktor`.
    entgeltp_update
        See :func:`entgeltp_update`.
    rentenwert
        See :func:`rentenwert`.
    rentner
        See basic input variable :ref:`rentner <rentner>`.

    Returns
    -------

    """

    if rentner:
        out = entgeltp_update * ges_rente_zugangsfaktor * rentenwert
    else:
        out = 0.0

    return out


@dates_active(end="2020-12-31")
def ges_rente_m(ges_rente_vor_grundr_m: float) -> float:
    return ges_rente_vor_grundr_m


@dates_active(start="2021-01-01", change_name="ges_rente_m")
@add_rounding_spec(params_key="ges_rente")
def ges_rente_m_nach_grundr(
    ges_rente_vor_grundr_m: float,
    grundr_zuschlag_m: float,
    rentner: bool,
) -> float:
    """Calculate total individual public pension including Grundrentenzuschlag. Is only
    active after 2021 when Grundrente is in place.

    Parameters
    ----------
    ges_rente_vor_grundr_m
        See :func:`ges_rente_vor_grundr_m`.
    grundr_zuschlag_m
        See :func:`grundr_zuschlag_m`.
    rentner
        See basic input variable :ref:`rentner <rentner>`.

    Returns
    -------

    """
    # Return 0 if person not yet retired
    out = ges_rente_vor_grundr_m + grundr_zuschlag_m if rentner else 0.0
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


def rentenwert_vorjahr(wohnort_ost: bool, ges_rente_params: dict) -> float:
    """Select the rentenwert of the last year depending on place of living.

    Parameters
    ----------
    wohnort_ost
        See basic input variable :ref:`wohnort_ost <wohnort_ost>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """
    params = ges_rente_params["rentenwert_vorjahr"]

    out = params["ost"] if wohnort_ost else params["west"]

    return float(out)


def entgeltp_update(entgeltp: float, entgeltp_update_lohn: float) -> float:
    """Update earning points.

    Given earnings, social insurance rules, average
    earnings in a particular year and potentially other
    variables (e.g., benefits for raising children,
    informal care), return the new earnings points.

    Parameters
    ----------
    entgeltp
        See basic input variable :ref:`entgeltp <entgeltp>`.
    entgeltp_update_lohn
        See :func:`entgeltp_update_lohn`.

    Returns
    -------

    """
    # Note: We might need some interaction between the two
    # ways to accumulate earnings points (e.g., how to
    # determine what constitutes a 'care period')
    out = entgeltp + entgeltp_update_lohn
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
    rentner: bool,
    age_of_retirement: float,
    ges_rente_regelaltersgrenze: float,
    referenz_alter_abschlag: float,
    _ges_rente_altersgrenze_abschlagsfrei: float,
    _ges_rente_altersgrenze_vorzeitig: float,
    ges_rente_vorauss_vorzeitig: bool,
    ges_rente_vorauss_regelrente: bool,
    ges_rente_params: dict,
) -> float:
    """Calculate the zugangsfaktor based on the year the subject retired.

    At the regelaltersgrenze - normal retirement age (NRA), the agent is allowed to
    get pensions with his full claim. In general, if the agent retires earlier or later,
    the Zugangsfaktor and therefore the pension claim is higher or lower.

    Legal reference: § 77 Abs. 2 Nr. 2 SGB VI

    However, under certain conditions agents can receive their full pension claim
    (Zugangsfaktor=1) at an earlier age - full retirement age (FRA) -  (e.g. women,
    long term insured, disabled). That is the zugangsfaktor is 1 in [FRA, NRA].
    It only increases after the NRA for all agents without exeptions.

    Since pension payments of the GRV always start at 1st day of month, day of birth
    within month does not matter. The eligibility always starts in the month after
    reaching the required age.

    Parameters
    ----------
    rentner
        See basic input variable :ref:`rentner <rentner>`.
    age_of_retirement
        See :func:`age_of_retirement`.
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    referenz_alter_abschlag
        See :func:`referenz_alter_abschlag`.
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

    if rentner and ges_rente_vorauss_regelrente:
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
                    + (age_of_retirement - referenz_alter_abschlag)
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

    # Return 0 if person not yet retired or retired before working at least 5 years
    else:
        out = 0.0

    out = max(out, 0.0)

    return out


def age_of_retirement(
    jahr_renteneintr: int,
    monat_renteneintr: int,
    geburtsjahr: int,
    geburtsmonat: int,
    rentner: bool,
) -> float:
    """
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
    rentner
        See basic input variable :ref:`rentner <rentner>`.


    Returns
    -------
    Age as float (monthly precision).

    """
    if rentner:
        out = (
            jahr_renteneintr - geburtsjahr + (monat_renteneintr - geburtsmonat - 1) / 12
        )
    else:
        out = float("Nan")
    return out


@dates_active(end="2011-12-31", change_name="_ges_rente_altersgrenze_abschlagsfrei")
def _ges_rente_altersgrenze_abschlagsfrei_ohne_besond_langj(
    ges_rente_regelaltersgrenze: float,
    ges_rente_frauen_altersgrenze: float,
    _ges_rente_langj_altersgrenze: float,
    _ges_rente_arbeitsl_altersgrenze: float,
    ges_rente_vorauss_regelrente: bool,
    ges_rente_vorauss_frauen: bool,
    ges_rente_vorauss_langj: bool,
    _ges_rente_vorauss_arbeitsl: bool,
) -> float:
    """Calculates the age, at which a person is eligible to claim the full pension. Full
    retirement age (FRA) without deductions. This age is smaller or equal to the
    regelaltersgrenze (FRA<=NRA) and depends on personal characteristics as gender,
    insurance duration, health/disability, employment status.

    Parameters
    ----------
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    ges_rente_frauen_altersgrenze
        See :func:`ges_rente_frauen_altersgrenze`.
    _ges_rente_langj_altersgrenze
        See :func:`_ges_rente_langj_altersgrenze`.
    _ges_rente_arbeitsl_altersgrenze
         See :func:`_ges_rente_arbeitsl_altersgrenze`.
    ges_rente_vorauss_regelrente
        See :func:`ges_rente_vorauss_regelrente`.
    ges_rente_vorauss_frauen
        See :func:`ges_rente_vorauss_frauen`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    _ges_rente_vorauss_arbeitsl:
        See :func:`_ges_rente_vorauss_arbeitsl`.
    Returns
    -------
    Lowest possible full retirement age (without deductions). Nan if
    person not eligible for a public pension. Includes abolishments
    of pension for women and unemployed via increase of respective
    thresholds to regelaltersgrenze after abolishment.

    """

    out = float("Nan")
    if ges_rente_vorauss_regelrente:
        out = ges_rente_regelaltersgrenze
    if ges_rente_vorauss_frauen:
        out = min([out, ges_rente_frauen_altersgrenze])
    if _ges_rente_vorauss_arbeitsl:
        out = min([out, _ges_rente_arbeitsl_altersgrenze])
    if ges_rente_vorauss_langj:
        out = min([out, _ges_rente_langj_altersgrenze])

    return out


@dates_active(
    start="2012-01-01",
    end="2017-12-31",
    change_name="_ges_rente_altersgrenze_abschlagsfrei",
)
def _ges_rente_altersgrenze_abschlagsfrei_mit_besond_langj(  # noqa: PLR0913
    ges_rente_regelaltersgrenze: float,
    ges_rente_frauen_altersgrenze: float,
    _ges_rente_langj_altersgrenze: float,
    _ges_rente_besond_langj_altersgrenze: float,
    _ges_rente_arbeitsl_altersgrenze: float,
    ges_rente_vorauss_regelrente: bool,
    ges_rente_vorauss_frauen: bool,
    ges_rente_vorauss_langj: bool,
    ges_rente_vorauss_besond_langj: bool,
    _ges_rente_vorauss_arbeitsl: bool,
) -> float:
    """Calculate the age, at which a person is eligible to claim the full pension. Full
    retirement age (FRA) without deductions. This age is smaller or equal to the
    regelaltersgrenze (FRA<=NRA) and depends on personal characteristics as gender,
    insurance duration, health/disability, employment status.

    Starting in 2012, the pension for the very long term insured (Altersrente für
    besonders langjährig Versicherte) is introduced. Policy becomes inactive in 2018
    because then all potential beneficiaries of the Rente wg. Arbeitslosigkeit and
    Rente für Frauen have reached the normal retirement age.

    Parameters
    ----------
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    ges_rente_frauen_altersgrenze
        See :func:`ges_rente_frauen_altersgrenze`.
    _ges_rente_langj_altersgrenze
        See :func:`_ges_rente_langj_altersgrenze`.
    _ges_rente_besond_langj_altersgrenze
        See :func:`_ges_rente_besond_langj_altersgrenze`.
    _ges_rente_arbeitsl_altersgrenze
        See :func:`_ges_rente_arbeitsl_altersgrenze`.
    ges_rente_vorauss_regelrente
        See :func:`ges_rente_vorauss_regelrente`.
    ges_rente_vorauss_frauen
        See :func:`ges_rente_vorauss_frauen`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    ges_rente_vorauss_besond_langj
        See :func:`ges_rente_vorauss_besond_langj`.
    _ges_rente_vorauss_arbeitsl
        See :func:`_ges_rente_vorauss_arbeitsl`.

    Returns
    -------
    Lowest possible full retirement age (without deductions). Nan if
    person not eligigble for a public pension.

    """

    out = float("inf")
    if ges_rente_vorauss_regelrente:
        out = ges_rente_regelaltersgrenze
    if ges_rente_vorauss_frauen:
        out = min([out, ges_rente_frauen_altersgrenze])
    if _ges_rente_vorauss_arbeitsl:
        out = min([out, _ges_rente_arbeitsl_altersgrenze])
    if ges_rente_vorauss_langj:
        out = min([out, _ges_rente_langj_altersgrenze])
    if ges_rente_vorauss_besond_langj:
        out = min([out, _ges_rente_besond_langj_altersgrenze])

    return out


@dates_active(start="2018-01-01", change_name="_ges_rente_altersgrenze_abschlagsfrei")
def _ges_rente_altersgrenze_abschlagsfrei_ohne_arbeitsl_frauen(
    ges_rente_regelaltersgrenze: float,
    _ges_rente_langj_altersgrenze: float,
    _ges_rente_besond_langj_altersgrenze: float,
    ges_rente_vorauss_regelrente: bool,
    ges_rente_vorauss_langj: bool,
    ges_rente_vorauss_besond_langj: bool,
) -> float:
    """Calculate the age, at which a person is eligible to claim the full pension. Full
    retirement age (FRA) without deductions. This age is smaller or equal to the
    regelaltersgrenze (FRA<=NRA) and depends on personal characteristics as gender,
    insurance duration, health/disability, employment status.

    Parameters
    ----------
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    _ges_rente_langj_altersgrenze
        See :func:`_ges_rente_langj_altersgrenze`.
    _ges_rente_besond_langj_altersgrenze
        See :func:`_ges_rente_besond_langj_altersgrenze`.
    ges_rente_vorauss_regelrente
        See :func:`ges_rente_vorauss_regelrente`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    ges_rente_vorauss_besond_langj
        See :func:`ges_rente_vorauss_besond_langj`.

    Returns
    -------
    Lowest possible full retirement age (without deductions). Nan if
    person not eligigble for a public pension.

    """

    out = float("inf")
    if ges_rente_vorauss_regelrente:
        out = ges_rente_regelaltersgrenze
    if ges_rente_vorauss_langj:
        out = min([out, _ges_rente_langj_altersgrenze])
    if ges_rente_vorauss_besond_langj:
        out = min([out, _ges_rente_besond_langj_altersgrenze])

    return out


@dates_active(end="2017-12-31", change_name="referenz_alter_abschlag")
def _referenz_alter_abschlag_mit_rente_arbeitsl_frauen(
    ges_rente_frauen_altersgrenze: float,
    _ges_rente_langj_altersgrenze: float,
    _ges_rente_arbeitsl_altersgrenze: float,
    ges_rente_vorauss_frauen: bool,
    ges_rente_vorauss_langj: bool,
    _ges_rente_vorauss_arbeitsl: bool,
) -> float:
    """Determines reference age for deduction calculation in case of early retirement
    (Zugangsfaktor). Nan if person is not eligible for early retirement. (The regular
    pension and the pension for very long term insured cannot be claimed early.
    Includes abolishement of Rente für Frauen und Arbeitslose via jump of the
    respective thresholds to regelaltersgrenze.)

    Policy becomes inactive in 2018 because then all potential beneficiaries of the
    Rente wg. Arbeitslosigkeit and Rente für Frauen have reached the normal retirement
    age.

    Parameters
    ----------
    ges_rente_frauen_altersgrenze
        See :func:`ges_rente_frauen_altersgrenze`.
    _ges_rente_langj_altersgrenze
        See :func:`_ges_rente_langj_altersgrenze`.
    _ges_rente_arbeitsl_altersgrenze
        See :func:`_ges_rente_arbeitsl_altersgrenze`.
    ges_rente_vorauss_frauen
        See :func:`ges_rente_vorauss_frauen`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    _ges_rente_vorauss_arbeitsl
        See :func:`_ges_rente_vorauss_arbeitsl`.

     Returns
    -------
    Reference age for deduction calculation.

    """
    if (
        ges_rente_vorauss_langj
        and ges_rente_vorauss_frauen
        and _ges_rente_vorauss_arbeitsl
    ):
        out = min(
            [
                ges_rente_frauen_altersgrenze,
                _ges_rente_langj_altersgrenze,
                _ges_rente_arbeitsl_altersgrenze,
            ]
        )
    elif ges_rente_vorauss_langj and ges_rente_vorauss_frauen:
        out = min([ges_rente_frauen_altersgrenze, _ges_rente_langj_altersgrenze])
    elif ges_rente_vorauss_langj and _ges_rente_vorauss_arbeitsl:
        out = min([_ges_rente_langj_altersgrenze, _ges_rente_arbeitsl_altersgrenze])
    elif ges_rente_vorauss_langj:
        out = _ges_rente_langj_altersgrenze
    elif ges_rente_vorauss_frauen:
        out = ges_rente_frauen_altersgrenze
    elif _ges_rente_vorauss_arbeitsl:
        out = _ges_rente_arbeitsl_altersgrenze
    else:
        out = float("Nan")

    return out


@dates_active(start="2018-01-01", change_name="referenz_alter_abschlag")
def _referenz_alter_abschlag_ohne_rente_arbeitsl_frauen(
    _ges_rente_langj_altersgrenze: float,
    ges_rente_vorauss_langj: bool,
) -> float:
    """Determines reference age for deduction calculation in case of early retirement
    (Zugangsfaktor). Nan if person is not eligible for early retirement. (The regular
    pension and the pension for very long term insured cannot be claimed early.
    Includes abolishement of Rente für Frauen und Arbeitslose via jump of the
    respective thresholds to regelaltersgrenze.)

    Parameters
    ----------
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
        out = float("Nan")

    return out


def ges_rente_regelaltersgrenze(geburtsjahr: int, ges_rente_params: dict) -> float:
    """Calculate the age, at which a person is eligible to claim the regular pension.
    Normal retirement age (NRA). This pension cannot be claimed earlier than at the NRA,
    ie it does not serve as reference for calculating deductions. However, it serves as
    reference for calculating gains in the Zugangsfakor in case of later retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.


    Returns
    -------
    Age as float.

    """
    out = piecewise_polynomial(
        x=geburtsjahr,
        thresholds=ges_rente_params["regelaltersgrenze"]["thresholds"],
        rates=ges_rente_params["regelaltersgrenze"]["rates"],
        intercepts_at_lower_thresholds=ges_rente_params["regelaltersgrenze"][
            "intercepts_at_lower_thresholds"
        ],
    )

    return out


def ges_rente_frauen_altersgrenze(
    birthdate_decimal: float,
    ges_rente_regelaltersgrenze: float,
    ges_rente_params: dict,
) -> float:
    """Calculate the age, at which a women is eligible to claim the full pension
    (without deductions). This pension scheme allows for early retirement from age 60
    with deductions. Hence this threshold is needed as reference for calculating the
    zugangsfaktor.

    Parameters
    ----------
    birthdate_decimal
        See :func:`birthdate_decimal`.
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    returns the lowest full retirement age for women.

    """
    if birthdate_decimal < ges_rente_params["first_birthyear_without_rente_für_frauen"]:
        out = piecewise_polynomial(
            x=birthdate_decimal,
            thresholds=ges_rente_params["altersgrenze_für_frauen_abschlagsfrei"][
                "thresholds"
            ],
            rates=ges_rente_params["altersgrenze_für_frauen_abschlagsfrei"]["rates"],
            intercepts_at_lower_thresholds=ges_rente_params[
                "altersgrenze_für_frauen_abschlagsfrei"
            ]["intercepts_at_lower_thresholds"],
        )
    else:
        out = ges_rente_regelaltersgrenze

    return out


def _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutz_pruefung(
    geburtsjahr: int,
    geburtsmonat: int,
    ges_rente_params: dict,
) -> float:
    """Age at which an unemployed is eligible to claim the full
    pension (without deductions) without Vertrauensschutz.

    Full retirement age depends on birth year and month.
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
    lowest full retirement age for unemployed.

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


@dates_active(end="1991-12-31", change_name="_ges_rente_arbeitsl_altersgrenze")
def _ges_rente_arbeitsl_altersgrenze_ohne_staffelung(
    ges_rente_params: dict,
) -> float:
    """Age at which an unemployed is eligible to claim the full
    pension (without deductions).

    Before the WFG (Gesetz für Wachstum und Beschäftigung) was implemented in 1997 the
    full retirement age was the same for every birth cohort.

    Parameters
    ----------
    ges_rente_params
        See params documentation
        :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    lowest full retirement age for unemployed.

    """

    return ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"]


@dates_active(
    start="1992-01-01", end="1996-07-28", change_name="_ges_rente_arbeitsl_altersgrenze"
)
def _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutz_pruefung_bis_1996(
    _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutz_pruefung: float,
) -> float:
    """Age at which an unemployed is eligible to claim the full
    pension (without deductions) without Vertrauensschutz.

    Parameters
    ----------
    _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutz_pruefung
        See :func:`_ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutz_pruefung`.

    Returns
    -------
    lowest full retirement age for unemployed.

    """
    return _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutz_pruefung


@dates_active(
    start="1996-07-29", end="2009-12-31", change_name="_ges_rente_arbeitsl_altersgrenze"
)
def _ges_rente_arbeitsl_altersgrenze_mit_vertrauensschutz_pruefung(
    geburtsjahr: int,
    geburtsmonat: int,
    ges_rente_params: dict,
    vertra_arbeitsl_1997: bool,
) -> float:
    """Age at which an unemployed is eligible to claim the full
    pension (without deductions) allowing for legitimate expectations.

    Full retirement age depends on birth year and month. Policy becomes inactive in 2010
    because then all potential beneficiaries have reached the normal retirement age.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    ges_rente_params
        See params documentation
        :ref:`ges_rente_params <ges_rente_params>`.
    vertra_arbeitsl_1997
        See basic input variable :ref:`vertra_arbeitsl_1997 <vertra_arbeitsl_1997>`.

    Returns
    -------
    lowest full retirement age for unemployed.

    """
    if (
        vertra_arbeitsl_1997
        and geburtsjahr
        <= ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei_vertrauensschutz"][
            "max_birthyear_old_regime"
        ]
    ):
        out = ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei_vertrauensschutz"][
            "entry_age_old_regime"
        ]

    elif vertra_arbeitsl_1997:
        out = ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei_vertrauensschutz"][
            geburtsjahr
        ][geburtsmonat]
    elif (
        geburtsjahr
        < ges_rente_params["altersgrenze_arbeitsl_abschlagsfrei"][
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


@dates_active(
    start="2010-01-01", end="2017-12-31", change_name="_ges_rente_arbeitsl_altersgrenze"
)
def _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutz_pruefung_ab_2010(
    _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutz_pruefung: float,
) -> float:
    """Age at which an unemployed is eligible to claim the full
    pension (without deductions) without Vertrauensschutz.

    Full retirement age depends on birth year and month. Policy becomes inactive in 2017
    because then all potential beneficiaries have reached the normal retirement age.
    Parameters
    ----------
    _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutz_pruefung
        See :func:`_ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutz_pruefung`.

    Returns
    -------
    lowest full retirement age for unemployed.

    """
    return _ges_rente_arbeitsl_altersgrenze_ohne_vertrauensschutz_pruefung


def _ges_rente_langj_altersgrenze(
    birthdate_decimal: float,
    ges_rente_params: dict,
    ges_rente_regelaltersgrenze: float,
) -> float:
    """Calculate the age, at which a long term insured person (at least 35 years) is
    eligible to claim the full pension (without deductions). This pension scheme allows
    for early retirement (e.g. age 63) with deductions. Hence this threshold is needed
    as reference for calculating the zugangsfaktor.

    Parameters
    ----------
    birthdate_decimal
        See :func:`birthdate_decimal`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.

    Returns
    -------
    Full retirement age (without deductions) for long term insured.

    """

    # From 1950 on, the altersgrenze of langjährig Versicherte is equal to the
    # Regelaltersgrenze which is indpendendent of the birth month and only depends on
    # the birth year.

    if birthdate_decimal < ges_rente_params["alignment_cohort_langj_versicherte"]:
        out = piecewise_polynomial(
            x=birthdate_decimal,
            thresholds=ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
                "thresholds"
            ],
            rates=ges_rente_params["altersgrenze_langj_versicherte_abschlagsfrei"][
                "rates"
            ],
            intercepts_at_lower_thresholds=ges_rente_params[
                "altersgrenze_langj_versicherte_abschlagsfrei"
            ]["intercepts_at_lower_thresholds"],
        )
    else:
        out = ges_rente_regelaltersgrenze

    return out


@dates_active(start="2012-01-01")
def _ges_rente_besond_langj_altersgrenze(
    geburtsjahr: int,
    birthdate_decimal: float,
    ges_rente_params: dict,
) -> float:
    """Calculate the threshold from which very long term insured people (at least 45
    years) can claim their full pension without deductions.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    birthdate_decimal
        See :func:`birthdate_decimal`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    Full retirement age (without deductions) for very long term insured.

    """
    if geburtsjahr < ges_rente_params["first_birthyear_besond_langj_versicherte"]:
        x = birthdate_decimal
    else:
        x = geburtsjahr

    out = piecewise_polynomial(
        x=x,
        thresholds=ges_rente_params["altersgrenze_besond_langj_versicherte"][
            "thresholds"
        ],
        rates=ges_rente_params["altersgrenze_besond_langj_versicherte"]["rates"],
        intercepts_at_lower_thresholds=ges_rente_params[
            "altersgrenze_besond_langj_versicherte"
        ]["intercepts_at_lower_thresholds"],
    )

    return out


@dates_active(end="2017-12-31", change_name="_ges_rente_altersgrenze_vorzeitig")
def _ges_rente_altersgrenze_vorzeitig_mit_rente_arbeitsl_frauen(  # noqa: PLR0913
    ges_rente_params: dict,
    ges_rente_vorauss_frauen: bool,
    ges_rente_vorauss_langj: bool,
    _ges_rente_vorauss_arbeitsl: bool,
    geburtsjahr: int,
    ges_rente_regelaltersgrenze: float,
    ges_rente_arbeitsl_vorzeitig: float,
) -> float:
    """Calculates the earliest age, at which a person is eligible to claim the a
    pension. Early retirement age (ERA) deductions. This age depends on personal
    characteristics as gender, insurance duration, health/disability, employment
    status.

    Policy becomes inactive in 2018 because then all potential beneficiaries of the
    Rente wg. Arbeitslosigkeit and Rente für Frauen have reached the normal retirement
    age.

    Parameters
    ----------
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.
    ges_rente_vorauss_frauen
        See :func:`ges_rente_vorauss_frauen`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    _ges_rente_vorauss_arbeitsl:
        See :func:`_ges_rente_vorauss_arbeitsl`.
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    ges_rente_arbeitsl_vorzeitig
        See :func:`ges_rente_arbeitsl_vorzeitig`.

     Returns
    -------
    Lowest possible early retirement age (potentially with deductions).

    """
    frauen_vorzeitig = piecewise_polynomial(
        x=geburtsjahr,
        thresholds=ges_rente_params["altersgrenze_für_frauen_vorzeitig"]["thresholds"],
        rates=ges_rente_params["altersgrenze_für_frauen_vorzeitig"]["rates"],
        intercepts_at_lower_thresholds=ges_rente_params[
            "altersgrenze_für_frauen_vorzeitig"
        ]["intercepts_at_lower_thresholds"],
    )

    arbeitsl_vorzeitig = ges_rente_arbeitsl_vorzeitig

    langjährig_vorzeitig = ges_rente_params["altersgrenze_langj_versicherte_vorzeitig"]

    out = ges_rente_regelaltersgrenze

    if ges_rente_vorauss_langj:
        out = langjährig_vorzeitig
    if ges_rente_vorauss_frauen:
        out = min([out, frauen_vorzeitig])
    if _ges_rente_vorauss_arbeitsl:
        out = min([out, arbeitsl_vorzeitig])

    return out


@dates_active(start="2018-01-01", change_name="_ges_rente_altersgrenze_vorzeitig")
def _ges_rente_altersgrenze_vorzeitig_ohne_rente_arbeitsl_frauen(
    ges_rente_params: dict,
    ges_rente_vorauss_langj: bool,
    ges_rente_regelaltersgrenze: float,
) -> float:
    """Calculates the earliest age, at which a person is eligible to claim the a
    pension. Early retirement age (ERA) deductions. This age depends on personal
    characteristics as gender, insurance duration, health/disability, employment
    status.

    Parameters
    ----------
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.

     Returns
    -------
    Lowest possible early retirement age (potentially with deductions).

    """

    out = ges_rente_regelaltersgrenze

    if ges_rente_vorauss_langj:
        out = ges_rente_params["altersgrenze_langj_versicherte_vorzeitig"]
    else:
        out = ges_rente_regelaltersgrenze

    return out


@dates_active(end="1991-12-31", change_name="ges_rente_arbeitsl_vorzeitig")
def _ges_rente_arbeitsl_vorzeitig_ohne_staffelung(
    ges_rente_params: dict,
) -> float:
    """Earliest age, at which an unemployed person is eligible to claim
    the pension for unemployed.

    Parameters
    ----------
    ges_rente_params
        See params documentation
        :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    early retirement age for unemployed.

    """

    return ges_rente_params["altersgrenze_arbeitsl_vorzeitig"]


def _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss(
    ges_rente_params: dict,
    geburtsjahr: int,
    geburtsmonat: int,
) -> float:
    """Earliest age, at which an unemployed person is eligible to claim
    the pension for unemployed.

    Parameters
    ----------
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.

    Returns
    -------
    Lowest possible early retirement age.
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


@dates_active(
    start="1992-01-01", end="1996-07-28", change_name="ges_rente_arbeitsl_vorzeitig"
)
def ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss_vor_1996(
    _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss: float,
) -> float:
    """Earliest age, at which an unemployed person is eligible to claim
    the pension for unemployed.

    Parameters
    ----------
    _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss
        See :func:`_ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss`.

    Returns
    -------
    Lowest possible early retirement age.
    """

    return _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss


@dates_active(
    start="1996-07-29", end="1996-09-26", change_name="ges_rente_arbeitsl_vorzeitig"
)
def ges_rente_arbeitsl_vorzeitig_mit_vertrauenss_1996(
    ges_rente_params: dict,
    geburtsjahr: int,
    geburtsmonat: int,
    vertra_arbeitsl_1997: bool,
) -> float:
    """Earliest age, at which an unemployed person is eligible to claim
    the pension for unemployed.

    Includes Vertrauensschutz rules implemented from July to September 1996.

    Parameters
    ----------
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    vertra_arbeitsl_2006
        See basic input variable :ref:`vertra_arbeitsl_2006
        <vertra_arbeitsl_2006>`.

    Returns
    -------
    Lowest possible early retirement age.
    """

    if vertra_arbeitsl_1997:
        arbeitsl_vorzeitig = ges_rente_params[
            "altersgrenze_arbeitsl_abschlag_vertrauensschutz"
        ]
    elif (
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


@dates_active(
    start="1996-09-27", end="2005-12-31", change_name="ges_rente_arbeitsl_vorzeitig"
)
def _ges_rente_arbeitsl_vorzeitig_ohne_staffelung_nach_1997(
    ges_rente_params: dict,
) -> float:
    """Earliest age, at which an unemployed person is eligible to claim
    the pension for unemployed.

    Parameters
    ----------
    ges_rente_params
        See params documentation
        :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------
    early retirement age for unemployed.

    """

    return ges_rente_params["altersgrenze_arbeitsl_vorzeitig"]


@dates_active(
    start="2006-01-01", end="2009-12-31", change_name="ges_rente_arbeitsl_vorzeitig"
)
def ges_rente_arbeitsl_vorzeitig_mit_vertrauenss(
    ges_rente_params: dict,
    geburtsjahr: int,
    geburtsmonat: int,
    vertra_arbeitsl_2006: bool,
) -> float:
    """Earliest age, at which an unemployed person is eligible to claim
    the pension for unemployed.

    Includes Vertrauensschutz rules implemented in 2006. Policy becomes inactive in 2010
    because then all potential beneficiaries have reached the normal retirement age.

    Parameters
    ----------
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    vertra_arbeitsl_2006
        See basic input variable :ref:`vertra_arbeitsl_2006
        <vertra_arbeitsl_2006>`.

    Returns
    -------
    Lowest possible early retirement age.
    """

    if vertra_arbeitsl_2006:
        arbeitsl_vorzeitig = ges_rente_params[
            "altersgrenze_arbeitsl_abschlag_vertrauensschutz"
        ]
    elif (
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


@dates_active(
    start="2010-01-01", end="2017-12-31", change_name="ges_rente_arbeitsl_vorzeitig"
)
def ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss_ab_2010(
    _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss: float,
) -> float:
    """Earliest age, at which an unemployed person is eligible to claim
    the pension for unemployed.

    Policy becomes inactive in 2018 because then all potential beneficiaries have
    reached the normal retirement age.
    Parameters
    ----------
    _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss
        See :func:`_ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss`.

    Returns
    -------
    Lowest possible early retirement age.
    """

    return _ges_rente_arbeitsl_vorzeitig_ohne_vertrauenss


@dates_active(end="2017-12-31", change_name="ges_rente_vorauss_vorzeitig")
def ges_rente_vorauss_vorzeitig_mit_rente_arbeitsl_frauen(
    ges_rente_vorauss_frauen: bool,
    ges_rente_vorauss_langj: bool,
    _ges_rente_vorauss_arbeitsl: bool,
) -> bool:
    """Determining eligibility for early retirement. Can only be claimed if
    eligible for "Rente für langjährig Versicherte" or "Rente für Frauen" or "Rente
    für Arbeitslose" (or -not yet implemented - for disabled).

    Policy becomes inactive in 2018 because then all potential beneficiaries of the
    Rente wg. Arbeitslosigkeit and Rente für Frauen have reached the normal retirement
    age.
    Parameters
    ----------
    ges_rente_vorauss_frauen
        See :func:`ges_rente_vorauss_frauen`.
    ges_rente_vorauss_langj
        See :func:`ges_rente_vorauss_langj`.
    _ges_rente_vorauss_arbeitsl
        See :func:`_ges_rente_vorauss_arbeitsl`.


    Returns
    -------
    Eligibility as bool.

    """

    out = (
        ges_rente_vorauss_frauen
        or ges_rente_vorauss_langj
        or _ges_rente_vorauss_arbeitsl
    )

    return out


@dates_active(start="2018-01-01", change_name="ges_rente_vorauss_vorzeitig")
def ges_rente_vorauss_vorzeitig_ohne_rente_arbeitsl_frauen(
    ges_rente_vorauss_langj: bool,
) -> bool:
    """Determining eligibility for early retirement. Can only be claimed if
    eligible for "Rente für langjährig Versicherte".


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


@dates_active(end="2017-12-31")
def ges_rente_vorauss_frauen(
    weiblich: bool,
    ges_rente_wartezeit_15: bool,
    y_pflichtbeitr_ab_40: float,
    geburtsjahr: int,
    ges_rente_params: dict,
) -> bool:
    """Determining the eligibility for Altersrente für Frauen (pension for
    women) Wartezeit 15 years, contributions 10 years after age 40, being a women.

    Policy becomes inactive in 2018 because then all potential beneficiaries have
    reached the normal retirement age.
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


@dates_active(end="2011-12-31", change_name="_ges_rente_vorauss_arbeitsl")
def _ges_rente_vorauss_arbeitsl_ohne_2012_reform(
    arbeitsl_1y_past_585: bool,
    ges_rente_wartezeit_15: bool,
    pflichtbeitr_8_in_10: bool,
) -> bool:
    """Eligibility for Altersrente für Arbeitslose (pension
    for unemployed. Wartezeit 15 years, 8 contributionyears past 10 years, being
    at least 1 year unemployed after age 58 and 6 months.

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


@dates_active(
    start="2012-01-01", end="2017-12-31", change_name="_ges_rente_vorauss_arbeitsl"
)
def _ges_rente_vorauss_arbeitsl_mit_2012_reform(
    arbeitsl_1y_past_585: bool,
    ges_rente_wartezeit_15: bool,
    pflichtbeitr_8_in_10: bool,
    birthdate_decimal: float,
    ges_rente_params: dict,
) -> bool:
    """Eligibility for Altersrente für Arbeitslose (pension
    for unemployed. Wartezeit 15 years, 8 contributionyears past 10 years, being
    at least 1 year unemployed after age 58 and 6 months and being born before 1952.

    Policy becomes inactive in 2018 because then all potential beneficiaries have
    reached the normal retirement age.
    Parameters
    ----------
    arbeitsl_1y_past_585
        See basic input variable
        :ref:`arbeitsl_1y_past_585 <arbeitsl_1y_past_585>`.
    ges_rente_wartezeit_15
        See :func:`ges_rente_wartezeit_15`
    pflichtbeitr_8_in_10
        See basic input variable :ref:`pflichtbeitr_8_in_10 <pflichtbeitr_8_in_10>`.
    birthdate_decimal
        See :func:`birthdate_decimal`
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
        and birthdate_decimal
        < ges_rente_params["first_birthyear_without_rente_für_arbeitsl"]
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


@dates_active(start="2012-01-01")
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


@dates_active(start="2012-01-01")
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


@dates_active(start="2012-01-01")
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
