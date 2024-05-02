import numpy as np
import pandas as pd
import pytest
from _gettsim.interface import compute_taxes_and_transfers
from pandas.testing import assert_series_equal

from _gettsim_tests._helpers import cached_set_up_policy_environment
from _gettsim_tests._policy_test_utils import PolicyTestData, load_policy_test_data

data = load_policy_test_data("demographic_vars")


@pytest.mark.parametrize(
    "test_data, column, expected",
    [
        (
            pd.DataFrame(
                {
                    "p_id": [
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7,
                        8,
                        9,
                        10,
                        11,
                        12,
                        13,
                        14,
                        15,
                        16,
                        17,
                    ],
                    "hh_id": [
                        1,
                        1,
                        1,
                        2,
                        2,
                        2,
                        3,
                        3,
                        3,
                        4,
                        4,
                        4,
                        5,
                        5,
                        5,
                        5,
                        6,
                    ],
                    "p_id_einstandspartner": [
                        2,
                        1,
                        -1,
                        5,
                        4,
                        -1,
                        8,
                        7,
                        -1,
                        11,
                        10,
                        -1,
                        14,
                        13,
                        16,
                        15,
                        -1,
                    ],
                }
            ),
            "anz_paare_hh",
            pd.Series(
                [
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    2,
                    2,
                    2,
                    2,
                    0,
                ],
                name="anz_paare_hh",
            ),
        ),
        (
            pd.DataFrame(
                {
                    "p_id": [
                        1,
                        2,
                        3,
                        4,
                        5,
                        6,
                        7,
                        8,
                        9,
                        10,
                        11,
                        12,
                        13,
                        14,
                        15,
                        16,
                        17,
                    ],
                    "hh_id": [
                        1,
                        1,
                        1,
                        2,
                        2,
                        2,
                        3,
                        3,
                        3,
                        4,
                        4,
                        4,
                        5,
                        5,
                        5,
                        5,
                        6,
                    ],
                    "p_id_einstandspartner": [
                        2,
                        1,
                        -1,
                        17,
                        -1,
                        -1,
                        8,
                        7,
                        -1,
                        11,
                        10,
                        -1,
                        14,
                        13,
                        16,
                        15,
                        4,
                    ],
                }
            ),
            "anz_paare_hh",
            pd.Series(
                [
                    1,
                    1,
                    1,
                    0,
                    0,
                    0,
                    1,
                    1,
                    1,
                    1,
                    1,
                    1,
                    2,
                    2,
                    2,
                    2,
                    0,
                ],
                name="anz_paare_hh",
            ),
        ),
    ],
)
def test_demographic_vars(
    test_data: PolicyTestData,
    column: str,
    expected: np.ndarray,
):
    policy_params, policy_functions = cached_set_up_policy_environment(date=2024)

    result = compute_taxes_and_transfers(
        data=test_data, params=policy_params, functions=policy_functions, targets=column
    )

    assert_series_equal(
        result[column],
        expected,
        check_dtype=False,
        atol=0.01,
        rtol=0,
    )
