import numpy as np

from gettsim.synthetic import create_synthetic_data


def test_synthetic():
    """
    Test creation of synthetic data
    """
    # run with defaults
    df = create_synthetic_data()

    # rent must be positive
    assert df["kaltmiete_m"].min() > 0
    # heating cost must be positive
    assert df["heizkost_m"].min() > 0
    # no NaN values
    assert df.notna().all().all()
    # correct dimensions for every household type
    assert len(df[df["hh_typ"] == "coup_0ch"] == 2)
    assert len(df[df["hh_typ"] == "sing_2ch"] == 3)
    assert len(df[df["hh_typ"] == "coup_2ch"] == 4)
    # unique personal id?
    assert df["p_id"].is_unique

    doppelverdiener = create_synthetic_data(
        hh_typen=["couple"], n_children=[0], double_earner=True, bruttolohn_m=2000
    )

    assert (doppelverdiener["bruttolohn_m"] > 0).all()
    # test heterogeneity
    incrange = create_synthetic_data(
        hh_typen=["couple"],
        heterogeneous_vars={
            "bruttolohn_m": list(np.arange(0, 6000, 1000)),
            "vermögen_hh": [0, 500_000, 1_000_000],
        },
    )
    # is household id unique?
    assert (
        incrange.groupby(["hh_id", "bruttolohn_m", "vermögen_hh"]).size() == 2
    ).all()

    assert incrange.notna().all().all()
