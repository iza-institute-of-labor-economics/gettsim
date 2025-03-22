"""Functions to compute parental leave benefits (Erziehungsgeld, -2007)."""

from _gettsim.aggregation import AggregateByPIDSpec
from _gettsim.function_types import policy_function

aggregation_specs = {
    "anspruchshöhe_m": AggregateByPIDSpec(
        p_id_to_aggregate_by="p_id_empfänger",
        source_col="anspruchshöhe_kind_m",
        aggr="sum",
    ),
}


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def betrag_m(
    anspruchshöhe_m: int,
    grundsätzlich_anspruchsberechtigt: bool,
) -> bool:
    """Total parental leave benefits (Erziehungsgeld) received by the parent.

    Legal reference: BErzGG (BGBl. I 1985 S. 2154; BGBl. I 2004 S. 206)

    Parameters
    ----------
    anspruchshöhe_m
        See :func:`anspruchshöhe_m`.
    grundsätzlich_anspruchsberechtigt
        See :func:`grundsätzlich_anspruchsberechtigt`.

    Returns
    -------
    Parental leave benefits (Erziehungsgeld).

    """
    if grundsätzlich_anspruchsberechtigt:
        out = anspruchshöhe_m
    else:
        out = 0.0

    return out


@policy_function(
    end_date="2003-12-31",
    leaf_name="anspruchshöhe_kind_m",
    params_key_for_rounding="erziehungsgeld",
)
def erziehungsgeld_kind_ohne_budgetsatz_m() -> float:
    raise NotImplementedError(
        """
    Erziehungsgeld is not implemented yet prior to 2004, see
    https://github.com/iza-institute-of-labor-economics/gettsim/issues/673
        """
    )


@policy_function(
    start_date="2004-01-01",
    end_date="2008-12-31",
    leaf_name="anspruchshöhe_kind_m",
    params_key_for_rounding="erziehungsgeld",
)
def anspruchshöhe_kind_mit_budgetsatz_m(
    kind_grundsätzlich_anspruchsberechtigt: bool,
    abzug_durch_einkommen_m: float,
    basisbetrag_m: float,
) -> float:
    """Parental leave benefit (Erziehungsgeld) on child level.

    For the calculation, the relevant income, the age of the youngest child, the income
    threshold and the eligibility for erziehungsgeld is needed.

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6

    Parameters
    ----------
    kind_grundsätzlich_anspruchsberechtigt
        See :func:`kind_grundsätzlich_anspruchsberechtigt`.
    abzug_durch_einkommen_m
        See :func:`abzug_durch_einkommen_m`.
    basisbetrag_m
        See :func:`erziehungsgeld_ohne_abzug`.


    Returns
    -------
    Monthly claim of parental leave benefit (Erziehungsgeld) on child level
    """
    if kind_grundsätzlich_anspruchsberechtigt:
        out = max(
            basisbetrag_m - abzug_durch_einkommen_m,
            0.0,
        )
    else:
        out = 0.0

    return out


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def basisbetrag_m(
    budgetsatz: bool,
    anzurechnendes_einkommen_y: float,
    einkommensgrenze_y: float,
    demographics__alter_monate: float,
    erziehungsgeld_params: dict,
) -> float:
    """Parental leave benefit (Erziehungsgeld) without means-test on child level.

    Parameters
    ----------
    budgetsatz
        See :See basic input variable :ref:`budgetsatz
        <budgetsatz>`.
    anzurechnendes_einkommen_y
        See :func:`anzurechnendes_einkommen_y`.
    einkommensgrenze_y
        See :func:`einkommensgrenze_y`.
    demographics__alter_monate
        See :func:`demographics__alter_monate`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    Parental leave benefit (Erziehungsgeld) without means-test
    """
    # no benefit if income is above threshold and child is younger than threshold
    if (
        anzurechnendes_einkommen_y > einkommensgrenze_y
        and demographics__alter_monate
        < erziehungsgeld_params["einkommensgrenze"]["start_age_m_reduced_income_limit"]
    ):
        out = 0.0
    elif budgetsatz:
        out = erziehungsgeld_params["erziehungsgeld_satz"]["budgetsatz"]
    else:
        out = erziehungsgeld_params["erziehungsgeld_satz"]["regelsatz"]

    return out


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def abzug_durch_einkommen_m(
    anzurechnendes_einkommen_m: float,
    einkommensgrenze_m: float,
    demographics__alter_monate: float,
    erziehungsgeld_params: dict,
) -> float:
    """Reduction of parental leave benefits (means-test).

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (p.209)

    Parameters
    ----------
    anzurechnendes_einkommen_m
        See :func:`anzurechnendes_einkommen_y`.
    einkommensgrenze_m
        See :func:`einkommensgrenze_y`.
    demographics__alter_monate
        See :func:`demographics__alter_monate`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    Income reduction for parental leave benefit (Erziehungsgeld)
    """
    if (
        anzurechnendes_einkommen_m > einkommensgrenze_m
        and demographics__alter_monate
        >= erziehungsgeld_params["einkommensgrenze"]["start_age_m_reduced_income_limit"]
    ):
        out = anzurechnendes_einkommen_m * erziehungsgeld_params["abschlag_faktor"]
    else:
        out = 0.0
    return out


