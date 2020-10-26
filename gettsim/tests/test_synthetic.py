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

    doppelverdiener = gettsim_hypo_data(hh_typen=["coup"], double_earner=True)

    assert (doppelverdiener["bruttolohn_m"] > 0).all()
