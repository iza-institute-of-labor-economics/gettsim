from __future__ import annotations

import numpy
import pandas as pd
import pytest

from _gettsim.config import DEFAULT_TARGETS
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import set_up_policy_environment
from _gettsim.synthetic import create_synthetic_data


@pytest.fixture
def synthetic_data_with_defaults():
    return create_synthetic_data()


@pytest.fixture
def synthetic_data_couple_with_children():
    return create_synthetic_data(n_adults=2, n_children=2)


@pytest.fixture
def synthetic_data_alleinerziehend():
    return create_synthetic_data(n_adults=1, n_children=1)


@pytest.fixture
def synthetic_data_no_children():
    return create_synthetic_data(n_adults=2, n_children=0)


@pytest.fixture
def synthetic_data_spec_variables():
    df = create_synthetic_data(
        n_adults=2,
        n_children=1,
        specs_constant_over_households={
            "basic_inputs__alter": [50, 30, 5],
            "basic_inputs__einkommen__bruttolohn_m": [1000, 2000, 0],
        },
    )
    return df


@pytest.fixture
def synthetic_data_spec_heterogeneous_married():
    df = create_synthetic_data(
        n_adults=2,
        n_children=1,
        adults_married=True,
        specs_constant_over_households={"basic_inputs__alter": [50, 30, 5]},
        specs_heterogeneous={
            "basic_inputs__einkommen__bruttolohn_m": [
                [i / 2, i / 2, 0] for i in range(0, 1001, 100)
            ]
        },
    )
    return df


@pytest.fixture
def synthetic_data_spec_heterogeneous_not_married():
    df = create_synthetic_data(
        n_adults=2,
        n_children=1,
        adults_married=False,
        specs_constant_over_households={"basic_inputs__alter": [50, 30, 5]},
        specs_heterogeneous={
            "basic_inputs__einkommen__bruttolohn_m": [
                [i / 2, i / 2, 0] for i in range(0, 1001, 100)
            ]
        },
    )
    return df


synthetic_data_fixtures_not_heterogeneous = [
    ("synthetic_data_with_defaults"),
    ("synthetic_data_couple_with_children"),
    ("synthetic_data_spec_variables"),
]

synthetic_data_fixtures = [
    *synthetic_data_fixtures_not_heterogeneous,
    "synthetic_data_spec_heterogeneous_married",
    "synthetic_data_spec_heterogeneous_not_married",
]


@pytest.mark.xfail(reason="Synthetic module was not updated to the new interface.")
@pytest.mark.parametrize(
    "df",
    synthetic_data_fixtures,
)
def test_positive_rent(df, request):
    df = request.getfixturevalue(df)
    assert df["basic_inputs__wohnen__bruttokaltmiete_m_hh"].min() > 0


@pytest.mark.xfail(reason="Synthetic module was not updated to the new interface.")
@pytest.mark.parametrize(
    "df",
    synthetic_data_fixtures,
)
def test_no_nans(df, request):
    df = request.getfixturevalue(df)
    assert df["basic_inputs__wohnen__bruttokaltmiete_m_hh"].notna().all().all()


@pytest.mark.xfail(reason="Synthetic module was not updated to the new interface.")
@pytest.mark.parametrize(
    "df",
    synthetic_data_fixtures_not_heterogeneous,
)
def test_unique_p_id(df, request):
    df = request.getfixturevalue(df)
    assert df["p_id"].is_unique


@pytest.mark.xfail(reason="Synthetic module was not updated to the new interface.")
@pytest.mark.parametrize(
    "df",
    synthetic_data_fixtures_not_heterogeneous,
)
def test_constant_hh_id(df, request):
    df = request.getfixturevalue(df)
    assert (df["hh_id"].max() == df["hh_id"]).all()


