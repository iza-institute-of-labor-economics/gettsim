import types


def create_function(func, func_name, arg_names):
    varnames = {k: k for k in func.__code__.co_varnames}
    renamed_varnames = {k: arg_names.get(k, k) for k in varnames}
    new_varnames = tuple(renamed_varnames.values())

    y_code = types.CodeType(
        func.__code__.co_argcount,
        func.__code__.co_kwonlyargcount,
        func.__code__.co_nlocals,
        func.__code__.co_stacksize,
        func.__code__.co_flags,
        func.__code__.co_code,
        func.__code__.co_consts,
        func.__code__.co_names,
        new_varnames,
        func.__code__.co_filename,
        func_name,
        func.__code__.co_firstlineno,
        func.__code__.co_lnotab,
    )

    return types.FunctionType(y_code, func.__globals__, func_name)
