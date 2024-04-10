"""Functions to compute parental leave benefits (Erziehungsgeld, -2007)."""

from _gettsim.shared import policy_info

aggregate_by_p_id_erziehungsgeld = {
    "erziehungsgeld_eltern_m": {
        "p_id_to_aggregate_by": "p_id_erziehgeld_empf",
        "source_col": "erziehungsgeld_kind_m",
        "aggr": "sum",
    },
}


@policy_info(start_date="2004-01-01", end="2008-12-31")
def erziehungsgeld_m(
    erziehungsgeld_eltern_m: int,
    erziehungsgeld_anspruch_eltern: bool,
) -> bool:
    """Total parental leave benefits (Erziehungsgeld).

    Parental leave benefits for the parent that claims the benefit.

    Legal reference: BErzGG (BGBl. I 1985 S. 2154; BGBl. I 2004 S. 206)

    Parameters
    ----------
    erziehungsgeld_eltern_m
        See :func:`erziehungsgeld_eltern_m`.
    erziehungsgeld_anspruch_eltern
        See :func:`erziehungsgeld_anspruch_eltern`.

    Returns
    -------
    Parental leave benefits (Erziehungsgeld).

    """
    if erziehungsgeld_anspruch_eltern:
        out = erziehungsgeld_eltern_m
    else:
        out = 0.0

    return out


@policy_info(
    end="2003-12-31", change_name="erziehungsgeld_kind_m", rounding_key="erziehungsgeld"
)
def erziehungsgeld_kind_ohne_budgetsatz_m() -> None:
    raise NotImplementedError(
        """
    Erziehungsgeld is not implemented yet prior to 2004, see
    https://github.com/iza-institute-of-labor-economics/gettsim/issues/673
        """
    )


@policy_info(
    start_date="2004-01-01",
    end="2008-12-31",
    change_name="erziehungsgeld_kind_m",
    rounding_key="erziehungsgeld",
)
def erziehungsgeld_kind_mit_budgetsatz_m(
    erziehungsgeld_anspruch_kind: bool,
    erziehungsgeld_abzug_transfer: float,
    erziehungsgeld_ohne_abzug_m: float,
) -> float:
    """Parental leave benefit (Erziehungsgeld) on child level.

    For the calculation, the relevant income, the age of the youngest child, the income
    threshold and the eligibility for erziehungsgeld is needed.

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6

    Parameters
    ----------
    erziehungsgeld_anspruch_kind
        See :func:`erziehungsgeld_anspruch_kind`.
    erziehungsgeld_abzug_transfer
        See :func:`erziehungsgeld_abzug_transfer`.
    erziehungsgeld_ohne_abzug_m
        See :func:`erziehungsgeld_ohne_abzug`.


    Returns
    -------
    Monthly claim of parental leave benefit (Erziehungsgeld) on child level
    """
    if erziehungsgeld_anspruch_kind:
        out = max(
            erziehungsgeld_ohne_abzug_m - erziehungsgeld_abzug_transfer,
            0.0,
        )
    else:
        out = 0.0

    return out


@policy_info(start_date="2004-01-01", end="2008-12-31")
def erziehungsgeld_ohne_abzug_m(
    budgetsatz_erzieh: bool,
    erziehungsgeld_eink_relev_kind_y: float,
    _erziehungsgeld_einkommensgrenze_kind_y: float,
    alter_monate: float,
    erziehungsgeld_params: dict,
) -> float:
    """Parental leave benefit (Erziehungsgeld) without means-test on child level.

    Parameters
    ----------
    budgetsatz_erzieh
        See :See basic input variable :ref:`budgetsatz_erzieh
        <budgetsatz_erzieh>`.
    erziehungsgeld_eink_relev_kind_y
        See :func:`erziehungsgeld_eink_relev_kind_y`.
    _erziehungsgeld_einkommensgrenze_kind_y
        See :func:`_erziehungsgeld_einkommensgrenze_kind_y`.
    alter_monate
        See :func:`alter_monate`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    Parental leave benefit (Erziehungsgeld) without means-test
    """
    # no benefit if income is above threshold and child is younger than threshold
    if (
        erziehungsgeld_eink_relev_kind_y > _erziehungsgeld_einkommensgrenze_kind_y
        and alter_monate
        < erziehungsgeld_params["einkommensgrenze"]["start_age_m_reduced_income_limit"]
    ):
        out = 0.0
    elif budgetsatz_erzieh:
        out = erziehungsgeld_params["erziehungsgeld_satz"]["budgetsatz"]
    else:
        out = erziehungsgeld_params["erziehungsgeld_satz"]["regelsatz"]

    return out


