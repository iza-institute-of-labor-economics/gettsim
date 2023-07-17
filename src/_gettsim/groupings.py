from typing import Callable

import numpy


def create_groupings() -> dict[str, Callable]:
    return {"bg_id": bg_id_numpy, "st_id": st_id_numpy}


def bg_id_numpy(  # noqa: PLR0913
    p_id: numpy.ndarray,
    hh_id: numpy.ndarray,
    alter: numpy.ndarray,
    p_id_einstandspartner: numpy.ndarray,
    p_id_elternteil_1: numpy.ndarray,
    p_id_elternteil_2: numpy.ndarray,
    eigener_bedarf_gedeckt: numpy.ndarray[bool],
):
    """
    Compute the ID of the Bedarfsgemeinschaft for each person.
    """
    # Build indexes
    p_id_to_index = {}
    p_id_to_p_ids_children = {}

    for index, current_p_id in enumerate(p_id):
        # Fast access from p_id to index
        p_id_to_index[current_p_id] = index

        # Fast access from p_id to p_ids of children
        current_p_id_elternteil_1 = p_id_elternteil_1[index]
        current_p_id_elternteil_2 = p_id_elternteil_2[index]

        if current_p_id_elternteil_1 != -1:
            if current_p_id_elternteil_1 not in p_id_to_p_ids_children:
                p_id_to_p_ids_children[current_p_id_elternteil_1] = []
            p_id_to_p_ids_children[current_p_id_elternteil_1].append(current_p_id)

        if current_p_id_elternteil_2 != -1:
            if current_p_id_elternteil_2 not in p_id_to_p_ids_children:
                p_id_to_p_ids_children[current_p_id_elternteil_2] = []
            p_id_to_p_ids_children[current_p_id_elternteil_2].append(current_p_id)

    p_id_to_bg_id = {}
    next_bg_id = 0

    for index, current_p_id in enumerate(p_id):
        # Already assigned a bg
        if current_p_id in p_id_to_bg_id:
            continue

        p_id_to_bg_id[current_p_id] = next_bg_id

        current_hh_id = hh_id[index]
        current_p_id_ehepartner = p_id_einstandspartner[index]
        current_p_id_children = p_id_to_p_ids_children.get(current_p_id, [])

        # Assign bg to ehepartner
        if current_p_id_ehepartner != -1:
            p_id_to_bg_id[current_p_id_ehepartner] = next_bg_id

        # Assign bg to children
        for current_p_id_child in current_p_id_children:
            child_index = p_id_to_index[current_p_id_child]
            child_hh_id = hh_id[child_index]
            child_enough_income = eigener_bedarf_gedeckt[child_index]
            child_alter = alter[child_index]
            child_p_id_children = p_id_to_p_ids_children.get(current_p_id_child, [])

            if (
                child_hh_id == current_hh_id
                and not child_enough_income
                and child_alter < 25
                and len(child_p_id_children) == 0
            ):
                p_id_to_bg_id[current_p_id_child] = next_bg_id

        next_bg_id += 1

    # Compute result vector
    result = [p_id_to_bg_id[current_p_id] for current_p_id in p_id]
    return numpy.asarray(result)


def st_id_numpy(
    p_id: numpy.ndarray,
    p_id_ehepartner: numpy.ndarray,
    gemeinsam_veranlagt: numpy.ndarray[bool],
):
    """
    Compute a Steuernummer (ID) for each person / couple.
    """
    p_id_to_st_id = {}
    p_id_to_gemeinsam_veranlagt = {}
    next_st_id = 0
    result = []

    for index, current_p_id in enumerate(p_id):
        current_p_id_ehepartner = p_id_ehepartner[index]
        current_gemeinsam_veranlagt = gemeinsam_veranlagt[index]

        if current_p_id_ehepartner != -1 and current_p_id_ehepartner in p_id_to_st_id:
            gemeinsam_veranlagt_ehepartner = p_id_to_gemeinsam_veranlagt[
                current_p_id_ehepartner
            ]

            if current_gemeinsam_veranlagt != gemeinsam_veranlagt_ehepartner:
                message = (
                    f"{current_p_id_ehepartner} and {current_p_id} are "
                    "married, but have different values for "
                    "gemeinsam_veranlagt."
                )
                raise ValueError(message)

            if current_gemeinsam_veranlagt:
                result.append(p_id_to_st_id[current_p_id_ehepartner])
                continue

        # New Steuersubjekt
        result.append(next_st_id)
        p_id_to_st_id[current_p_id] = next_st_id
        p_id_to_gemeinsam_veranlagt[current_p_id] = current_gemeinsam_veranlagt
        next_st_id += 1

    return numpy.asarray(result)
