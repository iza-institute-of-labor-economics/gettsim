def check_boolean(df, variable_list):
    for variable in variable_list:
        assert df[variable].dtype == bool
