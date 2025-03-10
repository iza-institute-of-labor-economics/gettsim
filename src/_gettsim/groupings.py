from collections import Counter
from collections.abc import Callable

import numpy

from _gettsim.functions.policy_function import policy_function


def create_groupings() -> dict[str, Callable]:
    return {
        "wohngeld": {
            "wthh_id": wthh_id_numpy,
        },
        "arbeitslosengeld_2": {
            "bg_id": bg_id_numpy,
            "eg_id": eg_id_numpy,
        },
        "demographics": {
            "fg_id": fg_id_numpy,
            "ehe_id": ehe_id_numpy,
        },
        "einkommensteuer": {
            "sn_id": sn_id_numpy,
        },
    }


@policy_function(skip_vectorization=True, leaf_name="bg_id")
def bg_id_numpy(
    fg_id: numpy.ndarray[int],
    demographics__alter: numpy.ndarray[int],
    arbeitslosengeld_2__eigenbedarf_gedeckt: numpy.ndarray[bool],
) -> numpy.ndarray[int]:
    """
    Compute the ID of the Bedarfsgemeinschaft for each person.
    """
    # TODO(@MImmesberger): Remove input variable arbeitslosengeld_2__eigenbedarf_gedeckt
    # once Bedarfsgemeinschaften are fully endogenous
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/763
    counter = Counter()
    result = []

    for index, current_fg_id in enumerate(fg_id):
        current_alter = demographics__alter[index]
        current_eigenbedarf_gedeckt = arbeitslosengeld_2__eigenbedarf_gedeckt[index]
        # TODO(@MImmesberger): Remove hard-coded number
        # https://github.com/iza-institute-of-labor-economics/gettsim/issues/668
        if current_alter < 25 and current_eigenbedarf_gedeckt:
            counter[current_fg_id] += 1
            result.append(current_fg_id * 100 + counter[current_fg_id])
        else:
            result.append(current_fg_id * 100)

    return numpy.asarray(result)


@policy_function(skip_vectorization=True, leaf_name="eg_id")
def eg_id_numpy(
    demographics__p_id: numpy.ndarray[int],
    demograpics__p_id_einstandspartner: numpy.ndarray[int],
) -> numpy.ndarray[int]:
    """
    Compute the ID of the Einstandsgemeinschaft for each person.
    """
    p_id_to_eg_id = {}
    next_eg_id = 0
    result = []

    for index, current_p_id in enumerate(demographics__p_id):
        current_demograpics__p_id_einstandspartner = demograpics__p_id_einstandspartner[
            index
        ]

        if (
            current_demograpics__p_id_einstandspartner >= 0
            and current_demograpics__p_id_einstandspartner in p_id_to_eg_id
        ):
            result.append(p_id_to_eg_id[current_demograpics__p_id_einstandspartner])
            continue

        # New Einstandsgemeinschaft
        result.append(next_eg_id)
        p_id_to_eg_id[current_p_id] = next_eg_id
        next_eg_id += 1

    return numpy.asarray(result)


@policy_function(skip_vectorization=True, leaf_name="ehe_id")
def ehe_id_numpy(
    demographics__p_id: numpy.ndarray[int],
    demograpics__p_id_ehepartner: numpy.ndarray[int],
) -> numpy.ndarray[int]:
    """
    Compute the ID of the Ehe for each person.
    """
    p_id_to_ehe_id = {}
    next_ehe_id = 0
    result = []

    for index, current_p_id in enumerate(demographics__p_id):
        current_demograpics__p_id_ehepartner = demograpics__p_id_ehepartner[index]

        if (
            current_demograpics__p_id_ehepartner >= 0
            and current_demograpics__p_id_ehepartner in p_id_to_ehe_id
        ):
            result.append(p_id_to_ehe_id[current_demograpics__p_id_ehepartner])
            continue

        # New Steuersubjekt
        result.append(next_ehe_id)
        p_id_to_ehe_id[current_p_id] = next_ehe_id
        next_ehe_id += 1

    return numpy.asarray(result)


