def elt_geld(person, params):
    """This function calculates the monthly benefits for having
    a child that is up to one year old (Elterngeld)"""

    if person["elt_zeit"]:
        elt_geld_calc = person["m_wage"] * params["elgfaktor"]

        person["elt_geld"] = min(elt_geld_calc, params["elgmax"])

    else:
        person["elt_geld"] = 0

    return person
