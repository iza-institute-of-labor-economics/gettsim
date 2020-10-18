from gettsim.hypo import gettsim_hypo_data


def test_hypo():
    """
    Test creation of hypothetical data
    """
    df = gettsim_hypo_data()

    # only 1 or 2 adults per tax unit
    assert df["anz_erwachsene_tu"].between(1, 2).all()
    # rent must be positive
    assert df["kaltmiete_m"].min() > 0
    # heating cost must be positive
    assert df["heizkost_m"].min() > 0
    # Only 1 adult in single parent household
    assert (df[df["hh_typ"].str.contains("sp")]["anz_erwachsene_hh"] == 1).all()
    # no NaN values
    assert df.notna().all().all()
