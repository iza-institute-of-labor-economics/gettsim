from __future__ import annotations

import datetime
import itertools

import numpy as np
import pandas as pd

from _gettsim.config import RESOURCE_DIR, SUPPORTED_GROUPINGS
from _gettsim.policy_environment import _load_parameter_group_from_yaml

current_year = datetime.datetime.today().year


def append_other_hh_members(
    df, hh_typ, n_children, age_adults, gen_female, age_children, double_earner
):
    """duplicates information from the one person already created as often as needed and
    adjusts columns that differ."""
    # create empty dataframe with correct columns and datatypes
    new_df = df.iloc[0:0].copy()
    if hh_typ == "single" and n_children == 0:
        return None

    # If couple, create an additional adult
    if hh_typ == "couple":
        adult = df.copy()
        adult["alter"] = age_adults[1]
        adult["weiblich"] = gen_female[1]
        if not double_earner:
            adult["bruttolohn_m"] = 0

        new_df = pd.concat(objs=[new_df, adult], ignore_index=True)

    if n_children > 0:
        child = df.copy()
        child["kind"] = True
        child["in_ausbildung"] = True
        child["bruttolohn_m"] = 0
        if n_children == 1:
            children = child.copy()
            children["alter"] = age_children[0]
        elif n_children == 2:
            children = pd.concat(objs=[child, child], ignore_index=True)
            children["alter"] = age_children
        else:
            raise ValueError(n_children)
        # append children
        new_df = pd.concat(objs=[new_df, children])
    else:
        pass

    new_df["tu_vorstand"] = False

    return new_df


