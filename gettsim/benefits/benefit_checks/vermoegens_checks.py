import numpy as np


def _regelbedarf_m_vermögens_check_hh(regelbedarf_m_hh, unter_vermögens_freibetrag_hh):
    """Set regelbedarf_m to zero if it exceeds the wealth exemption.

    If wealth exceeds the exemption, set benefits to zero (since ALG2 is not yet
    calculated, just set the need to zero)

    Parameters
    ----------
    regelbedarf_m_hh
    unter_vermögens_freibetrag_hh

    Returns
    -------

    """
    regelbedarf_m_hh.loc[~unter_vermögens_freibetrag_hh] = 0
    return regelbedarf_m_hh


def kinderzuschlag_vermögens_check_hh(
    _kinderzuschlag_m_vorläufig_hh, unter_vermögens_freibetrag_hh
):
    """Set kinderzuschlag_temp to zero if it exceeds the wealth exemption.

    Parameters
    ----------
    _kinderzuschlag_m_vorläufig_hh
    unter_vermögens_freibetrag_hh

    Returns
    -------

    """

    _kinderzuschlag_m_vorläufig_hh.loc[~unter_vermögens_freibetrag_hh] = 0
    return _kinderzuschlag_m_vorläufig_hh


def wohngeld_vermögens_check_hh(wohngeld_basis_hh, vermögen_hh, haushaltsgröße_hh):
    """Calculate a lump sum payment for wohngeld

    The payment depends on the wealth of the household and the number of household
    members.

    60.000 € pro Haushalt + 30.000 € für jedes Mitglied (Verwaltungsvorschrift)

    TODO: Need to write numbers to params.

    Parameters
    ----------
    wohngeld_basis_hh
    vermögen_hh
    haushaltsgröße_hh

    Returns
    -------

    """
    condition = vermögen_hh <= (60_000 + (30_000 * (haushaltsgröße_hh - 1)))
    wohngeld_basis_hh.loc[~condition] = 0
    return wohngeld_basis_hh


def unter_vermögens_freibetrag_hh(vermögen_hh, freibetrag_vermögen_hh):
    """

    Parameters
    ----------
    vermögen_hh
    freibetrag_vermögen_hh

    Returns
    -------

    """
    return vermögen_hh <= freibetrag_vermögen_hh


def freibetrag_vermögen_anspruch_hh(
    hh_id, kind, alter, geburtsjahr, arbeitsl_geld_2_params
):
    """Calculate exemptions based on individuals age.

    Parameters
    ----------
    hh_id
    kind
    alter
    geburtsjahr
    arbeitsl_geld_2_params

    Returns
    -------

    """

    out = alter * 0
    out.loc[geburtsjahr < 1948] = (
        arbeitsl_geld_2_params["vermögensfreibetrag"]["vor_1948"]
        * alter.loc[geburtsjahr < 1948]
    )
    out.loc[(1948 <= geburtsjahr) & ~kind] = (
        arbeitsl_geld_2_params["vermögensfreibetrag"]["standard"]
        * alter.loc[(1948 <= geburtsjahr) & ~kind]
    )

    return out.groupby(hh_id).sum()


def max_freibetrag_vermögen_hh(hh_id, geburtsjahr, kind, arbeitsl_geld_2_params):
    """

    Parameters
    ----------
    hh_id
    geburtsjahr
    kind
    arbeitsl_geld_2_params

    Returns
    -------

    """
    conditions = [
        geburtsjahr < 1957,
        (1958 <= geburtsjahr) & (geburtsjahr <= 1963),
        (1964 <= geburtsjahr) & ~kind,
        True,
    ]

    choices = [
        arbeitsl_geld_2_params["vermögensfreibetrag"]["1948_bis_1957"],
        arbeitsl_geld_2_params["vermögensfreibetrag"]["1958_bis_1963"],
        arbeitsl_geld_2_params["vermögensfreibetrag"]["nach_1963"],
        0,
    ]

    data = np.select(conditions, choices)
    out = geburtsjahr * 0.0 + data

    return out.groupby(hh_id).sum()


def freibetrag_vermögen_hh(
    freibetrag_vermögen_anspruch_hh,
    anz_minderj_hh,
    haushaltsgröße_hh,
    max_freibetrag_vermögen_hh,
    arbeitsl_geld_2_params,
):
    """

    Parameters
    ----------
    freibetrag_vermögen_anspruch_hh
    anz_minderj_hh
    haushaltsgröße_hh
    max_freibetrag_vermögen_hh
    arbeitsl_geld_2_params

    Returns
    -------

    """
    out = (
        freibetrag_vermögen_anspruch_hh
        + anz_minderj_hh * arbeitsl_geld_2_params["vermögensfreibetrag"]["kind"]
        + (haushaltsgröße_hh - anz_minderj_hh)
        * arbeitsl_geld_2_params["vermögensfreibetrag"]["ausstattung"]
    ).clip(upper=max_freibetrag_vermögen_hh)
    return out