@policy_info(start_date="2004-01-01", end="2008-12-31")
def erziehungsgeld_abzug_transfer(
    erziehungsgeld_eink_relev_kind_m: float,
    _erziehungsgeld_einkommensgrenze_kind_m: float,
    alter_monate: float,
    erziehungsgeld_params: dict,
) -> float:
    """Reduction of parental leave benefits (means-test).

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (p.209)

    Parameters
    ----------
    erziehungsgeld_eink_relev_kind_m
        See :func:`erziehungsgeld_eink_relev_kind_y`.
    _erziehungsgeld_einkommensgrenze_kind_m
        See :func:`_erziehungsgeld_einkommensgrenze_kind_y`.
    alter_monate
        See :func:`alter_monate`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    Income reduction for parental leave benefit (Erziehungsgeld)
    """
    if (
        erziehungsgeld_eink_relev_kind_m > _erziehungsgeld_einkommensgrenze_kind_m
        and alter_monate
        >= erziehungsgeld_params["einkommensgrenze"]["start_age_m_reduced_income_limit"]
    ):
        out = (
            erziehungsgeld_eink_relev_kind_m * erziehungsgeld_params["abschlag_faktor"]
        )
    else:
        out = 0.0
    return out


@policy_info(
    start_date="2004-01-01", end="2006-12-10", change_name="erziehungsgeld_anspruch_kind"
)
def _erziehungsgeld_anspruch_kind_vor_abschaffung(
    kind: bool,
    alter_monate: float,
    budgetsatz_erzieh: bool,
    erziehungsgeld_params: dict,
) -> bool:
    """Eligibility for parental leave benefit (Erziehungsgeld) on child level.

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.207)

    Parameters
    ----------
    kind
        See :See basic input variable :ref:`kind <kind>`.
    alter_monate
        See :func:`alter_monate`.
    budgetsatz_erzieh
        See :See basic input variable :ref:`budgetsatz_erzieh
        <budgetsatz_erzieh>`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    eligibility of (Erziehungsgeld) as a bool

    """
    if budgetsatz_erzieh:
        out = kind and alter_monate <= erziehungsgeld_params["end_age_m_budgetsatz"]

    else:
        out = kind and alter_monate <= erziehungsgeld_params["end_age_m_regelsatz"]

    return out


@policy_info(
    start_date="2006-12-11", end="2008-12-31", change_name="erziehungsgeld_anspruch_kind"
)
def _erziehungsgeld_anspruch_kind_nach_abschaffung(
    kind: bool,
    geburtsjahr: int,
    alter_monate: float,
    budgetsatz_erzieh: bool,
    erziehungsgeld_params: dict,
) -> bool:
    """Eligibility for parental leave benefit (Erziehungsgeld) on child level. Abolished
    for children born after the cut-off date.

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.207)

    Parameters
    ----------
    kind
        See :See basic input variable :ref:`kind <kind>`.
    geburtsjahr
        See :func:`geburtsjahr`.
    alter_monate
        See :func:`alter_monate`.
    budgetsatz_erzieh
        See :See basic input variable :ref:`budgetsatz_erzieh
        <budgetsatz_erzieh>`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    eligibility of (Erziehungsgeld) as a bool

    """
    if budgetsatz_erzieh and geburtsjahr <= erziehungsgeld_params["abolishment_cohort"]:
        out = kind and alter_monate <= erziehungsgeld_params["end_age_m_budgetsatz"]

    elif geburtsjahr <= erziehungsgeld_params["abolishment_cohort"]:
        out = kind and alter_monate <= erziehungsgeld_params["end_age_m_regelsatz"]

    else:
        out = False

    return out


@policy_info(start_date="2004-01-01", end="2008-12-31")
def erziehungsgeld_anspruch_eltern(
    arbeitsstunden_w: float,
    hat_kinder: bool,
    erziehungsgeld_anspruch_kind_fg: bool,
    erziehungsgeld_params: dict,
) -> bool:
    """Eligibility for parental leave benefit (Erziehungsgeld) on parental level.

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (p.207)

    Parameters
    ----------
    arbeitsstunden_w
        See :See basic input variable :ref:`arbeitsstunden_w <arbeitsstunden_w>`.
    hat_kinder
        See :See basic input variable :ref:`hat_kinder <hat_kinder>`.
    erziehungsgeld_anspruch_kind_fg
        See :func:`erziehungsgeld_anspruch_kind_fg`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    eligibility of parental leave benefit (Erziehungsgeld) as a bool

    """
    out = (
        erziehungsgeld_anspruch_kind_fg
        and (arbeitsstunden_w <= erziehungsgeld_params["arbeitsstunden_w_grenze"])
        and hat_kinder
    )

    return out


