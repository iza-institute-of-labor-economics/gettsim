"""Wohngeldrechtlicher Teilhaushalt ID."""

import numpy

from _gettsim.aggregation import AggregateByGroupSpec
from _gettsim.function_types import group_by_function

aggregation_specs = {
    "anzahl_personen_wthh": AggregateByGroupSpec(
        aggr="count",
    ),
}


@group_by_function()
def wthh_id(
    demographics__hh_id: numpy.ndarray[int],
    vorrangprüfungen__wohngeld_vorrang_vor_arbeitslosengeld_2_bg: numpy.ndarray[bool],
    vorrangprüfungen__wohngeld_und_kinderzuschlag_vorrang_vor_arbeitslosengeld_2_bg: numpy.ndarray[
        bool
    ],
) -> numpy.ndarray[int]:
    """
    Compute the ID of the wohngeldrechtlicher Teilhaushalt.
    """
    result = []
    for index, current_hh_id in enumerate(demographics__hh_id):
        if (
            vorrangprüfungen__wohngeld_vorrang_vor_arbeitslosengeld_2_bg[index]
            or vorrangprüfungen__wohngeld_und_kinderzuschlag_vorrang_vor_arbeitslosengeld_2_bg[
                index
            ]
        ):
            result.append(current_hh_id * 100 + 1)
        else:
            result.append(current_hh_id * 100)

    return numpy.asarray(result)
