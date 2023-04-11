import datetime
import json
from itertools import groupby

from _gettsim.functions_loader import load_internal_functions
from _gettsim.policy_environment import is_time_dependent, is_active_at_date


def function_name(f):
    return f.__name__

def function_path(f):
    return str(f.__module__).replace("_gettsim.", "").replace(".", "/") + ".py"

if __name__ == '__main__':
    date = datetime.date(2023, 1, 1)

    all_functions = [
        f
        for f in load_internal_functions().values()
        if not is_time_dependent(f) or (is_time_dependent(f) and is_active_at_date(f, date))
    ]

    result = {
        key: [function_name(function) for function in functions]
        for key, functions in groupby(all_functions, function_path)
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))
