from gettsim.dag import fail_if_functions_and_columns_overlap


def test_fail_if_functions_and_columns_overlap():
    func_dict = {"a": None}
    data = {"a": None}

    fail_if_functions_and_columns_overlap(func_dict, data)
