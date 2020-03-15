"""
Calculate income share not subject to transfer withdrawl using generic_functions.
"""
import datetime

import numpy as np
import yaml
from generic_functions import fill_intercepts_at_lower_thresholds
from generic_functions import piecewise_linear


def generate_arrays(dict_list):
    """Extract the relevant parameters for calc_e_anr_frei.

    Args:
        dict_list: dict_list of dictionaries specifying upper_thresholds and
              respective rates for a given legislature time.

    Returns:
        dict of 3 arrays for calc_e_anr_frei: upper_thresholds, rates and
        intercepts_at_lower_thresholds.
    """
    upper_thresholds = np.array([])
    rates = np.array([])

    i = 0
    for i in range(0, len(dict_list)):
        upper_thresholds = np.append(upper_thresholds, dict_list[i]["upper_threshold"])

        rates = np.append(rates, dict_list[i]["rate"])

    upper_thresholds = np.asfarray(upper_thresholds, float)

    intercepts = fill_intercepts_at_lower_thresholds(
        upper_thresholds, rates, 0, piecewise_linear
    )

    out = {
        "upper_thresholds": upper_thresholds,
        "rates": rates,
        "intercepts": intercepts,
    }

    return out


# --- Testrun
with open("./data/arbeitsl_geld_2_neu.yaml") as file:
    arbeitsl_geld_2 = yaml.full_load(file)

testdate_1 = datetime.date(2005, 1, 1)
testdate_2 = datetime.date(2005, 10, 1)

e_anr_frei_1 = piecewise_linear(
    900,
    generate_arrays(arbeitsl_geld_2["e_anr_frei"]["values"][testdate_1])[
        "upper_thresholds"
    ],
    generate_arrays(arbeitsl_geld_2["e_anr_frei"]["values"][testdate_1])["rates"],
    generate_arrays(arbeitsl_geld_2["e_anr_frei"]["values"][testdate_1])["intercepts"],
    side="left",
)

print(f"e_anr_frei_2: {e_anr_frei_1}")  # 210.0


e_anr_frei_2 = piecewise_linear(
    900,
    generate_arrays(arbeitsl_geld_2["e_anr_frei"]["values"][testdate_2])[
        "upper_thresholds"
    ],
    generate_arrays(arbeitsl_geld_2["e_anr_frei"]["values"][testdate_2])["rates"],
    generate_arrays(arbeitsl_geld_2["e_anr_frei"]["values"][testdate_2])["intercepts"],
    side="left",
)

print(f"e_anr_frei_2: {e_anr_frei_2}")  # 250.0
