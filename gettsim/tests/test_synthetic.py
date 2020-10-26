import numpy as np

from gettsim.syntethic import gettsim_hypo_data


def test_hypo():
    """
    Test creation of hypothetical data
    """
    df = gettsim_hypo_data()

    # rent must be positive
    assert df["kaltmiete_m"].min() > 0
    # heating cost must be positive
    assert df["heizkost_m"].min() > 0
    # no NaN values
    assert df.notna().all().all()
    # correct dimensions for every household type
    assert len(df[df["hh_typ"] == "coup"] == 2)
    assert len(df[df["hh_typ"] == "sp2ch"] == 3)
    assert len(df[df["hh_typ"] == "coup2ch"] == 4)
    # unique personal id?
    assert df["p_id"].is_unique

    doppelverdiener = gettsim_hypo_data(
        hh_typen=["coup"], double_earner=True, bruttolohn_m=2000
    )

    assert (doppelverdiener["bruttolohn_m"] > 0).all()

    incrange = gettsim_hypo_data(
        hh_typen=["coup"],
        heterogeneous_vars={
            "bruttolohn_m": list(np.arange(0, 6000, 1000)),
            "vermögen_hh": [0, 500_000, 1_000_000],
        },
    )

    # print(incrange[["hh_id", "p_id", "bruttolohn_m", "vermögen_hh"]])
    assert (
        incrange.groupby(["hh_id", "bruttolohn_m", "vermögen_hh"]).size() == 2
    ).all()

    assert incrange.notna().all().all()
