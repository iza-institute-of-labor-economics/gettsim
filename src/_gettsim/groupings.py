from collections import Counter
from collections.abc import Callable

import numpy


def create_groupings() -> dict[str, Callable]:
    return {
        "wthh_id": wthh_id_numpy,
        "wthh_id_endogen": wthh_id_endogen_numpy,
        "fg_id": fg_id_numpy,
        "bg_id": bg_id_numpy,
        "bg_id_endogen": bg_id_endogen_numpy,
        "eg_id": eg_id_numpy,
        "ehe_id": ehe_id_numpy,
        "sn_id": sn_id_numpy,
    }


def bg_id_numpy(
    hh_id: numpy.ndarray[int],
    fg_id: numpy.ndarray[int],
    arbeitsl_geld_2_kind_und_eigenbedarf_gedeckt: numpy.ndarray[bool],
) -> numpy.ndarray[int]:
    """
    ID of Bedarfsgemeinschaften.

    If not overwritten by user-provided bg_ids, all children who cover their needs are
    separated from the parental Bedarfsgemeinschaft.
    """
    _fail_if_more_than_one_fg_in_hh(hh_id, fg_id)

    counter = Counter()
    result = []

    for index, current_fg_id in enumerate(fg_id):
        if arbeitsl_geld_2_kind_und_eigenbedarf_gedeckt[index]:
            counter[current_fg_id] += 1
            result.append(current_fg_id * 100 + counter[current_fg_id])
        else:
            result.append(current_fg_id * 100)

    return numpy.asarray(result)


def bg_id_endogen_numpy(
    fg_id: numpy.ndarray[int],
    alle_beantragt_wohngeld_kinderzuschl_statt_arbeitsl_geld_2_fg: numpy.ndarray[bool],
    ist_kind_in_fg: numpy.ndarray[bool],
    beantragt_wohngeld_kinderzuschl_statt_arbeitsl_geld_2_endogen: numpy.ndarray[bool],
) -> numpy.ndarray[int]:
    """
    Compute the ID of the Bedarfsgemeinschaft endogenously for each person.
    """
    counter = Counter()
    result = []

    for index, current_fg_id in enumerate(fg_id):
        current_wog_kiz_statt_alg_2 = (
            beantragt_wohngeld_kinderzuschl_statt_arbeitsl_geld_2_endogen[index]
        )
        if alle_beantragt_wohngeld_kinderzuschl_statt_arbeitsl_geld_2_fg[index]:
            result.append(current_fg_id * 100)
        elif ist_kind_in_fg[index] and current_wog_kiz_statt_alg_2:
            counter[current_fg_id] += 1
            result.append(current_fg_id * 100 + counter[current_fg_id])
        else:
            result.append(current_fg_id * 100)

    return numpy.asarray(result)


def eg_id_numpy(
    p_id: numpy.ndarray[int],
    p_id_einstandspartner: numpy.ndarray[int],
) -> numpy.ndarray[int]:
    """
    Compute the ID of the Einstandsgemeinschaft for each person.
    """
    p_id_to_eg_id = {}
    next_eg_id = 0
    result = []

    for index, current_p_id in enumerate(p_id):
        current_p_id_einstandspartner = p_id_einstandspartner[index]

        if (
            current_p_id_einstandspartner >= 0
            and current_p_id_einstandspartner in p_id_to_eg_id
        ):
            result.append(p_id_to_eg_id[current_p_id_einstandspartner])
            continue

        # New Einstandsgemeinschaft
        result.append(next_eg_id)
        p_id_to_eg_id[current_p_id] = next_eg_id
        next_eg_id += 1

    return numpy.asarray(result)


def ehe_id_numpy(
    p_id: numpy.ndarray[int],
    p_id_ehepartner: numpy.ndarray[int],
) -> numpy.ndarray[int]:
    """
    Compute the ID of the Ehe for each person.
    """
    p_id_to_ehe_id = {}
    next_ehe_id = 0
    result = []

    for index, current_p_id in enumerate(p_id):
        current_p_id_ehepartner = p_id_ehepartner[index]

        if current_p_id_ehepartner >= 0 and current_p_id_ehepartner in p_id_to_ehe_id:
            result.append(p_id_to_ehe_id[current_p_id_ehepartner])
            continue

        # New Steuersubjekt
        result.append(next_ehe_id)
        p_id_to_ehe_id[current_p_id] = next_ehe_id
        next_ehe_id += 1

    return numpy.asarray(result)