@pytest.mark.xfail(reason="Synthetic module was not updated to the new interface.")
@pytest.mark.parametrize(
    "df, exp_n_rows",
    [
        ("synthetic_data_with_defaults", 1),
        ("synthetic_data_couple_with_children", 4),
        ("synthetic_data_spec_variables", 3),
        ("synthetic_data_spec_heterogeneous_married", 33),
    ],
)
def test_correct_size(df, exp_n_rows, request):
    df = request.getfixturevalue(df)
    assert df.shape[0] == exp_n_rows


@pytest.mark.xfail(reason="Synthetic module was not updated to the new interface.")
def test_alleinerziehend(synthetic_data_alleinerziehend):
    pd.testing.assert_series_equal(
        synthetic_data_alleinerziehend["basic_inputs__alleinerz"],
        pd.Series([True, False], name="basic_inputs__alleinerz"),
    )
    pd.testing.assert_series_equal(
        synthetic_data_alleinerziehend[
            "basic_inputs__einkommensteuer__gemeinsam_veranlagt"
        ],
        pd.Series(
            [False, False], name="basic_inputs__einkommensteuer__gemeinsam_veranlagt"
        ),
    )


@pytest.mark.xfail(reason="Synthetic module was not updated to the new interface.")
@pytest.mark.parametrize(
    "col, expected",
    [
        ("basic_inputs__alter", [50, 30, 5]),
        ("basic_inputs__einkommen__bruttolohn_m", [1000, 2000, 0]),
    ],
)
def test_specs_constant_over_households(col, expected, synthetic_data_spec_variables):
    pd.testing.assert_series_equal(
        synthetic_data_spec_variables[col], pd.Series(expected, name=col)
    )


@pytest.mark.xfail(reason="Synthetic module was not updated to the new interface.")
@pytest.mark.parametrize(
    "col, expected",
    [
        ("basic_inputs__alter", [50, 30, 5] * 11),
        (
            "basic_inputs__einkommen__bruttolohn_m",
            numpy.concatenate([[i / 2, i / 2, 0] for i in range(0, 1001, 100)]),
        ),
        (
            "basic_inputs__einkommensteuer__gemeinsam_veranlagt",
            [True, True, False] * 11,
        ),
    ],
)
def test_specs_heterogeneous(col, expected, synthetic_data_spec_heterogeneous_married):
    pd.testing.assert_series_equal(
        synthetic_data_spec_heterogeneous_married[col], pd.Series(expected, name=col)
    )


@pytest.mark.xfail(reason="Synthetic module was not updated to the new interface.")
@pytest.mark.parametrize(
    "n_adults, n_children, specs_constant_over_households,"
    " specs_heterogeneous, expectation",
    [
        (0, 2, None, None, pytest.raises(ValueError, match="'n_adults' must be")),
        (3, 2, None, None, pytest.raises(ValueError, match="'n_adults' must be")),
        (2, 11, None, None, pytest.raises(ValueError, match="'n_children' must be")),
        (
            2,
            0,
            {"demographics__alter": [30]},
            None,
            pytest.raises(ValueError, match="Length of"),
        ),
        (
            2,
            0,
            None,
            {
                "basic_inputs__alter": [[30, 20], [40, 30]],
                "basic_inputs__einkommen__bruttolohn_m": [[300, 200]],
            },
            pytest.raises(ValueError, match="Length of"),
        ),
    ],
)
def test_fail_if_functions_and_columns_overlap(
    n_adults,
    n_children,
    specs_constant_over_households,
    specs_heterogeneous,
    expectation,
):
    with expectation:
        create_synthetic_data(
            n_adults=n_adults,
            n_children=n_children,
            specs_constant_over_households=specs_constant_over_households,
            specs_heterogeneous=specs_heterogeneous,
        )


