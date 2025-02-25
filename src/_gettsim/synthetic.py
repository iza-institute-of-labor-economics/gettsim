from __future__ import annotations

import datetime

import numpy
import pandas as pd

from _gettsim.config import RESOURCE_DIR, SUPPORTED_GROUPINGS, TYPES_INPUT_VARIABLES
from _gettsim.policy_environment import _load_parameter_group_from_yaml

current_year = datetime.datetime.today().year


def create_synthetic_data(  # noqa: PLR0913
    n_adults=1,
    n_children=0,
    adults_married=True,
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
    adults_married : bool
        Whether the adults are married or not. Only relevant if n_adults is 2, default
        is True.
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
        "basic_inputs__weiblich": [
            bool(i % 2 == 1) for i in range(n_children + n_adults)
        ],
        "basic_inputs__alter": [35] * n_adults
        + [8, 5, 3, 1, 10, 9, 7, 6, 4, 2][:n_children],
        "basic_inputs__kind": [False] * n_adults + [True] * n_children,
        "basic_inputs__in_ausbildung": [False] * n_adults + [True] * n_children,
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
        n_adults,
        n_children,
        adults_married,
        specs_constant_over_households,
        specs_heterogeneous,
    )
    df = create_constant_across_households_variables(
        df, n_adults, n_children, policy_year
    )
    return df