def fg_id_numpy(  # noqa: PLR0913
    p_id: numpy.ndarray[int],
    hh_id: numpy.ndarray[int],
    alter: numpy.ndarray[int],
    p_id_einstandspartner: numpy.ndarray[int],
    p_id_elternteil_1: numpy.ndarray[int],
    p_id_elternteil_2: numpy.ndarray[int],
) -> numpy.ndarray[int]:
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
        # Already assigned a fg_id to this p_id via einstandspartner / parent
        if current_p_id in p_id_to_fg_id:
            continue

        p_id_to_fg_id[current_p_id] = next_fg_id

        current_hh_id = hh_id[index]
        current_p_id_einstandspartner = p_id_einstandspartner[index]
        current_p_id_children = p_id_to_p_ids_children.get(current_p_id, [])

        # Assign fg to einstandspartner
        if current_p_id_einstandspartner >= 0:
            p_id_to_fg_id[current_p_id_einstandspartner] = next_fg_id

        # Assign fg to children
        for current_p_id_child in current_p_id_children:
            child_index = p_id_to_index[current_p_id_child]
            child_hh_id = hh_id[child_index]
            child_alter = alter[child_index]
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
    result = [p_id_to_fg_id[current_p_id] for current_p_id in p_id]
    return numpy.asarray(result)


def sn_id_numpy(
    p_id: numpy.ndarray[int],
    p_id_ehepartner: numpy.ndarray[int],
    gemeinsam_veranlagt: numpy.ndarray[bool],
) -> numpy.ndarray[int]:
    """
    Compute a Steuernummer (ID) for each person / couple.
    """
    p_id_to_sn_id = {}
    p_id_to_gemeinsam_veranlagt = {}
    next_sn_id = 0
    result = []

    for index, current_p_id in enumerate(p_id):
        current_p_id_ehepartner = p_id_ehepartner[index]
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


def wthh_id_numpy(
    hh_id: numpy.ndarray[int],
    fg_id: numpy.ndarray[int],
    arbeitsl_geld_2_kind_und_eigenbedarf_gedeckt: numpy.ndarray[bool],
) -> numpy.ndarray[int]:
    """
    ID of the wohngeldrechtlicher Teilhaushalt.

    If not overwritten by user-provided wthh_ids, children who cover their needs are in
    the Wohngeld wthh and parents and children who do not cover their needs are in the
    Arbeitslosengeld II / Bürgergeld wthh.
    """
    _fail_if_more_than_one_fg_in_hh(hh_id, fg_id)

    result = []
    # Create candidate wthh_ids
    for index, current_hh_id in enumerate(hh_id):
        # Put children with covered needs in the Wohngeld wthh
        if arbeitsl_geld_2_kind_und_eigenbedarf_gedeckt[index]:
            result.append(current_hh_id * 100 + 1)
        # Parents and children who do not cover needs in ALG II wthh
        else:
            result.append(current_hh_id * 100)

    return numpy.asarray(result)


def wthh_id_endogen_numpy(
    hh_id: numpy.ndarray[int],
    beantragt_wohngeld_kinderzuschl_statt_arbeitsl_geld_2_endogen: numpy.ndarray[bool],
) -> numpy.ndarray[int]:
    """
    Compute the ID of the wohngeldrechtlicher Teilhaushalt endogenously.
    """
    result = []
    for index, current_hh_id in enumerate(hh_id):
        if beantragt_wohngeld_kinderzuschl_statt_arbeitsl_geld_2_endogen[index]:
            result.append(current_hh_id * 100 + 1)
        else:
            result.append(current_hh_id * 100)

    return numpy.asarray(result)


def _fail_if_more_than_one_fg_in_hh(
    hh_id: numpy.ndarray[int],
    fg_id: numpy.ndarray[int],
):
    """
    Fail if there is more than one `fg_id` in a household.

    GETTSIM does not support the endogenous creation of Bedarfsgemeinschaften in this
    case. The user has to provide `bg_id`, `wthh_id` and
    `beantragt_wohngeld_kinderzuschl_statt_arbeitsl_geld_2` themselves.

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
