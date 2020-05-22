import pandas as pd

from gettsim.benefits.wohngeld import wg
from gettsim.dynamic_function_generation import create_function
from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.tests.test_wohngeld import OUT_COLS


def wohngeld_basis_hh(
    hh_id,
    tu_id,
    p_id,
    tu_vorstand,
    kind,
    kaltmiete_m,
    heizkost_m,
    alleinerziehend,
    alter,
    immobilie_baujahr,
    kindergeld_anspruch,
    mietstufe,
    bruttolohn_m,
    ges_rente_m,
    _ertragsanteil,
    elterngeld_m,
    arbeitsl_geld_m,
    sonstig_eink_m,
    unterhaltsvors_m,
    brutto_eink_1,
    brutto_eink_4,
    brutto_eink_5,
    brutto_eink_6,
    eink_st_m,
    rentenv_beit_m,
    ges_krankenv_beit_m,
    behinderungsgrad,
    jahr,
    _st_rente_per_tu,
    arbeitsl_geld_m_per_tu,
    sonstig_eink_m_per_tu,
    brutto_eink_1_per_tu,
    brutto_eink_4_per_tu,
    brutto_eink_5_per_tu,
    brutto_eink_6_per_tu,
    eink_st_m_per_tu,
    rentenv_beit_m_per_tu,
    ges_krankenv_beit_m_per_tu,
    unterhaltsvors_m_per_tu,
    elterngeld_m_per_tu,
    _wohngeld_abzüge,
    _wohngeld_brutto_eink,
    _wohngeld_sonstiges_eink,
    _anzahl_kinder_unter_11_per_tu,
    _wohngeld_eink_abzüge,
    _wohngeld_eink,
    _wohngeld_min_miete,
    wohngeld_params,
):

    df = pd.concat(
        [
            hh_id,
            tu_id,
            p_id,
            tu_vorstand,
            kind,
            kaltmiete_m,
            heizkost_m,
            alleinerziehend,
            alter,
            immobilie_baujahr,
            kindergeld_anspruch,
            mietstufe,
            bruttolohn_m,
            ges_rente_m,
            _ertragsanteil,
            elterngeld_m,
            arbeitsl_geld_m,
            sonstig_eink_m,
            unterhaltsvors_m,
            brutto_eink_1,
            brutto_eink_4,
            brutto_eink_5,
            brutto_eink_6,
            eink_st_m,
            rentenv_beit_m,
            ges_krankenv_beit_m,
            behinderungsgrad,
            jahr,
            _st_rente_per_tu,
            arbeitsl_geld_m_per_tu,
            sonstig_eink_m_per_tu,
            brutto_eink_1_per_tu,
            brutto_eink_4_per_tu,
            brutto_eink_5_per_tu,
            brutto_eink_6_per_tu,
            eink_st_m_per_tu,
            rentenv_beit_m_per_tu,
            ges_krankenv_beit_m_per_tu,
            unterhaltsvors_m_per_tu,
            elterngeld_m_per_tu,
            _wohngeld_abzüge,
            _wohngeld_brutto_eink,
            _wohngeld_sonstiges_eink,
            _anzahl_kinder_unter_11_per_tu,
            _wohngeld_eink_abzüge,
            _wohngeld_eink,
            _wohngeld_min_miete,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=wg,
        level=["hh_id"],
        in_cols=df.columns.tolist(),
        out_cols=OUT_COLS,
        func_kwargs={"params": wohngeld_params},
    )

    return df["wohngeld_basis_hh"]


def _st_rente_per_tu(tu_id, _ertragsanteil, ges_rente_m):
    _st_rente = _ertragsanteil * ges_rente_m
    return _st_rente.groupby(tu_id).transform("sum")


def _groupby_sum(group, variable):
    """TODO: Rewrite to simple sum."""
    return variable.groupby(group).transform("sum")


for inc in [
    "arbeitsl_geld_m",
    "sonstig_eink_m",
    "brutto_eink_1",
    "brutto_eink_4",
    "brutto_eink_5",
    "brutto_eink_6",
    "eink_st_m",
    "rentenv_beit_m",
    "ges_krankenv_beit_m",
    "unterhaltsvors_m",
    "elterngeld_m",
]:
    __new_function = create_function(
        _groupby_sum, inc + "_per_tu", {"group": "tu_id", "variable": inc}
    )

    exec(f"{inc}_per_tu = __new_function")


def _wohngeld_abzüge(
    eink_st_m_per_tu, rentenv_beit_m_per_tu, ges_krankenv_beit_m_per_tu, wohngeld_params
):
    abzug_stufen = (
        (eink_st_m_per_tu > 0) * 1
        + (rentenv_beit_m_per_tu > 0)
        + (ges_krankenv_beit_m_per_tu > 0)
    )

    return abzug_stufen.replace(wohngeld_params["abzug_stufen"])


def _wohngeld_brutto_eink(
    brutto_eink_1_per_tu,
    brutto_eink_4_per_tu,
    brutto_eink_5_per_tu,
    brutto_eink_6_per_tu,
):
    return (
        brutto_eink_1_per_tu.clip(lower=0)
        + brutto_eink_4_per_tu.clip(lower=0)
        + brutto_eink_5_per_tu.clip(lower=0)
        + brutto_eink_6_per_tu.clip(lower=0)
    ) / 12


def _wohngeld_sonstiges_eink(
    arbeitsl_geld_m_per_tu,
    sonstig_eink_m_per_tu,
    _st_rente_per_tu,
    unterhaltsvors_m_per_tu,
    elterngeld_m_per_tu,
):
    return (
        arbeitsl_geld_m_per_tu
        + sonstig_eink_m_per_tu
        + _st_rente_per_tu
        + unterhaltsvors_m_per_tu
        + elterngeld_m_per_tu
    )


def _anzahl_kinder_unter_11_per_tu(tu_id, alter):
    return (alter < 11).groupby(tu_id).transform("sum")


def _wohngeld_eink_abzüge(
    _wohngeld_eink_abzüge_bis_2015, _wohngeld_eink_abzüge_ab_2016
):
    """
    Calculate deductions for handicapped, single parents and children who are working.

    """
    return (
        _wohngeld_eink_abzüge_bis_2015
        if _wohngeld_eink_abzüge_ab_2016.empty
        else _wohngeld_eink_abzüge_ab_2016
    )


def _wohngeld_eink_abzüge_bis_2015(
    jahr,
    bruttolohn_m,
    kindergeld_anspruch,
    behinderungsgrad,
    alleinerziehend,
    kind,
    _anzahl_kinder_unter_11_per_tu,
    wohngeld_params,
):
    bis_2015 = jahr <= 2015

    if bis_2015.any():
        workingchild = (bruttolohn_m > 0) & kindergeld_anspruch

        abzüge = (
            (behinderungsgrad > 80) * wohngeld_params["freib_behinderung"]["ab80"]
            + ((1 <= behinderungsgrad) & (behinderungsgrad <= 80))
            * wohngeld_params["freib_behinderung"]["u80"]
            + (
                workingchild
                * bruttolohn_m.clip(
                    lower=None, upper=wohngeld_params["freib_kinder"][24]
                )
            )
            + (
                (alleinerziehend & ~kind)
                * _anzahl_kinder_unter_11_per_tu
                * wohngeld_params["freib_kinder"][12]
            )
        )

    else:
        abzüge = pd.Series(dtype=float)

    return abzüge


def _wohngeld_eink_abzüge_ab_2016(
    jahr,
    bruttolohn_m,
    kindergeld_anspruch,
    behinderungsgrad,
    alleinerziehend,
    kind,
    wohngeld_params,
):
    ab_2016 = 2016 <= jahr

    if ab_2016.any():
        workingchild = (bruttolohn_m > 0) & kindergeld_anspruch

        abzüge = (
            (behinderungsgrad > 0) * wohngeld_params["freib_behinderung"]
            + workingchild
            * bruttolohn_m.clip(lower=0, upper=wohngeld_params["freib_kinder"][24])
            + alleinerziehend * wohngeld_params["freib_kinder"][12] * ~kind
        )
    else:
        abzüge = pd.Series(dtype=float)

    return abzüge


def _wohngeld_eink(
    tu_id,
    haushalts_größe,
    _wohngeld_eink_abzüge,
    _wohngeld_abzüge,
    _wohngeld_brutto_eink,
    _wohngeld_sonstiges_eink,
    wohngeld_params,
):
    _wohngeld_eink_abzüge_per_tu = _wohngeld_eink_abzüge.groupby(tu_id).transform("sum")

    vorläufiges_eink = (1 - _wohngeld_abzüge) * (
        _wohngeld_brutto_eink + _wohngeld_sonstiges_eink - _wohngeld_eink_abzüge_per_tu
    )

    unteres_eink = [
        wohngeld_params["min_eink"][hh_size]
        if hh_size < 12
        else wohngeld_params["min_eink"][12]
        for hh_size in haushalts_größe
    ]

    return vorläufiges_eink.clip(lower=unteres_eink)


def haushalts_größe(hh_id):
    return hh_id.groupby(hh_id).transform("size")


def _wohngeld_min_miete(haushalts_größe, wohngeld_params):
    data = [
        wohngeld_params["min_miete"][hh_size]
        if hh_size < 12
        else wohngeld_params["min_miete"][12]
        for hh_size in haushalts_größe
    ]
    return pd.Series(index=haushalts_größe.index, data=data)
