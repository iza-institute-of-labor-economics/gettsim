import pandas as pd


def kindergeld(df, tb):
    """ Child Benefit (kindergeld)
    Basic Amount for each child. Parents receive child benefit for every child up to
    18 years. Above, they get it only up to tb["kgage"] if the child is
    a) in education and
    b) not working too much / not receiving too much income (depending on the year)

    Returns:
        pd.series:
            kindergeld_basis: Kindergeld on the individual level
            kindergeld_tu_basis: Kindergeld summed up within the tax unit
    """
    kg = pd.DataFrame(index=df.index.copy())
    kg["tu_id"] = df["tu_id"]

    kg["child_count"] = tb["childben_elig_rule"](df, tb).cumsum()

    kg_amounts = {1: tb["kgeld1"], 2: tb["kgeld2"], 3: tb["kgeld3"], 4: tb["kgeld4"]}
    kg["kindergeld_basis"] = kg["child_count"].replace(kg_amounts)
    kg.loc[kg["child_count"] > 4, "kindergeld_basis"] = tb["kgeld4"]
    kg["kindergeld_tu_basis"] = kg.groupby("tu_id")["kindergeld_basis"].transform(sum)

    return kg[["kindergeld_basis", "kindergeld_tu_basis"]]


def kg_eligibility_hours(df, tb):
    """ Nowadays, kids must not work more than 20 hour
    returns a boolean variable whether a specific person is a child eligible for
    child benefit
    """
    df = df.copy()
    df["eligible"] = df["age"] <= 18
    df.loc[
        (df["age"].between(19, tb["kgage"]))
        & df["ineducation"]
        & (df["w_hours"] <= 20),
        "eligible",
    ] = True

    return df["eligible"]


def kg_eligibility_wage(df, tb):
    """ Before 2011, there was an income ceiling for children
    returns a boolean variable whether a specific person is a child eligible for
    child benefit
    """
    df = df.copy()
    df["eligible"] = df["age"] <= 18
    df.loc[
        (df["age"].between(19, tb["kgage"]))
        & df["ineducation"]
        & (df["m_wage"] <= tb["kgfreib"] / 12),
        "eligible",
    ] = True

    return df["eligible"]
