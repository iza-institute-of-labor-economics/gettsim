"""Income relevant for calculation of Kinderzuschlag."""

from _gettsim.functions.policy_function import policy_function

aggregate_by_group_kinderzuschl_eink = {
    "anzahl_kinder_bg": {
        "source_col": "kindergeld__anzahl_ansprüche",
        "aggr": "sum",
    },
}


def bruttoeinkommen_eltern_m(
    arbeitsl_geld_2_bruttoeink_m: float,
    kindergeld__anspruchsberechtigt: bool,
    erwachsen: bool,
) -> float:
    """Calculate parental gross income for calculation of child benefit.

    This variable is used to check whether the minimum income threshold for child
    benefit is met.

    Parameters
    ----------
    arbeitsl_geld_2_bruttoeink_m
        See :func:`arbeitsl_geld_2_bruttoeink_m`.
    kindergeld__anspruchsberechtigt
        See :func:`kindergeld__anspruchsberechtigt`.
    erwachsen
        See basic input variable :ref:`erwachsen <erwachsen>`.


    Returns
    -------

    """
    # TODO(@MImmesberger): Redesign the conditions in this function: False for adults
    # who do not have Kindergeld claims.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/704
    if erwachsen and (not kindergeld__anspruchsberechtigt):
        out = arbeitsl_geld_2_bruttoeink_m
    else:
        out = 0.0

    return out


@policy_function(params_key_for_rounding="kinderzuschl_eink")
def nettoeinkommen_eltern_m(
    arbeitsl_geld_2_nettoeink_nach_abzug_freibetrag_m: float,
    kindergeld__anspruchsberechtigt: bool,
    erwachsen: bool,
) -> float:
    """Parental income (after deduction of taxes, social insurance contributions, and
    other deductions) for calculation of child benefit.

    Parameters
    ----------
    arbeitsl_geld_2_nettoeink_nach_abzug_freibetrag_m
        See :func:`arbeitsl_geld_2_nettoeink_nach_abzug_freibetrag_m`.
    kindergeld__anspruchsberechtigt
        See :func:`kindergeld__anspruchsberechtigt`.
    erwachsen
        See basic input variable :ref:`erwachsen <erwachsen>`.

    Returns
    -------

    """
    # TODO(@MImmesberger): Redesign the conditions in this function: False for adults
    # who do not have Kindergeld claims.
    # https://github.com/iza-institute-of-labor-economics/gettsim/issues/704
    if erwachsen and (not kindergeld__anspruchsberechtigt):
        out = arbeitsl_geld_2_nettoeink_nach_abzug_freibetrag_m
    else:
        out = 0.0
    return out


@policy_function(end_date="2019-06-30")
def maximales_nettoeinkommen_m_bg(
    bedarf_m_bg: float,
    anzahl_kinder_bg: int,
    kinderzuschl_params: dict,
) -> float:
    """Calculate maximum income to be eligible for additional child benefit
    (Kinderzuschlag).

    There is a maximum income threshold, depending on the need, plus the potential kiz
    receipt (§6a (1) Nr. 3 BKGG).

    Parameters
    ----------
    bedarf_m_bg
        See :func:`bedarf_m_bg`.
    anzahl_kinder_bg
        See :func:`anzahl_kinder_bg`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    out = bedarf_m_bg + kinderzuschl_params["maximum"] * anzahl_kinder_bg

    kindersofortzuschl = kinderzuschl_params.get("kindersofortzuschl", 0.0)
    out += kindersofortzuschl * anzahl_kinder_bg

    return out


def mindestbruttoeinkommen_m_bg(
    anzahl_kinder_bg: int,
    alleinerz_bg: bool,
    kinderzuschl_params: dict,
) -> float:
    """Calculate minimal claim of child benefit (kinderzuschlag).

    Min income to be eligible for KIZ (different for singles and couples) (§6a (1) Nr. 2
    BKGG).

    Parameters
    ----------
    anzahl_kinder_bg
        See :func:`anzahl_kinder_bg
        <anzahl_kinder_bg>`.
    alleinerz_bg
        See basic input variable :ref:`alleinerz_bg <alleinerz_bg>`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    if anzahl_kinder_bg == 0:
        out = 0.0
    elif alleinerz_bg:
        out = kinderzuschl_params["min_eink_alleinerz"]
    else:
        out = kinderzuschl_params["min_eink_paare"]

    return out


def anzurechnendes_einkommen_eltern_m_bg(
    nettoeinkommen_eltern_m_bg: float,
    bedarf_m_bg: float,
    kinderzuschl_params: dict,
) -> float:
    """Calculate parental income subtracted from child benefit.

    (§6a (6) S. 3 BKGG)

    Parameters
    ----------
    nettoeinkommen_eltern_m_bg
        See :func:`nettoeinkommen_eltern_m_bg`.
    bedarf_m_bg
        See :func:`bedarf_m_bg`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    out = kinderzuschl_params["entzugsrate_eltern"] * (
        nettoeinkommen_eltern_m_bg - bedarf_m_bg
    )

    return max(out, 0.0)


def basisbetrag_kind_m(  # noqa: PLR0913
    kindergeld__anspruchsberechtigt: bool,
    bruttolohn_m: float,
    kind_unterh_erhalt_m: float,
    unterhaltsvorschuss__betrag_m: float,
    arbeitsl_geld_2_eink_anr_frei_m: float,
    kinderzuschl_params: dict,
) -> float:
    """Child benefit after children income for each eligible child is considered.

    (§6a (3) S.3 BKGG)

    Parameters
    ----------
    kindergeld__anspruchsberechtigt
        See :func:`kindergeld__anspruchsberechtigt`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    kind_unterh_erhalt_m
        See basic input variable :ref:`kind_unterh_erhalt_m <kind_unterh_erhalt_m>`.
    unterhaltsvorschuss__betrag_m
        See :func:`unterhaltsvorschuss__betrag_m`.
    arbeitsl_geld_2_eink_anr_frei_m
        See :func:`arbeitsl_geld_2_eink_anr_frei_m`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    out = kindergeld__anspruchsberechtigt * (
        kinderzuschl_params["maximum"]
        - kinderzuschl_params["entzugsrate_kind"]
        * (
            bruttolohn_m
            + kind_unterh_erhalt_m
            + unterhaltsvorschuss__betrag_m
            - arbeitsl_geld_2_eink_anr_frei_m
        )
    )

    return max(out, 0.0)
