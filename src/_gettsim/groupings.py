from collections import Counter
from collections.abc import Callable

import numpy


def create_groupings() -> dict[str, Callable]:
    return {
        "wthh_id": wthh_id_numpy,
        "fg_id": fg_id_numpy,
        "bg_id": bg_id_numpy,
        "bg_needs_covered_id": bg_children_needs_covered_numpy,
        "bg_parents_have_own_bg_id": bg_parents_have_own_bg_numpy,
        "bg_whole_fg_id": bg_whole_fg_numpy,
        "eg_id": eg_id_numpy,
        "ehe_id": ehe_id_numpy,
        "sn_id": sn_id_numpy,
    }


def bg_id_numpy(
    fg_id: numpy.ndarray[int],
    alter: numpy.ndarray[int],
    eigenbedarf_gedeckt: numpy.ndarray[bool],
) -> numpy.ndarray[int]:
    """
    Compute the ID of the Bedarfsgemeinschaft given the result of the Günstigerprüfung.
    """


def bg_children_needs_covered_numpy(
    fg_id: numpy.ndarray[int],
    alter: numpy.ndarray[int],
) -> numpy.ndarray[int]:
    """
    Compute the ID of the Bedarfsgemeinschaft assuming that all children are not part of
    the parental BG.

    Parameters
    ----------
    fg_id
        The ID of the Familiengemeinschaft for each person.

    Returns
    -------

    """
    return _create_bg_id(
        fg_id=fg_id,
        alter=alter,
        eigenbedarf_gedeckt=numpy.full(fg_id.shape, True),
    )


def bg_parents_have_own_bg_numpy(
    fg_id: numpy.ndarray[int],
    alter: numpy.ndarray[int],
    eigenbedarf_gedeckt: numpy.ndarray[bool],
):
    """Compute the ID of the Bedarfsgemeinschaft assuming that parents and children who
    cannot cover their needs are in a different BG than children who can.

    This is the first candidate for the Günstigerprüfung (only children who cover their
    needs have a potential Wohngeld claim, parents and children who cannot cover their
    needs have a potential claim on ALG II / Bürgergeld).
    """
    return _create_bg_id(
        fg_id=fg_id,
        alter=alter,
        needs_covered=eigenbedarf_gedeckt,
    )


def bg_whole_fg_numpy(
    fg_id: numpy.ndarray[int],
) -> numpy.ndarray[int]:
    """Compute the ID of the Bedarfsgemeinschaft assuming that all parents and children
    are in the same BG, regardless of whether children can cover their needs.

    This is the second candidate for the Günstigerprüfung (the whole
    Familiengemeinschaft has a potential claim on Wohngeld).
    """
    return fg_id * 100


def _create_bg_id(
    fg_id: numpy.ndarray[int],
    alter: numpy.ndarray[int],
    needs_covered: numpy.ndarray[bool],
) -> numpy.ndarray[int]:
    """
    Compute the ID of the Bedarfsgemeinschaft for each person.
    """
    counter = Counter()
    result = []

    for index, current_fg_id in enumerate(fg_id):
        current_alter = alter[index]
        current_eigenbedarf_gedeckt = needs_covered[index]
        # TODO(@MImmesberger): Remove hard-coded number
        # https://github.com/iza-institute-of-labor-economics/gettsim/issues/668
        if current_alter < 25 and current_eigenbedarf_gedeckt:
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
    wohngeld_vorrang_bg: numpy.ndarray[bool],
    wohngeld_kinderzuschl_vorrang_bg: numpy.ndarray[bool],
) -> numpy.ndarray[int]:
    """
    Compute the ID of the wohngeldrechtlicher Teilhaushalt given the result of the
    Günstigerprüfung.
    """


def wthh_parents_have_own_bg_numpy(
    hh_id: numpy.ndarray[int],
    fg_id: numpy.ndarray[int],
    eigenbedarf_gedeckt: numpy.ndarray[bool],
    kind: numpy.ndarray[bool],
) -> numpy.ndarray[int]:
    """
    Compute the ID of the wohngeldrechtlicher Teilhaushalt assuming that parents and
    children who cannot cover their needs are in a different WTHH than children who can.

    This is the first candidate for the Günstigerprüfung.
    """

    _fail_if_more_than_one_fg_in_hh(hh_id, fg_id)

    result = []
    for index, current_hh_id in enumerate(hh_id):
        if kind[index] and eigenbedarf_gedeckt[index]:
            # Parents and children who cannot cover their needs, potential claim on
            # ALG II
            result.append(current_hh_id * 100 + 1)
        else:
            # Children who can cover their needs, potential claim on Wohngeld
            result.append(current_hh_id * 100)

    return numpy.asarray(result)


def wthh_whole_fg_numpy(
    hh_id: numpy.ndarray[int],
    fg_id: numpy.ndarray[int],
) -> numpy.ndarray[int]:
    """
    Compute the ID of the wohngeldrechtlicher Teilhaushalt assuming that the whole
    Familiengemeinschaft forms one Wohngeldhaushalt.

    This is the second candidate for the Günstigerprüfung.
    """

    _fail_if_more_than_one_fg_in_hh(hh_id, fg_id)

    result = []
    for index, current_hh_id in enumerate(hh_id):
        result.append(current_hh_id * 100)

    return numpy.asarray(result)


def _fail_if_more_than_one_fg_in_hh(
    hh_id: numpy.ndarray[int],
    fg_id: numpy.ndarray[int],
):
    """
    Fail if there is more than one `fg_id` in a household.

    GETTSIM does not support the endogenous creation of Bedarfsgemeinschaften in this
    case. The user has to provide `bg_id` and `wthh_id` themselves.

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
