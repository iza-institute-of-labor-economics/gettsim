def aggr(df, inc, unit):
    """ Function to aggregate some (income) variable within the household

        args:
            df: the dataframe in which aggregation takes place. Needs to have
            the variable 'inc', but also ['zveranl', 'hid', 'tu_id']
        inc: the variable to aggregate
        unit: The household members among which you aggregate;
        'adult_married': the 2 adults of the tax unit (if they are married!)
                         Do this for taxable incomes and the like.
                         If they are not married, but form a tax unit,
                         which makes sense from a labor supply point of view,
                         the variable 'inc' is not summed up.
        'all_tu': all members (incl. children) of the tax_unit
        'all_hh': all members (incl. children) of the Household

        returns one series with suffix _tu or _tu_k, depending on the
        parameter 'withkids'
    """
    if unit == "adult_married":
        df[inc + "_tu"] = df[inc]
        df[df["zveranl"]][inc + "tu"] = df[df["zveranl"]][inc].sum()
        return df[inc + "_tu"]

    if unit == "all_tu":
        df = df.join(
            df.groupby(["tu_id"])[inc].sum(), on=["tu_id"], how="left", rsuffix="_sum"
        )
        df[inc + "_tu_k"] = df[inc + "_sum"]

        return df[inc + "_tu_k"]

    if unit == "all_hh":
        df = df.join(
            df.groupby(["hid"])[inc].sum(), on=["hid"], how="left", rsuffix="_sum"
        )
        df[inc + "_hh"] = df[inc + "_sum"]

        return df[inc + "_hh"]
