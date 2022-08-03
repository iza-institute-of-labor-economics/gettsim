from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.shared import add_rounding_spec


def sum_ges_rente_priv_rente_m(priv_rente_m: float, ges_rente_m: float) -> float:
    """Calculate total pension as sum of private and public pension.

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
def ges_rente_nach_grundr_m(
    ges_rente_vor_grundr_m: float,
    grundr_zuschlag_m: float,
    rentner: bool,
) -> float:
    """Calculate total public pension including Grundrentenzuschlag. Is
    only active after 2021 when Grundrente is in place.

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


@add_rounding_spec(params_key="ges_rente")
def ges_rente_vor_grundr_m(
    ges_rente_zugangsfaktor: float,
    entgeltp_update: float,
    rentenwert: float,
    rentner: bool,
) -> float:
    """Old-Age Pensions claim without Grundrentenzuschlag.
    The function follows the following equation:

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

    # Return 0 if person not yet retired
    if rentner:
        out = entgeltp_update * ges_rente_zugangsfaktor * rentenwert
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

    models 'Rentenformel':
    https://de.wikipedia.org/wiki/Rentenformel
    https://de.wikipedia.org/wiki/Rentenanpassungsformel

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

    # ToDo: Does the scaling bonus really apply to current wages or only to those that
    # ToDo: had been earned during GDR times?

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


def ges_rente_zugangsfaktor(
    geburtsjahr: int,
    rentner: bool,
    jahr_renteneintr: int,
    ges_rente_regelaltersgrenze: float,
    ges_rente_grenze_langjährig_frau: float,
    ges_rente_grenz_voll_altersrente: float,
    ges_rente_params: dict,
) -> float:
    """Calculate the zugangsfaktor based on the year the
    subject retired.

    At the regelaltersgrenze - normal retirement age (NRA), the agent is allowed to
    get pensions with his full claim. In general, if the agent retires earlier or later,
    the Zugangsfaktor and therefore the pension claim is higher or lower.

    Legal reference: § 77 Abs. 2 Nr. 2 SGB VI

    However, under certain conditions agents can receive their full pension claim
    (Zugangsfaktor=1) at an earlier age - full retirement age (FRA) -  (e.g. women,
    long term insured, disabled). That is the zugangsfaktor is 1 in [FRA, NRA].
    It only increases after the NRA for all agents without exeptions.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    rentner
        See basic input variable :ref:`rentner <rentner>`.
    jahr_renteneintr
        See basic input variable :ref:`jahr_renteneintr <jahr_renteneintr>`.
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    ges_rente_grenze_langjährig_frau
        See :func:`ges_rente_grenze_langjährig_frau`
    ges_rente_grenz_voll_altersrente
        See :func:`ges_rente_grenz_voll_altersrente`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """
    if rentner:
        # Calc age at retirement
        alter_renteneintritt = jahr_renteneintr - geburtsjahr

        # Calc difference to full retirement age (FRA)
        diff_volle_rente = alter_renteneintritt - ges_rente_grenz_voll_altersrente
        # Calc difference to FRA of long term insured or pension for women
        # (Altersgrenze langjährig Versicherte , Altersrente für Frauen).
        diff_longterm_pension_age = (
            alter_renteneintritt - ges_rente_grenze_langjährig_frau
        )
        # Calc difference to normal retirement age (Regelaltersgrenze)
        diff_regelrente = alter_renteneintritt - ges_rente_regelaltersgrenze
        faktor_pro_jahr_vorzeitig = ges_rente_params[
            "zugangsfaktor_veränderung_pro_jahr"
        ]["vorzeitiger_renteneintritt"]
        faktor_pro_jahr_später = ges_rente_params["zugangsfaktor_veränderung_pro_jahr"][
            "späterer_renteneintritt"
        ]

        # Zugangsfaktor <1: if retired before full retirement age, it is measured
        # relative to the threshold for long term insured or pension for women. Note:
        # we need both  diff_volle_rente and diff_longterm_pension_age here!
        # Zugangsfaktor >1: if retired after ges_rente_regelaltersgrenze
        # Zugangsfaktor =1: if retired between [FRA, NRA]
        # Note: Not yet implemented a feasibility check  - if person retires early but
        # is not women or long term insured it will calculate very high penalty
        # (pensionage 9000) this may happen if person is disabled or unemployed
        # before retirement - not implemented yet.
        if diff_volle_rente < 0:  # [ERA,FRA)
            out = 1 + diff_longterm_pension_age * faktor_pro_jahr_vorzeitig
        elif diff_regelrente > 0:  # [NRA, inf]
            out = 1 + diff_regelrente * faktor_pro_jahr_später
        else:  # [FRA,NRA]
            out = 1
        out = max(out, 0.0)
    # Return 0 if person not yet retired
    else:
        out = 0.0

    return out


def ges_rente_regelaltersgrenze(
    geburtsjahr: int, ges_rente_vorraus_regelrente: bool, ges_rente_params: dict
) -> float:
    """Calculates the age, at which a person is eligible to claim the regular pension.
        Normal retirement age (NRA). This pension cannot be claimed earlier than at the
        NRA, ie it does not serve as reference for calculating deductions. However, it
        serves as reference for calculating gains in the Zugangsfakor in case
        of later retirement.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.
    ges_rente_vorraus_regelrente
        See :func: ``ges_rente_vorraus_regelrente``.

    Returns
    -------
    """
    if ges_rente_vorraus_regelrente:
        out = piecewise_polynomial(
            x=geburtsjahr,
            thresholds=ges_rente_params["regelaltersgrenze"]["thresholds"],
            rates=ges_rente_params["regelaltersgrenze"]["rates"],
            intercepts_at_lower_thresholds=ges_rente_params["regelaltersgrenze"][
                "intercepts_at_lower_thresholds"
            ],
        )
    else:
        out = 9000  # arbitrary high number to represent non-feasible retirement age
    return out


def ges_rente_grenze_langjährig_frau(
    geburtsjahr: int,
    geburtsmonat: int,
    ges_rente_params: dict,
    ges_rente_vorraussetz_frauen: bool,
    ges_rente_vorraussetz_langjährig: bool,
) -> float:
    """Calculates the age, at which a longterm insured person or women is eligible to
        claim the full pension. Full retirement age (FRA) without deductions.
        This age is smaller or equal to the regelaltersgrenze (FRA<=NRA). These two
        pension schemes allow for early retirement with deductions. Hence these
        thresholds are needed as reference for calculating the
        zugangsfaktor.


    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.
    ges_rente_vorraussetz_frauen
        See :func:`ges_rente_vorraussetz_frauen`
    ges_rente_vorraussetz_langjährig
        See :func:``ges_rente_vorraussetz_langjährig``

    Returns
    -------
    returns the lowest full retirement age out of the pension schemes that allow for
    early claims with deductions.

    """

    if geburtsjahr < 1951:
        x_long = geburtsjahr + (geburtsmonat - 1) / 12
    else:
        x_long = geburtsjahr

    if ges_rente_vorraussetz_langjährig:
        pension_for_long = piecewise_polynomial(
            x=x_long,
            thresholds=ges_rente_params["altersgrenze_langjährig_versicherte"][
                "thresholds"
            ],
            rates=ges_rente_params["altersgrenze_langjährig_versicherte"]["rates"],
            intercepts_at_lower_thresholds=ges_rente_params[
                "altersgrenze_langjährig_versicherte"
            ]["intercepts_at_lower_thresholds"],
        )
    else:
        pension_for_long = (
            9000  # arbitrary high number to represent non-feasible retirement age
        )

    if geburtsjahr < 1945:
        x_wom = geburtsjahr + (geburtsmonat - 1) / 12
    else:
        x_wom = geburtsjahr

    if ges_rente_vorraussetz_frauen:
        pension_for_women = piecewise_polynomial(
            x=x_wom,
            thresholds=ges_rente_params["altersrente_für_frauen"]["thresholds"],
            rates=ges_rente_params["altersrente_für_frauen"]["rates"],
            intercepts_at_lower_thresholds=ges_rente_params["altersrente_für_frauen"][
                "intercepts_at_lower_thresholds"
            ],
        )
    else:
        pension_for_women = (
            9000  # arbitrary high number to represent non-feasible retirement age
        )

    out = min(pension_for_women, pension_for_long)

    return out


def ges_rente_grenz_voll_altersrente(
    geburtsjahr: int,
    ges_rente_params: dict,
    ges_rente_grenze_langjährig_frau: float,
    ges_rente_regelaltersgrenze: float,
    ges_rente_vorrauss_besond_lang: bool,
) -> float:
    """Calculates the age, at which a person is eligible to claim the full pension.
        Full retirement age (FRA) without deductions. This age is smaller or equal
        to the regelaltersgrenze (FRA<=NRA) and depends on personal characteristics
        as gender, insurance duration, health/disability, employment status.

    Parameters
    ----------
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    geburtsmonat
        See basic input variable :ref:`geburtsmonat <geburtsmonat>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.
    ges_rente_grenze_langjährig_frau
        See :func:`ges_rente_grenze_langjährig_frau`.
    ges_rente_regelaltersgrenze
        See :func:`ges_rente_regelaltersgrenze`.
    ges_rente_vorrauss_besond_lang
        See:func:`ges_rente_vorrauss_besond_lang`.

    Returns
    -------
    Lowest possible full retirement age (without deductions).
    """

    regelrente = ges_rente_regelaltersgrenze
    pension_long_or_women = ges_rente_grenze_langjährig_frau

    if ges_rente_vorrauss_besond_lang:
        pension_for_extralong = piecewise_polynomial(
            x=geburtsjahr,
            thresholds=ges_rente_params[
                "altersgrenze_besonders_langjährig_versicherte"
            ]["thresholds"],
            rates=ges_rente_params["altersgrenze_besonders_langjährig_versicherte"][
                "rates"
            ],
            intercepts_at_lower_thresholds=ges_rente_params[
                "altersgrenze_besonders_langjährig_versicherte"
            ]["intercepts_at_lower_thresholds"],
        )
    else:
        pension_for_extralong = (
            9000  # arbitrary high number to represent non-feasible retirement age
        )

    out = min([regelrente, pension_long_or_women, pension_for_extralong])

    return out


def ges_rente_vorraus_regelrente(ges_rente_wartezeit_5: float) -> bool:
    """Function determining the eligibility for the Regelaltersrente.

    Parameters
    ----------
    ges_rente_wartezeit_5
        See :func:`ges_rente_wartezeit_5`.
    """
    out = ges_rente_wartezeit_5 >= 5

    return out


def ges_rente_vorraussetz_frauen(
    weiblich: bool, ges_rente_wartezeit_15: float, jahre_beiträg_nach40: float
) -> bool:  # , ges_rente_params: dict
    """Function determining the eligibility for pension for women
        Wartezeit 15 years, contributions 10 years after age 40,
        being a women.

    Parameters
    ----------
    weiblich
        See basic input variable :ref:`weiblich <weiblich>`.
    ges_rente_wartezeit_15
        See :func:`ges_rente_wartezeit_15`
    jahre_beiträg_nach40
        See basic input variable :ref:`jahre_beiträg_nach40 <jahre_beiträg_nach40>`.
    Returns
    -------
    Eligibility as bool.

    """
    # todo: condition with employment after 40
    if weiblich and ges_rente_wartezeit_15 >= 15 and jahre_beiträg_nach40 >= 10:
        out = True
    else:
        out = False

    return out


def ges_rente_vorraussetz_langjährig(ges_rente_wartezeit_35: float) -> bool:
    """Determining the eligibility for pension for long-term insured
        Wartezeit 35 years.

    Parameters
    ----------
    ges_rente_wartezeit_35
        See :func: `ges_rente_wartezeit_35`.

    Returns
    -------
    Eligibility as bool.

    """
    out = ges_rente_wartezeit_35 >= 35

    return out


def ges_rente_vorrauss_besond_lang(ges_rente_wartezeit_45: float) -> bool:
    """Determining the eligibility for pension for very long-term insured
        Wartezeit 45 years. "Rente für besonders langjährig Versicherte"
        aka "Rente mit 63".

    Parameters
    ----------
    ges_rente_wartezeit_45
        See :func:`ges_rente_wartezeit_45`

    Returns
    -------
    Eligibility as bool.

    """

    out = ges_rente_wartezeit_45 >= 45

    return out


# todo implement eligibility function and eligibility in regelaltersrente function.
def ges_rente_wartezeit_5(
    pflichtbeitragszeit: float, freiw_beitragszeit: float, ersatzzeit: float
) -> float:
    """Aggregates time periods that are relevant for the general eligibility
    of the regular pension (regelaltersrente). "Allgemeine Wartezeit".

    Parameters
    ----------
    pflichtbeitragszeit
        See basic input variable :ref:`pflichtbeitragszeit <pflichtbeitragszeit>`.
    freiw_beitragszeit
        See basic input variable :ref:`freiw_beitragszeit <freiw_beitragszeit>`.
    ersatzzeit
        See basic input variable :ref:`ersatzzeit <ersatzzeit>`.

    Returns
    -------
    wartezeit in years
    """
    out = (pflichtbeitragszeit + freiw_beitragszeit + ersatzzeit) / 12

    return out


# todo imaybe implement default  for zeiten if vars
#  not available? somewhere swtich for eligibility in interface?


def ges_rente_wartezeit_15(
    pflichtbeitragszeit: float, freiw_beitragszeit: float, ersatzzeit: float
) -> float:
    """Aggregates time periods that are relevant for the pension
    for women and Leistungen zur Teilhabe. Wartezeit von 15 Jahren.

    Parameters
    ----------
    pflichtbeitragszeit
        See basic input variable :ref:`pflichtbeitragszeit <pflichtbeitragszeit>`.
    freiw_beitragszeit
        See basic input variable :ref:`freiw_beitragszeit <freiw_beitragszeit>`.
    ersatzzeit
        See basic input variable :ref:`ersatzzeit <ersatzzeit>`.

    Returns
    -------
    wartezeit in years
    """
    out = (pflichtbeitragszeit + freiw_beitragszeit + ersatzzeit) / 12

    return out


def ges_rente_wartezeit_35(
    rententrechtl_zeit: float,
    pflichtbeitragszeit: float,
    freiw_beitragszeit: float,
    anrechnungszeit: float,
    ersatzzeit: float,
    kinder_berückz: float,
    pflege9295_berückz: float,
) -> float:
    """Aggregates time periods that are relevant for the eligibility of pension
    for long-term insured. Wartezeit von 35 Jahren. All "rentenrechtliche Zeiten"
    are considered.

    Parameters
    ----------
    rententrechtl_zeit
        See basic input variable :ref:`rententrechtl_zeit <rententrechtl_zeit>`.
    pflichtbeitragszeit
        See basic input variable :ref:`pflichtbeitragszeit <pflichtbeitragszeit>`.
    freiw_beitragszeit
        See basic input variable :ref:`freiw_beitragszeit <freiw_beitragszeit>`.
    ersatzzeit
        See basic input variable :ref:`ersatzzeit <ersatzzeit>`.
    anrechnungszeit
        See basic input variable :ref:`anrechnungszeit <anrechnungszeit>`.
    kinder_berückz
        See basic input variable :ref:`kinder_berückz <kinder_berückz>`.
    pflege9295_berückz
        See basic input variable :ref:`pflege9295_berückz <pflege9295_berückz>`.

    Returns
    -------
    wartezeit in years

    """
    if rententrechtl_zeit > 0:  # is not missing
        out = rententrechtl_zeit / 12
    else:
        out = (
            pflichtbeitragszeit
            + freiw_beitragszeit
            + anrechnungszeit
            + ersatzzeit
            + pflege9295_berückz
            + kinder_berückz
        ) / 12
    return out


# seite 27 Dok _19_wartezeiten
def ges_rente_wartezeit_45(
    pflichtbeitragszeit: float,
    freiw_beitragszeit: float,
    anrechnungszeit_45: float,
    ersatzzeit: float,
    kinder_berückz: float,
    pflege9295_berückz: float,
) -> float:
    """Aggregates time periods that are relevant for the eligibility of pension
    for very long-term insured. Wartezeit von 45 Jahren. Not all "rentenrechtliche
    Zeiten" are considered. Years with voluntary contributions are only considered
    if at least 18 years of mandatory contributions (pflichtbeitragszeit). Not all
    anrechnungszeiten are considered, but only specific ones (e.g. ALG I, Kurzarbeit
    but not ALG II).

    Parameters
    ----------
    pflichtbeitragszeit
        See basic input variable :ref:`pflichtbeitragszeit <pflichtbeitragszeit>`.
    freiw_beitragszeit
        See basic input variable :ref:`freiw_beitragszeit <freiw_beitragszeit>`.
    ersatzzeit
        See basic input variable :ref:`ersatzzeit <ersatzzeit>`.
    anrechnungszeit_45
        See basic input variable :ref:`anrechnungszeit_45 <anrechnungszeit_45>`.
    kinder_berückz
        See basic input variable :ref:`kinder_berückz <kinder_berückz>`.
    pflege9295_berückz
        See basic input variable :ref:`pflege9295_berückz <pflege9295_berückz>`.

    Returns
    -------
    wartezeit in years
    """
    if pflichtbeitragszeit >= (18 * 12):
        freiwilligbeitr = freiw_beitragszeit
    else:
        freiwilligbeitr = 0

    out = (
        pflichtbeitragszeit
        + freiwilligbeitr
        + anrechnungszeit_45
        + ersatzzeit
        + pflege9295_berückz
        + kinder_berückz
    ) / 12

    return out
