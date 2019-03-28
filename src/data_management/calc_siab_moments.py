""" generates moments from SIAB Data

    should be based on which years?
"""

import pandas as pd
import numpy as np

# import statsmodels.api as sm
import statsmodels.formula.api as smf
from bld.project_paths import project_paths_join as ppj
from statsmodels.iolib.summary2 import summary_col
import matplotlib.pyplot as plt


def ols2csv(filename, out):
    with open(filename, "w") as f:
        for line in out:
            f.write(line)


df = pd.read_pickle(ppj("SIAB_PATH", "siab_recoded.pickle"))

# kick out very early years
df = df[df["year"] > 1990]

# inspect data
df[(df["female"] == 0) & (df["age"].between(15, 65))].groupby("year")["working"].sum().plot(
)
df[(df["female"] == 1) & (df["age"].between(15, 65))].groupby("year")["working"].sum().plot(
)
plt.savefig(ppj("OUT_FIGURES", "siab_employment.png"))
plt.clf()
df[(df["female"] == 0) & (df["age"].between(15, 65))].groupby("year")["unempl"].sum().plot(
)
df[(df["female"] == 1) & (df["age"].between(15, 65))].groupby("year")["unempl"].sum().plot(
)
plt.savefig(ppj("OUT_FIGURES", "siab_unemployment.png"))


df = df.sort_values(by=["pers_id", "spell"])
# Employment Dynamics
# Transition rates between labor market status
df["empstat_l"] = df["empstat"].shift(1)
# Transition matrix. needs to be differentiated by subgroups

trans_emp = pd.DataFrame(
    columns=["n"],
    index=pd.MultiIndex.from_product(
        [df["female"].unique(), df["empstat_l"].unique(), df["empstat"].unique()],
        names=["female", "from", "to"],
    ),
)

for gr in df["female"].unique():
    for before in df["empstat"].unique():
        for after in df["empstat"].unique():
            transition = (
                (df["empstat"] == after) & (df["empstat_l"] == before) & (df["female"] == gr)
            )
            # Count number of particular transitions and write into matrix
            trans_emp.loc[gr, before, after] = transition.sum()

# replace the counts with shares
trans_emp = trans_emp.dropna()
trans_emp = trans_emp.div(trans_emp.groupby(level=["female", "from"]).sum())
trans_emp = trans_emp.fillna(0)

print("Transition matrix between employment states: \n {}".format(trans_emp))

# OLS Regressions of log wage on experience, education, by gender
df["experience2"] = df["experience"] ** 2
df.loc[df["wage"] > 0, "log_wage"] = np.log(df["wage"])

men = df[(df["female"] == 0) & (~df["log_wage"].isna()) & (~df["experience"].isna())]
ols_wage_male = smf.ols(formula="log_wage ~ experience + experience2 + age + C(skill)", data=men)

women = df[(df["female"] == 1) & (~df["log_wage"].isna()) & (~df["experience"].isna())]
ols_wage_female = smf.ols(
    formula="log_wage ~ experience + experience2 + age + C(skill)", data=women
)
print(
    "OLS of log wage on experience and education \n {}".format(
        summary_col(
            [ols_wage_male.fit(), ols_wage_female.fit()], stars=True, model_names=["Men", "Women"]
        )
    )
)


# Export Regression results
# ols2csv(ppj("OUT_DATA", "siab_ols_wage_male.csv"),
# ols_wage_male.fit().params)
# ols2csv(ppj("OUT_DATA", "siab_ols_wage_female.csv"),
#       ols_wage_female.fit().params)
ols_wage_male.fit().params.to_csv(ppj("OUT_DATA", "siab_ols_wage_male.csv"), header=True)
ols_wage_female.fit().params.to_csv(ppj("OUT_DATA", "siab_ols_wage_female.csv"), header=True)


# keep only the most recent year.
df = df[df["year"] == df["year"].max()]
# Age Group
df["agegr"] = df["age"] // 5

df["ft"] = df["teilzeit"] == 0
df["pt"] = df["teilzeit"] == 1
# By which variables are moments to be generated?
groupvars = ["female", "agegr"]
# Proportion of full-time work
ft_shares = df.groupby(groupvars)["ft"].mean()
# Proportion of part-time work
pt_shares = df.groupby(groupvars)["pt"].mean()
# Proportion out of work
inact_shares = df.groupby(groupvars)["inact"].mean()

# Work experience by age
exp_by_age = df.groupby(groupvars)["experience"].mean()

for out in [ft_shares, pt_shares, inact_shares, exp_by_age]:
    headers = groupvars + [out.name]
    out.to_csv(
        path_or_buf=ppj("OUT_DATA", "siab_{}.csv".format(out.name)),
        index=groupvars,
        header=True,
        index_label=groupvars,
    )
    print(out)

# TO DO: Export results
