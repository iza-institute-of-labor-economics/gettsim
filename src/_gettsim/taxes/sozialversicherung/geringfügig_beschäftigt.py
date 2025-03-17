"""Marginally employed."""

from _gettsim.function_types import policy_function


@policy_function()
def geringfügig_beschäftigt(
    einkommensteuer__einnahmen__bruttolohn_m: float, minijob_grenze: float
) -> bool:
    """Individual earns less than marginal employment threshold.

    Marginal employed pay no social insurance contributions.

    Legal reference: § 8 Abs. 1 Satz 1 and 2 SGB IV

    Parameters
    ----------
    einkommensteuer__einnahmen__bruttolohn_m
        See basic input variable :ref:`einkommensteuer__einnahmen__bruttolohn_m <einkommensteuer__einnahmen__bruttolohn_m>`.
    minijob_grenze
        See :func:`minijob_grenze`.


    Returns
    -------
    Whether person earns less than marginal employment threshold.

    """
    return einkommensteuer__einnahmen__bruttolohn_m <= minijob_grenze


@policy_function(
    end_date="1999-12-31",
    leaf_name="minijob_grenze",
    params_key_for_rounding="sozialv_beitr",
)
def minijob_grenze_unterscheidung_ost_west(
    demographics__wohnort_ost: bool, sozialv_beitr_params: dict
) -> float:
    """Minijob income threshold depending on place of living (East or West Germany).

    Until 1999, the threshold is different for East and West Germany.

    Parameters
    ----------
    demographics__wohnort_ost
        See basic input variable :ref:`demographics__wohnort_ost <demographics__wohnort_ost>`.
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    Returns
    -------

    """
    west = sozialv_beitr_params["geringfügige_eink_grenzen_m"]["minijob"]["west"]
    ost = sozialv_beitr_params["geringfügige_eink_grenzen_m"]["minijob"]["ost"]
    out = ost if demographics__wohnort_ost else west
    return float(out)


@policy_function(
    start_date="2000-01-01",
    end_date="2022-09-30",
    leaf_name="minijob_grenze",
    params_key_for_rounding="sozialv_beitr",
)
def minijob_grenze_einheitlich(sozialv_beitr_params: dict) -> float:
    """Minijob income threshold depending on place of living.

    From 2000 onwards, the threshold is the same for all of Germany. Until September
    2022, the threshold is exogenously set.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.
    Returns
    -------

    """
    return float(sozialv_beitr_params["geringfügige_eink_grenzen_m"]["minijob"])


@policy_function(
    start_date="2022-10-01",
    leaf_name="minijob_grenze",
    params_key_for_rounding="sozialv_beitr",
)
def minijob_grenze_from_minimum_wage(sozialv_beitr_params: dict) -> float:
    """Minijob income threshold since 10/2022. Since then, it is calculated endogenously
    from the statutory minimum wage.

    Parameters
    ----------
    sozialv_beitr_params
        See params documentation :ref:`sozialv_beitr_params <sozialv_beitr_params>`.

    Returns
    -------
    Marginal Job Threshold

    """
    return (
        sozialv_beitr_params["mindestlohn"]
        * sozialv_beitr_params["geringf_eink_faktor"]
        / sozialv_beitr_params["geringf_eink_divisor"]
    )
