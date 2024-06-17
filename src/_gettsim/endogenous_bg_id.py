"""This module computes the bg_id endogenously.

It follows this logic:

1. We determine Familiengemeinschaften that have no claim for Bürgergeld. These will
   always be in the same Bedarfsgemeinschaft and wohngeldrechtlicher Teilhaushalt.
2. We do the Vorrangprüfung and Günstigerprüfung for two candidate specifications: a)
   Parents and children that cannot cover their SGB II needs are in a different
   Bedarfsgemeinschaft than children who can cover their SGB II needs; b) the whole
   Familiengemeinschaft is in the same Bedarfsgemeinschaft. We then compute whether in
   Scenario (a), the Bedarfsgemeinschaft is eligible for Bürgergeld (Vorrangprüfung). If
   not, we accept scenario (b). If the Bedarfsgemeinschaft of scenario (a) is eligible
   for Bürgergeld, we take the specification that maximizes income on the fg level
   (Günstigerprüfung / eingeschränktes Wahlrecht zwischen Wohngeld und Bürgergeld).
3. We assign the bg_id and wthh_id according to the results of the Vorrang- and
   Günstigerprüfung. We also determine whether the BG takes up Bürgergeld or Wohngeld
   which is a basic input variable in GETTSIM (`wohngeld_und_kiz_günstiger_als_sgb_ii`).
"""

import numpy
import pandas as pd

from _gettsim.groupings import bg_id_numpy
from _gettsim.interface import compute_taxes_and_transfers


def determine_bg_and_wthh_ids(
    data,
    params: dict[str, any],
    functions: dict[str, callable],
) -> [pd.Series, pd.Series]:
    """Determine bg_id and wthh_id endogenously. Also determines the outcome of the
    Günstigerprüfung.

    Return the correct setting of bg_id and wthh_id using the Günstiger- and
    Vorrangprüfung of Wohngeld and Bürgergeld given the input data.

    Parameters
    ----------
    data : pd.DataFrame
        The input data.
    params : dict[str, any]
        The policy parameters.
    functions : dict[str, callable]
        The policy functions.
    """
    bg_id_result = {}
    wthh_id_result = {}
    wohngeld_und_kiz_günstiger_als_sgb_ii = {}

    input_data = data.copy().set_index("p_id")

    _fail_if_bg_or_wthh_id_already_present(input_data)

    if "fg_id" not in input_data.columns:
        # Compute a dict of fg_ids
        fg_ids = compute_fg_id(
            data=input_data,
            params=params,
            functions=functions,
        )
        # Assign fg_ids to input_data
        input_data["fg_id"] = pd.Series(fg_ids)

    _fail_if_more_than_one_fg_in_hh(
        hh_id=input_data["hh_id"].to_numpy(),
        fg_id=input_data["fg_id"].to_numpy(),
    )

    ### Step 1: Set bg_id and wthh_id if there is no Bürgergeld claim for whole fg
    # Compute Bürgergeld claim
    fgs_with_covered_needs = bürgergeld_claim_for_whole_fg(
        data=input_data,
        policy_params=params,
        policy_functions=functions,
    )
    # Set bg_id to fg_id if needs of whole fg are covered
    bg_id_update = {
        p_id: fg_ids[p_id] * 100
        for p_id in input_data.index
        if p_id in fgs_with_covered_needs
    }
    bg_id_result.update(bg_id_update)
    # Set wthh_id to fg_id if needs of whole fg are covered
    wthh_id_update = {
        p_id: fg_ids[p_id] * 100
        for p_id in input_data.index
        if p_id in fgs_with_covered_needs
    }
    wthh_id_result.update(wthh_id_update)
    # Set wohngeld_und_kiz_günstiger_als_sgb_ii to True if needs of whole fg are covered
    wohngeld_und_kiz_günstiger_als_sgb_ii_update = {
        p_id: True for p_id in input_data.index if p_id in fgs_with_covered_needs
    }
    wohngeld_und_kiz_günstiger_als_sgb_ii.update(
        wohngeld_und_kiz_günstiger_als_sgb_ii_update
    )

    ### Step 2: Determine whether needs are covered individually
    input_data_without_covered_fgs = input_data.loc[
        ~input_data.index.isin(fgs_with_covered_needs)
    ]
    needs_covered_individually_dict = _own_needs_covered_individually(
        data=input_data_without_covered_fgs,
        policy_params=params,
        policy_functions=functions,
    )
    ### Step 3: Perform Vorrang- and Günstigerprüfung
    wthh_id_update, bg_id_update, wohngeld_und_kiz_günstiger_als_sgb_ii_update = (
        vorrangprüfung_and_günstigerprüfung_on_fg_level(
            data=input_data_without_covered_fgs,
            policy_params=params,
            policy_functions=functions,
            needs_covered_individually_dict=needs_covered_individually_dict,
        )
    )
    bg_id_result.update(bg_id_update)
    wthh_id_result.update(wthh_id_update)
    wohngeld_und_kiz_günstiger_als_sgb_ii.update(
        wohngeld_und_kiz_günstiger_als_sgb_ii_update
    )

    return (
        pd.Series(bg_id_result).astype(int),
        pd.Series(wthh_id_result).astype(int),
        pd.Series(wohngeld_und_kiz_günstiger_als_sgb_ii).astype(bool),
    )


