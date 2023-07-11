from typing import Callable

import numpy


def create_groupings() -> dict[str, Callable]:
    return {"st_id": st_id_numpy}


def st_id_numpy(
    p_id: numpy.ndarray,
    p_id_ehepartner: numpy.ndarray,
    gemeinsam_veranlagt: numpy.ndarray[bool]
):
    p_id_to_st_id = {}
    p_id_to_gemeinsam_veranlagt = {}
    next_st_id = 0
    result = []

    for current_p_id, index in enumerate(p_id):
        current_p_id_ehepartner = p_id_ehepartner[index]
        current_gemeinsam_veranlagt = gemeinsam_veranlagt[index]

        if (
            current_p_id_ehepartner != -1
            and current_p_id_ehepartner in p_id_to_st_id
        ):
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

    result = numpy.asarray(result)
    return result
