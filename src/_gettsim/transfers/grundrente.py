from _gettsim.piecewise_functions import piecewise_polynomial
from _gettsim.shared import add_rounding_spec


@add_rounding_spec(rounding_key="ges_rente")
def grundr_zuschlag_m(
    grundr_zuschlag_vor_eink_anr_m: float, grundr_zuschlag_eink_m: float
) -> float:
    """Calculate Grundrentenzuschlag (additional monthly pensions payments resulting
    from Grundrente)

    Parameters
    ----------
    grundr_zuschlag_vor_eink_anr_m
        See :func:`grundr_zuschlag_vor_eink_anr_m`.
    grundr_zuschlag_eink_m
        See :func:`grundr_zuschlag_eink_m`.

    Returns
    -------

    """
    out = grundr_zuschlag_vor_eink_anr_m - grundr_zuschlag_eink_m
    return max(out, 0.0)


def _grundr_zuschlag_eink_vor_freibetrag_m(
    rente_vorj_vor_grundr_proxy_m: float,
    bruttolohn_vorj_m: float,
    eink_selbst_y: float,
    eink_vermietung_y: float,
    kapitaleink_y: float,
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
      depends on pension income through `ges_krankenv_beitr_m` -> `vorsorgeaufw` ->
      `freibeträge`

    Reference: § 97a Abs. 2 S. 1 SGB VI

    Parameters
    ----------
    rente_vorj_vor_grundr_proxy_m
        See :func:`rente_vorj_vor_grundr_proxy_m`.
    bruttolohn_vorj_m
        See :func:`bruttolohn_vorj_m`.
    eink_selbst_y
        See :func:`eink_selbst_y`.
    eink_vermietung_y
        See :func:`eink_vermietung_y`.
    kapitaleink_y
        See :func:`kapitaleink_y`.

    Returns
    -------

    """

    # Sum income over different income sources.
    out = (
        rente_vorj_vor_grundr_proxy_m
        + bruttolohn_vorj_m
        + eink_selbst_y / 12  # income from self-employment
        + eink_vermietung_y / 12  # rental income
        + kapitaleink_y / 12
    )

    return out


@add_rounding_spec(rounding_key="ges_rente")
def grundr_zuschlag_eink_m(
    _grundr_zuschlag_eink_vor_freibetrag_m_ehe: float,
    p_id_ehepartner: int,
    rentenwert: float,
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
    _grundr_zuschlag_eink_vor_freibetrag_m_ehe
        See :func:`_grundr_zuschlag_eink_vor_freibetrag_m_ehe`.
    p_id_ehepartner
        See :func:`p_id_ehepartner`.
    rentenwert
        See :func:`rentenwert`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.
    Returns
    -------

    """

    # Calculate relevant income following the crediting rules using the values for
    # singles and those for married subjects
    # Note: Thresholds are defined relativ to rentenwert which is implemented by
    # dividing the income by rentenwert and multiply rentenwert to the result.
    if p_id_ehepartner >= 0:
        einkommensanr_params = ges_rente_params["grundr_einkommensanr_verheiratet"]
    else:
        einkommensanr_params = ges_rente_params["grundr_einkommensanr_single"]

    out = (
        piecewise_polynomial(
            x=_grundr_zuschlag_eink_vor_freibetrag_m_ehe / rentenwert,
            thresholds=einkommensanr_params["thresholds"],
            rates=einkommensanr_params["rates"],
            intercepts_at_lower_thresholds=einkommensanr_params[
                "intercepts_at_lower_thresholds"
            ],
        )
        * rentenwert
    )

    return out


@add_rounding_spec(rounding_key="ges_rente")
def grundr_zuschlag_vor_eink_anr_m(
    grundr_zuschlag_bonus_entgeltp: float,
    grundr_bew_zeiten: int,
    rentenwert: float,
    ges_rente_zugangsfaktor: float,
    ges_rente_params: dict,
) -> float:
    """Calculate additional monthly pensions payments resulting from Grundrente, without
    taking into account income crediting rules.

    The Zugangsfaktor is limited to 1 and considered Grundrentezeiten
    are limited to 35 years (420 months).

    Parameters
    ----------
    grundr_zuschlag_bonus_entgeltp
        See :func:`grundr_zuschlag_bonus_entgeltp`.
    grundr_bew_zeiten
        See basic input variable
        :ref:`grundr_bew_zeiten <grundr_bew_zeiten>`.
    rentenwert
        See :func:`rentenwert`.
    ges_rente_zugangsfaktor
        See :func:`ges_rente_zugangsfaktor`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """

    # Winsorize Bewertungszeiten and Zugangsfaktor at maximum values
    grundr_bew_zeiten_wins = min(
        grundr_bew_zeiten, ges_rente_params["grundr_zeiten"]["max"]
    )
    ges_rente_zugangsfaktor_wins = min(
        ges_rente_zugangsfaktor, ges_rente_params["grundr_zugangsfaktor_max"]
    )

    out = (
        grundr_zuschlag_bonus_entgeltp
        * grundr_bew_zeiten_wins
        * rentenwert
        * ges_rente_zugangsfaktor_wins
    )
    return out


def grundr_bew_zeiten_avg_entgeltp(
    grundr_entgeltp: float, grundr_bew_zeiten: int
) -> float:
    """Compute average number of Entgeltpunkte earned per month of
    Grundrentenbewertungszeiten.

    Parameters
    ----------
    grundr_entgeltp
        See basic input variable
        :ref:`grundr_entgeltp <grundr_entgeltp>`.
    grundr_bew_zeiten
        See basic input variable
        :ref:`grundr_bew_zeiten <grundr_bew_zeiten>`.

    Returns
    -------

    """
    if grundr_bew_zeiten > 0:
        out = grundr_entgeltp / grundr_bew_zeiten

    # Return 0 if grundr_bew_zeiten is 0. Then, grundr_entgeltp should be 0, too.
    else:
        out = 0

    return out


@add_rounding_spec(rounding_key="ges_rente")
def grundr_zuschlag_höchstwert_m(grundr_zeiten: int, ges_rente_params: dict) -> float:
    """Calculate the maximum allowed number of average Entgeltpunkte (per month) after
    adding bonus of Entgeltpunkte for a given number of Grundrentenzeiten.

    Parameters
    ----------
    grundr_zeiten
        See basic input variable :ref:`grundr_zeiten <grundr_zeiten>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """
    # Calculate number of months above minimum threshold
    months_above_thresh = (
        min(grundr_zeiten, ges_rente_params["grundr_zeiten"]["max"])
        - ges_rente_params["grundr_zeiten"]["min"]
    )

    # Calculate höchstwert
    out = (
        ges_rente_params["grundr_höchstwert"]["base"]
        + ges_rente_params["grundr_höchstwert"]["increment"] * months_above_thresh
    )

    return out


@add_rounding_spec(rounding_key="ges_rente")
def grundr_zuschlag_bonus_entgeltp(
    grundr_bew_zeiten_avg_entgeltp: float,
    grundr_zuschlag_höchstwert_m: float,
    grundr_zeiten: int,
    ges_rente_params: dict,
) -> float:
    """Calculate additional Entgeltpunkte for pensioner.

    In general, the average of monthly Entgeltpunkte earnd in Grundrentenzeiten is
    doubled, or extended to the individual Höchstwert if doubling would exceed the
    Höchstwert. Then, the value is multiplied by 0.875.

    Legal reference: § 76g SGB VI

    Parameters
    ----------
    grundr_bew_zeiten_avg_entgeltp
        See :func:`grundr_bew_zeiten_avg_entgeltp`.
    grundr_zuschlag_höchstwert_m
        See :func:`grundr_zuschlag_höchstwert_m`.
    grundr_zeiten
        See basic input variable :ref:`grundr_zeiten <grundr_zeiten>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """

    # Return 0 if Grundrentenzeiten below minimum
    if grundr_zeiten < ges_rente_params["grundr_zeiten"]["min"]:
        out = 0.0
    else:
        # Case 1: Entgeltpunkte less than half of Höchstwert
        if grundr_bew_zeiten_avg_entgeltp <= (0.5 * grundr_zuschlag_höchstwert_m):
            out = grundr_bew_zeiten_avg_entgeltp

        # Case 2: Entgeltpunkte more than half of Höchstwert, but below Höchstwert
        elif grundr_bew_zeiten_avg_entgeltp < grundr_zuschlag_höchstwert_m:
            out = grundr_zuschlag_höchstwert_m - grundr_bew_zeiten_avg_entgeltp

        # Case 3: Entgeltpunkte above Höchstwert
        elif grundr_bew_zeiten_avg_entgeltp > grundr_zuschlag_höchstwert_m:
            out = 0.0

    # Multiply additional Engeltpunkte by factor
    out = out * ges_rente_params["grundr_faktor_bonus"]

    return out


@add_rounding_spec(rounding_key="ges_rente")
def rente_vorj_vor_grundr_proxy_m(  # noqa: PLR0913
    rentner: bool,
    priv_rente_m: float,
    jahr_renteneintr: int,
    geburtsjahr: int,
    alter: int,
    entgeltp_west: float,
    entgeltp_ost: float,
    ges_rente_zugangsfaktor: float,
    ges_rente_params: dict,
) -> float:
    """Estimated amount of public pensions of last year excluding Grundrentenzuschlag.

    Parameters
    ----------
    rentner
        See basic input variable :ref:`rentner <rentner>`.
    priv_rente_m
        See basic input variable :ref:`priv_rente_m <priv_rente_m>`. Assume this did not
        change from last year.
    jahr_renteneintr
        See basic input variable :ref:`jahr_renteneintr <jahr_renteneintr>`.
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    entgeltp_west
        See basic input variable :ref:`entgeltp_west <entgeltp_west>`.
    entgeltp_ost
        See basic input variable :ref:`entgeltp_ost <entgeltp_ost>`.
    ges_rente_zugangsfaktor
        See :func:`ges_rente_zugangsfaktor`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """

    # Calculate if subect was retired last year
    if rentner:
        rentner_vorjahr = jahr_renteneintr < geburtsjahr + alter
    else:
        rentner_vorjahr = False

    if rentner_vorjahr:
        out = (
            entgeltp_west * ges_rente_params["rentenwert_vorjahr"]["west"]
            + entgeltp_ost * ges_rente_params["rentenwert_vorjahr"]["ost"]
        ) * ges_rente_zugangsfaktor + priv_rente_m
    else:
        out = 0.0

    return out


def grundr_berechtigt(grundr_zeiten: int, ges_rente_params: dict) -> bool:
    """Whether person has accumulated enough insured years to be eligible.

    Parameters
    ----------
    grundr_zeiten
        See :func:`grundr_zeiten`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """
    out = grundr_zeiten >= ges_rente_params["grundr_zeiten"]["min"]
    return out
