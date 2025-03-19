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
        sozialversicherung__pflege__beitrag__hat_kinder = [True] * n_adults + [
            False
        ] * n_children
    else:
        sozialversicherung__pflege__beitrag__hat_kinder = [False] * (n_adults)
    # Add specifications and create DataFrame
    all_households = [
        {
            "hh_id": [i] * (n_adults + n_children),
            "hh_typ": [hh_typ_string] * (n_adults + n_children),
            "sozialversicherung__pflege__beitrag__hat_kinder": sozialversicherung__pflege__beitrag__hat_kinder,  # noqa: E501
            "alleinerziehend": alleinerziehend,
            # Assumption: All children are biological children of the adults, children
            # do not have children themselves
            "sozialversicherung__pflege__beitrag__anzahl_kinder_bis_24": [n_children]
            * n_adults
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
    group_ids = [f"{g}_id" for g in exogenous_groupings]
    df["p_id"] = df.index

    df = return_df_with_ids_for_aggregation(df, n_adults, n_children, adults_married)

    df = df[["p_id", *group_ids] + [c for c in df if c not in [*group_ids, "p_id"]]]
    df = df.sort_values(by=[*group_ids, "p_id"])

    return df


def return_df_with_ids_for_aggregation(data, n_adults, n_children, adults_married):
    """Create IDs for different groupings.

    Creates the following IDs:
    - demographics__p_id_elternteil_1
    - demographics__p_id_elternteil_2
    - kindergeld__p_id_empfänger
    - erziehungsgeld__p_id_empfänger
    - arbeitslosengeld_2__p_id_einstandspartner
    - demographics__p_id_ehepartner
    - einkommensteuer__abzüge__p_id_betreuungskosten_träger

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
        data["demographics__p_id_elternteil_1"] = -1
        data["demographics__p_id_elternteil_2"] = -1
    data["kindergeld__p_id_empfänger"] = data["demographics__p_id_elternteil_1"]
    data["erziehungsgeld__p_id_empfänger"] = data["demographics__p_id_elternteil_1"]
    data["einkommensteuer__abzüge__p_id_betreuungskosten_träger"] = data[
        "demographics__p_id_elternteil_1"
    ]

    # Create other IDs
    if n_adults == 1:
        data["demographics__p_id_ehepartner"] = -1
        data["arbeitslosengeld_2__p_id_einstandspartner"] = data[
            "demographics__p_id_ehepartner"
        ]
    else:
        data_adults = data.query("kind == False").copy()
        for demographics__hh_id, group in data_adults.groupby("hh_id"):
            relevant_rows = (data_adults["hh_id"] == demographics__hh_id).values
            data_adults.loc[
                relevant_rows, "arbeitslosengeld_2__p_id_einstandspartner"
            ] = group["p_id"].tolist()[::-1]
        data = pd.merge(
            data,
            data_adults[["p_id", "arbeitslosengeld_2__p_id_einstandspartner"]],
            on="p_id",
            how="left",
        ).fillna(-1)
        data["arbeitslosengeld_2__p_id_einstandspartner"] = data[
            "arbeitslosengeld_2__p_id_einstandspartner"
        ].astype(numpy.int64)
        if adults_married:
            data["demographics__p_id_ehepartner"] = data[
                "arbeitslosengeld_2__p_id_einstandspartner"
            ]
        else:
            data["demographics__p_id_ehepartner"] = -1

    return data


def return_p_id_elternteil(data, n_adults):
    """Find the demographics__p_id_elternteil_1 and demographics__p_id_elternteil_2."""
    # demographics__p_id_elternteil_1 is the first adult in the household
    elternteil_1_candidate = {
        demographics__hh_id: group["p_id"].iloc[0]
        for demographics__hh_id, group in data.groupby("hh_id")
    }
    # Apply candidate id if demographics__kind, else -1
    data["demographics__p_id_elternteil_1"] = data.apply(
        lambda x: elternteil_1_candidate[x["hh_id"]] if x["kind"] else -1,
        axis=1,
    )
    if n_adults == 2:
        data["demographics__p_id_elternteil_2"] = data.apply(
            lambda x: x["demographics__p_id_elternteil_1"] + 1 if x["kind"] else -1,
            axis=1,
        )
    else:
        data["demographics__p_id_elternteil_2"] = -1
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

    # Take care of arbeitslosengeld_2__arbeitslosengeld_2_bezug_im_vorjahr
    if (
        policy_year >= 2023
        and "arbeitslosengeld_2__arbeitslosengeld_2_bezug_im_vorjahr" not in df
    ):
        df["arbeitslosengeld_2__arbeitslosengeld_2_bezug_im_vorjahr"] = True

    default_values = {
        "einkommensteuer__gemeinsam_veranlagt": (
            df["kind"] == False if n_adults == 2 else False  # noqa: E712
        ),
        "eigenbedarf_gedeckt": False,
        "mietstufe": 3,
        "geburtsmonat": 1,
        "geburtstag": 1,
        "rente__altersrente__freiwillige_beitragsmonate": 5.0,
        "rente__altersrente__schulausbildung_m": 10.0,
        "rente__altersrente__kinderberücksichtigungszeiten_monate": 24.0,
        "rente__altersrente__pflegeberücksichtigungszeiten_monate": 1.0,
        "elterngeld__nettoeinkommen_vorjahr_m": 20000.0,
        "geburtsjahr": policy_year - df["alter"],
        "jahr_renteneintr": policy_year - df["alter"] + 67,
        "rente__grundrente__sozialversicherung__rente__grundrente__grundrentenzeiten_monate": (  # noqa: E501
            df["alter"] - 20
        ).clip(lower=0)
        * 12,
        "rente__grundrente__bewertungszeiten_monate": (df["alter"] - 20).clip(lower=0)
        * 12,
        "entgeltp": (df["alter"] - 20).clip(lower=0).astype(float),
        "rente__grundrente__entgeltpunkte": (df["alter"] - 20)
        .clip(lower=0)
        .astype(float),
        "rente__altersrente__pflichtbeitragsmonate": (
            (df["alter"] - 25).clip(lower=0) * 12
        ).astype(float),
        "rente__altersrente__pflichtbeitragsmonate_alt": (
            (df["alter"] - 40).clip(lower=0) * 12
        ).astype(float),
        "wohnfläche_hh": float(bg_daten["wohnfläche"][hh_typ_string_lookup]),
        "wohnen__bruttokaltmiete_m_hh": float(
            bg_daten["bruttokaltmiete"][hh_typ_string_lookup]
        ),
        "arbeitslosengeld_2__heizkosten_m_hh": float(
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