def compute_fg_id(
    data,
    params: dict[str, any],
    functions: dict[str, callable],
) -> dict[int, int]:
    """Let GETTSIM compute the fg_id.

    Returns a dict that maps each p_id to an fg_id.

    Parameters
    ----------
    data : pd.DataFrame
        The input data.
    params : dict[str, any]
        The policy parameters.
    functions : dict[str, callable]
        The policy functions.
    """
    input_data = data.copy().reset_index()
    result = (
        compute_taxes_and_transfers(
            data=input_data,
            params=params,
            functions=functions,
            targets=["fg_id"],
        )
        .join(input_data["p_id"])
        .reset_index()
        .set_index("p_id")
    )

    return result["fg_id"].to_dict()


def bürgergeld_claim_for_whole_fg(
    data,
    policy_params: dict[str, any],
    policy_functions: dict[str, callable],
) -> dict[int, bool]:
    """Determine which fg_id has a Bürgergeld claim for the whole fg excluding child
    income.

    Assumes that the whole fg_id forms a Bedarfsgemeinschaft and computes their
    Bürgergeld claim. If there is no Bürgergeld claim, the fg_id does not qualify for
    SGB II transfers and, hence, will have the same bg_id and wthh_id.

    Parameters
    ----------
    data : pd.DataFrame
        The input data.
    policy_params : dict[str, any]
        The policy parameters.
    policy_functions : dict[str, callable]
        The policy functions.
    """
    input_data = data.copy().reset_index()
    input_data["bg_id"] = input_data["fg_id"]

    ## Call GETTSIM to compute if eigenbedarf is covered
    gettsim_result = (
        compute_taxes_and_transfers(
            data=input_data,
            params=policy_params,
            functions=policy_functions,
            targets=["arbeitsl_geld_2_vor_vorrang_ohne_kindereinkommen_m_bg"],
        )
        .join(input_data["p_id"])
        .set_index("p_id")
    )
    result_only_fgs_without_bürgergeld_claim = gettsim_result.query(
        "arbeitsl_geld_2_vor_vorrang_ohne_kindereinkommen_m_bg == 0.0"
    )

    fgs_with_covered_needs = {
        p_id: True for p_id in result_only_fgs_without_bürgergeld_claim.index
    }

    return fgs_with_covered_needs


def _own_needs_covered_individually(
    data,
    policy_params: dict[str, any],
    policy_functions: dict[str, callable],
) -> dict[int, bool]:
    """Individuals that can cover their SGB II needs with own income.

    Returns a dict that maps each p_id to a boolean indicating whether the
    individual can cover their SGB II needs with their own income.

    Parameters
    ----------
    data : pd.DataFrame
        The input data.
    policy_params : dict[str, any]
        The policy parameters.
    policy_functions : dict[str, callable]
        The policy functions.
    """
    input_data = data.copy().reset_index()
    # TODO: Move this function to this module
    input_data["bg_id"] = bg_id_numpy(
        fg_id=input_data["fg_id"].to_numpy(),
        alter=input_data["alter"].to_numpy(),
        eigenbedarf_gedeckt=[True for _ in range(len(input_data))],
    )

    # Call GETTSIM to compute if eigenbedarf is covered
    result_vorrangprüfung = (
        compute_taxes_and_transfers(
            data=input_data,
            params=policy_params,
            functions=policy_functions,
            targets=["vorrangprüfung_bg"],
        )
        .join(input_data["p_id"])
        .reset_index()
        .set_index("p_id")
    )["vorrangprüfung_bg"]

    return result_vorrangprüfung.to_dict()


