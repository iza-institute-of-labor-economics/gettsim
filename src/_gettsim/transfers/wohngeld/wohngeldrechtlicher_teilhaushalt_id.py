"""Wohngeldrechtlicher Teilhaushalt ID."""

import numpy

from _gettsim.functions.grouping_function import grouping_function


@grouping_function()
def wthh_id(
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
