import pandas as pd

from gettsim.pre_processing.apply_tax_funcs import apply_tax_transfer_func
from gettsim.taxes.kindergeld import kindergeld


def _kindergeld_anspruch_nach_stunden(
    alter, in_ausbildung, arbeitsstunden_w, kindergeld_params
):
    """
    Nowadays, kids must not work more than 20 hour
    returns a boolean variable whether a specific person is a child eligible for
    child benefit

    Parameters
    ----------
    alter
    in_ausbildung
    arbeitsstunden_w
    kindergeld_params

    Returns
    -------

    """
    out = alter <= 18
    out.loc[
        (alter.between(19, kindergeld_params["kindergeld_hoechstalter"]))
        & in_ausbildung
        & (arbeitsstunden_w <= kindergeld_params["kindergeld_stundengrenze"])
    ] = True

    return out.rename("_kindergeld_anspruch")


def _kindergeld_anspruch_nach_lohn(
    alter, in_ausbildung, bruttolohn_m, kindergeld_params
):
    """
    Before 2011, there was an income ceiling for children
    returns a boolean variable whether a specific person is a child eligible for
    child benefit

    Parameters
    ----------
    alter
    kindergeld_params
    in_ausbildung
    bruttolohn_m

    Returns
    -------

    """
    out = alter <= 18
    out.loc[
        (alter.between(19, kindergeld_params["kindergeld_hoechstalter"]))
        & in_ausbildung
        & (bruttolohn_m <= kindergeld_params["kindergeld_einkommensgrenze"] / 12)
    ] = True

    return out.rename("_kindergeld_anspruch")


def kindergeld_m_basis(
    hh_id,
    tu_id,
    p_id,
    alter,
    arbeitsstunden_w,
    in_ausbildung,
    bruttolohn_m,
    _kindergeld_anspruch,
    kindergeld_params,
):

    df = pd.concat(
        [
            hh_id,
            tu_id,
            p_id,
            alter,
            arbeitsstunden_w,
            in_ausbildung,
            bruttolohn_m,
            _kindergeld_anspruch,
        ],
        axis=1,
    )

    df = apply_tax_transfer_func(
        df,
        tax_func=kindergeld,
        level=["hh_id", "tu_id"],
        in_cols=df.columns.to_list(),
        out_cols=["kindergeld_m_basis"],
        func_kwargs={"params": kindergeld_params},
    )

    return df["kindergeld_m_basis"]


def kindergeld_m_tu_basis(kindergeld_m_basis, tu_id):
    """

    Parameters
    ----------
    kindergeld_m_basis
    tu_id

    Returns
    -------

    """
    out = kindergeld_m_basis.groupby(tu_id).apply(sum)
    return out.rename("kindergeld_m_tu_basis")