def vorrangprüfung_and_günstigerprüfung_on_fg_level(
    data,
    policy_params: dict[str, any],
    policy_functions: dict[str, callable],
    needs_covered_individually_dict: dict[int, bool],
) -> [pd.Series, pd.Series, pd.Series]:
    """Outcome of the Vorrang- and Günstigerprüfung on `fg` level.

    The Günstigerprüfung is preceeded by the Vorrangprüfung which checks whether the
    Bedarfsgemeinschaft can cover its own SGB II needs. If they do, they can only apply
    for Wohngeld. If they do not, the Günstigerprüfung checks which constellation of
    bg_ids and wthh_ids maximizes income for the individuals in the fg. Individuals have
    a limited right to choose between Wohngeld and Bürgergeld: If Wohngeld yields the
    higher transfer, they can apply for it even if their own needs are not covered
    without Wohngeld.
    """
    wthh_id_result = {}
    bg_id_result = {}
    wohngeld_und_kiz_günstiger_als_sgb_ii_result = {}
    input_data = data.copy().reset_index()
    # Set candidate bg_ids and wthh_ids
    candidates = _create_data_with_candidate_ids(
        needs_covered_individually_dict=needs_covered_individually_dict,
        data=input_data,
    )

    # Call GETTSIM for both candidates
    results = {}
    for name, df in candidates.items():
        results[name] = (
            compute_taxes_and_transfers(
                data=df,
                params=policy_params,
                functions=policy_functions,
                targets=[
                    "vorrangprüfung_bg",
                    "_transfereinkommen_für_günstigerprüfung_fg",
                    "wohngeld_m_wthh",
                    "kinderzuschl_m_bg",
                    "arbeitsl_geld_2_m_bg",
                ],
            )
            .reset_index()
            .join(
                df[
                    [
                        "hh_id",
                        "p_id",
                        "wthh_id",
                        "bg_id",
                        "wohngeld_und_kiz_günstiger_als_sgb_ii",
                        "fg_id",
                    ]
                ]
            )
            .set_index("p_id")
        )

    hh_ids = numpy.unique(input_data["hh_id"])
    for this_hh_id in hh_ids:
        current_hh_parents_have_own_bg = results["candidate_parents_have_own_bg"].query(
            f"hh_id == {this_hh_id}"
        )
        parental_bg = current_hh_parents_have_own_bg.query(
            "wohngeld_und_kiz_günstiger_als_sgb_ii == False"
        )
        current_hh_fg_forms_bg = results["candidate_fg_forms_bg"].query(
            f"hh_id == {this_hh_id}"
        )

        _fail_if_bg_id_or_wthh_id_not_unique(data=[parental_bg, current_hh_fg_forms_bg])

        whole_fg_wohngeld_günstiger = (
            current_hh_fg_forms_bg["_transfereinkommen_für_günstigerprüfung_fg"].max()
            > current_hh_parents_have_own_bg[
                "_transfereinkommen_für_günstigerprüfung_fg"
            ].max()
        )
        # Not eligible for BüG or fg income is maximized by Wohngeld for parental BG
        if parental_bg["vorrangprüfung_bg"].all() or whole_fg_wohngeld_günstiger:
            wthh_id_update = dict(
                zip(current_hh_fg_forms_bg.index, current_hh_fg_forms_bg["wthh_id"])
            )
            bg_id_update = dict(
                zip(current_hh_fg_forms_bg.index, current_hh_fg_forms_bg["bg_id"])
            )
            wohngeld_und_kiz_günstiger_als_sgb_ii_result_update = dict(
                zip(
                    current_hh_fg_forms_bg.index,
                    current_hh_fg_forms_bg["wohngeld_und_kiz_günstiger_als_sgb_ii"],
                )
            )
        # Bürgergeld for parental BG maximizes fg income
        else:
            wthh_id_update = dict(
                zip(
                    current_hh_parents_have_own_bg.index,
                    current_hh_parents_have_own_bg["wthh_id"],
                )
            )
            bg_id_update = dict(
                zip(
                    current_hh_parents_have_own_bg.index,
                    current_hh_parents_have_own_bg["bg_id"],
                )
            )
            wohngeld_und_kiz_günstiger_als_sgb_ii_result_update = dict(
                zip(
                    current_hh_parents_have_own_bg.index,
                    current_hh_parents_have_own_bg[
                        "wohngeld_und_kiz_günstiger_als_sgb_ii"
                    ],
                )
            )

        wthh_id_result.update(wthh_id_update)
        bg_id_result.update(bg_id_update)
        wohngeld_und_kiz_günstiger_als_sgb_ii_result.update(
            wohngeld_und_kiz_günstiger_als_sgb_ii_result_update
        )

    _fail_if_not_all_p_ids_are_covered(
        data=input_data,
        id_list=[
            wthh_id_result,
            bg_id_result,
            wohngeld_und_kiz_günstiger_als_sgb_ii_result,
        ],
    )

    return wthh_id_result, bg_id_result, wohngeld_und_kiz_günstiger_als_sgb_ii_result


