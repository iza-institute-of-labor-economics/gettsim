"""
This module contains auxiliary functions, which complete the parameter dictionary by
applying some tax specific rules. These are rules which are defined by law to for
example mitigate the start if taxation. While the exact parameter values change with
each tax update, the rule to calculate them remains the same.
"""
import copy

from gettsim.pre_processing.piecewise_functions import check_threholds


def transition_threshold(soli_st_satz, soli_st_uebergang, freigrenze):
    """Transition threshold for soli.

    This function calculates the upper threshold for interval 1 for the piecewise
    function in soli_st.yaml. Interval 1 is used to moderate the start of soli
    taxation. From this threshold on, the regular soli rate("soli_st_satz") is
    applied to the basis of soli calculation. Before the transition rate (
    "soli_st_uebergang") is applied to the difference of basis and "freigrenze". It
    uses the three parameters actually given in the law.
    """
    threshold = freigrenze / (1 - soli_st_satz / soli_st_uebergang)
    return threshold


def add_progressionsfaktor(param_dict, parameter):
    """Quadratic factor of tax tariff function.

    The German tax tariff is defined on several income intervals with distinct
    marginal tax rates at the thresholds. To ensure an almost linear increase of
    the average tax rate, the German tax tariff is defined as a quadratic function,
    where the quadratic rate is the so called linear Progressionsfaktor. For its
    calculation one needs the lower (low_thres) and upper (upper_thres) thresholds of
    the interval as well as the marginal tax rate of the interval (rate_iv) and of the
    following interval (rate_fiv). The formula is then given by:

    (rate_fiv - rate_iv) / (2 * (upper_thres - low_thres))

    """
    out_dict = copy.deepcopy(param_dict)
    interval_keys = sorted(key for key in out_dict if isinstance(key, int))
    # Check and extract lower thresholds.
    lower_thresholds, upper_thresholds = check_threholds(
        param_dict, parameter, interval_keys
    )
    for key in interval_keys:
        if "rate_quadratic" not in out_dict[key]:
            out_dict[key]["rate_quadratic"] = (
                out_dict[key + 1]["rate_linear"] - out_dict[key]["rate_linear"]
            ) / (2 * (upper_thresholds[key] - lower_thresholds[key]))
    return out_dict
