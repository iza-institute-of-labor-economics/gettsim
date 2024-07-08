from _gettsim.shared import policy_info

aggregate_by_group_benefit_checks = {
    "alle_beantragt_wohngeld_kinderzuschl_statt_arbeitsl_geld_2_fg": {
        "source_col": "beantragt_wohngeld_kinderzuschl_statt_arbeitsl_geld_2_endogen",
        "aggr": "all",
    },
}


def beantragt_wohngeld_kinderzuschl_statt_arbeitsl_geld_2_endogen(
    wohngeld_kinderzuschl_vorrangig_bg: bool,
    wohngeld_kinderzuschl_günstiger: bool,
) -> bool:
    """Individual receives Wohngeld and Kinderzuschlag instead of Arbeitslosengeld II.

    Calculated endogenously.

    Parameters
    ----------
    wohngeld_vorrangig_bg
        See :func:`wohngeld_vorrangig_bg`.
    wohngeld_kinderzuschl_günstiger
        See :func:`wohngeld_kinderzuschl_günstiger`.

    Returns
    -------

    """
    return wohngeld_kinderzuschl_vorrangig_bg or wohngeld_kinderzuschl_günstiger


def beantragt_wohngeld_kinderzuschl_statt_arbeitsl_geld_2(
    arbeitsl_geld_2_kind_und_eigenbedarf_gedeckt: bool,
) -> bool:
    """Individual receives Wohngeld and Kinderzuschlag instead of Arbeitslosengeld II.

    If not specified by the user, this function assumes that children who cover their
    SGB II needs are not in the parental Bedarfsgemeinschaft. In this case, this
    function is used as a candidate specification for the Günstigerprüfung.

    It returns `False` for all parents (independent of covered SGB II needs).

    Parameters
    ----------
    arbeitsl_geld_2_kind_und_eigenbedarf_gedeckt
        See :func:`arbeitsl_geld_2_kind_und_eigenbedarf_gedeckt`.

    Returns
    -------

    """
    return arbeitsl_geld_2_kind_und_eigenbedarf_gedeckt


def wohngeld_kinderzuschl_vorrangig_bg(  # noqa: PLR0913
    arbeitsl_geld_2_nettoeink_vor_abzug_freibetrag_m_bg: float,
    arbeitsl_geld_2_regelbedarf_m_bg: float,
    kindergeld_zur_bedarfsdeckung_m_bg: float,
    kind_unterh_erhalt_m_bg: float,
    unterhaltsvors_m_bg: float,
    kindergeldübertrag_m_bg: float,
) -> bool:
    """Wohngeld and Kinderzuschlag have priority over Arbeitslosengeld II / Bürgergeld.

    Housing benefit has priority if the sum of housing benefit and income covers the
    needs according to SGB II of the Bedarfsgemeinschaft.

    Parameters
    ----------
    arbeitsl_geld_2_nettoeink_vor_abzug_freibetrag_m_bg
        See :func:`arbeitsl_geld_2_nettoeink_vor_abzug_freibetrag_m_bg`.
    arbeitsl_geld_2_regelbedarf_m_bg
        See :func:`arbeitsl_geld_2_regelbedarf_m_bg`.
    kindergeld_zur_bedarfsdeckung_m_bg
        See :func:`kindergeld_zur_bedarfsdeckung_m_bg`.
    kind_unterh_erhalt_m_bg
        See :func:`kind_unterh_erhalt_m_bg`.
    unterhaltsvors_m_bg
        See :func:`unterhaltsvors_m_bg`.
    kindergeldübertrag_m_bg
        See :func:`kindergeldübertrag_m_bg`.

    Returns
    -------

    """
    return (
        arbeitsl_geld_2_nettoeink_vor_abzug_freibetrag_m_bg
        + kindergeld_zur_bedarfsdeckung_m_bg
        + kind_unterh_erhalt_m_bg
        + unterhaltsvors_m_bg
        + kindergeldübertrag_m_bg
        >= arbeitsl_geld_2_regelbedarf_m_bg
    )


def wohngeld_kinderzuschl_günstiger(
    kinder_mit_gedecktem_bedarf_in_fg: bool,
    gesamte_fg_in_einer_bg_günstiger: bool,
    arbeitsl_geld_2_kind_und_eigenbedarf_gedeckt: bool,
    wohngeld_kinderzuschl_größer_als_arbeitsl_geld_2_fg: bool,
) -> bool:
    """It is more favorable to receive Wohngeld and Kinderzuschlag instead of
    Arbeitslosengeld II / Bürgergeld.

    If this is the case, individuals can choose to receive Wohngeld and Kinderzuschlag
    instead of Arbeitslosengeld II / Bürgergeld even if the transfers don't have
    priority over Arbeitslosengeld II / Bürgergeld (eingeschränktes Wahlrecht).

    Parameters
    ----------
    kinder_mit_gedecktem_bedarf_in_fg
        See :func:`kinder_mit_gedecktem_bedarf_in_fg`.
    gesamte_fg_in_einer_bg_günstiger
        See :func:`gesamte_fg_in_einer_bg_günstiger`.
    arbeitsl_geld_2_kind_und_eigenbedarf_gedeckt
        See :func:`arbeitsl_geld_2_kind_und_eigenbedarf_gedeckt`.
    wohngeld_kinderzuschl_größer_als_arbeitsl_geld_2_fg
        See :func:`wohngeld_kinderzuschl_größer_als_arbeitsl_geld_2_fg`.

    Returns
    -------

    """
    # Children who cover their needs are in BG with parens -> FG receives Wohngeld
    if gesamte_fg_in_einer_bg_günstiger and kinder_mit_gedecktem_bedarf_in_fg:
        out = True
    # Children who cover their needs are not in parental BG -> Children who cover their
    # needs receive Wohngeld, everyone else Arbeitslosengeld II / Bürgergeld
    elif (not gesamte_fg_in_einer_bg_günstiger) and kinder_mit_gedecktem_bedarf_in_fg:
        out = arbeitsl_geld_2_kind_und_eigenbedarf_gedeckt
    # There are no children that cover their needs -> Simple favorability check on FG
    # level
    elif not kinder_mit_gedecktem_bedarf_in_fg:
        out = wohngeld_kinderzuschl_größer_als_arbeitsl_geld_2_fg

    return out


