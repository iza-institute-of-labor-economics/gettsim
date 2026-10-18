from __future__ import annotations

from typing import TYPE_CHECKING

from gettsim.tt import (
    RoundingSpec,
    TTSIMUnit,
    cast_ttsim_unit,
    policy_function,
)

if TYPE_CHECKING:
    from types import ModuleType


@policy_function(
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_MONTH,
        base=0.01,
        direction="nearest",
        reference="§ 123 SGB VI Abs. 1",
    ),
    start_date="2021-01-01",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def betrag_m(basisbetrag_m: float, anzurechnendes_einkommen_m: float) -> float:
    """Additional monthly pensions payments (Grundrentenzuschlag)."""
    out = basisbetrag_m - anzurechnendes_einkommen_m
    return max(out, 0.0)


@policy_function(
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_MONTH,
        base=0.01,
        direction="nearest",
        reference="§ 123 SGB VI Abs. 1",
    ),
    start_date="2021-01-01",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def anzurechnendes_einkommen_m(
    einkommen_vorjahr_m_ehe: float,
    familie__anzahl_personen_ehe: int,
    rentenwert_für_einkommensgrenzen_m: float,
    einkommensgrenzen_ohne_ehegatte: dict[str, float],
    einkommensgrenzen_mit_ehegatte: dict[str, float],
    anrechnungssätze: dict[str, float],
    xnp: ModuleType,
) -> float:
    """Income which is deducted from Grundrentenzuschlag.

    The income of the Berechtigter and their spouse is added up. Above the lower
    threshold, 60 % of the income up to the upper threshold is credited; above the
    upper threshold, the full excess is credited as well. Married Berechtigte get the
    higher thresholds for couples, also if the spouse has no income or lives apart.

    Each threshold is a multiple of the Rentenwert, rounded up to a full Euro. Changes
    of the thresholds take effect on 1 January, so the Rentenwert of the previous
    1 July applies for the whole calendar year.

    Reference: § 97a Abs. 1, Abs. 4 S. 1-5 SGB VI
    """
    # The couple's income is compared with the thresholds, and the result is credited
    # in full against each spouse's Zuschlag, so the sum loses its group level here.
    einkommen_m = cast_ttsim_unit(
        einkommen_vorjahr_m_ehe, unit=TTSIMUnit.CURRENCY.PER_MONTH
    )
    ohne_ehegatte = familie__anzahl_personen_ehe == 1
    untere_grenze_m = xnp.ceil(
        rentenwert_für_einkommensgrenzen_m
        * (
            einkommensgrenzen_ohne_ehegatte["untere_grenze"]
            if ohne_ehegatte
            else einkommensgrenzen_mit_ehegatte["untere_grenze"]
        )
    )
    obere_grenze_m = xnp.ceil(
        rentenwert_für_einkommensgrenzen_m
        * (
            einkommensgrenzen_ohne_ehegatte["obere_grenze"]
            if ohne_ehegatte
            else einkommensgrenzen_mit_ehegatte["obere_grenze"]
        )
    )

    einkommen_zwischen_den_grenzen = min(
        max(einkommen_m - untere_grenze_m, 0.0),
        obere_grenze_m - untere_grenze_m,
    )
    einkommen_über_der_oberen_grenze = max(einkommen_m - obere_grenze_m, 0.0)
    return (
        anrechnungssätze["zwischen_den_grenzen"] * einkommen_zwischen_den_grenzen
        + anrechnungssätze["über_der_oberen_grenze"] * einkommen_über_der_oberen_grenze
    )


