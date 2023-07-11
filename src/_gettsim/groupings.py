from typing import Callable

import numpy


def create_groupings() -> dict[str, Callable]:
    return {"st_id": st_id_numpy}


def st_id_numpy(p_id: numpy.ndarray, p_id_ehepartner: numpy.ndarray):
    person_id_to_steuersubject_id = {}
    next_steuersubject_id = 0
    result = []

    for person_id, index in enumerate(p_id):
        person_id_ehepartner = p_id_ehepartner[index]

        if (
            person_id_ehepartner != -1
            and person_id_ehepartner in person_id_to_steuersubject_id
        ):
            result.append(person_id_to_steuersubject_id[person_id_ehepartner])
        else:
            result.append(next_steuersubject_id)
            person_id_to_steuersubject_id[person_id] = next_steuersubject_id
            next_steuersubject_id += 1

    result = numpy.asarray(result)
    return result
