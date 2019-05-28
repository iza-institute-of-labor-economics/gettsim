# -*- coding: utf-8 -*-
"""
Created on Fri May 24 09:17:49 2019

@author: iza6354
"""
import pandas as pd

from bld.project_paths import project_paths_join as ppj


def mw_pensions(df):
    """ Calculates mean wages by SOEP year. Will be used in tax_transfer for pension calculations
    """
    print("Pensions Calculations...")
    rent = df[["syear", "m_wage", "female", "east", "pweight", "civilservant"]][
        (df["m_wage"] > 100) & ~df["selfemployed"]
    ]
    # calculates weighted mean wages by year
    # all earnings.
    rent["wage_weighted"] = rent["m_wage"] * 12 * rent["pweight"]
    # only wages subject to social security contributions
    rent["wage_weighted_subsample"] = rent["wage_weighted"][
        ~rent["civilservant"] & (rent["m_wage"] > 450)
    ]
    rent["pweight_sub"] = rent["pweight"][~rent["civilservant"] & (rent["m_wage"] > 450)]
    years = rent.groupby("syear")
    mw = pd.DataFrame()
    mw["meanwages"] = round(years["wage_weighted"].sum() / years["pweight"].sum(), 2)
    mw["meanwages_sub"] = round(
        years["wage_weighted_subsample"].sum() / years["pweight_sub"].sum(), 2
    )
    return mw


if __name__ == "__main__":
    df = pd.read_pickle(ppj("SOEP_PATH", "2_taxben_input.dta"))
    mw_pensions(df)