@policy_function(
    rounding_spec=RoundingSpec(
        unit=TTSIMUnit.EUR.PER_MONTH,
        base=0.01,
        direction="nearest",
        reference="§ 123 SGB VI Abs. 1",
    ),
    start_date="2021-01-01",
    unit=TTSIMUnit.CURRENCY.PER_MONTH,
)
def basisbetrag_m(
    mean_entgeltpunkte_zuschlag_m: float,
    bewertungszeiten_monate: int,
    sozialversicherung__rente__rentenwert_m: float,
    sozialversicherung__rente__altersrente__zugangsfaktor: float,
    maximaler_zugangsfaktor: float,
    berücksichtigte_wartezeit_monate: dict[str, int],
) -> float:
    """Grundrente without taking into account income crediting rules.

    The Zugangsfaktor is limited to 1 and considered Grundrentezeiten are limited to
    35 years (420 months).
    """
    bewertungszeiten = min(
        bewertungszeiten_monate,
        berücksichtigte_wartezeit_monate["max"],
    )
    zugangsfaktor = min(
        sozialversicherung__rente__altersrente__zugangsfaktor,
        maximaler_zugangsfaktor,
    )

    return (
        mean_entgeltpunkte_zuschlag_m
        * bewertungszeiten
        * sozialversicherung__rente__rentenwert_m
        * zugangsfaktor
    )


@policy_function(start_date="2021-01-01", unit=TTSIMUnit.DIMENSIONLESS.PER_MONTH)
def mean_entgeltpunkte_pro_bewertungsmonat_m(
    mean_entgeltpunkte: float,
    bewertungszeiten_monate: int,
) -> float:
    """Average number of Entgeltpunkte earned per month of Grundrentenbewertungszeiten."""
    if bewertungszeiten_monate > 0:
        out = mean_entgeltpunkte / bewertungszeiten_monate

    # Return 0 if bewertungszeiten_monate is 0. Then, mean_entgeltpunkte should be 0, too.
    else:
        out = 0

    return out


@policy_function(
    rounding_spec=RoundingSpec(
        base=0.0001,
        direction="nearest",
        reference="§76g SGB VI Abs. 4 Nr. 4",
    ),
    start_date="2021-01-01",
    unit=TTSIMUnit.DIMENSIONLESS.PER_MONTH,
)
def höchstbetrag_m(
    grundrentenzeiten_monate: int,
    berücksichtigte_wartezeit_monate: dict[str, int],
    höchstwert_der_entgeltpunkte: dict[str, float],
) -> float:
    """Maximum allowed number of average Entgeltpunkte."""
    # The number of increment-steps above the threshold — a plain count multiplying
    # the per-month increment.
    months_above_thresh = cast_ttsim_unit(
        min(
            grundrentenzeiten_monate,
            berücksichtigte_wartezeit_monate["max"],
        )
        - berücksichtigte_wartezeit_monate["min"],
        unit=TTSIMUnit.DIMENSIONLESS,
    )

    return (
        höchstwert_der_entgeltpunkte["base"]
        + höchstwert_der_entgeltpunkte["increment"] * months_above_thresh
    )


@policy_function(
    rounding_spec=RoundingSpec(
        base=0.0001,
        direction="nearest",
        reference="§ 123 SGB VI Abs. 1",
    ),
    start_date="2021-01-01",
    unit=TTSIMUnit.DIMENSIONLESS.PER_MONTH,
)
def mean_entgeltpunkte_zuschlag_m(
    mean_entgeltpunkte_pro_bewertungsmonat_m: float,
    höchstbetrag_m: float,
    grundrentenzeiten_monate: int,
    berücksichtigte_wartezeit_monate: dict[str, int],
    bonusfaktor: float,
) -> float:
    """Additional Entgeltpunkte.

    In general, the average of monthly Entgeltpunkte earnd in Grundrentenzeiten is
    doubled, or extended to the individual Höchstwert if doubling would exceed the
    Höchstwert. Then, the value is multiplied by 0.875.

    Legal reference: § 76g SGB VI
    """
    # A per-month zero for the "no additional Entgeltpunkte" branches, so every branch
    # yields the declared `1 / month` (a bare 0.0 would infer dimensionless here).
    kein_zuschlag_m = cast_ttsim_unit(0.0, unit=TTSIMUnit.DIMENSIONLESS.PER_MONTH)

    out = kein_zuschlag_m
    # Return 0 if Grundrentenzeiten below minimum
    if grundrentenzeiten_monate < berücksichtigte_wartezeit_monate["min"]:
        out = kein_zuschlag_m
    else:
        # Case 1: Entgeltpunkte less than half of Höchstwert
        if mean_entgeltpunkte_pro_bewertungsmonat_m <= (0.5 * höchstbetrag_m):
            out = mean_entgeltpunkte_pro_bewertungsmonat_m

        # Case 2: Entgeltpunkte more than half of Höchstwert, but below Höchstwert
        elif mean_entgeltpunkte_pro_bewertungsmonat_m < höchstbetrag_m:
            out = höchstbetrag_m - mean_entgeltpunkte_pro_bewertungsmonat_m

        # Case 3: Entgeltpunkte above Höchstwert
        elif mean_entgeltpunkte_pro_bewertungsmonat_m > höchstbetrag_m:
            out = kein_zuschlag_m

    # Multiply additional Engeltpunkte by factor
    return out * bonusfaktor


