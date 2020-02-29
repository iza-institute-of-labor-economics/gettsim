"""This module contains auxiliary functions to apply the tax transfer functions on
household, tax unit or individual level."""


def apply_tax_transfer_func(
    df, tax_func, level, in_cols, out_cols, func_args=None, func_kwargs=None
):
    func_args = [] if func_args is None else func_args
    func_kwargs = {} if func_kwargs is None else func_kwargs

    df = df.reindex(columns=df.columns.tolist() + out_cols)
    if len(df.index) == 0:
        return df
    else:
        df.loc[:, in_cols + out_cols] = df.groupby(level)[in_cols + out_cols].apply(
            _apply_squeeze_function, tax_func, level, func_args, func_kwargs
        )
        return df


def _apply_squeeze_function(group, tax_func, level, func_args, func_kwargs):
    if level == ["hid", "tu_id", "pid"]:
        person = tax_func(group.squeeze(), *func_args, **func_kwargs)
        for var in person.index:
            group.loc[:, var] = person[var]
        return group
    else:
        return tax_func(group, *func_args, **func_kwargs)