@policy_function(
    start_date="2004-01-01",
    end_date="2006-12-10",
    leaf_name="kind_grundsätzlich_anspruchsberechtigt",
)
def _kind_grundsätzlich_anspruchsberechtigt_vor_abschaffung(
    demographics__kind: bool,
    demographics__alter_monate: float,
    budgetsatz: bool,
    erziehungsgeld_params: dict,
) -> bool:
    """Eligibility for parental leave benefit (Erziehungsgeld) on child level.

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.207)

    Parameters
    ----------
    demographics__kind
        See :See basic input variable :ref:`demographics__kind <demographics__kind>`.
    demographics__alter_monate
        See :func:`demographics__alter_monate`.
    budgetsatz
        See :See basic input variable :ref:`budgetsatz
        <budgetsatz>`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    eligibility of (Erziehungsgeld) as a bool

    """
    if budgetsatz:
        out = (
            demographics__kind
            and demographics__alter_monate
            <= erziehungsgeld_params["end_age_m_budgetsatz"]
        )

    else:
        out = (
            demographics__kind
            and demographics__alter_monate
            <= erziehungsgeld_params["end_age_m_regelsatz"]
        )

    return out


@policy_function(
    start_date="2006-12-11",
    end_date="2008-12-31",
    leaf_name="kind_grundsätzlich_anspruchsberechtigt",
)
def _kind_grundsätzlich_anspruchsberechtigt_nach_abschaffung(
    demographics__kind: bool,
    demographics__geburtsjahr: int,
    demographics__alter_monate: float,
    budgetsatz: bool,
    erziehungsgeld_params: dict,
) -> bool:
    """Eligibility for parental leave benefit (Erziehungsgeld) on child level. Abolished
    for children born after the cut-off date.

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.207)

    Parameters
    ----------
    demographics__kind
        See :See basic input variable :ref:`demographics__kind <demographics__kind>`.
    demographics__geburtsjahr
        See :func:`demographics__geburtsjahr`.
    demographics__alter_monate
        See :func:`demographics__alter_monate`.
    budgetsatz
        See :See basic input variable :ref:`budgetsatz
        <budgetsatz>`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    eligibility of (Erziehungsgeld) as a bool

    """
    if (
        budgetsatz
        and demographics__geburtsjahr <= erziehungsgeld_params["abolishment_cohort"]
    ):
        out = (
            demographics__kind
            and demographics__alter_monate
            <= erziehungsgeld_params["end_age_m_budgetsatz"]
        )

    elif demographics__geburtsjahr <= erziehungsgeld_params["abolishment_cohort"]:
        out = (
            demographics__kind
            and demographics__alter_monate
            <= erziehungsgeld_params["end_age_m_regelsatz"]
        )

    else:
        out = False

    return out


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def grundsätzlich_anspruchsberechtigt(
    demographics__arbeitsstunden_w: float,
    kind_grundsätzlich_anspruchsberechtigt_fg: bool,
    erziehungsgeld_params: dict,
) -> bool:
    """Eligibility for parental leave benefit (Erziehungsgeld) on parental level.

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (p.207)

    Parameters
    ----------
    demographics__arbeitsstunden_w
        See :See basic input variable :ref:`demographics__arbeitsstunden_w <demographics__arbeitsstunden_w>`.
    kind_grundsätzlich_anspruchsberechtigt_fg
        See :func:`kind_grundsätzlich_anspruchsberechtigt_fg`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    eligibility of parental leave benefit (Erziehungsgeld) as a bool

    """
    out = kind_grundsätzlich_anspruchsberechtigt_fg and (
        demographics__arbeitsstunden_w
        <= erziehungsgeld_params["arbeitsstunden_w_grenze"]
    )

    return out


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def anzurechnendes_einkommen_y(
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_vorjahr_y_fg: float,
    arbeitslosengeld_2__anzahl_erwachsene_fg: int,
    kind_grundsätzlich_anspruchsberechtigt: bool,
    erziehungsgeld_params: dict,
    eink_st_abzuege_params: dict,
) -> float:
    """Income relevant for means testing for parental leave benefit (Erziehungsgeld).

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (p.209)

    There is special rule for "Beamte, Soldaten und Richter" which is not
    implemented yet.

    Parameters
    ----------
    einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_vorjahr_y_fg
        See :func:`einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_vorjahr_y_fg`.
    arbeitslosengeld_2__anzahl_erwachsene_fg
        See :func:`arbeitslosengeld_2__anzahl_erwachsene_fg`.
    kind_grundsätzlich_anspruchsberechtigt
        See :func:`kind_grundsätzlich_anspruchsberechtigt`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------
    Relevant income
    """

    if kind_grundsätzlich_anspruchsberechtigt:
        out = (
            einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_vorjahr_y_fg
            - eink_st_abzuege_params["werbungskostenpauschale"]
            * arbeitslosengeld_2__anzahl_erwachsene_fg
        ) * erziehungsgeld_params["pauschal_abzug_auf_einkommen"]
    else:
        out = 0.0
    return out


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def einkommensgrenze_y(
    einkommensgrenze_ohne_geschwisterbonus: float,
    arbeitslosengeld_2__anzahl_kinder_fg: float,
    kind_grundsätzlich_anspruchsberechtigt: bool,
    erziehungsgeld_params: dict,
) -> float:
    """Income threshold for parental leave benefit (Erziehungsgeld).

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.208)

    Parameters
    ----------
    einkommensgrenze_ohne_geschwisterbonus
        See :func:`einkommensgrenze_ohne_geschwisterbonus`.
    arbeitslosengeld_2__anzahl_kinder_fg
        See :func:`arbeitslosengeld_2__anzahl_kinder_fg`.
    kind_grundsätzlich_anspruchsberechtigt
        See :func:`kind_grundsätzlich_anspruchsberechtigt`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    income threshold for parental leave benefit (Erziehungsgeld) on child level
    """

    out = (
        einkommensgrenze_ohne_geschwisterbonus
        + (arbeitslosengeld_2__anzahl_kinder_fg - 1)
        * erziehungsgeld_params["aufschlag_einkommen"]
    )
    if not kind_grundsätzlich_anspruchsberechtigt:
        out = 0.0
    return out


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def einkommensgrenze_ohne_geschwisterbonus(
    demographics__alleinerziehend_fg: bool,
    demographics__alter_monate: float,
    budgetsatz: bool,
    erziehungsgeld_params: dict,
) -> float:
    """Income threshold for parental leave benefit (Erziehungsgeld) on child level
    before adding the bonus for additional children

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.208)

    Parameters
    ----------
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.
    demographics__alleinerziehend_fg
        See :func:`demographics__alleinerziehend_fg`.
    demographics__alter_monate
        See :func:`demographics__alter_monate`.
    budgetsatz
        See :See basic input variable :ref:`budgetsatz
        <budgetsatz>`.

    Returns
    -------
    Income threshold for parental leave benefit (Erziehungsgeld) before child bonus
    """
    # There are different income thresholds depending on the age of the child,
    # the fact if a person is a single parent, and if regelsatz or budgetsatz is applied

    if (
        demographics__alter_monate
        < erziehungsgeld_params["einkommensgrenze"]["start_age_m_reduced_income_limit"]
    ):
        limit = "limit"
    else:
        limit = "reduced_limit"

    if demographics__alleinerziehend_fg:
        status_eltern = "alleinerziehend"
    else:
        status_eltern = "paar"

    if budgetsatz:
        satz = "budgetsatz"
    else:
        satz = "regelsatz"

    out = erziehungsgeld_params["einkommensgrenze"][limit][status_eltern][satz]

    return out