@policy_function(start_date="2021-01-01", unit=TTSIMUnit.DIMENSIONLESS)
def grundsätzlich_anspruchsberechtigt(
    grundrentenzeiten_monate: int,
    berücksichtigte_wartezeit_monate: dict[str, int],
) -> bool:
    """Has accumulated enough insured years to be eligible."""
    return grundrentenzeiten_monate >= berücksichtigte_wartezeit_monate["min"]


@policy_function(start_date="2021-01-01", unit=TTSIMUnit.CURRENCY.PER_YEAR)
def einkommen_für_einkommensberechnung_im_folgejahr_y(
    einkommensteuer__zu_versteuerndes_einkommen_y_sn: float,
    einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y_sn: float,
    einkommensteuer__einkünfte__sonstige__rente__besteuerungsanteil: float,
    einkommensteuer__einkünfte__sonstige__rente__einnahmen_mit_besteuerungsanteil_y: float,
    familie__anzahl_personen_sn: int,
) -> float:
    """Income relevant for the Grundrentenzuschlag in the following calendar year.

    This target can be used as the input `einkommen_vorjahr_m` in a GETTSIM call for
    the following year. It is the sum of

    - the zu versteuerndes Einkommen,
    - the steuerfreier Teil of pensions taxed at the Besteuerungsanteil, and
    - the capital income subject to the Abgeltungsteuer.

    The zu versteuerndes Einkommen and the capital income of jointly assessed spouses
    are split equally between them; only the couple's sum enters the crediting.
    Negative income is not floored at zero.

    Some notes:

    - The zu versteuerndes Einkommen is the one used for the income tax, i.e., it
      deducts the Kinderfreibeträge only if they are more favourable than the
      Kindergeld (§ 2 Abs. 5 S. 2 EStG would deduct them in any case).
    - The Grundrentenzuschlag is tax-free (§ 3 Nr. 14a EStG) and therefore not part
      of the income; the deduction of § 97a Abs. 2 S. 7 SGB VI (until 2026) has
      nothing to deduct.
    - Not modelled: the tax-free part of Versorgungsbezüge (§ 97a Abs. 2 S. 1 Nr. 2
      SGB VI) and the 1/10 rule for capital income under § 20 Abs. 1 Nr. 6 EStG
      (Nr. 3), because GETTSIM has no inputs for them; foreign income (Abs. 3
      S. 2-3); and the fallback to cut gross pensions if the tax office has no data
      (Abs. 2 S. 4-5).
    - The Deutsche Rentenversicherung uses the income of the year two (or three)
      years before. Here, the income of the previous year is used.

    Reference: § 97a Abs. 2 S. 1 SGB VI
    """
    zu_versteuerndes_einkommen_y = (
        einkommensteuer__zu_versteuerndes_einkommen_y_sn / familie__anzahl_personen_sn
    )
    kapitaleinkünfte_y = (
        einkommensteuer__einkünfte__aus_kapitalvermögen__betrag_y_sn
        / familie__anzahl_personen_sn
    )
    steuerfreier_teil_der_renten_y = (
        1 - einkommensteuer__einkünfte__sonstige__rente__besteuerungsanteil
    ) * einkommensteuer__einkünfte__sonstige__rente__einnahmen_mit_besteuerungsanteil_y
    return (
        zu_versteuerndes_einkommen_y
        + steuerfreier_teil_der_renten_y
        + kapitaleinkünfte_y
    )