def _create_data_with_candidate_ids(
    needs_covered_individually_dict: dict[int, bool],
    data,
) -> dict:
    """Helper function to set the candidate bg_ids and wthh_ids.

    There are two candidate outcomes:
        Candidate 1: Parents and children who cannot cover their needs are in a
        different Bedarfsgemeisnschaft than children who can cover their needs.
            - Parents receive Bürgergeld, children receive Wohngeld
        Candidate 2: The whole fg is in the same Bedarfsgemeinschaft.
            - Whole fg receives Wohngeld
    """
    input_data = data.copy()
    ### Initialize wthh_id columns
    input_data["wthh_id_no_wohngeld"] = input_data["fg_id"] * 100
    input_data["wthh_id_with_wohngeld"] = input_data["fg_id"] * 100 + 1

    ### Candidate 1
    candidate_fg_forms_bg = input_data.copy()
    candidate_fg_forms_bg["wthh_id"] = input_data["wthh_id_with_wohngeld"]
    candidate_fg_forms_bg["bg_id"] = input_data["fg_id"] * 100
    candidate_fg_forms_bg["_needs_covered_individually"] = candidate_fg_forms_bg[
        "p_id"
    ].map(needs_covered_individually_dict)
    candidate_fg_forms_bg["wohngeld_und_kiz_günstiger_als_sgb_ii"] = (
        candidate_fg_forms_bg.groupby("fg_id")["_needs_covered_individually"].transform(
            "any"
        )
    )

    ### Candidate 2
    candidate_parents_have_own_bg = input_data.copy()

    # Assign wthh_id_no_wohngeld to all adults
    candidate_parents_have_own_bg.loc[
        ~candidate_parents_have_own_bg["kind"], "wthh_id"
    ] = candidate_parents_have_own_bg["wthh_id_no_wohngeld"]
    candidate_parents_have_own_bg.loc[
        ~candidate_parents_have_own_bg["kind"],
        "wohngeld_und_kiz_günstiger_als_sgb_ii",
    ] = False

    # Assign wthh_id_no_wohngeld to children whose needs are not covered
    needs_not_covered = input_data["p_id"].apply(
        lambda x: not needs_covered_individually_dict[x]
    )
    candidate_parents_have_own_bg.loc[
        candidate_parents_have_own_bg["kind"] & needs_not_covered, "wthh_id"
    ] = candidate_parents_have_own_bg["wthh_id_no_wohngeld"]
    candidate_parents_have_own_bg.loc[
        candidate_parents_have_own_bg["kind"] & needs_not_covered,
        "wohngeld_und_kiz_günstiger_als_sgb_ii",
    ] = False

    # Assign wthh_id_with_wohngeld to other children
    candidate_parents_have_own_bg.loc[
        candidate_parents_have_own_bg["kind"] & ~needs_not_covered,
        "wthh_id",
    ] = candidate_parents_have_own_bg["wthh_id_with_wohngeld"]
    candidate_parents_have_own_bg.loc[
        candidate_parents_have_own_bg["kind"] & ~needs_not_covered,
        "wohngeld_und_kiz_günstiger_als_sgb_ii",
    ] = True

    # Set bg_id
    candidate_parents_have_own_bg["bg_id"] = _set_bg_id_based_on_covered_needs_check(
        needs_covered_individually_dict=needs_covered_individually_dict,
        data=candidate_parents_have_own_bg,
    )

    # Set types
    candidate_fg_forms_bg["wthh_id"] = candidate_fg_forms_bg["wthh_id"].astype(int)
    candidate_fg_forms_bg["bg_id"] = candidate_fg_forms_bg["bg_id"].astype(int)
    candidate_fg_forms_bg["wohngeld_und_kiz_günstiger_als_sgb_ii"] = (
        candidate_fg_forms_bg["wohngeld_und_kiz_günstiger_als_sgb_ii"].astype(bool)
    )
    candidate_parents_have_own_bg["wthh_id"] = candidate_parents_have_own_bg[
        "wthh_id"
    ].astype(int)
    candidate_parents_have_own_bg["bg_id"] = candidate_parents_have_own_bg[
        "bg_id"
    ].astype(int)
    candidate_parents_have_own_bg["wohngeld_und_kiz_günstiger_als_sgb_ii"] = (
        candidate_parents_have_own_bg["wohngeld_und_kiz_günstiger_als_sgb_ii"].astype(
            bool
        )
    )

    return {
        "candidate_fg_forms_bg": candidate_fg_forms_bg,
        "candidate_parents_have_own_bg": candidate_parents_have_own_bg,
    }


