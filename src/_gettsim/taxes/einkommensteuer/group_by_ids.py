"""Steuernummer ID."""

import numpy

from _gettsim.function_types import group_by_function


@group_by_function()
def sn_id(
    demographics__p_id: numpy.ndarray[int],
    demographics__p_id_ehepartner: numpy.ndarray[int],
    gemeinsam_veranlagt: numpy.ndarray[bool],
) -> numpy.ndarray[int]:
    """
    Compute a Steuernummer (ID) for each person / couple.
    """
    p_id_to_sn_id = {}
    p_id_to_gemeinsam_veranlagt = {}
    next_sn_id = 0
    result = []

    for index, current_p_id in enumerate(demographics__p_id):
        current_p_id_ehepartner = demographics__p_id_ehepartner[index]
        current_gemeinsam_veranlagt = gemeinsam_veranlagt[index]

        if current_p_id_ehepartner >= 0 and current_p_id_ehepartner in p_id_to_sn_id:
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
                result.append(p_id_to_sn_id[current_p_id_ehepartner])
                continue

        # New Steuersubjekt
        result.append(next_sn_id)
        p_id_to_sn_id[current_p_id] = next_sn_id
        p_id_to_gemeinsam_veranlagt[current_p_id] = current_gemeinsam_veranlagt
        next_sn_id += 1

    return numpy.asarray(result)
