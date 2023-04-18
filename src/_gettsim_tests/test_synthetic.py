from __future__ import annotations

import pandas as pd
from _gettsim.synthetic import create_synthetic_data


def test_default():
    df = create_synthetic_data()

    # rent must be positive
    assert df["bruttokaltmiete_m_hh"].min() > 0

    # heating cost must be positive
    assert df["heizkosten_m_hh"].min() > 0

    # no NaN values
    assert df.notna().all().all()

    # correct dimension
    assert df.shape[0] == 1


def test_couple_with_children():
    df = create_synthetic_data(n_adults=2, n_children=2)

    # no NaN values
    assert df.notna().all().all()

    # correct dimension
    assert df.shape[0] == 4

    # unique personal id?
    assert df["p_id"].is_unique

    # constant hh_id
    assert (df["hh_id"].max() == df["hh_id"]).all()


def test_specs_constant_over_households():
    df = create_synthetic_data(
        n_adults=2,
        n_children=1,
        specs_constant_over_households={
            "alter": [50, 30, 5],
            "bruttolohn_m": [1000, 2000, 0],
        },
    )

    pd.testing.assert_series_equal(df["alter"], pd.Series([50, 30, 5], name="alter"))
    pd.testing.assert_series_equal(
        df["bruttolohn_m"], pd.Series([1000, 2000, 0], name="bruttolohn_m")
    )


def test_specs_heterogeneous():
    df = create_synthetic_data(
        n_adults=2,
        n_children=1,
        specs_constant_over_households={"alter": [50, 30, 5]},
        specs_heterogeneous={
            "bruttolohn_m": [[i / 2, i / 2, 0] for i in range(0, 1001, 100)]
        },
    )

    # no NaN values
    assert df.notna().all().all()

    # correct dimension
    assert df.shape[0] == 33

    # unique personal id?
    assert df["p_id"].is_unique

    pd.testing.assert_series_equal(
        df["alter"], pd.Series([50, 30, 5] * 11, name="alter")
    )
    pd.testing.assert_series_equal(
        df["bruttolohn_m"].head(3),
        pd.Series([0, 0, 0], dtype=float, name="bruttolohn_m"),
        check_index=False,
    )
    pd.testing.assert_series_equal(
        df["bruttolohn_m"].tail(3),
        pd.Series([500, 500, 0], dtype=float, name="bruttolohn_m"),
        check_index=False,
    )
