from _gettsim.shared import dates_active

aggregation_kinderzuschl_eink = {
    "_kinderzuschl_anz_kinder_anspruch_bg": {
        "source_col": "kindergeld_anspruch",
        "aggr": "sum",
    },
}


def kinderzuschl_bruttoeink_eltern_m(
    arbeitsl_geld_2_bruttoeink_m: float,
    eltern: bool,
) -> float:
    """Calculate parental gross income for calculation of child benefit.

    This variable is used to check whether the minimum income threshold for child
    benefit is met.

    Parameters
    ----------
    arbeitsl_geld_2_bruttoeink_m
        See :func:`arbeitsl_geld_2_bruttoeink_m`.
    eltern
        See :func:`eltern`.

    Returns
    -------

    """

    if eltern:
        out = arbeitsl_geld_2_bruttoeink_m
    else:
        out = 0.0

    return out


def kinderzuschl_eink_eltern_m(
    arbeitsl_geld_2_eink_m: float,
    eltern: bool,
) -> float:
    """Parental income (after deduction of taxes, social insurance contributions, and
    other deductions) for calculation of child benefit.

    Parameters
    ----------
    arbeitsl_geld_2_eink_m_tu
        See :func:`arbeitsl_geld_2_eink_m_tu`.
    eltern
        See basic input variable :ref:`eltern <eltern>`.

    Returns
    -------

    """
    if eltern:
        out = arbeitsl_geld_2_eink_m
    else:
        out = 0.0
    return out


@dates_active(end="2010-12-31", change_name="kinderzuschl_eink_regel_m_tu")
def kinderzuschl_eink_regel_m_bg_arbeitsl_geld_2_params_old(
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh: float,
    alleinerz_bg: bool,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate income relevant for calculation of child benefit until 2010.

    Parameters
    ----------
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh`.
    alleinerz_bg
        See :func:`alleinerz_bg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    if alleinerz_bg:
        out = arbeitsl_geld_2_params["regelsatz"] * (
            1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
        )
    else:
        out = (
            arbeitsl_geld_2_params["regelsatz"]
            * arbeitsl_geld_2_params["anteil_regelsatz"]["zwei_erwachsene"]
            * 2
        )

    return float(out)


@dates_active(start="2011-01-01")
def kinderzuschl_eink_regel_m_bg(
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh: float,
    alleinerz_bg: bool,
    arbeitsl_geld_2_params: dict,
) -> float:
    """Calculate income relevant for calculation of child benefit since 2011.

    Parameters
    ----------
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh`.
    alleinerz_bg
        See :func:`alleinerz_bg`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    if alleinerz_bg:
        out = arbeitsl_geld_2_params["regelsatz"][1] * (
            1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
        )
    else:
        out = arbeitsl_geld_2_params["regelsatz"][2] * 2

    return float(out)


def kinderzuschl_eink_relev_m_bg(
    kinderzuschl_eink_regel_m_bg: float, kinderzuschl_kost_unterk_m_bg: float
) -> float:
    """Aggregate relevant income and rental costs.

    Parameters
    ----------
    kinderzuschl_eink_regel_m_bg
        See :func:`kinderzuschl_eink_regel_m_bg`.
    kinderzuschl_kost_unterk_m_bg
        See :func:`kinderzuschl_kost_unterk_m_bg`.

    Returns
    -------

    """
    return kinderzuschl_eink_regel_m_bg + kinderzuschl_kost_unterk_m_bg


@dates_active(end="2019-06-30")
def kinderzuschl_eink_max_m_bg(
    kinderzuschl_eink_relev_m_bg: float,
    _kinderzuschl_anz_kinder_anspruch_bg: int,
    kinderzuschl_params: dict,
) -> float:
    """Calculate maximum income to be eligible for additional child benefit
    (Kinderzuschlag).

    There is a maximum income threshold, depending on the need, plus the potential kiz
    receipt (§6a (1) Nr. 3 BKGG).

    Parameters
    ----------
    kinderzuschl_eink_relev_m_bg
        See :func:`kinderzuschl_eink_relev_m_bg`.
    _kinderzuschl_anz_kinder_anspruch_bg
        See :func:`_kinderzuschl_anz_kinder_anspruch_bg`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    out = (
        kinderzuschl_eink_relev_m_bg
        + kinderzuschl_params["maximum"] * _kinderzuschl_anz_kinder_anspruch_bg
    )

    kindersofortzuschl = kinderzuschl_params.get("kindersofortzuschl", None)
    if not kindersofortzuschl:
        kindersofortzuschl = 0
    out += kindersofortzuschl * _kinderzuschl_anz_kinder_anspruch_bg

    return out


def kinderzuschl_eink_min_m_bg(
    anz_kinder_bg: int,
    alleinerz_bg: bool,
    kinderzuschl_params: dict,
) -> float:
    """Calculate minimal claim of child benefit (kinderzuschlag).

    Min income to be eligible for KIZ (different for singles and couples) (§6a (1) Nr. 2
    BKGG).

    Parameters
    ----------
    anz_kinder_hh
        See basic input variable :ref:`anz_kinder_hh <anz_kinder_hh>`.
    alleinerz_hh
        See basic input variable :ref:`alleinerz_hh <alleinerz_hh>`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    if anz_kinder_bg == 0:
        out = 0.0
    elif alleinerz_bg:
        out = kinderzuschl_params["min_eink_alleinerz"]
    else:
        out = kinderzuschl_params["min_eink_paare"]

    return out


def kinderzuschl_kindereink_abzug_m(  # noqa: PLR0913
    kindergeld_anspruch: bool,
    bruttolohn_m: float,
    kind_unterh_erhalt_m: float,
    unterhaltsvors_m: float,
    arbeitsl_geld_2_eink_anr_frei_m: float,
    kinderzuschl_params: dict,
) -> float:
    """Child benefit after children income for each eligible child is considered.

    # ToDo: consider self-employment income of the child.

    (§6a (3) S.3 BKGG)

    Parameters
    ----------
    kindergeld_anspruch
        See :func:`kindergeld_anspruch`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    kind_unterh_erhalt_m
        See basic input variable :ref:`kind_unterh_erhalt_m <kind_unterh_erhalt_m>`.
    unterhaltsvors_m
        See :func:`unterhaltsvors_m`.
    arbeitsl_geld_2_eink_anr_frei_m
        See :func:`arbeitsl_geld_2_eink_anr_frei_m`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    out = kindergeld_anspruch * (
        kinderzuschl_params["maximum"]
        - kinderzuschl_params["entzugsrate_kind"]
        * (
            bruttolohn_m
            + kind_unterh_erhalt_m
            + unterhaltsvors_m
            - arbeitsl_geld_2_eink_anr_frei_m
        )
    )

    return max(out, 0.0)


def kinderzuschl_eink_anrechn_m_bg(
    kinderzuschl_eink_eltern_m_bg: float,
    kinderzuschl_eink_relev_m_bg: float,
    kinderzuschl_params: dict,
) -> float:
    """Calculate parental income subtracted from child benefit.

    (§6a (6) S. 3 BKGG)

    Parameters
    ----------
    kinderzuschl_eink_eltern_m_bg
        See :func:`kinderzuschl_eink_eltern_m_bg`.
    kinderzuschl_eink_relev_m_bg
        See :func:`kinderzuschl_eink_relev_m_bg`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    out = kinderzuschl_params["entzugsrate_eltern"] * (
        kinderzuschl_eink_eltern_m_bg - kinderzuschl_eink_relev_m_bg
    )

    return max(out, 0.0)
