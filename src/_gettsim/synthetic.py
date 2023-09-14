from __future__ import annotations

import datetime

import pandas as pd

from _gettsim.config import RESOURCE_DIR, SUPPORTED_GROUPINGS, TYPES_INPUT_VARIABLES
from _gettsim.policy_environment import _load_parameter_group_from_yaml

current_year = datetime.datetime.today().year


def create_synthetic_data(
    n_adults=1,
    n_children=0,
    specs_constant_over_households=None,
    specs_heterogeneous=None,
    policy_year=current_year,
):
    """Create a dataset with hypothetical household types, which can be used as input
    for GETTSIM.

    Parameters
    ----------
    n_adults : int
        Number of adults in the household, must be either 1 or 2, default is 1.
    n_children : int
        Number of children in the household, must be 0, 1, or 2, default is 0.
    specs_constant_over_households : dict of lists
        Values for variables that might vary within households, but are constant across
        households.
    specs_heterogeneous : dict of lists of lists
        Values for variables that vary over households.
    policy_year : int
        Year for which the data set should be created. This is relevant for the
        calculation of birthyear based on age.

    Returns
    -------
    data : pd.DataFrame containing all variables that are needed to run GETTSIM.

    """
    # Check inputs
    if n_adults not in [1, 2]:
        raise ValueError("'n_adults' must be either 1 or 2")
    if n_children not in list(range(11)):
        raise ValueError("'n_children' must be between 0 and 10.")

    default_constant_specs = {
        "weiblich": [bool(i % 2 == 1) for i in range(n_children + n_adults)],
        "alter": [35] * n_adults + [8, 5, 3, 1, 10, 9, 7, 6, 4, 2][:n_children],
        "kind": [False] * n_adults + [True] * n_children,
        "in_ausbildung": [False] * n_adults + [True] * n_children,
    }
    if specs_constant_over_households:
        default_constant_specs.update(specs_constant_over_households)
    specs_constant_over_households = default_constant_specs

    # Make sure length of lists in specs_constant_over_households is correct
    for var in specs_constant_over_households:
        if len(specs_constant_over_households[var]) != n_adults + n_children:
            raise ValueError(
                f"Length of {var} in specs_constant_over_households is not correct."
            )

    if specs_heterogeneous is None:
        specs_heterogeneous = {}
    df = create_basic_households(
        n_adults, n_children, specs_constant_over_households, specs_heterogeneous
    )
    df = create_constant_across_households_variables(
        df, n_adults, n_children, policy_year
    )
    return df


def create_basic_households(
    n_adults, n_children, specs_constant_over_households, specs_heterogeneous
):
    """Create basic variables for all households.

    Basic variables are variables which:

    - are important to differentiate the individual household members
    - or vary across households (as specified in specs_heterogeneous)

    Parameters
    ----------
    n_adults : int
        Number of adults in the household.
    n_children : int
        Number of children in the household.
    specs_constant_over_households : dict of lists
        Values for variables that might vary within households, but are constant across
        households. The length of the lists must be equal to n_adults + n_children.
    specs_heterogeneous : dict of lists of lists
        Values for variables that vary over households. The length of the outer lists
        equal the number of generated households and must be the same over all entries
        in specs_heterogeneous. The inner lists must be of length n_adults +
        n_children.

    Returns
    -------
    data : pd.DataFrame containing all basic variables.

    """
    hh_typ_string = create_vg_typ_string(n_adults, n_children)

    # Identify number of households
    if len(specs_heterogeneous) > 0:
        n_households = len(next(iter(specs_heterogeneous.values())))
    else:
        n_households = 1

    for col in specs_heterogeneous:
        if len(specs_heterogeneous[col]) != n_households:
            raise ValueError(
                f"Length of {col} in specs_heterogeneous is not "
                "the same as all the other columns."
            )

    if n_adults == 1 and n_children > 0:
        alleinerziehend = [True] + [False] * n_children
    else:
        alleinerziehend = [False] * (n_children + n_adults)
    if n_children > 0:
        hat_kinder = [True] * n_adults + [False] * n_children
    else:
        hat_kinder = [False] * (n_adults)
    # Add specifications and create DataFrame
    all_households = [
        {
            "vg_id": [i] * (n_adults + n_children),
            "tu_id": [i] * (n_adults + n_children),
            "hh_typ": [hh_typ_string] * (n_adults + n_children),
            "hat_kinder": hat_kinder,
            "alleinerz": alleinerziehend,
            # Assumption: All children are biological children of the adults, children
            # do not have children themselves
            "anz_eig_kind_bis_24": [n_children] * n_adults + [0] * n_children,
            **specs_constant_over_households,
            **{v: k[i] for v, k in specs_heterogeneous.items()},
        }
        for i in range(n_households)
    ]
    df = pd.DataFrame(
        {
            k: [v for i in range(len(all_households)) for v in all_households[i][k]]
            for k in all_households[0]
        }
    )

    group_ids = [f"{g}_id" for g in SUPPORTED_GROUPINGS]
    df["p_id"] = df.index
    df = df[["p_id", *group_ids] + [c for c in df if c not in [*group_ids, "p_id"]]]
    df = df.sort_values(by=[*group_ids, "p_id"])

    return df


