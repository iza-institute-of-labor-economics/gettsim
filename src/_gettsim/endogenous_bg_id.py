"""This module computes the bg_id endogenously.

Step 1: Compute the fg_id.

"""

import numpy
import pandas as pd

from _gettsim.groupings import bg_id_numpy
from _gettsim.interface import compute_taxes_and_transfers


def determine_bg_and_wthh_ids(
    data: pd.DataFrame,
    params: dict[str, any],
    functions: dict[str, callable],
) -> [pd.Series, pd.Series]:
    """Determine bg_id and wthh_id endogenously.

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

    input_data = data.copy()

    _fail_if_bg_or_wthh_id_already_present(input_data)
    _fail_if_minimal_specification_missing(input_data)

    if "fg_id" not in input_data.columns:
        # Compute a dict of fg_ids
        fg_ids = compute_fg_id(
            data=input_data,
            params=params,
            functions=functions,
        )
        # Assign fg_ids to input_data
        input_data["fg_id"] = fg_ids

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
        p_id: fg_ids[p_id]
        for p_id in input_data["p_id"]
        if p_id in fgs_with_covered_needs
    }
    bg_id_result.update(bg_id_update)
    # Set wthh_id to fg_id if needs of whole fg are covered
    wthh_id_update = {
        p_id: fg_ids[p_id]
        for p_id in input_data["p_id"]
        if p_id in fgs_with_covered_needs
    }
    wthh_id_result.update(wthh_id_update)

    ### Step 2: Determine whether needs are covered individually
    input_data_without_covered_fgs = input_data.query(
        "p_id not in @fgs_with_covered_needs"
    )
    needs_covered_individually_dict = _own_needs_covered_individually(
        data=input_data_without_covered_fgs,
        policy_params=params,
        policy_functions=functions,
    )

    ### Step 3: Perform Vorrang- and Günstigerprüfung
    bg_id_update, wthh_id_update = vorrangprüfung_and_günstigerprüfung_on_fg_level(
        data=input_data_without_covered_fgs,
        policy_params=params,
        policy_functions=functions,
        needs_covered_individually_dict=needs_covered_individually_dict,
    )
    bg_id_result.update(bg_id_update)
    wthh_id_result.update(wthh_id_update)

    return pd.Series(bg_id_result), pd.Series(wthh_id_result)


def compute_fg_id(
    data: pd.DataFrame,
    policy_params: dict[str, any],
    policy_functions: dict[str, callable],
) -> dict[int, int]:
    """Let GETTSIM compute the fg_id.

    Returns a dict that maps each p_id to an fg_id.

    Parameters
    ----------
    data : pd.DataFrame
        The input data.
    policy_params : dict[str, any]
        The policy parameters.
    policy_functions : dict[str, callable]
        The policy functions.
    """
    result = (
        compute_taxes_and_transfers(
            data=data,
            params=policy_params,
            functions=policy_functions,
            targets=["fg_id"],
        )
        .join(data["p_id"])
        .reset_index()
        .set_index("p_id")
    )

    return result["fg_id"].to_dict()


def bürgergeld_claim_for_whole_fg(
    data: pd.DataFrame,
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
    input_data = data.copy()
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
        .reset_index()
        .set_index("p_id")
    )
    result_only_fgs_without_bürgergeld_claim = gettsim_result.query(
        "arbeitsl_geld_2_vor_vorrang_ohne_kindereinkommen_m_bg == 0.0"
    )

    return result_only_fgs_without_bürgergeld_claim.to_dict()


def _own_needs_covered_individually(
    data: pd.DataFrame,
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
    input_data = data.copy()
    # TODO: Move this function to this module
    input_data["bg_id"] = bg_id_numpy(
        fg_id=input_data["fg_id"].to_numpy(),
        hh_id=input_data["hh_id"].to_numpy(),
        alter=input_data["alter"].to_numpy(),
        eigenbedarf_gedeckt=[True for _ in range(len(input_data))],
    )

    # Call GETTSIM to compute if eigenbedarf is covered
    result_vorrangprüfung = (
        compute_taxes_and_transfers(
            data=input_data,
            params=policy_params,
            functions=policy_functions,
            targets=[
                "vorrangprüfung_bg",
            ],
        )
        .join(input_data["p_id"])
        .reset_index()
        .set_index("p_id")
    )["vorrangprüfung_bg"]

    return result_vorrangprüfung.to_dict()


def vorrangprüfung_and_günstigerprüfung_on_fg_level(
    data: pd.DataFrame,
    policy_params: dict[str, any],
    policy_functions: dict[str, callable],
    needs_covered_individually_dict: dict[int, bool],
) -> [pd.Series, pd.Series]:
    """Outcome of the Vorrang- and Günstigerprüfung on `fg` level.

    The Günstigerprüfung is preceeded by the Vorrangprüfung which checks whether the
    Bedarfsgemeinschaft can cover its own SGB II needs. If they do, they can only apply
    for Wohngeld. If they do not, the Günstigerprüfung checks which constellation of
    bg_ids and wthh_ids maximizes income for the individuals in the fg. Individuals have
    a limited right to choose between Wohngeld and Bürgergeld: If Wohngeld yields the
    higher transfer, they can apply for it even if their own needs are not covered
    without Wohngeld.
    """
    input_data = data.copy()
    # Set candidate bg_ids and wthh_ids
    candidates = _create_data_with_candidate_ids(
        needs_covered_individually_dict=needs_covered_individually_dict,
        data=input_data,
    )

    # Call GETTSIM for both candidates
    results = {}
    for name, df in candidates.items():
        results[name] = compute_taxes_and_transfers(
            data=df,
            params=policy_params,
            functions=policy_functions,
            targets=["günstigerprüfung_on_hh_level"],
        )


def _create_data_with_candidate_ids(
    needs_covered_individually_dict: dict[int, bool],
    data: pd.DataFrame,
) -> dict[pd.Dataframe, pd.Dataframe]:
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
    input_data["wthh_id_no_wohngeld"] = input_data["hh_id"] * 100
    input_data["wthh_id_with_wohngeld"] = input_data["hh_id"] * 100 + 1

    ### Candidate 1
    candidate_fg_forms_bg = input_data.copy()
    candidate_fg_forms_bg["wthh_id"] = input_data["wthh_id_with_wohngeld"]
    candidate_fg_forms_bg["bg_id"] = input_data["fg_id"]

    ### Candidate 2
    candidate_parents_have_own_bg = input_data.copy()

    # Assign wthh_id_no_wohngeld to all adults
    candidate_parents_have_own_bg.loc[
        not candidate_parents_have_own_bg["kind"], "wthh_id"
    ] = candidate_parents_have_own_bg["wthh_id_no_wohngeld"]

    # Assign wthh_id_no_wohngeld to children whose needs are not covered
    needs_not_covered = input_data["p_id"].apply(
        lambda x: not needs_covered_individually_dict[x]
    )
    candidate_parents_have_own_bg.loc[
        candidate_parents_have_own_bg["kind"] & needs_not_covered, "wthh_id"
    ] = candidate_parents_have_own_bg["wthh_id_no_wohngeld"]

    # Assign wthh_id_with_wohngeld to other children
    candidate_parents_have_own_bg.loc[
        candidate_parents_have_own_bg["kind"]
        & candidate_parents_have_own_bg["wthh_id"].isnull(),
        "wthh_id",
    ] = candidate_parents_have_own_bg["wthh_id_with_wohngeld"]
    candidate_parents_have_own_bg["wthh_id"] = candidate_parents_have_own_bg[
        "wthh_id"
    ].astype(int)

    # Set bg_id
    candidate_parents_have_own_bg["bg_id"] = _set_bg_id_based_on_covered_needs_check(
        eigenbedarf_gedeckt_dict=needs_covered_individually_dict,
        input_data=candidate_parents_have_own_bg,
    ).astype(int)

    return {
        "candidate_fg_forms_bg": candidate_fg_forms_bg,
        "candidate_parents_have_own_bg": candidate_parents_have_own_bg,
    }


def _set_bg_id_based_on_covered_needs_check(
    needs_covered_individually_dict: dict[int, bool],
    data: pd.DataFrame,
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


def _fail_if_minimal_specification_missing(data: pd.DataFrame) -> None:
    """Raise an error if the minimal specification is missing."""


def _fail_if_bg_or_wthh_id_already_present(data: pd.DataFrame) -> None:
    """Raise an error if bg_id or wthh_id is already in data."""
    if "bg_id" in data.columns or "wthh_id" in data.columns:
        raise ValueError(
            "bg_id or wthh_id are already in the data. Remove them if you want to "
            "compute them endogenously."
        )
