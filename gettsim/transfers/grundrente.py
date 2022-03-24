from gettsim.piecewise_functions import piecewise_polynomial
from gettsim.shared import add_rounding_spec
from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries


@add_rounding_spec(params_key="ges_rente")
def grundr_zuschlag_m(
    grundr_zuschlag_vor_eink_anr_m: FloatSeries, grundr_zuschlag_eink_m: FloatSeries
) -> FloatSeries:
    """Calculate Grundrentenzuschlag (additional monthly pensions payments
    resulting from Grundrente)

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
    rente_vorj_vor_grundr_proxy_m: FloatSeries,
    bruttolohn_vorj_m: FloatSeries,
    eink_selbst: FloatSeries,
    vermiet_eink: FloatSeries,
    kapitaleink: FloatSeries,
) -> FloatSeries:
    """Calculate total income relevant for Grundrentenzuschlag before deductions are
    subtracted.

    Some notes:

    - The Grundrentenzuschlag (in previous years) is not part of the relevant income and
      does not lower the Grundrentenzuschlag (reference: § 97a Abs. 2 S. 7 SGB VI).
    - The Deutsche Rentenversicherung uses the income of the year two to three years
      ago to be able to use administrative data on this income for the calculation:
      "It can be assumed that the tax office regularly has the data two years after
      the end of the assessment period, which can be retrieved from the pension
      insurance."
    - Warning: Currently, earnings of dependent work and pensions are based on the
      last year, and other income on the current year instead of the year
      two years ago to avoid the need for several new input variables.

    # ToDo: Freibeträge for income are currently not considered
    # ToDo: as freibeträge_tu depends on pension income through
    # ToDo: `ges_krankenv_beitr_m` -> `vorsorge` -> `freibeträge`

    Reference: § 97a Abs. 2 S. 1 SGB VI

    Parameters
    ----------
    rente_vorj_vor_grundr_proxy_m
        See :func:`rente_vorj_vor_grundr_proxy_m`.
    bruttolohn_vorj_m
        See :func:`bruttolohn_vorj_m`.
    eink_selbst
        See :func:`eink_selbst`.
    vermiet_eink
        See :func:`vermiet_eink`.
    kapitaleink
        See :func:`kapitaleink`.

    Returns
    -------

    """

    # Sum income over different income sources.
    out = (
        rente_vorj_vor_grundr_proxy_m
        + bruttolohn_vorj_m
        + eink_selbst / 12  # income from self-employment
        + vermiet_eink / 12  # rental income
        + kapitaleink / 12
    )

    return out


@add_rounding_spec(params_key="ges_rente")
def grundr_zuschlag_eink_m(
    _grundr_zuschlag_eink_vor_freibetrag_m_tu: FloatSeries,
    gemeinsam_veranlagt_tu: BoolSeries,
    rentenwert: FloatSeries,
    ges_rente_params: dict,
) -> FloatSeries:
    """Calculate income which is deducted from Grundrentenzuschlag.

    Apply allowances. There are upper and lower thresholds for singles and
    couples. 60% of income between the upper and lower threshold is credited against
    the Grundrentenzuschlag. All the income above the upper threshold is credited
    against the Grundrentenzuschlag.

    Reference: § 97a Abs. 4 S. 2, 4 SGB VI

    Parameters
    ----------
    _grundr_zuschlag_eink_vor_freibetrag_m_tu
        See :func:`_grundr_zuschlag_eink_vor_freibetrag_m_tu`.
    gemeinsam_veranlagt_tu
        See :func:`gemeinsam_veranlagt_tu`.
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
    if gemeinsam_veranlagt_tu:
        einkommensanr_params = ges_rente_params["grundr_einkommensanr_verheiratet"]
    else:
        einkommensanr_params = ges_rente_params["grundr_einkommensanr_single"]

    out = (
        piecewise_polynomial(
            x=_grundr_zuschlag_eink_vor_freibetrag_m_tu / rentenwert,
            thresholds=einkommensanr_params["thresholds"],
            rates=einkommensanr_params["rates"],
            intercepts_at_lower_thresholds=einkommensanr_params[
                "intercepts_at_lower_thresholds"
            ],
        )
        * rentenwert
    )

    return out