def create_constant_across_households_variables(df, n_adults, n_children, policy_year):
    """Add variables to household that do not vary over households.

    This module could at some point be reused to impute default values for missing
    variables when GETTSIM is run.

    """
    df = df.copy()

    # Defaults for Wohnfläche, Kaltmiete, Heizkosten are taken from official data
    bg_daten = _load_parameter_group_from_yaml(
        datetime.date(policy_year, 1, 1),
        RESOURCE_DIR / "synthetic_data" / "bedarfsgemeinschaften",
    )

    # Use data for 2 children if there are more than 2 children in the household.
    n_children_lookup = n_children if n_children <= 2 else 2
    hh_typ_string_lookup = create_vg_typ_string(n_adults, n_children_lookup)

    # Take care of bürgerg_bezug_vorj
    if policy_year >= 2023 and "bürgerg_bezug_vorj" not in df:
        df["bürgerg_bezug_vorj"] = True

    default_values = {
        "mietstufe": 3,
        "geburtsmonat": 1,
        "geburtstag": 1,
        "m_freiw_beitrag": 5.0,
        "m_schul_ausbild": 10.0,
        "m_kind_berücks_zeit": 24.0,
        "m_pfleg_berücks_zeit": 1.0,
        "geburtsjahr": policy_year - df["alter"],
        "jahr_renteneintr": policy_year - df["alter"] + 67,
        "grundr_zeiten": (df["alter"] - 20).clip(lower=0) * 12,
        "grundr_bew_zeiten": (df["alter"] - 20).clip(lower=0) * 12,
        "entgeltp": (df["alter"] - 20).clip(lower=0).astype(float),
        "grundr_entgeltp": (df["alter"] - 20).clip(lower=0).astype(float),
        "m_pflichtbeitrag": ((df["alter"] - 25).clip(lower=0) * 12).astype(float),
        "m_pflichtbeitrag_alt": ((df["alter"] - 40).clip(lower=0) * 12).astype(float),
        "wohnfläche_vg": float(bg_daten["wohnfläche"][hh_typ_string_lookup]),
        "bruttokaltmiete_m_vg": float(
            bg_daten["bruttokaltmiete"][hh_typ_string_lookup]
        ),
        "heizkosten_m_vg": float(bg_daten["heizkosten"][hh_typ_string_lookup]),
        "kind_unterh_anspr_m": 0.0,
        "kind_unterh_erhalt_m": 0.0,
    }

    # Set default values for new columns.
    for input_col, col_type in TYPES_INPUT_VARIABLES.items():
        if input_col not in df:
            if input_col in default_values:
                df[input_col] = default_values[input_col]
            else:
                if col_type == bool:
                    df[input_col] = False
                elif col_type == int:
                    df[input_col] = 0
                elif col_type == float:
                    df[input_col] = 0.0
                else:
                    raise ValueError(f"Column type {col_type} not yet supported.")

    return df


def create_vg_typ_string(n_adults, n_children):
    return f"{'single' if n_adults == 1 else 'couple'}_{n_children}_children"
