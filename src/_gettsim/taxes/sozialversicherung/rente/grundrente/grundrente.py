from _gettsim.function_types import policy_function
from _gettsim.piecewise_functions import piecewise_polynomial


@policy_function(params_key_for_rounding="ges_rente")
def betrag_m(basisbetrag_m: float, anzurechnendes_einkommen_m: float) -> float:
    """Calculate Grundrentenzuschlag (additional monthly pensions payments resulting
    from Grundrente)

    Parameters
    ----------
    basisbetrag_m
        See :func:`basisbetrag_m`.
    anzurechnendes_einkommen_m
        See :func:`anzurechnendes_einkommen_m`.

    Returns
    -------

    """
    out = basisbetrag_m - anzurechnendes_einkommen_m
    return max(out, 0.0)


@policy_function()
def einkommen_m(
    proxy_rente_vorjahr_m: float,
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_vorjahr_m: float,
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m: float,
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m: float,
    einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y: float,
) -> float:
    """Calculate total income relevant for Grundrentenzuschlag before deductions are
    subtracted.

    Some notes:

    - The Grundrentenzuschlag (in previous years) is not part of the relevant income and
      does not lower the Grundrentenzuschlag (reference: § 97a Abs. 2 S. 7 SGB VI).
    - The Deutsche Rentenversicherung uses the income of the year two to three years ago
      to be able to use administrative data on this income for the calculation: "It can
      be assumed that the tax office regularly has the data two years after the end of
      the assessment period, which can be retrieved from the pension insurance."
    - Warning: Currently, earnings of dependent work and pensions are based on the last
      year, and other income on the current year instead of the year two years ago to
      avoid the need for several new input variables.
    - Warning: Freibeträge for income are currently not considered as `freibeträge_y`
      depends on pension income through
      `sozialversicherung__kranken__beitrag__betrag_versicherter_m` ->
      `vorsorgeaufw` -> `freibeträge`

    Reference: § 97a Abs. 2 S. 1 SGB VI

    Parameters
    ----------
    proxy_rente_vorjahr_m
        See :func:`proxy_rente_vorjahr_m`.
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_vorjahr_m
        See :func:`einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_vorjahr_m`.
    einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m
        See :func:`einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m`.
    einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m
        See :func:`einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m`.
    einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y
        See :func:`einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y`.

    Returns
    -------

    """

    # Sum income over different income sources.
    out = (
        proxy_rente_vorjahr_m
        + einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_vorjahr_m
        + einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m  # income from self-employment
        + einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m  # rental income
        + einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y
    )

    return out


@policy_function(params_key_for_rounding="ges_rente")
def anzurechnendes_einkommen_m(
    einkommen_m_ehe: float,
    demographics__anzahl_personen_ehe: int,
    sozialversicherung__rente__altersrente__rentenwert: float,
    ges_rente_params: dict,
) -> float:
    """Calculate income which is deducted from Grundrentenzuschlag.

    Apply allowances. There are upper and lower thresholds for singles and
    couples. 60% of income between the upper and lower threshold is credited against
    the Grundrentenzuschlag. All the income above the upper threshold is credited
    against the Grundrentenzuschlag.

    Reference: § 97a Abs. 4 S. 2, 4 SGB VI

    Parameters
    ----------
    einkommen_m_ehe
        See :func:`einkommen_m_ehe`.
    demographics__anzahl_personen_ehe
        See :func:`demographics__anzahl_personen_ehe`.
    sozialversicherung__rente__altersrente__rentenwert
        See :func:`sozialversicherung__rente__altersrente__rentenwert`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.
    Returns
    -------

    """

    # Calculate relevant income following the crediting rules using the values for
    # singles and those for married subjects
    # Note: Thresholds are defined relativ to rentenwert which is implemented by
    # dividing the income by rentenwert and multiply rentenwert to the result.
    if demographics__anzahl_personen_ehe == 1:
        einkommensanr_params = ges_rente_params["grundr_einkommensanr_verheiratet"]
    else:
        einkommensanr_params = ges_rente_params["grundr_einkommensanr_single"]

    out = (
        piecewise_polynomial(
            x=einkommen_m_ehe / sozialversicherung__rente__altersrente__rentenwert,
            thresholds=einkommensanr_params["thresholds"],
            rates=einkommensanr_params["rates"],
            intercepts_at_lower_thresholds=einkommensanr_params[
                "intercepts_at_lower_thresholds"
            ],
        )
        * sozialversicherung__rente__altersrente__rentenwert
    )

    return out


