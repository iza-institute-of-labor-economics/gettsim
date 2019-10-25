import numpy as np


def kindergeld(tax_unit, tb):
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

    child_count = tb["childben_elig_rule"](tax_unit, tb).cumsum()

    kg_amounts = {1: tb["kgeld1"], 2: tb["kgeld2"], 3: tb["kgeld3"], 4: tb["kgeld4"]}
    tax_unit["kindergeld_basis"] = child_count.replace(kg_amounts)
    tax_unit.loc[child_count > 4, "kindergeld_basis"] = tb["kgeld4"]
    tax_unit["kindergeld_tu_basis"] = np.sum(tax_unit["kindergeld_basis"])

    return tax_unit


def kg_eligibility_hours(tax_unit, tb):
    """ Nowadays, kids must not work more than 20 hour
    returns a boolean variable whether a specific person is a child eligible for
    child benefit
    """
    elig = tax_unit["age"] <= 18
    elig[
        (tax_unit["age"].between(19, tb["kgage"]))
        & tax_unit["ineducation"]
        & (tax_unit["w_hours"] <= 20)
    ] = True

    return elig


def kg_eligibility_wage(tax_unit, tb):
    """ Before 2011, there was an income ceiling for children
    returns a boolean variable whether a specific person is a child eligible for
    child benefit
    """
    elig = tax_unit["age"] <= 18
    elig[
        (tax_unit["age"].between(19, tb["kgage"]))
        & tax_unit["ineducation"]
        & (tax_unit["m_wage"] <= tb["kgfreib"] / 12)
    ] = True

    return elig
