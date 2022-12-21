from __future__ import annotations

import numpy as np
from _gettsim.interface import compute_taxes_and_transfers
from _gettsim.policy_environment import set_up_policy_environment
from _gettsim.synthetic import create_synthetic_data


def test_synthetic():
    """Test creation of synthetic data."""
    # run with defaults
    df = create_synthetic_data()
    # rent must be positive
    assert df["bruttokaltmiete_m_hh"].min() > 0
    # heating cost must be positive
    assert df["heizkosten_m_hh"].min() > 0
    # no NaN values
    assert df.notna().all().all()
    # correct dimensions for every household type
    assert len(df[df["hh_typ"] == "couple_0_children"] == 2)
    assert len(df[df["hh_typ"] == "single_2_children"] == 3)
    assert len(df[df["hh_typ"] == "couple_2_children"] == 4)
    # unique personal id?
    assert df["p_id"].is_unique

    doppelverdiener = create_synthetic_data(
        hh_typen=["couple"], n_children=[0], double_earner=True, bruttolohn_m=2000
    )

    assert (doppelverdiener["bruttolohn_m"] > 0).all()

    # test heterogeneity
    incrange = create_synthetic_data(
        hh_typen=["couple"],
        n_children=0,
        heterogeneous_vars={
            "bruttolohn_m": list(np.arange(0, 6000, 1000)),
            "vermögen_bedürft_hh": [10_000, 500_000, 1_000_000],
        },
    )
    # is household id unique?
    assert (incrange.groupby("hh_id").size() == 2).all()

    assert incrange.notna().all().all()

    # finally, run through gettsim
    policy_params, policy_functions = set_up_policy_environment(2020)
    results = compute_taxes_and_transfers(df, policy_params, policy_functions)
    assert len(results) == len(df)
