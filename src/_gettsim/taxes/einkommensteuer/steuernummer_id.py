"""Steuernummer ID."""

import numpy

from _gettsim.functions.policy_function import policy_function


@policy_function(skip_vectorization=True, leaf_name="sn_id")
def sn_id_numpy(
    demographics__p_id: numpy.ndarray[int],
    demograpics__p_id_ehepartner: numpy.ndarray[int],
    einkommensteuer__gemeinsam_veranlagt: numpy.ndarray[bool],
) -> numpy.ndarray[int]:
    """
    Compute a Steuernummer (ID) for each person / couple.
    """
    p_id_to_sn_id = {}
    p_id_to_einkommensteuer__gemeinsam_veranlagt = {}
    next_sn_id = 0
    result = []

    for index, current_p_id in enumerate(demographics__p_id):
        current_p_id_ehepartner = demograpics__p_id_ehepartner[index]
        current_gemeinsam_veranlagt = einkommensteuer__gemeinsam_veranlagt[index]

        if current_p_id_ehepartner >= 0 and current_p_id_ehepartner in p_id_to_sn_id:
            einkommensteuer__gemeinsam_veranlagt_ehepartner = (
                p_id_to_einkommensteuer__gemeinsam_veranlagt[current_p_id_ehepartner]
            )

            if (
                current_gemeinsam_veranlagt
                != einkommensteuer__gemeinsam_veranlagt_ehepartner
            ):
                message = (
                    f"{current_p_id_ehepartner} and {current_p_id} are "
                    "married, but have different values for "
                    "einkommensteuer__gemeinsam_veranlagt."
                )
                raise ValueError(message)

            if current_gemeinsam_veranlagt:
                result.append(p_id_to_sn_id[current_p_id_ehepartner])
                continue

        # New Steuersubjekt
        result.append(next_sn_id)
        p_id_to_sn_id[current_p_id] = next_sn_id
        p_id_to_einkommensteuer__gemeinsam_veranlagt[current_p_id] = (
            current_gemeinsam_veranlagt
        )
        next_sn_id += 1

    return numpy.asarray(result)
