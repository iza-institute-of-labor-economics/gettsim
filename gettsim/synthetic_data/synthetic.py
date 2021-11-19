import datetime
import itertools

import numpy as np
import pandas as pd

from gettsim.config import ROOT_DIR
from gettsim.policy_environment import _load_parameter_group_from_yaml


def append_other_hh_members(
    df, hh_typ, n_children, age_adults, age_children, double_earner
):
    """
    duplicates information from the one person already created
    as often as needed and adjusts columns that differ
    """
    # create empty dataframe with correct columns and datatypes
    new_df = df.iloc[0:0].copy()
    if hh_typ == "single" and n_children == 0:
        return None

    # If couple, create an additional adult
    if hh_typ == "couple":
        adult = df.copy()
        adult["alter"] = age_adults[1]
        if not double_earner:
            adult["bruttolohn_m"] = 0

        new_df = new_df.append(adult, ignore_index=True)

    child = df.copy()
    child["kind"] = True
    child["in_ausbildung"] = True
    child["bruttolohn_m"] = 0

    if n_children == 1:
        children = child.copy()
        children["alter"] = age_children[0]
    elif n_children == 2:
        children = child.append(child, ignore_index=True)
        children["alter"] = age_children
    else:
        children = None

    # append children
    new_df = new_df.append(children)
    new_df["tu_vorstand"] = False

    return new_df


def create_synthetic_data(
    hh_typen=None,
    n_children=None,
    age_adults=None,
    age_children=None,
    baujahr=1980,
    double_earner=False,
    policy_year=datetime.datetime.now().year,
    heterogeneous_vars=(),
    **kwargs,
):
    """
    Creates a dataset with hypothetical household types,
    which can be used as input for gettsim

    hh_typen (list of str):
        Allowed Household Types: 'single', 'couple'

    n_children (list of int):
        number of children

    age_adults (list of int):
        Assumed age of adult(s)

    age_children (list of int):
        Assumed age of children (first and second child, respectively)

    baujahr (int):
        Construction year of building

    double_earner (bool):
        whether or not both adults should be assigned the same value for 'bruttolohn_m'

    heterogenous_vars (dict):
        if specified, contains the variable name as key and a list of values

    policy_year (int):
        the year from which the reference data on housing are drawn.

    kwargs:

    bruttolohn_m, kapital_eink_m, eink_selbst_m, vermögen_hh (int):
        values for income and wealth, respectively.
        only valid if heterogenous_vars is empty
    """
    # Set Defaults
    if hh_typen is None:
        hh_typen = ["single", "couple"]
    if n_children is None:
        n_children = [0, 1, 2]
    if age_adults is None:
        age_adults = [35, 35]
    if age_children is None:
        age_children = [3, 8]

    # Check inputs
    for t in hh_typen:
        if t not in ["single", "couple"]:
            raise ValueError("household type must be either 'single'  or 'couple'")

    if type(hh_typen) is not list:
        raise ValueError("'hh_typen' must be a list")

    if type(n_children) is not list:
        if n_children not in [0, 1, 2]:
            raise ValueError("'n_children' must be 0, 1, or 2.")
        else:
            n_children = [n_children]

    for a in age_adults + age_children:
        if (a < 0) or (type(a) != int):
            raise ValueError(f"illegal value for age: {a}")

    if len(heterogeneous_vars) == 0:
        # If no heterogeneity specified,
        # just create the household types with default incomes.
        synth = create_one_set_of_households(
            hh_typen,
            n_children,
            age_adults,
            age_children,
            baujahr,
            double_earner,
            policy_year,
            bruttolohn_m=kwargs.get("bruttolohn_m", 2000),
        )
    else:
        synth = pd.DataFrame()
        dimensions = range(len(np.hstack(list(heterogeneous_vars.values()))))
        dim_counter = 0
        # find out how many dimensions there are in order to set household id.
        # loop over variables to vary
        for hetvar in heterogeneous_vars.keys():
            # allow only certain variables to vary
            if hetvar not in [
                "bruttolohn_m",
                "kapital_eink_m",
                "eink_selbst_m",
                "vermögen_hh",
            ]:
                raise ValueError(
                    f"Illegal value for variable to vary across households: {hetvar}"
                )
            for value in heterogeneous_vars[hetvar]:
                synth = synth.append(
                    create_one_set_of_households(
                        hh_typen,
                        n_children,
                        age_adults,
                        age_children,
                        baujahr,
                        double_earner,
                        policy_year,
                        dimension=dimensions[dim_counter],
                        **{hetvar: value},
                    )
                )
                dim_counter += 1

    synth = synth.reset_index()
    synth["p_id"] = synth.index

    return synth


