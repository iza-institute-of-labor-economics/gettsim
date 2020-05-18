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
    tax_unit["kindergeld_anspruch"] = tax_unit["_kindergeld_anspruch"].cumsum()
    # Kindergeld_Anspruch is the cumulative sum of eligible children.
    # This maps to the dictionary key for the kindergeld amount
    tax_unit["kindergeld_m_basis"] = tax_unit["kindergeld_anspruch"].replace(
        params["kindergeld"]
    )
    tax_unit.loc[tax_unit["kindergeld_anspruch"] > 4, "kindergeld_m_basis"] = params[
        "kindergeld"
    ][4]
    return tax_unit