@policy_info(start_date="2004-01-01", end="2008-12-31")
def erziehungsgeld_eink_relev_kind_y(
    bruttolohn_vorj_y_fg: float,
    anz_erwachsene_fg: int,
    erziehungsgeld_anspruch_kind: bool,
    erziehungsgeld_params: dict,
    eink_st_abzuege_params: dict,
) -> float:
    """Income relevant for means testing for parental leave benefit (Erziehungsgeld).

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (p.209)

    There is special rule for "Beamte, Soldaten und Richter" which is not
    implemented yet.

    Parameters
    ----------
    bruttolohn_vorj_y_fg
        See :func:`bruttolohn_vorj_y_fg`.
    anz_erwachsene_fg
        See :func:`anz_erwachsene_fg`.
    erziehungsgeld_anspruch_kind
        See :func:`erziehungsgeld_anspruch_kind`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------
    Relevant income
    """

    if erziehungsgeld_anspruch_kind:
        out = (
            bruttolohn_vorj_y_fg
            - eink_st_abzuege_params["werbungskostenpauschale"] * anz_erwachsene_fg
        ) * erziehungsgeld_params["pauschal_abzug_auf_einkommen"]
    else:
        out = 0.0
    return out


@policy_info(start_date="2004-01-01", end="2008-12-31")
def _erziehungsgeld_einkommensgrenze_kind_y(
    _erziehungsgeld_einkommensgrenze_vor_aufschl: float,
    anz_kinder_mit_kindergeld_fg: float,
    erziehungsgeld_anspruch_kind: bool,
    erziehungsgeld_params: dict,
) -> float:
    """Income threshold for parental leave benefit (Erziehungsgeld).

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.208)

    Parameters
    ----------
    _erziehungsgeld_einkommensgrenze_vor_aufschl
        See :func:`_erziehungsgeld_einkommensgrenze_vor_aufschl`.
    anz_kinder_mit_kindergeld_fg
        See :func:`anz_kinder_mit_kindergeld_fg`.
    erziehungsgeld_anspruch_kind
        See :func:`erziehungsgeld_anspruch_kind`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    income threshold for parental leave benefit (Erziehungsgeld) on child level
    """

    out = (
        _erziehungsgeld_einkommensgrenze_vor_aufschl
        + (anz_kinder_mit_kindergeld_fg - 1)
        * erziehungsgeld_params["aufschlag_einkommen"]
    )
    if not erziehungsgeld_anspruch_kind:
        out = 0.0
    return out


@policy_info(start_date="2004-01-01", end="2008-12-31")
def _erziehungsgeld_einkommensgrenze_vor_aufschl(
    alleinerz_fg: bool,
    alter_monate: float,
    budgetsatz_erzieh: bool,
    erziehungsgeld_params: dict,
) -> float:
    """Income threshold for parental leave benefit (Erziehungsgeld) on child level
    before adding the bonus for additional children

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.208)

    Parameters
    ----------
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.
    alleinerz_fg
        See :func:`alleinerz_fg`.
    alter_monate
        See :func:`alter_monate`.
    budgetsatz_erzieh
        See :See basic input variable :ref:`budgetsatz_erzieh
        <budgetsatz_erzieh>`.

    Returns
    -------
    Income threshold for parental leave benefit (Erziehungsgeld) before child bonus
    """
    # There are different income thresholds depending on the age of the child,
    # the fact if a person is a single parent, and if regelsatz or budgetsatz is applied

    if (
        alter_monate
        < erziehungsgeld_params["einkommensgrenze"]["start_age_m_reduced_income_limit"]
    ):
        limit = "limit"
    else:
        limit = "reduced_limit"

    if alleinerz_fg:
        status_eltern = "alleinerz"
    else:
        status_eltern = "paar"

    if budgetsatz_erzieh:
        satz = "budgetsatz"
    else:
        satz = "regelsatz"

    out = erziehungsgeld_params["einkommensgrenze"][limit][status_eltern][satz]

    return out