def _set_bg_id_based_on_covered_needs_check(
    needs_covered_individually_dict: dict[int, bool],
    data,
) -> pd.Series:
    """Helper function to set a candidate bg_id given wthh_id and information about
    needs covered.
    """
    # Base bg_id on fg_id
    data["base_bg_id"] = data["fg_id"] * 100

    # Default assignment for all to base_bg_id
    data["bg_id"] = data["base_bg_id"]

    # Identify children with needs covered
    children_needs_covered = data["kind"] & data["p_id"].map(
        needs_covered_individually_dict
    ).fillna(False)

    # Assign unique bg_id to each child with needs covered
    data.loc[children_needs_covered, "bg_id"] = data["base_bg_id"] + data["p_id"]

    return data["bg_id"].astype(int)


def _fail_if_more_than_one_fg_in_hh(
    hh_id: numpy.ndarray[int],
    fg_id: numpy.ndarray[int],
):
    """
    Fail if there is more than one `fg_id` in a household.

    Parameters
    ----------
    hh_id : numpy.ndarray[int]
        Array of household IDs.
    fg_id : numpy.ndarray[int]
        Array of family group IDs.
    """
    unique_hh_ids = numpy.unique(hh_id)
    hh_ids_with_multiple_fgs_list = []
    for this_hh_id in unique_hh_ids:
        # Find all family group IDs for the current household ID
        fg_ids_in_hh = fg_id[hh_id == this_hh_id]
        if len(numpy.unique(fg_ids_in_hh)) > 1:
            hh_ids_with_multiple_fgs_list.append(this_hh_id)
    hh_ids_with_multiple_fgs = set(hh_ids_with_multiple_fgs_list)
    error_msg = (
        "There are households with more than one `fg_id`. GETTSIM does not support the "
        "endogenous creation of Bedarfsgemeinschaften in this case yet. Please provide "
        "`bg_id` and `wthh_id` yourself for the following households: "
        f"{hh_ids_with_multiple_fgs}."
    )
    assert len(hh_ids_with_multiple_fgs) == 0, error_msg


def _fail_if_bg_or_wthh_id_already_present(data) -> None:
    """Raise an error if bg_id or wthh_id is already in data."""
    if "bg_id" in data.columns or "wthh_id" in data.columns:
        raise ValueError(
            "bg_id or wthh_id are already in the data. Remove them if you want to "
            "compute them endogenously."
        )


def _fail_if_bg_id_or_wthh_id_not_unique(data: list) -> None:
    """Raise an error if bg_id or wthh_id is not unique in the data."""
    for this_data in data:
        if this_data["bg_id"].nunique() > 1 or this_data["wthh_id"].nunique() > 1:
            raise ValueError("bg_id or wthh_id are not unique in the data.")


def _fail_if_not_all_p_ids_are_covered(data, id_list: list[dict]) -> None:
    """Raise an error if not all p_ids were assigned a bg_id or wthh_id."""
    for this_id_dict in id_list:
        if len([p_id for p_id in data["p_id"] if p_id not in this_id_dict]) > 0:
            raise ValueError("Not all p_ids were assigned a bg_id or wthh_id.")