@policy_function(skip_vectorization=True, leaf_name="fg_id")
def fg_id_numpy(  # noqa: PLR0913
    demographics__p_id: numpy.ndarray[int],
    demographics__hh_id: numpy.ndarray[int],
    demographics__alter: numpy.ndarray[int],
    demograpics__p_id_einstandspartner: numpy.ndarray[int],
    demographics__p_id_elternteil_1: numpy.ndarray[int],
    demographics__p_id_elternteil_2: numpy.ndarray[int],
) -> numpy.ndarray[int]:
    """
    Compute the ID of the Familiengemeinschaft for each person.
    """
    # Build indexes
    p_id_to_index = {}
    p_id_to_p_ids_children = {}

    for index, current_p_id in enumerate(demographics__p_id):
        # Fast access from demographics__p_id to index
        p_id_to_index[current_p_id] = index

        # Fast access from demographics__p_id to p_ids of children
        current_demographics__p_id_elternteil_1 = demographics__p_id_elternteil_1[index]
        current_demographics__p_id_elternteil_2 = demographics__p_id_elternteil_2[index]

        if current_demographics__p_id_elternteil_1 >= 0:
            if current_demographics__p_id_elternteil_1 not in p_id_to_p_ids_children:
                p_id_to_p_ids_children[current_demographics__p_id_elternteil_1] = []
            p_id_to_p_ids_children[current_demographics__p_id_elternteil_1].append(
                current_p_id
            )

        if current_demographics__p_id_elternteil_2 >= 0:
            if current_demographics__p_id_elternteil_2 not in p_id_to_p_ids_children:
                p_id_to_p_ids_children[current_demographics__p_id_elternteil_2] = []
            p_id_to_p_ids_children[current_demographics__p_id_elternteil_2].append(
                current_p_id
            )

    p_id_to_fg_id = {}
    next_fg_id = 0

    for index, current_p_id in enumerate(demographics__p_id):
        # Already assigned a fg_id to this demographics__p_id via einstandspartner /
        # parent
        if current_p_id in p_id_to_fg_id:
            continue

        p_id_to_fg_id[current_p_id] = next_fg_id

        current_hh_id = demographics__hh_id[index]
        current_demograpics__p_id_einstandspartner = demograpics__p_id_einstandspartner[
            index
        ]
        current_p_id_children = p_id_to_p_ids_children.get(current_p_id, [])

        # Assign fg to einstandspartner
        if current_demograpics__p_id_einstandspartner >= 0:
            p_id_to_fg_id[current_demograpics__p_id_einstandspartner] = next_fg_id

        # Assign fg to children
        for current_p_id_child in current_p_id_children:
            child_index = p_id_to_index[current_p_id_child]
            child_hh_id = demographics__hh_id[child_index]
            child_alter = demographics__alter[child_index]
            child_p_id_children = p_id_to_p_ids_children.get(current_p_id_child, [])

            if (
                child_hh_id == current_hh_id
                # TODO (@MImmesberger): Check correct conditions for grown up children
                # https://github.com/iza-institute-of-labor-economics/gettsim/pull/509
                # TODO(@MImmesberger): Remove hard-coded number
                # https://github.com/iza-institute-of-labor-economics/gettsim/issues/668
                and child_alter < 25
                and len(child_p_id_children) == 0
            ):
                p_id_to_fg_id[current_p_id_child] = next_fg_id

        next_fg_id += 1

    # Compute result vector
    result = [p_id_to_fg_id[current_p_id] for current_p_id in demographics__p_id]
    return numpy.asarray(result)


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


@policy_function(skip_vectorization=True, leaf_name="wthh_id")
def wthh_id_numpy(
    demographics__hh_id: numpy.ndarray[int],
    vorrangpruefungen__wohngeld_vorrang_bg: numpy.ndarray[bool],
    vorrangpruefungen__wohngeld_kinderzuschlag_vorrang_bg: numpy.ndarray[bool],
) -> numpy.ndarray[int]:
    """
    Compute the ID of the wohngeldrechtlicher Teilhaushalt.
    """
    result = []
    for index, current_hh_id in enumerate(demographics__hh_id):
        if (
            vorrangpruefungen__wohngeld_vorrang_bg[index]
            or vorrangpruefungen__wohngeld_kinderzuschlag_vorrang_bg[index]
        ):
            result.append(current_hh_id * 100 + 1)
        else:
            result.append(current_hh_id * 100)

    return numpy.asarray(result)
