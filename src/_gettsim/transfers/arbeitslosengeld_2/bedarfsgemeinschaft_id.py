from collections import Counter

import numpy

from _gettsim.functions.grouping_function import grouping_function


@grouping_function()
def bg_id(
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
