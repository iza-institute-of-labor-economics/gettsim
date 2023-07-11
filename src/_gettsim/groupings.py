from typing import Callable

import numpy


def create_groupings() -> dict[str, Callable]:
    return {
        "bg_id": bg_id_numpy,
        "st_id": st_id_numpy
    }

def bg_id_numpy(
    p_id: numpy.ndarray,
    hh_id: numpy.ndarray,
    alter: numpy.ndarray,
    p_id_ehepartner: numpy.ndarray,
    p_id_elternteil_1: numpy.ndarray,
    p_id_elternteil_2: numpy.ndarray,
    enough_income: numpy.ndarray[bool],
):
    # Fast access from p_id to index
    p_id_to_index = {}
    for index, current_p_id in enumerate(p_id):
        p_id_to_index[current_p_id] = index

    # Fast access from p_id to p_ids of children
    p_id_to_p_ids_children = {}
    for index, current_p_id in enumerate(p_id):
        current_p_id_elternteil_1 = p_id_elternteil_1[index]
        current_p_id_elternteil_2 = p_id_elternteil_2[index]

        if current_p_id_elternteil_1 not in p_id_to_p_ids_children:
            p_id_to_p_ids_children[current_p_id_elternteil_1] = []
        p_id_to_p_ids_children[current_p_id_elternteil_1].append(current_p_id)

        if current_p_id_elternteil_2 not in p_id_to_p_ids_children:
            p_id_to_p_ids_children[current_p_id_elternteil_2] = []
        p_id_to_p_ids_children[current_p_id_elternteil_2].append(current_p_id)

    p_id_to_bg_id = {}
    next_bg_id = 0

    for index, current_p_id in enumerate(p_id):
        current_p_id_ehepartner = p_id_ehepartner[index]
        current_p_id_children = p_id_to_p_ids_children.get(current_p_id, [])
        current_alters = alter[index]
        current_enough_income = enough_income[index]

        # TODO
        p_id_to_bg_id[current_p_id] = next_bg_id


    # Compute result vector
    result = []
    for current_p_id in p_id:
        result.append(p_id_to_bg_id[current_p_id])
    return numpy.asarray(result)

def st_id_numpy(
    p_id: numpy.ndarray,
    p_id_ehepartner: numpy.ndarray,
    gemeinsam_veranlagt: numpy.ndarray[bool],
):
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
