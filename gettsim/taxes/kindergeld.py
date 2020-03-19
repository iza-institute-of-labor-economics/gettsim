import numpy as np


def kindergeld(tax_unit, params):
    """ Child Benefit (kindergeld)
    Basic Amount for each child. Parents receive child benefit for every child up to
    18 years. Above, they get it only up to kindergeld_params["kgage"] if the child is
    a) in education and
    b) not working too much / not receiving too much income (depending on the year)

    Returns:
        pd.series:
            kindergeld_m_basis: Kindergeld on the individual level
            kindergeld_m_tu_basis: Kindergeld summed up within the tax unit
    """

    tax_unit["kindeld_anspruch"] = params["kindergeld_anspruch_regel"](
        tax_unit, params
    ).cumsum()

    kg_amounts = {
        1: params["kgeld1"],
        2: params["kgeld2"],
        3: params["kgeld3"],
        4: params["kgeld4"],
    }
    tax_unit["kindergeld_m_basis"] = tax_unit["kindeld_anspruch"].replace(kg_amounts)
    tax_unit.loc[tax_unit["kindeld_anspruch"] > 4, "kindergeld_m_basis"] = params[
        "kgeld4"
    ]
    tax_unit["kindergeld_m_tu_basis"] = np.sum(tax_unit["kindergeld_m_basis"])

    return tax_unit


def kindergeld_anspruch_nach_stunden(tax_unit, params):
    """ Nowadays, kids must not work more than 20 hour
    returns a boolean variable whether a specific person is a child eligible for
    child benefit
    """
    anspruch = tax_unit["alter"] <= 18
    anspruch[
        (tax_unit["alter"].between(19, params["kgage"]))
        & tax_unit["in_ausbildung"]
        & (tax_unit["arbeitsstunden_w"] <= 20)
    ] = True

    return anspruch


def kindergeld_anspruch_nach_lohn(tax_unit, params):
    """ Before 2011, there was an income ceiling for children
    returns a boolean variable whether a specific person is a child eligible for
    child benefit
    """
    anspruch = tax_unit["alter"] <= 18
    anspruch[
        (tax_unit["alter"].between(19, params["kgage"]))
        & tax_unit["in_ausbildung"]
        & (tax_unit["bruttolohn_m"] <= params["kgfreib"] / 12)
    ] = True

    return anspruch