def create_synthetic_data(
    hh_typen=None,
    n_children=None,
    age_adults=None,
    gen_female=None,
    age_children=None,
    baujahr=1980,
    double_earner=False,
    policy_year=current_year,
    heterogeneous_vars=(),
    **kwargs,
):
    """Creates a dataset with hypothetical household types, which can be used as input
    for GETTSIM.

    hh_typen (list of str):
        Allowed Household Types: 'single', 'couple'

    n_children (list of int):
        number of children

    age_adults (list of int):
        Assumed age of adult(s)

    gen_female (list of bool):
        Assumend gender of adult(s), 'False' male 'True' female

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

    bruttolohn_m, kapitaleink_brutto_m, eink_selbst_m, vermögen_bedürft_hh (int):
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
    if gen_female is None:
        gen_female = [False, True]
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

    for g in gen_female:
        if g not in [False, True]:
            raise ValueError("gender weiblich must be bool.")

    p_id_min = 0
    group_mins = {}
    for g in SUPPORTED_GROUPINGS:
        group_mins[g] = 0

    if len(heterogeneous_vars) == 0:
        # If no heterogeneity specified,
        # just create the household types with default incomes.
        synth = create_one_set_of_households(
            p_id_min,
            group_mins,
            hh_typen,
            n_children,
            age_adults,
            gen_female,
            age_children,
            baujahr,
            double_earner,
            policy_year,
            bruttolohn_m=kwargs.get("bruttolohn_m", 2000.0),
        )
    else:
        synth = pd.DataFrame()
        dimensions = range(len(np.hstack(list(heterogeneous_vars.values()))))
        dim_counter = 0
        # find out how many dimensions there are in order to set household id.
        # loop over variables to vary
        for hetvar in heterogeneous_vars:
            # allow only certain variables to vary
            if hetvar not in [
                "bruttolohn_m",
                "kapitaleink_brutto_m",
                "eink_selbst_m",
                "vermögen_bedürft_hh",
            ]:
                raise ValueError(
                    f"Illegal value for variable to vary across households: {hetvar}"
                )
            for value in heterogeneous_vars[hetvar]:
                synth = pd.concat(
                    objs=[
                        synth,
                        create_one_set_of_households(
                            p_id_min,
                            group_mins,
                            hh_typen,
                            n_children,
                            age_adults,
                            gen_female,
                            age_children,
                            baujahr,
                            double_earner,
                            policy_year,
                            dimension=dimensions[dim_counter],
                            **{hetvar: value},
                        ),
                    ]
                )
                p_id_min = synth["p_id"].max() + 1
                for g in SUPPORTED_GROUPINGS:
                    group_mins[g] = synth[f"{g}_id"].max() + 1
                dim_counter += 1
        synth = synth.reset_index(drop=True)
    return synth


def create_one_set_of_households(
    p_id_min,
    group_mins,
    hh_typen,
    n_children,
    age_adults,
    gen_female,
    age_children,
    baujahr,
    double_earner,
    policy_year,
    **kwargs,
):
    """Create one set of households.

    If hetereogeneity in a dimension is considered (e.g. income) this creates all
    households with the same value.

    """
    # Initiate empty dataframe.
    # Same order as 'Basic Input Variables' in the documentation
    output_columns = [
        "kind",
        "bruttolohn_m",
        "alter",
        "weiblich",
        "rentner",
        "alleinerz",
        "wohnort_ost",
        "in_priv_krankenv",
        "priv_rentenv_beitr_m",
        "in_ausbildung",
        "selbstständig",
        "hat_kinder",
        "betreuungskost_m",
        "sonstig_eink_m",
        "eink_selbst_m",
        "eink_vermietung_m",
        "kapitaleink_brutto_m",
        "bruttokaltmiete_m_hh",
        "heizkosten_m_hh",
        "wohnfläche_hh",
        "bewohnt_eigentum_hh",
        "arbeitsstunden_w",
        "bruttolohn_vorj_m",
        "geburtstag",
        "geburtsmonat",
        "geburtsjahr",
        "jahr_renteneintr",
        "m_elterngeld",
        "m_elterngeld_mut_hh",
        "m_elterngeld_vat_hh",
        "behinderungsgrad",
        "mietstufe",
        "immobilie_baujahr",
        "vermögen_bedürft_hh",
        "entgeltp",
        "grundr_bew_zeiten",
        "grundr_entgeltp",
        "grundr_zeiten",
        "priv_rente_m",
        "schwerbeh_g",
        "m_pflichtbeitrag",
        "m_freiw_beitrag",
        "m_mutterschutz",
        "m_arbeitsunfähig",
        "m_krank_ab_16_bis_24",
        "m_arbeitslos",
        "m_ausbild_suche",
        "m_schul_ausbild",
        "m_geringf_beschäft",
        "m_alg1_übergang",
        "m_ersatzzeit",
        "m_kind_berücks_zeit",
        "m_pfleg_berücks_zeit",
        "y_pflichtbeitr_ab_40",
        "anwartschaftszeit",
        "arbeitssuchend",
        "m_durchg_alg1_bezug",
        "soz_vers_pflicht_5j",
        "bürgerg_bezug_vorj",
    ]
    # Create one row per desired household
    n_rows = len(hh_typen) * len(n_children)
    df = pd.DataFrame(
        columns=output_columns,
        data=np.zeros((n_rows, len(output_columns))),
    )
    for g in group_mins:
        df[f"{g}_id"] = pd.RangeIndex(n_rows) + group_mins[g]

    # Some columns require boolean type. initiate them with False
    for bool_col in [
        "selbstständig",
        "wohnort_ost",
        "hat_kinder",
        "kind",
        "rentner",
        "gem_veranlagt",
        "in_ausbildung",
        "alleinerz",
        "bewohnt_eigentum_hh",
        "in_priv_krankenv",
        "schwerbeh_g",
        "anwartschaftszeit",
        "arbeitssuchend",
    ]:
        df[bool_col] = False

    # Take care of bürgerg_bezug_vorj
    if policy_year >= 2023:
        df["bürgerg_bezug_vorj"] = True

    # Other columns require int type
    for int_col in [
        "behinderungsgrad",
        "m_elterngeld",
        "m_elterngeld_mut_hh",
        "m_elterngeld_vat_hh",
    ]:
        df[int_col] = df[int_col].astype(int)

    # 'Custom' initializations
    df["alter"] = age_adults[0]
    df["weiblich"] = gen_female[0]
    df["immobilie_baujahr"] = baujahr

    # Household Types
    all_types = pd.DataFrame(
        columns=["hht", "nch"], data=itertools.product(hh_typen, n_children)
    )

    df["hh_typ"] = all_types["hht"] + "_" + all_types["nch"].astype(str) + "_children"

    # wohnfläche_hh, Kaltmiete, Heizkosten are taken from official data
    bg_daten = _load_parameter_group_from_yaml(
        datetime.date(policy_year, 1, 1),
        RESOURCE_DIR / "synthetic_data" / "bedarfsgemeinschaften",
    )
    df["wohnfläche_hh"] = df["hh_typ"].map(bg_daten["wohnfläche"]).astype(float)
    df["bruttokaltmiete_m_hh"] = (
        df["hh_typ"].map(bg_daten["bruttokaltmiete"]).astype(float)
    )
    df["heizkosten_m_hh"] = df["hh_typ"].map(bg_daten["heizkosten"]).astype(float)
    df["mietstufe"] = 3

    # Income and wealth
    df["bruttolohn_m"] = kwargs.get("bruttolohn_m", 0.0)
    df["kapitaleink_brutto_m"] = kwargs.get("kapitaleink_brutto_m", 0.0)
    df["eink_selbst_m"] = kwargs.get("eink_selbst_m", 0.0)
    df["vermögen_bedürft_hh"] = kwargs.get("vermögen_bedürft_hh", 0.0)

    # append entries for children and partner
    for hht in hh_typen:
        for nch in n_children:
            df = pd.concat(
                objs=[
                    df,
                    append_other_hh_members(
                        df[
                            (df["hh_typ"].str[:6] == hht)
                            & (df["hh_typ"].str[7:8].astype(int) == nch)
                        ],
                        hht,
                        nch,
                        age_adults,
                        gen_female,
                        age_children,
                        double_earner,
                    ),
                ]
            )
    df = df.reset_index(drop=True)
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
        "alleinerz",
    ] = True

    # Retirement variables
    df["grundr_zeiten"] = (df["alter"] - 20).clip(lower=0) * 12
    df["grundr_bew_zeiten"] = df["grundr_zeiten"]
    df["entgeltp"] = df["grundr_zeiten"] / 12
    df["grundr_entgeltp"] = df["entgeltp"]

    # Rente Wartezeiten
    df["m_pflichtbeitrag"] = ((df["alter"] - 25).clip(lower=0) * 12).astype(float)
    df["y_pflichtbeitr_ab_40"] = ((df["alter"] - 40).clip(lower=0) * 12).astype(float)
    df["m_freiw_beitrag"] = 5.0
    df["m_ersatzzeit"] = 0.0
    df["m_schul_ausbild"] = 10.0
    df["m_arbeitsunfähig"] = 0.0
    df["m_krank_ab_16_bis_24"] = 0.0
    df["m_mutterschutz"] = 0.0
    df["m_arbeitslos"] = 0.0
    df["m_ausbild_suche"] = 0.0
    df["m_alg1_übergang"] = 0.0
    df["m_geringf_beschäft"] = 0.0
    df["m_kind_berücks_zeit"] = 24.0
    df["m_pfleg_berücks_zeit"] = 1.0

    group_ids = [f"{g}_id" for g in SUPPORTED_GROUPINGS]
    df = df.reset_index()
    df = df.sort_values(by=[*group_ids, "index"])
    df = df.drop(columns=["index"]).reset_index(drop=True)
    df["p_id"] = df.index + p_id_min

    df = df.sort_values(by=[*group_ids, "p_id"])

    return df[["p_id", *group_ids] + ["hh_typ"] + output_columns]