def create_basic_households(
    n_adults,
    n_children,
    adults_married,
    specs_constant_over_households,
    specs_heterogeneous,
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
    adults_married : bool
        Whether the adults are married or not. Only relevant if n_adults is 2.
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
    hh_typ_string = create_hh_typ_string(n_adults, n_children)

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
        ges_pflegev_hat_kinder = [True] * n_adults + [False] * n_children
    else:
        ges_pflegev_hat_kinder = [False] * (n_adults)
    # Add specifications and create DataFrame
    all_households = [
        {
            "groupings__hh_id": [i] * (n_adults + n_children),
            "basic_inputs__hh_typ": [hh_typ_string] * (n_adults + n_children),
            "basic_inputs__ges_pflegev_hat_kinder": ges_pflegev_hat_kinder,
            "basic_inputs__alleinerz": alleinerziehend,
            # Assumption: All children are biological children of the adults, children
            # do not have children themselves
            "basic_inputs__ges_pflegev_anz_kinder_bis_24": [n_children] * n_adults
            + [0] * n_children,
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

    exogenous_groupings = [
        key
        for key, value in SUPPORTED_GROUPINGS.items()
        if not value.get("potentially_endogenous", True)
    ]
    group_ids = [f"groupings__{g}_id" for g in exogenous_groupings]
    df["groupings__p_id"] = df.index

    df = return_df_with_ids_for_aggregation(df, n_adults, n_children, adults_married)

    df = df[
        ["groupings__p_id", *group_ids]
        + [c for c in df if c not in [*group_ids, "groupings__p_id"]]
    ]
    df = df.sort_values(by=[*group_ids, "groupings__p_id"])

    return df


def return_df_with_ids_for_aggregation(data, n_adults, n_children, adults_married):
    """Create IDs for different groupings.

    Creates the following IDs:
    - p_id_elternteil_1
    - p_id_elternteil_2
    - p_id_kindergeld_empf
    - p_id_erziehgeld_empf
    - p_id_einstandspartner
    - p_id_ehepartner
    - p_id_betreuungsk_träger

    Parameters
    ----------
    data : pd.DataFrame
        DataFrame containing all basic variables.
    n_adults : int
        Number of adults in the household.
    n_children : int
        Number of children in the household.
    adults_married : bool
        Whether the adults are married or not. Only relevant if n_adults is 2.

    Returns
    -------
    data : pd.DataFrame
        DataFrame containing all basic variables and the new IDs.
    """
    # Create Elternteil IDs
    if n_children > 0:
        data = return_p_id_elternteil(data=data, n_adults=n_adults)
    else:
        data["groupings__p_id_elternteil_1"] = -1
        data["groupings__p_id_elternteil_2"] = -1
    data["groupings__p_id_kindergeld_empf"] = data["groupings__p_id_elternteil_1"]
    data["groupings__p_id_erziehgeld_empf"] = data["groupings__p_id_elternteil_1"]
    data["groupings__p_id_betreuungsk_träger"] = data["groupings__p_id_elternteil_1"]

    # Create other IDs
    if n_adults == 1:
        data["groupings__p_id_ehepartner"] = -1
        data["groupings__p_id_einstandspartner"] = data["groupings__p_id_ehepartner"]
    else:
        data_adults = data.query("basic_inputs__kind == False").copy()
        for hh_id, group in data_adults.groupby("groupings__hh_id"):
            relevant_rows = (data_adults["groupings__hh_id"] == hh_id).values
            data_adults.loc[relevant_rows, "groupings__p_id_einstandspartner"] = group[
                "groupings__p_id"
            ].tolist()[::-1]
        data = pd.merge(
            data,
            data_adults[["groupings__p_id", "groupings__p_id_einstandspartner"]],
            on="groupings__p_id",
            how="left",
        ).fillna(-1)
        data["groupings__p_id_einstandspartner"] = data[
            "groupings__p_id_einstandspartner"
        ].astype(numpy.int64)
        if adults_married:
            data["groupings__p_id_ehepartner"] = data[
                "groupings__p_id_einstandspartner"
            ]
        else:
            data["groupings__p_id_ehepartner"] = -1

    return data


def return_p_id_elternteil(data, n_adults):
    """Find the p_id_elternteil_1 and p_id_elternteil_2."""
    # p_id_elternteil_1 is the first adult in the household
    elternteil_1_candidate = {
        hh_id: group["groupings__p_id"].iloc[0]
        for hh_id, group in data.groupby("groupings__hh_id")
    }
    # Apply candidate id if kind, else -1
    data["groupings__p_id_elternteil_1"] = data.apply(
        lambda x: elternteil_1_candidate[x["groupings__hh_id"]]
        if x["basic_inputs__kind"]
        else -1,
        axis=1,
    )
    if n_adults == 2:
        data["groupings__p_id_elternteil_2"] = data.apply(
            lambda x: x["groupings__p_id_elternteil_1"] + 1
            if x["basic_inputs__kind"]
            else -1,
            axis=1,
        )
    else:
        data["groupings__p_id_elternteil_2"] = -1
    return data


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
    n_children_lookup = min(n_children, 2)
    hh_typ_string_lookup = create_hh_typ_string(n_adults, n_children_lookup)

    # Take care of bürgerg_bezug_vorj
    if policy_year >= 2023 and "basic_inputs__bürgerg_bezug_vorj" not in df:
        df["basic_inputs__bürgerg_bezug_vorj"] = True

    default_values = {
        "basic_inputs__gemeinsam_veranlagt": (
            df["basic_inputs__kind"] == False if n_adults == 2 else False  # noqa: E712
        ),
        "basic_inputs__eigenbedarf_gedeckt": False,
        "basic_inputs__mietstufe": 3,
        "basic_inputs__geburtsmonat": 1,
        "basic_inputs__geburtstag": 1,
        "basic_inputs__m_freiw_beitrag": 5.0,
        "basic_inputs__m_schul_ausbild": 10.0,
        "basic_inputs__m_kind_berücks_zeit": 24.0,
        "basic_inputs__m_pfleg_berücks_zeit": 1.0,
        "basic_inputs__elterngeld_nettoeinkommen_vorjahr_m": 20000.0,
        "basic_inputs__geburtsjahr": policy_year - df["basic_inputs__alter"],
        "basic_inputs__jahr_renteneintr": policy_year - df["basic_inputs__alter"] + 67,
        "basic_inputs__grundr_zeiten": (df["basic_inputs__alter"] - 20).clip(lower=0)
        * 12,
        "basic_inputs__grundr_bew_zeiten": (df["basic_inputs__alter"] - 20).clip(
            lower=0
        )
        * 12,
        "basic_inputs__entgeltp": (df["basic_inputs__alter"] - 20)
        .clip(lower=0)
        .astype(float),
        "basic_inputs__grundr_entgeltp": (df["basic_inputs__alter"] - 20)
        .clip(lower=0)
        .astype(float),
        "basic_inputs__m_pflichtbeitrag": (
            (df["basic_inputs__alter"] - 25).clip(lower=0) * 12
        ).astype(float),
        "basic_inputs__m_pflichtbeitrag_alt": (
            (df["basic_inputs__alter"] - 40).clip(lower=0) * 12
        ).astype(float),
        "basic_inputs__wohnfläche_hh": float(
            bg_daten["wohnfläche"][hh_typ_string_lookup]
        ),
        "basic_inputs__arbeitslosengeld_2__bruttokaltmiete_m_hh": float(
            bg_daten["bruttokaltmiete"][hh_typ_string_lookup]
        ),
        "basic_inputs__arbeitslosengeld_2__heizkosten_m_hh": float(
            bg_daten["heizkosten"][hh_typ_string_lookup]
        ),
    }

    # Set default values for new columns.
    types_input_variables_with_qualified_names = tree_to_dict_with_qualified_name(  # noqa: F821
        TYPES_INPUT_VARIABLES
    )
    for input_col, col_type in types_input_variables_with_qualified_names.items():
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


def create_hh_typ_string(n_adults, n_children):
    return f"{'single' if n_adults == 1 else 'couple'}_{n_children}_children"
