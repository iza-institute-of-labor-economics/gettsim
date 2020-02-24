def check_data(df):
    bool_variables = ["child", "east", "female"]
    for variable in bool_variables:
        try:
            assert df[variable].dtype == bool
        except TypeError:
            print(f"{variable} is not of type boolean.")

    positive_vars = ["mietstufe", "wohnfl", "miete"]
    for var in positive_vars:
        try:
            print(var)
            print(df[var].min())
            assert df[var].min() > 0
        except ValueError:
            print(f"{var} must be strictly positive.")
            print(df[var].describe())

    try:
        assert df.notna().all()
    except ValueError:
        print("")

    try:
        assert (df.groupby("hid")["head"].sum() == 1).all()
    except ValueError:
        print("There must be exactly one household head per household.")
        print(df["hid"].first())
