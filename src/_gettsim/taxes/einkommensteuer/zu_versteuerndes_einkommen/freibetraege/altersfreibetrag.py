"""Tax allowances for the elderly."""

from _gettsim.config import numpy_or_jax as np
from _gettsim.shared import policy_info


@policy_info(end_date="2004-12-31", name_in_dag="eink_st_altersfreib_y")
def eink_st_altersfreib_y_bis_2004(  # noqa: PLR0913
    bruttolohn_m: float,
    alter: int,
    kapitaleink_brutto_m: float,
    eink_selbst_m: float,
    eink_vermietung_m: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate tax deduction allowance for elderly until 2004.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    kapitaleink_brutto_m
        See basic input variable :ref:`kapitaleink_brutto_m <kapitaleink_brutto_m>`.
    eink_selbst_m
        See :func:`eink_selbst_m`.
    eink_vermietung_m
        See basic input variable :ref:`eink_vermietung_m <eink_vermietung_m>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------

    """
    altersgrenze = eink_st_abzuege_params["altersentlastungsbetrag_altersgrenze"]
    weiteres_einkommen = max(
        kapitaleink_brutto_m + eink_selbst_m + eink_vermietung_m, 0.0
    )
    if alter > altersgrenze:
        out = min(
            eink_st_abzuege_params["altersentlastung_quote"]
            * 12
            * (bruttolohn_m + weiteres_einkommen),
            eink_st_abzuege_params["altersentlastungsbetrag_max"],
        )
    else:
        out = 0.0

    return out


@policy_info(start_date="2005-01-01", name_in_dag="eink_st_altersfreib_y")
def eink_st_altersfreib_y_ab_2005(  # noqa: PLR0913
    bruttolohn_m: float,
    geringfügig_beschäftigt: bool,
    alter: int,
    geburtsjahr: int,
    kapitaleink_brutto_m: float,
    eink_selbst_m: float,
    eink_vermietung_m: float,
    eink_st_abzuege_params: dict,
) -> float:
    """Calculate tax deduction allowance for elderly since 2005.

    Parameters
    ----------
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    alter
        See basic input variable :ref:`alter <alter>`.
    geburtsjahr
        See basic input variable :ref:`geburtsjahr <geburtsjahr>`.
    kapitaleink_brutto_m
        See basic input variable :ref:`kapitaleink_brutto_m <kapitaleink_brutto_m>`.
    eink_selbst_m
        See :func:`eink_selbst_m`.
    eink_vermietung_m
        See basic input variable :ref:`eink_vermietung_m <eink_vermietung_m>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.
    geringfügig_beschäftigt
        See :func:`geringfügig_beschäftigt`.

    Returns
    -------

    """
    # Maximum tax credit by birth year.
    bins = sorted(eink_st_abzuege_params["altersentlastungsbetrag_max"])
    if geburtsjahr <= 1939:
        selected_bin = 1940
    else:
        # Select corresponding bin.
        selected_bin = bins[
            np.searchsorted(np.asarray([*bins, np.inf]), geburtsjahr, side="right") - 1
        ]

    # Select appropriate tax credit threshold and quota.
    out_max = eink_st_abzuege_params["altersentlastungsbetrag_max"][selected_bin]

    einkommen_lohn = 0 if geringfügig_beschäftigt else bruttolohn_m
    weiteres_einkommen = max(
        kapitaleink_brutto_m + eink_selbst_m + eink_vermietung_m, 0.0
    )
    out_quote = (
        eink_st_abzuege_params["altersentlastung_quote"][selected_bin]
        * 12
        * (einkommen_lohn + weiteres_einkommen)
    )

    if alter > eink_st_abzuege_params["altersentlastungsbetrag_altersgrenze"]:
        out = min(out_quote, out_max)
    else:
        out = 0.0

    return out
