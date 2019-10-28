from gettsim.tests.auxiliary_test_tax import load_tb

def elt_geld(df):
    """This function calculates the monthly benefits for having
    a child that is up to one year old (Elterngeld)"""

    eltg_df = df

    eltg_df["elt_geld"] = 0

    receiving = eltg_df.loc[eltg_df["elt_zeit"], "pid"]

    elt_geld = []

    for pid in receiving:
        referece_year = (
            eltg_df.loc[(eltg_df["elt_zeit"] == True) & (eltg_df["pid"] == pid), "year"]
            - 1
        )

        tb = load_tb(referece_year.item())

        calculated = (
            eltg_df.loc[
                (eltg_df["pid"] == pid) & (eltg_df["year"] == referece_year.item()),
                "m_wage",
            ].item()
            * tb["elgfaktor"]
        )

        elt_geld += [min(calculated, tb["elgmax"])]

    eltg_df.loc[eltg_df["elt_zeit"], "elt_geld"] = elt_geld

    return eltg_df["elt_geld"]