def gesamte_fg_in_einer_bg_günstiger(
    _transfereinkommen_gleiche_bg_eltern_kinder_fg: float,
    _transfereinkommen_getrennte_bg_eltern_kinder_fg: float,
    kinder_mit_gedecktem_bedarf_in_fg: bool,
) -> bool:
    """It is more favorable to have the whole Familiengemeinschaft in one
    Bedarfsgemeinschaft.

    Parameters
    ----------
    _transfereinkommen_gleiche_bg_eltern_kinder_fg
        See :func:`_transfereinkommen_gleiche_bg_eltern_kinder_fg`.
    _transfereinkommen_getrennte_bg_eltern_kinder_fg
        See :func:`_transfereinkommen_getrennte_bg_eltern_kinder_fg`..

    Returns
    -------

    """
    return (
        (
            _transfereinkommen_gleiche_bg_eltern_kinder_fg
            >= _transfereinkommen_getrennte_bg_eltern_kinder_fg
        )
        if kinder_mit_gedecktem_bedarf_in_fg
        else True
    )


def wohngeld_kinderzuschl_größer_als_arbeitsl_geld_2_fg(
    wohngeld_anspruchshöhe_m_fg: float,
    kinderzuschlag_anspruchshöhe_m_fg: float,
    arbeitsl_geld_2_anspruchshöhe_m_fg: float,
) -> bool:
    """Wohngeld and Kinderzuschlag are higher than Arbeitslosengeld II / Bürgergeld.

    Parameters
    ----------
    wohngeld_anspruchshöhe_m_fg
        See :func:`wohngeld_anspruchshöhe_m_fg`.
    kinderzuschlag_anspruchshöhe_m_fg
        See :func:`kinderzuschlag_anspruchshöhe_m_fg`.
    arbeitsl_geld_2_anspruchshöhe_m_fg
        See :func:`arbeitsl_geld_2_anspruchshöhe_m_fg`.

    Returns
    -------

    """
    return (
        wohngeld_anspruchshöhe_m_fg + kinderzuschlag_anspruchshöhe_m_fg
        >= arbeitsl_geld_2_anspruchshöhe_m_fg
    )


def _transfereinkommen_gleiche_bg_eltern_kinder_fg(
    wohngeld_anspruchshöhe_m_fg: float,
    kinderzuschlag_anspruchshöhe_m_fg: float,
) -> float:
    """Transfers if children with needs covered are part of the Familiengemeinschaft and
    whole Familiengemeinschaft forms a Bedarfsgemeinschaft.

    Parameters
    ----------
    wohngeld_anspruchshöhe_m_fg
        See :func:`wohngeld_anspruchshöhe_m_fg`.
    kinderzuschlag_anspruchshöhe_m_fg
        See :func:`kinderzuschlag_anspruchshöhe_m_fg`.

    Returns
    -------

    """
    return wohngeld_anspruchshöhe_m_fg + kinderzuschlag_anspruchshöhe_m_fg


@policy_info(skip_vectorization=True)
def _transfereinkommen_getrennte_bg_eltern_kinder(
    wohngeld_anspruchshöhe_m_wthh: float,
    kinderzuschl_anspruchshöhe_m_bg: float,
    arbeitsl_geld_2_anspruchshöhe_m_bg: float,
    anz_personen_wthh: int,
    anz_personen_bg: int,
) -> float:
    """Transfers if children with needs covered are part of the Familiengemeinschaft not
    part of the parental Bedarfsgemeinschaft.

    Parameters
    ----------
    wohngeld_anspruchshöhe_m_wthh
        See :func:`wohngeld_anspruchshöhe_m_wthh`.
    kinderzuschl_anspruchshöhe_m_bg
        See :func:`kinderzuschl_anspruchshöhe_m_bg`.
    arbeitsl_geld_2_anspruchshöhe_m_bg
        See :func:`arbeitsl_geld_2_anspruchshöhe_m_bg`.

    Returns
    -------

    """
    wohngeld_individual = wohngeld_anspruchshöhe_m_wthh / anz_personen_wthh
    kinderzuschlag_individual = kinderzuschl_anspruchshöhe_m_bg / anz_personen_bg
    alg2_individual = arbeitsl_geld_2_anspruchshöhe_m_bg / anz_personen_bg
    return wohngeld_individual + kinderzuschlag_individual + alg2_individual
