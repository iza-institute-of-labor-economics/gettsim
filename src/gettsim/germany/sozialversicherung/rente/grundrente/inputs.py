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


@policy_input(start_date="2021-01-01", unit=TTSIMUnit.CURRENCY.PER_MONTH.PER_EHE)
def einkommen_vorjahr_m_ehe() -> float:
    """Income of the couple relevant for the Grundrentenzuschlag (§ 97a SGB VI).

    The sum of the zu versteuerndes Einkommen, the steuerfreier Teil of pensions, and
    the capital income subject to the Abgeltungsteuer of the person and their spouse
    in the previous calendar year, as a monthly amount.

    GETTSIM can calculate this input based on the data of the previous calendar year
    using the target `('sozialversicherung', 'rente', 'grundrente',
    'einkommen_im_folgejahr_m_ehe')`.
    """