@policy_function(params_key_for_rounding="ges_rente")
def basisbetrag_m(
    durchschnittliche_entgeltpunkte_zuschlag: float,
    bewertungszeiten_m: int,
    sozialversicherung__rente__altersrente__rentenwert: float,
    sozialversicherung__rente__altersrente__zugangsfaktor: float,
    ges_rente_params: dict,
) -> float:
    """Calculate additional monthly pensions payments resulting from Grundrente, without
    taking into account income crediting rules.

    The Zugangsfaktor is limited to 1 and considered Grundrentezeiten
    are limited to 35 years (420 months).

    Parameters
    ----------
    durchschnittliche_entgeltpunkte_zuschlag
        See :func:`durchschnittliche_entgeltpunkte_zuschlag`.
    bewertungszeiten_m
        See basic input variable
        :ref:`bewertungszeiten_m <bewertungszeiten_m>`.
    sozialversicherung__rente__altersrente__rentenwert
        See :func:`sozialversicherung__rente__altersrente__rentenwert`.
    sozialversicherung__rente__altersrente__zugangsfaktor
        See :func:`sozialversicherung__rente__altersrente__zugangsfaktor`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """

    # Winsorize Bewertungszeiten and Zugangsfaktor at maximum values
    bewertungszeiten_m_wins = min(
        bewertungszeiten_m,
        ges_rente_params["grundrentenzeiten_m"]["max"],
    )
    ges_rente_zugangsfaktor_wins = min(
        sozialversicherung__rente__altersrente__zugangsfaktor,
        ges_rente_params["grundr_zugangsfaktor_max"],
    )

    out = (
        durchschnittliche_entgeltpunkte_zuschlag
        * bewertungszeiten_m_wins
        * sozialversicherung__rente__altersrente__rentenwert
        * ges_rente_zugangsfaktor_wins
    )
    return out


@policy_function()
def durchschnittliche_entgeltpunkte(
    mean_entgeltpunkte: float, bewertungszeiten_m: int
) -> float:
    """Compute average number of Entgeltpunkte earned per month of
    Grundrentenbewertungszeiten.

    Parameters
    ----------
    mean_entgeltpunkte
        See basic input variable
        :ref:`mean_entgeltpunkte <mean_entgeltpunkte>`.
    bewertungszeiten_m
        See basic input variable
        :ref:`bewertungszeiten_m <bewertungszeiten_m>`.

    Returns
    -------

    """
    if bewertungszeiten_m > 0:
        out = mean_entgeltpunkte / bewertungszeiten_m

    # Return 0 if bewertungszeiten_m is 0. Then, mean_entgeltpunkte should be 0, too.
    else:
        out = 0

    return out


@policy_function(params_key_for_rounding="ges_rente")
def höchstbetrag_m(
    grundrentenzeiten_m: int,
    ges_rente_params: dict,
) -> float:
    """Calculate the maximum allowed number of average Entgeltpunkte (per month) after
    adding bonus of Entgeltpunkte for a given number of Grundrentenzeiten.

    Parameters
    ----------
    grundrentenzeiten_m
        See basic input variable :ref:`grundrentenzeiten_m <grundrentenzeiten_m>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """
    # Calculate number of months above minimum threshold
    months_above_thresh = (
        min(
            grundrentenzeiten_m,
            ges_rente_params["grundrentenzeiten_m"]["max"],
        )
        - ges_rente_params["grundrentenzeiten_m"]["min"]
    )

    # Calculate höchstwert
    out = (
        ges_rente_params["grundr_höchstwert"]["base"]
        + ges_rente_params["grundr_höchstwert"]["increment"] * months_above_thresh
    )

    return out


