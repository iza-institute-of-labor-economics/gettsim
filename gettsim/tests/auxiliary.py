import pandas as pd


def select_output_by_level(out_col, year_data, dtype=float):
    if "_tu" in out_col:
        grouped_id = "tu_id"
    elif "_hh" in out_col:
        grouped_id = "hh_id"
    else:
        return year_data[out_col]

    # If level is not person, create custom series.
    out = pd.Series(index=year_data[grouped_id].unique(), name=out_col, dtype=dtype)
    for index in out.index:
        out.loc[index] = year_data[year_data[grouped_id] == index][out_col].iloc[0]
    return out
