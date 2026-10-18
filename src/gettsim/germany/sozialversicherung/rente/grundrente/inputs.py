"""Input columns."""

from __future__ import annotations

from gettsim.tt import TTSIMUnit, policy_input


@policy_input(start_date="2021-01-01", unit=TTSIMUnit.MONTHS)
def bewertungszeiten_monate() -> int:
    """Number of months determining amount of Grundrente."""


@policy_input(start_date="2021-01-01", unit=TTSIMUnit.MONTHS)
def grundrentenzeiten_monate() -> int:
    """Number of months determining eligibility for Grundrente."""


@policy_input(start_date="2021-01-01", unit=TTSIMUnit.DIMENSIONLESS)
def mean_entgeltpunkte() -> float:
    """Mean Entgeltpunkte during Bewertungszeiten."""


@policy_input(start_date="2021-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH)
def einkommen_vorjahr_m() -> float:
    """Income relevant for the Grundrentenzuschlag (§ 97a Abs. 2 S. 1 SGB VI).

    The sum of the person's zu versteuerndes Einkommen, the steuerfreier Teil of their
    pensions, and their capital income subject to the Abgeltungsteuer in the previous
    calendar year, as a monthly amount. For jointly assessed spouses, each holds half
    of the joint zu versteuerndes Einkommen.

    GETTSIM can calculate this input based on the data of the previous calendar year
    using the target `('sozialversicherung', 'rente', 'grundrente',
    'einkommen_für_einkommensberechnung_im_folgejahr_m')`.
    """
