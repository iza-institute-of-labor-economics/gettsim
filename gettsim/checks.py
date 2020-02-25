def check_data(df):
    bool_variables = [
        "child",
        "east",
        "female",
        "head",
        "haskids",
        "pkv",
        "ineducation",
        "eigentum",
        "pensioner",
    ]
    for variable in bool_variables:
        try:
            assert df[variable].dtype == bool
        except TypeError:
            print(f"{variable} is not of type boolean.")

    positive_vars = ["mietstufe", "wohnfl", "miete"]
    for var in positive_vars:
        try:
            assert df[var].min() > 0
        except ValueError:
            print(f"{var} must be strictly positive.")

    try:
        assert df.notna().all().all()
    except ValueError:
        print("NaN value encountered in input data")

    try:
        assert (df.groupby("hid")["head"].sum() == 1).all()
        assert (df.groupby("hid_tu")["head_tu"].sum() == 1).all()
    except ValueError:
        print("There must be exactly one household head per household.")
        print(df["hid"].first())