@pytest.mark.xfail(reason="Synthetic module was not updated to the new interface.")
@pytest.mark.parametrize(
    "fixture, expected",
    [
        (
            "synthetic_data_spec_heterogeneous_not_married",
            {
                "p_id": list(range(33)),
                "demographics__p_id_elternteil_1": [
                    -1 if i % 3 != 2 else i - 2 for i in range(33)
                ],
                "demographics__p_id_elternteil_2": [
                    -1 if i % 3 != 2 else i - 1 for i in range(33)
                ],
                "kindergeld__p_id_empfänger": [
                    -1 if i % 3 != 2 else i - 2 for i in range(33)
                ],
                "erziehungsgeld__p_id_empfänger": [
                    -1 if i % 3 != 2 else i - 2 for i in range(33)
                ],
                "demographics__p_id_ehepartner": [-1 for i in range(33)],
                "arbeitslosengeld_2__p_id_einstandspartner": [
                    i + 1 if i % 3 == 0 else i - 1 if i % 3 == 1 else -1
                    for i in range(33)
                ],
                "einkommensteuer__freibeträge__p_id_betreuungskosten_träger": [
                    -1 if i % 3 != 2 else i - 2 for i in range(33)
                ],
            },
        ),
        (
            "synthetic_data_spec_heterogeneous_married",
            {
                "p_id": list(range(33)),
                "demographics__p_id_elternteil_1": [
                    -1 if i % 3 != 2 else i - 2 for i in range(33)
                ],
                "demographics__p_id_elternteil_2": [
                    -1 if i % 3 != 2 else i - 1 for i in range(33)
                ],
                "kindergeld__p_id_empfänger": [
                    -1 if i % 3 != 2 else i - 2 for i in range(33)
                ],
                "erziehungsgeld__p_id_empfänger": [
                    -1 if i % 3 != 2 else i - 2 for i in range(33)
                ],
                "demographics__p_id_ehepartner": [
                    i + 1 if i % 3 == 0 else i - 1 if i % 3 == 1 else -1
                    for i in range(33)
                ],
                "arbeitslosengeld_2__p_id_einstandspartner": [
                    i + 1 if i % 3 == 0 else i - 1 if i % 3 == 1 else -1
                    for i in range(33)
                ],
                "einkommensteuer__freibeträge__p_id_betreuungskosten_träger": [
                    -1 if i % 3 != 2 else i - 2 for i in range(33)
                ],
            },
        ),
        (
            "synthetic_data_alleinerziehend",
            {
                "p_id": [0, 1],
                "demographics__p_id_elternteil_1": [-1, 0],
                "demographics__p_id_elternteil_2": [-1, -1],
                "kindergeld__p_id_empfänger": [-1, 0],
                "erziehungsgeld__p_id_empfänger": [-1, 0],
                "demographics__p_id_ehepartner": [-1, -1],
                "arbeitslosengeld_2__p_id_einstandspartner": [-1, -1],
                "einkommensteuer__freibeträge__p_id_betreuungskosten_träger": [
                    -1,
                    0,
                ],
            },
        ),
        (
            "synthetic_data_no_children",
            {
                "p_id": [0, 1],
                "demographics__p_id_elternteil_1": [-1, -1],
                "demographics__p_id_elternteil_2": [-1, -1],
                "kindergeld__p_id_empfänger": [-1, -1],
                "erziehungsgeld__p_id_empfänger": [-1, -1],
                "demographics__p_id_ehepartner": [1, 0],
                "arbeitslosengeld_2__p_id_einstandspartner": [1, 0],
                "einkommensteuer__freibeträge__p_id_betreuungskosten_träger": [
                    -1,
                    -1,
                ],
            },
        ),
    ],
)
def test_p_id_groups(fixture, expected, request):
    df = request.getfixturevalue(fixture)
    for col, values in expected.items():
        pd.testing.assert_series_equal(df[col], pd.Series(values, name=col))


@pytest.mark.xfail(reason="Synthetic module was not updated to the new interface.")
@pytest.mark.parametrize(
    "fixture, policy_date",
    [("synthetic_data_couple_with_children", y) for y in range(2015, 2024)],
)
def test_default_targets(fixture, policy_date, request):
    environment = set_up_policy_environment(policy_date)
    compute_taxes_and_transfers(
        data_tree=request.getfixturevalue(fixture),
        targets_tree=DEFAULT_TARGETS,
        environment=environment,
    )
