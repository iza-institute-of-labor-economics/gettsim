from gettsim.typing import BoolSeries
from gettsim.typing import FloatSeries
from gettsim.typing import IntSeries

aggregation_kinderzuschl_eink = {
    "_kinderzuschl_anz_kinder_anspruch_hh": {
        "source_col": "kindergeld_anspruch",
        "aggr": "sum",
    },
}


def kinderzuschl_eink_regel_m_hh_bis_2010(
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh: FloatSeries,
    anz_erwachsene_hh: IntSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate income relevant for calculation of child benefit until 2010.

    # ToDo: Why alleinerziehend Mehrbedarf for anz_erwachsene_hh == 2, but not
    # ToDO: for anz_erwachsene_hh > 2


    Parameters
    ----------
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh`.
    anz_erwachsene_hh
        See :func:`anz_erwachsene_hh`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    if anz_erwachsene_hh == 1:
        out = arbeitsl_geld_2_params["regelsatz"] * (
            1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
        )
    elif anz_erwachsene_hh == 2:
        out = (
            arbeitsl_geld_2_params["regelsatz"]
            * arbeitsl_geld_2_params["anteil_regelsatz"]["zwei_erwachsene"]
            * (2 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh)
        )
    elif anz_erwachsene_hh > 2:
        out = (
            arbeitsl_geld_2_params["regelsatz"]
            * arbeitsl_geld_2_params["anteil_regelsatz"]["weitere_erwachsene"]
            * anz_erwachsene_hh
        )

    return out


def kinderzuschl_eink_regel_m_hh_ab_2011(
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh: FloatSeries,
    anz_erwachsene_hh: IntSeries,
    arbeitsl_geld_2_params: dict,
) -> FloatSeries:
    """Calculate income relevant for calculation of child benefit since 2011.

    Parameters
    ----------
    _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
        See :func:`_arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh`.
    anz_erwachsene_hh
        See :func:`anz_erwachsene_hh`.
    arbeitsl_geld_2_params
        See params documentation :ref:`arbeitsl_geld_2_params <arbeitsl_geld_2_params>`.

    Returns
    -------

    """
    if anz_erwachsene_hh == 1:
        out = arbeitsl_geld_2_params["regelsatz"][1] * (
            1 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
        )
    elif anz_erwachsene_hh == 2:
        out = arbeitsl_geld_2_params["regelsatz"][2] * (
            2 + _arbeitsl_geld_2_alleinerz_mehrbedarf_m_hh
        )
    elif anz_erwachsene_hh > 2:
        out = arbeitsl_geld_2_params["regelsatz"][3] * anz_erwachsene_hh

    return out


def kinderzuschl_eink_relev_m(
    kinderzuschl_eink_regel_m_hh: FloatSeries, kinderzuschl_kost_unterk_m: FloatSeries
) -> FloatSeries:
    """Aggregate relevant income and rental costs.

    # ToDo: Find out if it should be calculated on tu or hh level
    Parameters
    ----------
    kinderzuschl_eink_regel_m_hh
        See :func:`kinderzuschl_eink_regel_m_hh`.
    kinderzuschl_kost_unterk_m
        See :func:`kinderzuschl_kost_unterk_m`.

    Returns
    -------

    """
    return kinderzuschl_eink_regel_m_hh + kinderzuschl_kost_unterk_m


def kinderzuschl_eink_max_m_hh(
    kinderzuschl_eink_relev_m: FloatSeries,
    _kinderzuschl_anz_kinder_anspruch_hh: IntSeries,
    kinderzuschl_params: dict,
) -> FloatSeries:
    """Calculate maximum income to be eligible for additional
       child benefit (Kinderzuschlag).

    There is a maximum income threshold, depending on the need, plus the potential kiz
    receipt (§6a (1) Nr. 3 BKGG).

    Parameters
    ----------
    kinderzuschl_eink_relev_m
        See :func:`kinderzuschl_eink_relev_m`.
    _kinderzuschl_anz_kinder_anspruch_hh
        See :func:`_kinderzuschl_anz_kinder_anspruch_hh`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    out = (
        kinderzuschl_eink_relev_m
        + kinderzuschl_params["maximum"] * _kinderzuschl_anz_kinder_anspruch_hh
    )

    return out


def kinderzuschl_eink_min_m_hh(
    anz_kinder_hh: BoolSeries, alleinerz_hh: BoolSeries, kinderzuschl_params: dict,
) -> FloatSeries:
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
    if anz_kinder_hh == 0:
        out = 0.0
    elif alleinerz_hh:
        out = kinderzuschl_params["min_eink_alleinerz"]
    else:
        out = kinderzuschl_params["min_eink_paare"]

    return out


def kinderzuschl_kindereink_abzug_m(
    kindergeld_anspruch: BoolSeries,
    bruttolohn_m: FloatSeries,
    unterhaltsvors_m: FloatSeries,
    kinderzuschl_params: dict,
) -> FloatSeries:
    """Child benefit after children income for each eligible child is considered.

    (§6a (3) S.3 BKGG)

    Parameters
    ----------
    kindergeld_anspruch
        See :func:`kindergeld_anspruch`.
    bruttolohn_m
        See basic input variable :ref:`bruttolohn_m <bruttolohn_m>`.
    unterhaltsvors_m
        See :func:`unterhaltsvors_m`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    out = kindergeld_anspruch * (
        kinderzuschl_params["maximum"]
        - kinderzuschl_params["entzugsrate_kind"] * (bruttolohn_m + unterhaltsvors_m)
    )

    return max(out, 0.0)


def kinderzuschl_eink_anrechn_m(
    arbeitsl_geld_2_eink_m_hh: FloatSeries,
    kinderzuschl_eink_relev_m: FloatSeries,
    kinderzuschl_params: dict,
) -> FloatSeries:
    """Calculate parental income subtracted from child benefit.

    (§6a (6) S. 3 BKGG)

    Parameters
    ----------
    arbeitsl_geld_2_eink_m_hh
        See :func:`arbeitsl_geld_2_eink_m_hh`.
    kinderzuschl_eink_relev_m
        See :func:`kinderzuschl_eink_relev_m`.
    kinderzuschl_params
        See params documentation :ref:`kinderzuschl_params <kinderzuschl_params>`.

    Returns
    -------

    """
    out = kinderzuschl_params["entzugsrate_eltern"] * (
        arbeitsl_geld_2_eink_m_hh - kinderzuschl_eink_relev_m
    )

    return max(out, 0.0)