@add_rounding_spec(params_key="ges_rente")
def grundr_zuschlag_vor_eink_anr_m(
    grundr_zuschlag_bonus_entgeltp: FloatSeries,
    grundr_bew_zeiten: IntSeries,
    rentenwert: FloatSeries,
    ges_rente_zugangsfaktor: FloatSeries,
    ges_rente_params: dict,
) -> FloatSeries:
    """Calculate additional monthly pensions payments resulting from
    Grundrente, without taking into account income crediting rules.

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
    if grundr_bew_zeiten > ges_rente_params["grundr_zeiten"]["max"]:
        grundr_bew_zeiten = ges_rente_params["grundr_zeiten"]["max"]
    else:
        grundr_bew_zeiten = grundr_bew_zeiten

    if ges_rente_zugangsfaktor > ges_rente_params["grundr_zugangsfaktor_max"]:
        ges_rente_zugangsfaktor = ges_rente_params["grundr_zugangsfaktor_max"]
    else:
        ges_rente_zugangsfaktor = ges_rente_zugangsfaktor

    out = (
        grundr_zuschlag_bonus_entgeltp
        * grundr_bew_zeiten
        * rentenwert
        * ges_rente_zugangsfaktor
    )
    return out


def grundr_bew_zeiten_avg_entgeltp(
    grundr_entgeltp: FloatSeries, grundr_bew_zeiten: IntSeries
) -> FloatSeries:
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
    out = grundr_entgeltp / grundr_bew_zeiten
    return out


@add_rounding_spec(params_key="ges_rente")
def grundr_zuschlag_höchstwert_m(
    grundr_zeiten: IntSeries, ges_rente_params: dict
) -> FloatSeries:
    """Calculates the maximum allowed number of average Entgeltpunkte (per month)
    after adding bonus of Entgeltpunkte for a given number of Grundrentenzeiten.

    Parameters
    ----------
    grundr_zeiten
        See basic input variable :ref:`grundr_zeiten <grundr_zeiten>`.
    ges_rente_params
        See params documentation :ref:`ges_rente_params <ges_rente_params>`.

    Returns
    -------

    """
    if grundr_zeiten > ges_rente_params["grundr_zeiten"]["max"]:
        grundr_zeiten = ges_rente_params["grundr_zeiten"]["max"]
    else:
        grundr_zeiten = grundr_zeiten

    # Calculate number of months above minimum threshold
    months_above_thresh = grundr_zeiten - ges_rente_params["grundr_zeiten"]["min"]

    # Calculate höchstwert
    out = (
        ges_rente_params["grundr_höchstwert"]["base"]
        + ges_rente_params["grundr_höchstwert"]["increment"] * months_above_thresh
    )

    return out


@add_rounding_spec(params_key="ges_rente")
def grundr_zuschlag_bonus_entgeltp(
    grundr_bew_zeiten_avg_entgeltp: FloatSeries,
    grundr_zuschlag_höchstwert_m: FloatSeries,
    grundr_zeiten: IntSeries,
    ges_rente_params: dict,
) -> FloatSeries:
    """Calculate additional Entgeltpunkte for pensioner.

    In general, the average of monthly Entgeltpunkte earnd in Grundrentenzeiten is
    doubled, or extended to the individual Höchstwert if doubling would exceed the
    Höchstwert. Then, the value is multiplied by 0.875.

    Legal reference: § 76g SGB VI

    # ToDo: Revise when transitioning to scalars. In particular, adjust
    # ToDO: piecewise_polynomial to allow for individual specific thresholds
    # ToDo: and get rid of hard-coded numbers (0.5)

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


@add_rounding_spec(params_key="ges_rente")
def rente_vorj_vor_grundr_proxy_m(
    rentner: BoolSeries,
    rentenwert_vorjahr: FloatSeries,
    priv_rente_m: FloatSeries,
    jahr_renteneintr: IntSeries,
    geburtsjahr: IntSeries,
    alter: IntSeries,
    entgeltp: FloatSeries,
    ges_rente_zugangsfaktor: FloatSeries,
) -> FloatSeries:
    """Estimated amount of public pensions of last year excluding Grundrentenzuschlag.
    rentner
        See basic input variable :ref:`rentner <rentner>`.
    rentenwert_vorjahr
        See :func:`rentenwert_vorjahr`.
    priv_rente_m
        See basic input variable :ref:`priv_rente_m <priv_rente_m>`.
    jahr_renteneintr
        See basic input variable :ref:`jahr_renteneintr <jahr_renteneintr>`.
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    entgeltp
        See basic input variable :ref:`entgeltp <entgeltp>`.
    ges_rente_zugangsfaktor
        See :func:`ges_rente_zugangsfaktor`.

    Returns
    -------
    """

    if rentner:
        # Assume priv_rente_m did not change
        # ToDo: Use current_year as argument of this function once we addressed
        # ToDo: issue #211
        # Calculate if subect was retired last year
        current_year = geburtsjahr + alter
        rentner_vorjahr = jahr_renteneintr <= current_year - 1
        if not rentner_vorjahr:
            out = 0.0
        else:
            out = entgeltp * ges_rente_zugangsfaktor * rentenwert_vorjahr + priv_rente_m
    else:
        out = 0.0

    return out


def grundr_berechtigt(grundr_zeiten: IntSeries, ges_rente_params: dict) -> BoolSeries:
    """Indicates that person is not entitled to Freibetragsregelung.

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
