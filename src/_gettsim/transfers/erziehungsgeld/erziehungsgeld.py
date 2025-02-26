"""Functions to compute parental leave benefits (Erziehungsgeld, -2007)."""

from _gettsim.aggregation import AggregateByPIDSpec
from _gettsim.functions.policy_function import policy_function

aggregation_specs = {
    "anspruchshöhe_eltern_m": AggregateByPIDSpec(
        p_id_to_aggregate_by="p_id_erziehgeld_empf",
        source_col="anspruchshöhe_kind_m",
        aggr="sum",
    ),
}


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def betrag_m(
    anspruchshöhe_eltern_m: int,
    eltern_grundsätzlich_anspruchsberechtigt: bool,
) -> bool:
    """Total parental leave benefits (Erziehungsgeld).

    Parental leave benefits for the parent that claims the benefit.

    Legal reference: BErzGG (BGBl. I 1985 S. 2154; BGBl. I 2004 S. 206)

    Parameters
    ----------
    anspruchshöhe_eltern_m
        See :func:`anspruchshöhe_eltern_m`.
    eltern_grundsätzlich_anspruchsberechtigt
        See :func:`eltern_grundsätzlich_anspruchsberechtigt`.

    Returns
    -------
    Parental leave benefits (Erziehungsgeld).

    """
    if eltern_grundsätzlich_anspruchsberechtigt:
        out = anspruchshöhe_eltern_m
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
    elterngeld__kind_grundsätzlich_anspruchsberechtigt: bool,
    abzug_durch_einkommen_m: float,
    basisbetrag_m: float,
) -> float:
    """Parental leave benefit (Erziehungsgeld) on child level.

    For the calculation, the relevant income, the age of the youngest child, the income
    threshold and the eligibility for erziehungsgeld is needed.

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6

    Parameters
    ----------
    elterngeld__kind_grundsätzlich_anspruchsberechtigt
        See :func:`elterngeld__kind_grundsätzlich_anspruchsberechtigt`.
    abzug_durch_einkommen_m
        See :func:`abzug_durch_einkommen_m`.
    basisbetrag_m
        See :func:`erziehungsgeld_ohne_abzug`.


    Returns
    -------
    Monthly claim of parental leave benefit (Erziehungsgeld) on child level
    """
    if elterngeld__kind_grundsätzlich_anspruchsberechtigt:
        out = max(
            basisbetrag_m - abzug_durch_einkommen_m,
            0.0,
        )
    else:
        out = 0.0

    return out


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def basisbetrag_m(
    budgetsatz_erzieh: bool,
    anzurechnendes_einkommen_y: float,
    einkommensgrenze_y: float,
    demographic_vars__alter_monate: float,
    erziehungsgeld_params: dict,
) -> float:
    """Parental leave benefit (Erziehungsgeld) without means-test on child level.

    Parameters
    ----------
    budgetsatz_erzieh
        See :See basic input variable :ref:`budgetsatz_erzieh
        <budgetsatz_erzieh>`.
    anzurechnendes_einkommen_y
        See :func:`anzurechnendes_einkommen_y`.
    einkommensgrenze_y
        See :func:`einkommensgrenze_y`.
    demographic_vars__alter_monate
        See :func:`demographic_vars__alter_monate`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    Parental leave benefit (Erziehungsgeld) without means-test
    """
    # no benefit if income is above threshold and child is younger than threshold
    if (
        anzurechnendes_einkommen_y > einkommensgrenze_y
        and demographic_vars__alter_monate
        < erziehungsgeld_params["einkommensgrenze"]["start_age_m_reduced_income_limit"]
    ):
        out = 0.0
    elif budgetsatz_erzieh:
        out = erziehungsgeld_params["erziehungsgeld_satz"]["budgetsatz"]
    else:
        out = erziehungsgeld_params["erziehungsgeld_satz"]["regelsatz"]

    return out


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def abzug_durch_einkommen_m(
    anzurechnendes_einkommen_m: float,
    einkommensgrenze_m: float,
    demographic_vars__alter_monate: float,
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
    demographic_vars__alter_monate
        See :func:`demographic_vars__alter_monate`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    Income reduction for parental leave benefit (Erziehungsgeld)
    """
    if (
        anzurechnendes_einkommen_m > einkommensgrenze_m
        and demographic_vars__alter_monate
        >= erziehungsgeld_params["einkommensgrenze"]["start_age_m_reduced_income_limit"]
    ):
        out = anzurechnendes_einkommen_m * erziehungsgeld_params["abschlag_faktor"]
    else:
        out = 0.0
    return out


@policy_function(
    start_date="2004-01-01",
    end_date="2006-12-10",
    leaf_name="elterngeld__kind_grundsätzlich_anspruchsberechtigt",
)
def _elterngeld__kind_grundsätzlich_anspruchsberechtigt_vor_abschaffung(
    kind: bool,
    demographic_vars__alter_monate: float,
    budgetsatz_erzieh: bool,
    erziehungsgeld_params: dict,
) -> bool:
    """Eligibility for parental leave benefit (Erziehungsgeld) on child level.

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.207)

    Parameters
    ----------
    kind
        See :See basic input variable :ref:`kind <kind>`.
    demographic_vars__alter_monate
        See :func:`demographic_vars__alter_monate`.
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
        out = (
            kind
            and demographic_vars__alter_monate
            <= erziehungsgeld_params["end_age_m_budgetsatz"]
        )

    else:
        out = (
            kind
            and demographic_vars__alter_monate
            <= erziehungsgeld_params["end_age_m_regelsatz"]
        )

    return out


