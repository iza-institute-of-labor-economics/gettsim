import numpy as np


def abgelt_st(tax_unit, eink_st_params, eink_st_abzuege_params):
    """ Capital Income Tax / Abgeltungsteuer
        since 2009, captial income is taxed with a flatrate of 25%.
    """
    tax_unit["abgelt_st_m"] = 0
    if eink_st_params["jahr"] >= 2009:
        tax_unit.loc[~tax_unit["gem_veranlagt"], "abgelt_st_m"] = eink_st_params[
            "abgelt_st_satz"
        ] * np.maximum(
            tax_unit["brutto_eink_5"]
            - eink_st_abzuege_params["sparerpauschbetrag"]
            - eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"],
            0,
        ).round(
            2
        )
        tax_unit.loc[tax_unit["gem_veranlagt"], "abgelt_st_m"] = (
            0.5
            * eink_st_params["abgelt_st_satz"]
            * np.maximum(
                tax_unit["brutto_eink_5_tu"]
                - 2
                * (
                    eink_st_abzuege_params["sparerpauschbetrag"]
                    + eink_st_abzuege_params["sparer_werbungskosten_pauschbetrag"]
                ),
                0,
            )
        ).round(2)
    return tax_unit