def create_one_set_of_households(
    hh_typen,
    n_children,
    age_adults,
    age_children,
    baujahr,
    double_earner,
    policy_year,
    **kwargs,
):
    """ creates one set of households
    """
    # Initiate empty dataframe.
    # Same order as 'Basic Input Variables' in the documentation
    output_columns = [
        "kind",
        "bruttolohn_m",
        "alter",
        "rentner",
        "alleinerziehend",
        "wohnort_ost",
        "prv_krankenv",
        "prv_rente_beitr_m",
        "in_ausbildung",
        "selbstständig",
        "hat_kinder",
        "betreuungskost_m",
        "sonstig_eink_m",
        "eink_selbst_m",
        "vermiet_eink_m",
        "kapital_eink_m",
        "bruttokaltmiete_m_hh",
        "heizkosten_m_hh",
        "wohnfläche_hh",
        "bewohnt_eigentum_hh",
        "arbeitsl_lfdj_m",
        "arbeitsl_vorj_m",
        "arbeitsl_vor2j_m",
        "arbeitsstunden_w",
        "bruttolohn_vorj_m",
        "geburtstag",
        "geburtsmonat",
        "geburtsjahr",
        "jahr_renteneintr",
        "m_elterngeld",
        "m_elterngeld_mut",
        "m_elterngeld_vat",
        "behinderungsgrad",
        "mietstufe",
        "immobilie_baujahr",
        "vermögen_hh",
        "entgeltpunkte",
        "gr_bewertungszeiten",
        "entgeltp_grundr",
        "grundrentenzeiten",
        "prv_rente_m",
    ]
    # Create one row per desired household
    df = pd.DataFrame(
        columns=output_columns,
        data=np.zeros((len(hh_typen) * len(n_children), len(output_columns))),
    )

    # Some columns require boolean type. initiate them with False
    for bool_col in [
        "selbstständig",
        "wohnort_ost",
        "hat_kinder",
        "kind",
        "rentner",
        "gem_veranlagt",
        "in_ausbildung",
        "alleinerziehend",
        "bewohnt_eigentum_hh",
        "prv_krankenv",
    ]:
        df[bool_col] = False

    # Other columns require int type
    for int_col in [
        "behinderungsgrad",
        "m_elterngeld",
        "m_elterngeld_mut",
        "m_elterngeld_vat",
        "arbeitsl_lfdj_m",
        "arbeitsl_vorj_m",
        "arbeitsl_vor2j_m",
    ]:
        df[int_col] = df[int_col].astype(int)

    # 'Custom' initializations
    df["alter"] = age_adults[0]
    df["immobilie_baujahr"] = baujahr

    # Household Types
    all_types = pd.DataFrame(
        columns=["hht", "nch"], data=itertools.product(hh_typen, n_children)
    )

    df["hh_typ"] = all_types["hht"] + "_" + all_types["nch"].astype(str) + "_children"

    # wohnfläche_hh, Kaltmiete, Heizkosten are taken from official data
    bg_daten = _load_parameter_group_from_yaml(
        datetime.date(policy_year, 1, 1),
        f"{ROOT_DIR}/synthetic_data/bedarfsgemeinschaften",
    )
    df["wohnfläche_hh"] = df["hh_typ"].map(bg_daten["wohnfläche"])
    df["bruttokaltmiete_m_hh"] = df["hh_typ"].map(bg_daten["bruttokaltmiete"])
    df["heizkosten_m_hh"] = df["hh_typ"].map(bg_daten["heizkosten"])
    df["mietstufe"] = 3

    # Income and wealth
    df["bruttolohn_m"] = kwargs.get("bruttolohn_m", 0)
    df["kapital_eink_m"] = kwargs.get("kapital_eink_m", 0)
    df["eink_selbst_m"] = kwargs.get("eink_selbst_m", 0)
    df["vermögen_hh"] = kwargs.get("vermögen_hh", 0)
    dim = kwargs.get("dimension", 1)

    df["hh_id"] = 100 * dim + df.index
    df["tu_id"] = 100 * dim + df.index

    # append entries for children and partner
    for hht in hh_typen:
        for nch in n_children:
            df = df.append(
                append_other_hh_members(
                    df[
                        (df["hh_typ"].str[:6] == hht)
                        & (df["hh_typ"].str[7:8].astype(int) == nch)
                    ],
                    hht,
                    nch,
                    age_adults,
                    age_children,
                    double_earner,
                )
            )
    df = df.reset_index()
    df["geburtsjahr"] = policy_year - df["alter"]
    df["geburtsmonat"] = 1
    df["geburtstag"] = 1
    df["jahr_renteneintr"] = df["geburtsjahr"] + 67

    df.loc[~df["kind"], "hat_kinder"] = (
        df.groupby("hh_typ")["kind"].transform("sum") > 0
    )
    df.loc[df["bruttolohn_m"] > 0, "arbeitsstunden_w"] = 38

    # All adults in couples are assumed to be married
    df["gem_veranlagt"] = False
    df.loc[
        (df["hh_typ"].str.contains("couple")) & (~df["kind"]), "gem_veranlagt"
    ] = True

    # Single Parent Dummy
    df.loc[
        (df["hh_typ"].str.contains("single"))
        & (df["hh_typ"].str[7:8].astype(int) > 0)
        & (~df["kind"]),
        "alleinerziehend",
    ] = True

    # Retirement variables
    df["grundrentenzeiten"] = (df["alter"] - 20).clip(lower=0) * 12
    df["gr_bewertungszeiten"] = df["grundrentenzeiten"]
    df["entgeltpunkte"] = df["grundrentenzeiten"] / 12
    df["entgeltp_grundr"] = df["entgeltpunkte"]

    df = df.sort_values(by=["hh_typ", "hh_id"])

    df = df.reset_index()
    df["p_id"] = df.index

    return df[["hh_id", "tu_id", "p_id", "hh_typ"] + output_columns]