@policy_function(
    start_date="2006-12-11",
    end_date="2008-12-31",
    leaf_name="elterngeld__kind_grundsätzlich_anspruchsberechtigt",
)
def _elterngeld__kind_grundsätzlich_anspruchsberechtigt_nach_abschaffung(
    kind: bool,
    geburtsjahr: int,
    demographic_vars__alter_monate: float,
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
    demographic_vars__alter_monate
        See :func:`demographic_vars__alter_monate`.
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
        out = (
            kind
            and demographic_vars__alter_monate
            <= erziehungsgeld_params["end_age_m_budgetsatz"]
        )

    elif geburtsjahr <= erziehungsgeld_params["abolishment_cohort"]:
        out = (
            kind
            and demographic_vars__alter_monate
            <= erziehungsgeld_params["end_age_m_regelsatz"]
        )

    else:
        out = False

    return out


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def eltern_grundsätzlich_anspruchsberechtigt(
    arbeitsstunden_w: float,
    elterngeld__kind_grundsätzlich_anspruchsberechtigt_fg: bool,
    erziehungsgeld_params: dict,
) -> bool:
    """Eligibility for parental leave benefit (Erziehungsgeld) on parental level.

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (p.207)

    Parameters
    ----------
    arbeitsstunden_w
        See :See basic input variable :ref:`arbeitsstunden_w <arbeitsstunden_w>`.
    elterngeld__kind_grundsätzlich_anspruchsberechtigt_fg
        See :func:`elterngeld__kind_grundsätzlich_anspruchsberechtigt_fg`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    eligibility of parental leave benefit (Erziehungsgeld) as a bool

    """
    out = elterngeld__kind_grundsätzlich_anspruchsberechtigt_fg and (
        arbeitsstunden_w <= erziehungsgeld_params["arbeitsstunden_w_grenze"]
    )

    return out


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def anzurechnendes_einkommen_y(
    bruttolohn_vorj_y_fg: float,
    demographic_vars__anzahl_erwachsene_fg: int,
    elterngeld__kind_grundsätzlich_anspruchsberechtigt: bool,
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
    demographic_vars__anzahl_erwachsene_fg
        See :func:`demographic_vars__anzahl_erwachsene_fg`.
    elterngeld__kind_grundsätzlich_anspruchsberechtigt
        See :func:`elterngeld__kind_grundsätzlich_anspruchsberechtigt`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.
    eink_st_abzuege_params
        See params documentation :ref:`eink_st_abzuege_params <eink_st_abzuege_params>`.

    Returns
    -------
    Relevant income
    """

    if elterngeld__kind_grundsätzlich_anspruchsberechtigt:
        out = (
            bruttolohn_vorj_y_fg
            - eink_st_abzuege_params["werbungskostenpauschale"]
            * demographic_vars__anzahl_erwachsene_fg
        ) * erziehungsgeld_params["pauschal_abzug_auf_einkommen"]
    else:
        out = 0.0
    return out


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def einkommensgrenze_y(
    einkommensgrenze_ohne_geschwisterbonus: float,
    kindergeld__anzahl_kinder_fg: float,
    elterngeld__kind_grundsätzlich_anspruchsberechtigt: bool,
    erziehungsgeld_params: dict,
) -> float:
    """Income threshold for parental leave benefit (Erziehungsgeld).

    Legal reference: Bundesgesetzblatt Jahrgang 2004 Teil I Nr. 6 (pp.208)

    Parameters
    ----------
    einkommensgrenze_ohne_geschwisterbonus
        See :func:`einkommensgrenze_ohne_geschwisterbonus`.
    kindergeld__anzahl_kinder_fg
        See :func:`kindergeld__anzahl_kinder_fg`.
    elterngeld__kind_grundsätzlich_anspruchsberechtigt
        See :func:`elterngeld__kind_grundsätzlich_anspruchsberechtigt`.
    erziehungsgeld_params
        See params documentation :ref:`erziehungsgeld_params <erziehungsgeld_params>`.

    Returns
    -------
    income threshold for parental leave benefit (Erziehungsgeld) on child level
    """

    out = (
        einkommensgrenze_ohne_geschwisterbonus
        + (kindergeld__anzahl_kinder_fg - 1)
        * erziehungsgeld_params["aufschlag_einkommen"]
    )
    if not elterngeld__kind_grundsätzlich_anspruchsberechtigt:
        out = 0.0
    return out


@policy_function(start_date="2004-01-01", end_date="2008-12-31")
def einkommensgrenze_ohne_geschwisterbonus(
    alleinerz_fg: bool,
    demographic_vars__alter_monate: float,
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
    demographic_vars__alter_monate
        See :func:`demographic_vars__alter_monate`.
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
        demographic_vars__alter_monate
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
