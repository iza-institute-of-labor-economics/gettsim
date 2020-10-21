import datetime

import numpy as np
import pandas as pd

from gettsim.policy_environment import _load_parameter_group_from_yaml


def create_other_hh_members(
    df, hh_typ, alter, alter_kind_1, alter_kind_2, doppelverdiener
):
    """
    duplicates information from the one person already created
    as often as needed.
    """
    new_df = df[df["hh_typ"] == hh_typ].copy()
    # Single: no additional person needed
    if hh_typ == "sing":
        return None
    # Single Parent one child
    if hh_typ == "sp1ch":
        new_df["kind"] = True
        new_df["alter"] = alter_kind_1
    # Single Parent two children
    if hh_typ == "sp2ch":
        new_df = new_df.append(new_df, ignore_index=True)
        new_df["kind"] = pd.Series([True, True])
        new_df["alter"] = pd.Series([alter_kind_1, alter_kind_2])
    if hh_typ == "coup1ch":
        new_df = new_df.append(new_df, ignore_index=True)
        new_df["kind"] = pd.Series([False, True])
        new_df["alter"] = pd.Series([alter, alter_kind_1])
    if hh_typ == "coup2ch":
        new_df = new_df.append([new_df] * 2, ignore_index=True)
        new_df["kind"] = pd.Series([False, True, True])
        new_df["alter"] = pd.Series([alter, alter_kind_1, alter_kind_2])

    # Make sure new household members are not heads
    new_df["tu_vorstand"] = False
    # Children are in education
    new_df["in_ausbildung"] = new_df["kind"]
    # children do not have earnings
    df.loc[df["kind"], "bruttolohn_m"] = 0
    # If single earner household, the partner is assigned zero wage as well
    if not doppelverdiener:
        df.loc[~df["kind"], "bruttolohn_m"] = 0
    return new_df


def gettsim_hypo_data(
    hh_typen=("sing", "sp1ch", "sp2ch", "coup", "coup1ch", "coup2ch"),
    bruttolohn=2000,
    alter=35,
    alter_kind_1=3,
    alter_kind_2=8,
    baujahr=1980,
    doppelverdiener=False,
    policy_year=datetime.datetime.now().year,
):
    """
    Creates a dataset with hypothetical household types,
    which can be used as input for gettsim

    hh_typen (tuple of str):
        Allowed Household Types:
        - 'sing' - Single, no kids
        - 'sp1ch' - Single Parent, one child
        - 'sp2ch' - Single Parent, two children
        - 'coup' - Couple, no kids
        - 'coup1ch' - Couple, one child
        - 'coup2ch' - Couple, two children

    bruttolohn (int):
        Gross monthly wage for the household head.

    alter, alter_kind_1, alter_kind_2 (int):
        Assumed age of adult(s) and first and second child

    baujahr (int):
        Construction year of building

    doppelverdiener (bool):
        whether or not both adults should be assigned income

    policy_year:
        the year from which the reference data are drawn.
    """
    # Check inputs
    for t in hh_typen:
        if t not in ["sing", "sp1ch", "sp2ch", "coup", "coup1ch", "coup2ch"]:
            raise ValueError(f"illegal household type: {t}")

    # initiate empty dataframe
    output_columns = [
        "tu_vorstand",
        "vermögen_hh",
        "alter",
        "selbstständig",
        "wohnort_ost",
        "hat_kinder",
        "bruttolohn_m",
        "eink_selbst_m",
        "ges_rente_m",
        "prv_krankenv",
        "prv_krankv_beit_m",
        "prv_rente_beit_m",
        "bruttolohn_vorj_m",
        "arbeitsl_lfdj_m",
        "arbeitsl_vorj_m",
        "arbeitsl_vor2j_m",
        "arbeitsstunden_w",
        "geburtsjahr",
        "entgeltpunkte",
        "kind",
        "rentner",
        "betreuungskost_m",
        "miete_unterstellt",
        "kapital_eink_m",
        "vermiet_eink_m",
        "kaltmiete_m",
        "heizkost_m",
        "jahr_renteneintr",
        "behinderungsgrad",
        "wohnfläche",
        "gem_veranlagt",
        "in_ausbildung",
        "alleinerziehend",
        "bewohnt_eigentum",
        "immobilie_baujahr",
        "sonstig_eink_m",
    ]

    df = pd.DataFrame(
        columns=output_columns, data=np.zeros((len(hh_typen), len(output_columns)))
    )

    # Some columns require boolean type. initiate them with False
    for c in [
        "selbstständig",
        "wohnort_ost",
        "hat_kinder",
        "kind",
        "rentner",
        "gem_veranlagt",
        "in_ausbildung",
        "alleinerziehend",
        "bewohnt_eigentum",
        "prv_krankenv",
    ]:
        df[c] = False

    # 'Custom' initializations
    df["tu_vorstand"] = True
    df["alter"] = alter
    df["immobilie_baujahr"] = baujahr
    for c in ["arbeitsl_lfdj_m", "arbeitsl_vorj_m", "arbeitsl_vor2j_m"]:
        df[c] = 12

    df["hh_typ"] = pd.Series(hh_typen)

    # Wohnfläche, Kaltmiete, Heizkosten are taken from official data
    bg_daten = _load_parameter_group_from_yaml(
        datetime.date(policy_year, 1, 1), "bedarfsgemeinschaften"
    )
    df["wohnfläche"] = df["hh_typ"].map(bg_daten["wohnfläche"])
    df["kaltmiete_m"] = df["hh_typ"].map(bg_daten["kaltmiete"])
    df["heizkost_m"] = df["hh_typ"].map(bg_daten["heizkosten"])

    df["bruttolohn_m"] = bruttolohn

    df = df.sort_values(by=["hh_typ", "bruttolohn_m"])

    df["hh_id"] = df.index
    df["tu_id"] = df.index

    # append entries for children and partner
    for hht in hh_typen:
        df = df.append(
            create_other_hh_members(
                df, hht, alter, alter_kind_1, alter_kind_2, doppelverdiener
            )
        )
    df["geburtsjahr"] = policy_year - df["alter"]
    df["jahr_renteneintr"] = df["geburtsjahr"] + 67

    df["hat_kinder"] = df["hh_typ"].str.contains("ch")

    df.loc[df["bruttolohn_m"] > 0, "arbeitsstunden_w"] = 38

    # All adults in couples are assumed to be married
    df.loc[(df["hh_typ"].str.contains("coup")) & (~df["kind"]), "gem_veranlagt"] = True
    df.loc[(df["hh_typ"].str.contains("sp")) & (~df["kind"]), "alleinerziehend"] = True

    df = df.sort_values(by=["hh_typ", "hh_id"])

    df = df.reset_index()
    df["p_id"] = df.index

    return df[["hh_id", "tu_id", "p_id", "hh_typ"] + output_columns]
