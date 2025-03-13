"""Tax allowances for the elderly."""

from _gettsim.config import numpy_or_jax as np
from _gettsim.function_types import policy_function


@policy_function(end_date="2004-12-31", leaf_name="altersfreibetrag_y")
def altersfreibetrag_y_bis_2004(  # noqa: PLR0913
    einkommen__bruttolohn_m: float,
    demographics__alter: int,
    einkommen__bruttokapitaleinkommen_m: float,
    einkommen__aus_selbstständigkeit_m: float,
    einkommen__aus_vermietung_m: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate tax deduction allowance for elderly until 2004.

    Parameters
    ----------
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.
    demographics__alter
        See basic input variable :ref:`demographics__alter <demographics__alter>`.
    einkommen__bruttokapitaleinkommen_m
        See basic input variable :ref:`einkommen__bruttokapitaleinkommen_m <einkommen__bruttokapitaleinkommen_m>`.
    einkommen__aus_selbstständigkeit_m
        See :func:`einkommen__aus_selbstständigkeit_m`.
    einkommen__aus_vermietung_m
        See basic input variable :ref:`einkommen__aus_vermietung_m <einkommen__aus_vermietung_m>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    altersgrenze = eink_st_abzuege_params["altersentlastungsbetrag_altersgrenze"]
    weiteres_einkommen = max(
        einkommen__bruttokapitaleinkommen_m
        + einkommen__aus_selbstständigkeit_m
        + einkommen__aus_vermietung_m,
        0.0,
    )
    if demographics__alter > altersgrenze:
        out = min(
            eink_st_abzuege_params["altersentlastung_quote"]
            * 12
            * (einkommen__bruttolohn_m + weiteres_einkommen),
            eink_st_abzuege_params["altersentlastungsbetrag_max"],
        )
    else:
        out = 0.0

    return out


@policy_function(start_date="2005-01-01", leaf_name="altersfreibetrag_y")
def altersfreibetrag_y_ab_2005(  # noqa: PLR0913
    einkommen__bruttolohn_m: float,
    sozialversicherung__geringfügig_beschäftigt: bool,
    demographics__alter: int,
    demographics__geburtsjahr: int,
    einkommen__bruttokapitaleinkommen_m: float,
    einkommen__aus_selbstständigkeit_m: float,
    einkommen__aus_vermietung_m: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate tax deduction allowance for elderly since 2005.

    Parameters
    ----------
    einkommen__bruttolohn_m
        See basic input variable :ref:`einkommen__bruttolohn_m <einkommen__bruttolohn_m>`.
    demographics__alter
        See basic input variable :ref:`demographics__alter <demographics__alter>`.
    demographics__geburtsjahr
        See basic input variable :ref:`demographics__geburtsjahr <demographics__geburtsjahr>`.
    einkommen__bruttokapitaleinkommen_m
        See basic input variable :ref:`einkommen__bruttokapitaleinkommen_m <einkommen__bruttokapitaleinkommen_m>`.
    einkommen__aus_selbstständigkeit_m
        See :func:`einkommen__aus_selbstständigkeit_m`.
    einkommen__aus_vermietung_m
        See basic input variable :ref:`einkommen__aus_vermietung_m <einkommen__aus_vermietung_m>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    sozialversicherung__geringfügig_beschäftigt
        See :func:`sozialversicherung__geringfügig_beschäftigt`.

    Returns
    -------

    """
    # Maximum tax credit by birth year.
    bins = sorted(eink_st_abzuege_params["altersentlastungsbetrag_max"])
    if demographics__geburtsjahr <= 1939:
        selected_bin = 1940
    else:
        # Select corresponding bin.
        selected_bin = bins[
            np.searchsorted(
                np.asarray([*bins, np.inf]), demographics__geburtsjahr, side="right"
            )
            - 1
        ]

    # Select appropriate tax credit threshold and quota.
    out_max = eink_st_abzuege_params["altersentlastungsbetrag_max"][selected_bin]

    einkommen_lohn = (
        0 if sozialversicherung__geringfügig_beschäftigt else einkommen__bruttolohn_m
    )
    weiteres_einkommen = max(
        einkommen__bruttokapitaleinkommen_m
        + einkommen__aus_selbstständigkeit_m
        + einkommen__aus_vermietung_m,
        0.0,
    )
    out_quote = (
        eink_st_abzuege_params["altersentlastung_quote"][selected_bin]
        * 12
        * (einkommen_lohn + weiteres_einkommen)
    )

    if (
        demographics__alter
        > eink_st_abzuege_params["altersentlastungsbetrag_altersgrenze"]
    ):
        out = min(out_quote, out_max)
    else:
        out = 0.0

    return out
