from _gettsim.shared import dates_active

aggregation_erziehungsgeld = {
    "bruttolohn_vorj_m_tu": {
        "source_col": "bruttolohn_vorj_m",
        "aggr": "cumsum",
    },
    "anz_kinder_mit_kindergeld_tu": {
        "source_col": "kindergeld_anspruch",
        "aggr": "sum",
    },
}

@dates_active(end="2006-12-31")
def erziehungsgeld_m(
        erziehungsgeld_params: dict,
        erziehungsgeld_anspruch: bool,
        erziehungsgeld_einkommen_relev: float,
        erziehungsgeld_einkommensgrenze: float,
        alter_monate_jüngstes_mitglied_hh: int,
) -> float:
    """
    Todo: People can decide whether they want the "regelsatz" for up to 24 month
          or a higher "budgetiertes Erziehungsgeld" for just 12 month
    """
    # if the income is higher than the threshold within the first 6 month there
    # is no erziehungsgeld claim at all
    if (erziehungsgeld_anspruch and 
        alter_monate_jüngstes_mitglied_hh < 7 and
        erziehungsgeld_einkommen_relev > erziehungsgeld_einkommensgrenze):
        out = 0.0
    
    elif (erziehungsgeld_anspruch and 
        erziehungsgeld_einkommen_relev < erziehungsgeld_einkommensgrenze):
        out = erziehungsgeld_params["erziehungsgeld_regelsatz"]
    # if the income is higher than the threshold and the child is older than
    # 7 month the Erziehungsgeld is reduced
    elif (erziehungsgeld_anspruch and
          alter_monate_jüngstes_mitglied_hh > 7 and
          erziehungsgeld_einkommen_relev > erziehungsgeld_einkommensgrenze):
        
        abzug = (erziehungsgeld_einkommen_relev * 
                 erziehungsgeld_params["reduzierung_erziehungsgeld"])
        out = max(erziehungsgeld_params["erziehungsgeld_regelsatz"]-abzug , 0.0)

    return out


def erziehungsgeld_anspruch(
        arbeitsstunden_w: float,
        hat_kinder: bool,
        alter_monate_jüngstes_mitglied_hh: int,

) -> bool:
    """
    
    """
    
    out = (hat_kinder 
           and alter_monate_jüngstes_mitglied_hh < 24
           and arbeitsstunden_w <= 30)

    return out

def erziehungsgeld_einkommen_relev(
        bruttolohn_vorj_m: float,
        bruttolohn_vorj_m_tu: float,
        erziehungsgeld_params: dict,
        alleinerz: bool,
        eink_st_abzuege_params: dict
        
) -> bool:
    """
    Todo: There is special rule for "Beamte, Soldaten und Richter" which is not
          implemented yet
    """
 
    if alleinerz:
        out = ((bruttolohn_vorj_m * 12  - eink_st_abzuege_params["werbungskostenpauschale"]) 
                *  erziehungsgeld_params["pauschal_abzug_auf_einkommen"])
    else:
        out = ((bruttolohn_vorj_m_tu * 12 - eink_st_abzuege_params["werbungskostenpauschale"] * 2) 
               *  erziehungsgeld_params["pauschal_abzug_auf_einkommen"])

    return out

def erziehungsgeld_einkommensgrenze(
        erziehungsgeld_params: dict,
        alleinerz: bool,
        alter_monate_jüngstes_mitglied_hh: int,
        anz_kinder_mit_kindergeld_tu: int,
) -> float:
    """
    
    """
    # There are different income threshold depending on the age of the child
    # the fact if a person is a single parent
    if alter_monate_jüngstes_mitglied_hh < 7:
        if alleinerz:
            out = erziehungsgeld_params["einkommensgrenze_bis_6m"]["alleinerz"]
        else:
            out = erziehungsgeld_params["einkommensgrenze_bis_6m"]["paar"]
    else:
        if alleinerz:
            out = erziehungsgeld_params["einkommensgrenze_ab_7m"]["alleinerz"]
        else:
            out = erziehungsgeld_params["einkommensgrenze_ab_7m"]["paar"]
    # For every additional child the income threshold is increasing by a fixed amount
    out += ((anz_kinder_mit_kindergeld_tu - 1) 
            * erziehungsgeld_params["aufschlag_einkommen"])
    return out