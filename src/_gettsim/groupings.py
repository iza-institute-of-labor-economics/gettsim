from collections import Counter
from collections.abc import Callable

import numpy


def create_groupings() -> dict[str, Callable]:
    return {"bg_id": bg_id_numpy, "fg_id": fg_id_numpy, "sn_id": sn_id_numpy}


def bg_id_numpy(
    fg_id: numpy.ndarray[int],
    alter: numpy.ndarray[int],
    eigener_bedarf_gedeckt: numpy.ndarray[bool],
):
    """
    Compute the ID of the Bedarfsgemeinschaft for each person.
    """
    counter = Counter()
    result = []

    for index, current_fg_id in enumerate(fg_id):
        current_alter = alter[index]
        current_eigener_bedarf_gedeckt = eigener_bedarf_gedeckt[index]
        if current_alter < 25 and current_eigener_bedarf_gedeckt:
            counter[current_fg_id] += 1
            result.append(current_fg_id * 100 + counter[current_fg_id])
        else:
            result.append(current_fg_id * 100)

    return numpy.asarray(result)


def fg_id_numpy(  # noqa: PLR0913
    p_id: numpy.ndarray,
    hh_id: numpy.ndarray,
    alter: numpy.ndarray,
    p_id_einstandspartner: numpy.ndarray,
    p_id_elternteil_1: numpy.ndarray,
    p_id_elternteil_2: numpy.ndarray,
):
    """
    Compute the ID of the Familiengemeinschaft for each person.
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

        if current_p_id_elternteil_1 >= 0:
            if current_p_id_elternteil_1 not in p_id_to_p_ids_children:
                p_id_to_p_ids_children[current_p_id_elternteil_1] = []
            p_id_to_p_ids_children[current_p_id_elternteil_1].append(current_p_id)

        if current_p_id_elternteil_2 >= 0:
            if current_p_id_elternteil_2 not in p_id_to_p_ids_children:
                p_id_to_p_ids_children[current_p_id_elternteil_2] = []
            p_id_to_p_ids_children[current_p_id_elternteil_2].append(current_p_id)

    p_id_to_fg_id = {}
    next_fg_id = 0

    for index, current_p_id in enumerate(p_id):
        # Already assigned a fg
        if current_p_id in p_id_to_fg_id:
            continue

        p_id_to_fg_id[current_p_id] = next_fg_id

        current_vg_id = hh_id[index]
        current_p_id_einstandspartner = p_id_einstandspartner[index]
        current_p_id_children = p_id_to_p_ids_children.get(current_p_id, [])

        # Assign fg to einstandspartner
        if current_p_id_einstandspartner >= 0:
            p_id_to_fg_id[current_p_id_einstandspartner] = next_fg_id

        # Assign fg to children
        for current_p_id_child in current_p_id_children:
            child_index = p_id_to_index[current_p_id_child]
            child_vg_id = hh_id[child_index]
            child_alter = alter[child_index]
            child_p_id_children = p_id_to_p_ids_children.get(current_p_id_child, [])

            if (
                child_vg_id == current_vg_id
                # TODO (@hmgaudecker): Add correct conditions for grown up children
                # https://github.com/iza-institute-of-labor-economics/gettsim/pulls/509
                and child_alter < 25
                and len(child_p_id_children) == 0
            ):
                p_id_to_fg_id[current_p_id_child] = next_fg_id

        next_fg_id += 1

    # Compute result vector
    result = [p_id_to_fg_id[current_p_id] for current_p_id in p_id]
    return numpy.asarray(result)


def sn_id_numpy(
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
        current_p_id_einstandspartner = p_id_ehepartner[index]
        current_gemeinsam_veranlagt = gemeinsam_veranlagt[index]

        if (
            current_p_id_einstandspartner >= 0
            and current_p_id_einstandspartner in p_id_to_st_id
        ):
            gemeinsam_veranlagt_ehepartner = p_id_to_gemeinsam_veranlagt[
                current_p_id_einstandspartner
            ]

            if current_gemeinsam_veranlagt != gemeinsam_veranlagt_ehepartner:
                message = (
                    f"{current_p_id_einstandspartner} and {current_p_id} are "
                    "married, but have different values for "
                    "gemeinsam_veranlagt."
                )
                raise ValueError(message)

            if current_gemeinsam_veranlagt:
                result.append(p_id_to_st_id[current_p_id_einstandspartner])
                continue

        # New Steuersubjekt
        result.append(next_st_id)
        p_id_to_st_id[current_p_id] = next_st_id
        p_id_to_gemeinsam_veranlagt[current_p_id] = current_gemeinsam_veranlagt
        next_st_id += 1

    return numpy.asarray(result)
