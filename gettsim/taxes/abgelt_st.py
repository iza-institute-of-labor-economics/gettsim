import numpy as np


def abgelt_st(tax_unit, e_st_params, e_st_abzuege_params):
    """ Capital Income Tax / Abgeltungsteuer
        since 2009, captial income is taxed with a flatrate of 25%.
    """
    tax_unit["abgelt_st"] = 0
    if e_st_params["year"] >= 2009:
        tax_unit.loc[~tax_unit["gem_veranlagt"], "abgelt_st"] = e_st_params[
            "abgst"
        ] * np.maximum(
            tax_unit["brutto_eink_5"]
            - e_st_abzuege_params["spsparf"]
            - e_st_abzuege_params["spwerbz"],
            0,
        ).round(
            2
        )
        tax_unit.loc[tax_unit["gem_veranlagt"], "abgelt_st"] = (
            0.5
            * e_st_params["abgst"]
            * np.maximum(
                tax_unit["brutto_eink_5_tu"]
                - 2 * (e_st_abzuege_params["spsparf"] + e_st_abzuege_params["spwerbz"]),
                0,
            )
        ).round(2)
    return tax_unit
