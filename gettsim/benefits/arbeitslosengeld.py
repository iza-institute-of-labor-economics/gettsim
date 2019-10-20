import numpy as np

from gettsim.taxes.calc_taxes import soli_formula


def ui(df_row, tb):
    """Return the Unemployment Benefit based on
    employment status and income from previous years.

    """

    # ui["m_alg1_soep"] = df["alg_soep"].fillna(0)

    alg_entgelt = _alg_entgelt(df_row, tb)

    eligible = check_eligibility_alg(df_row)

    if eligible.all():
        if df_row["child_num_tu"].sum() == 0:
            df_row["m_alg1"] = alg_entgelt * tb["agsatz0"]
        else:
            df_row["m_alg1"] = alg_entgelt * tb["agsatz1"]
    else:
        df_row["m_alg1"] = 0.0
    return df_row


def _alg_entgelt(df_row, tb):
    """ Calculating the claim for the Arbeitslosengeldgeld, depending on the current
    wage."""
    westost = "o" if df_row["east"].all() else "w"
    # Relevant wage is capped at the contribution thresholds
    alg_wage = np.minimum(tb["rvmaxek" + westost], df_row["m_wage_l1"])

    # We need to deduct lump-sum amounts for contributions, taxes and soli
    alg_ssc = tb["alg1_abz"] * alg_wage
    # assume west germany for this particular calculation
    # df['east'] = False
    # Fictive taxes (Lohnsteuer) are approximated by applying the wage to the tax tariff
    alg_tax = tb["tax_schedule"](12 * alg_wage - tb["werbung"], tb)

    alg_soli = soli_formula(alg_tax, tb)

    return np.maximum(0, alg_wage - alg_ssc - alg_tax / 12 - alg_soli / 12)


def check_eligibility_alg(df_row):
    """Checking eligibility, depending on the months worked beforehand, the age and
    other variables.."""
    # Months of unemployment beforehand.
    mts_ue = df_row["months_ue"] + df_row["months_ue_l1"] + df_row["months_ue_l2"]
    # BENEFIT AMOUNT
    # Check Eligiblity.
    # Then different rates for parent and non-parents
    # Take into account actual wages
    # there are different replacement rates depending on presence of children
    return (
        (mts_ue.between(1, 12))
        & (df_row["age"] < 65)
        & (df_row["m_pensions"] == 0)
        & (df_row["w_hours"] < 15)
    )