@policy_function(params_key_for_rounding="ges_rente")
def durchschnittliche_entgeltpunkte_zuschlag(
    durchschnittliche_entgeltpunkte: float,
    höchstbetrag_m: float,
    grundrentenzeiten_m: int,
    ges_rente_params: dict,
) -> float:
    """Calculate additional Entgeltpunkte for pensioner.

    In general, the average of monthly Entgeltpunkte earnd in Grundrentenzeiten is
    doubled, or extended to the individual Höchstwert if doubling would exceed the
    Höchstwert. Then, the value is multiplied by 0.875.

    Legal reference: § 76g SGB VI

    Parameters
    ----------
    durchschnittliche_entgeltpunkte
        See :func:`durchschnittliche_entgeltpunkte`.
    höchstbetrag_m
        See :func:`höchstbetrag_m`.
    grundrentenzeiten_m
        See basic input variable :ref:`grundrentenzeiten_m <grundrentenzeiten_m>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """

    # Return 0 if Grundrentenzeiten below minimum
    if grundrentenzeiten_m < ges_rente_params["grundrentenzeiten_m"]["min"]:
        out = 0.0
    else:
        # Case 1: Entgeltpunkte less than half of Höchstwert
        if durchschnittliche_entgeltpunkte <= (0.5 * höchstbetrag_m):
            out = durchschnittliche_entgeltpunkte

        # Case 2: Entgeltpunkte more than half of Höchstwert, but below Höchstwert
        elif durchschnittliche_entgeltpunkte < höchstbetrag_m:
            out = höchstbetrag_m - durchschnittliche_entgeltpunkte

        # Case 3: Entgeltpunkte above Höchstwert
        elif durchschnittliche_entgeltpunkte > höchstbetrag_m:
            out = 0.0

    # Multiply additional Engeltpunkte by factor
    out = out * ges_rente_params["grundr_faktor_bonus"]

    return out


@policy_function(params_key_for_rounding="ges_rente")
def proxy_rente_vorjahr_m(  # noqa: PLR0913
    sozialversicherung__rente__bezieht_rente: bool,
    sozialversicherung__rente__private_rente_betrag_m: float,
    sozialversicherung__rente__jahr_renteneintritt: int,
    demographics__geburtsjahr: int,
    demographics__alter: int,
    sozialversicherung__rente__entgeltpunkte_west: float,
    sozialversicherung__rente__entgeltpunkte_ost: float,
    sozialversicherung__rente__altersrente__zugangsfaktor: float,
    ges_rente_params: dict,
) -> float:
    """Estimated amount of public pensions of last year excluding Grundrentenzuschlag.

    Parameters
    ----------
    sozialversicherung__rente__bezieht_rente
        See basic input variable :ref:`sozialversicherung__rente__bezieht_rente <sozialversicherung__rente__bezieht_rente>`.
    sozialversicherung__rente__private_rente_betrag_m
        See basic input variable :ref:`sozialversicherung__rente__private_rente_betrag_m <sozialversicherung__rente__private_rente_betrag_m>`. Assume this did not
        change from last year.
    sozialversicherung__rente__jahr_renteneintritt
        See basic input variable :ref:`sozialversicherung__rente__jahr_renteneintritt <sozialversicherung__rente__jahr_renteneintritt>`.
    demographics__geburtsjahr
        See basic input variable :ref:`demographics__geburtsjahr <demographics__geburtsjahr>`.
    demographics__alter
        See basic input variable :ref:`demographics__alter <demographics__alter>`.
    sozialversicherung__rente__entgeltpunkte_west
        See basic input variable :ref:`sozialversicherung__rente__entgeltpunkte_west <sozialversicherung__rente__entgeltpunkte_west>`.
    sozialversicherung__rente__entgeltpunkte_ost
        See basic input variable :ref:`sozialversicherung__rente__entgeltpunkte_ost <sozialversicherung__rente__entgeltpunkte_ost>`.
    sozialversicherung__rente__altersrente__zugangsfaktor
        See :func:`sozialversicherung__rente__altersrente__zugangsfaktor`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """

    # Calculate if subect was retired last year
    if sozialversicherung__rente__bezieht_rente:
        rentner_vorjahr = (
            sozialversicherung__rente__jahr_renteneintritt
            < demographics__geburtsjahr + demographics__alter
        )
    else:
        rentner_vorjahr = False

    if rentner_vorjahr:
        out = (
            (
                sozialversicherung__rente__entgeltpunkte_west
                * ges_rente_params["rentenwert_vorjahr"]["west"]
                + sozialversicherung__rente__entgeltpunkte_ost
                * ges_rente_params["rentenwert_vorjahr"]["ost"]
            )
            * sozialversicherung__rente__altersrente__zugangsfaktor
            + sozialversicherung__rente__private_rente_betrag_m
        )
    else:
        out = 0.0

    return out


@policy_function()
def grundsätzlich_anspruchsberechtigt(
    grundrentenzeiten_m: int,
    ges_rente_params: dict,
) -> bool:
    """Whether person has accumulated enough insured years to be eligible.

    Parameters
    ----------
    grundrentenzeiten_m
        See :func:`grundrentenzeiten_m`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """
    out = grundrentenzeiten_m >= ges_rente_params["grundrentenzeiten_m"]["min"]
    return out
