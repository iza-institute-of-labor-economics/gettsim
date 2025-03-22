# Typical output variables

The table below gives an overview of typical variables selected by users to simulate
with GETTSIM. You can simulate them by defining them as target in
{func}`compute_taxes_and_transfers <_gettsim.interface.compute_taxes_and_transfers>`.
You can find their individual calculation in the documentation of all {ref}`functions`.

```{list-table}
* - Variables
  - Description
* - {func}`sozialversicherung__rente__beitrag__betrag_versicherter_m <_gettsim.functions.all_functions_for_docs.sozialversicherung__rente__beitrag__betrag_versicherter_m>`
  - Monthly amount employee old-age pensions contributions
* - {func}`sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_m <_gettsim.functions.all_functions_for_docs.sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_m>`
  - Monthly amount employee unempl. insurance contributions
* - {func}`sozialversicherung__kranken__beitrag__betrag_versicherter_m <_gettsim.functions.all_functions_for_docs.sozialversicherung__kranken__beitrag__betrag_versicherter_m>`
  - Monthly amount employee health insurance contributions
* - {func}`sozialversicherung__pflege__beitrag__betrag_versicherter_m <_gettsim.functions.all_functions_for_docs.sozialversicherung__pflege__beitrag__betrag_versicherter_m>`
  - Monthly amount of long term care insurance
* - {func}`sozialversicherung__arbeitslosen__betrag_m <_gettsim.functions.all_functions_for_docs.sozialversicherung__arbeitslosen__betrag_m>`
  - Monthly amount of unemployment assistance
* - {func}`neue_entgeltpunkte <_gettsim.functions.all_functions_for_docs.neue_entgeltpunkte>`
  - Updated earning points for pension claim
* - {func}`einkommensteuer__abgeltungssteuer__betrag_y_sn <_gettsim.functions.all_functions_for_docs.einkommensteuer__abgeltungssteuer__betrag_y_sn>`
  - Capital income tax on Steuernummer level
* - {func}`solidaritätszuschlag__betrag_y_sn <_gettsim.functions.all_functions_for_docs.solidaritätszuschlag__betrag_y_sn>`
  - Solidarity surcharge on Steuernummer level
* - {func}`kindergeld__betrag_m <_gettsim.functions.all_functions_for_docs.kindergeld__betrag_m>`
  - Monthly child benefit
* - {func}`einkommensteuer__betrag_y_sn <_gettsim.functions.all_functions_for_docs.einkommensteuer__betrag_y_sn>`
  - Income Tax on Steuernummer level
* - {func}`lohnsteuer__betrag_m` <_gettsim.functions.all_functions_for_docs.lohnsteuer__betrag_m>`
  - Withholding tax
* - {func}`lohnsteuer__betrag_soli_m <_gettsim.functions.all_functions_for_docs.lohnsteuer__betrag_soli_m>`
  - Solidarity surcharge on withholding tax
* - {func}`unterhaltsvorschuss__betrag_m <_gettsim.functions.all_functions_for_docs.unterhaltsvorschuss__betrag_m>`
  - Alimony advance payment
* - {func}`arbeitslosengeld_2__betrag_m_bg <_gettsim.functions.all_functions_for_docs.arbeitslosengeld_2__betrag_m_bg>`
  - Monthly subsistence payment on household level
* - {func}`kinderzuschlag__betrag_m_bg <_gettsim.functions.all_functions_for_docs.kinderzuschlag__betrag_m_bg>`
  - Monthly additional child benefit, household sum
* - {func}`elterngeld__betrag_m <_gettsim.functions.all_functions_for_docs.elterngeld__betrag_m>`
  - Monthly parental leave benefit
* - {func}`wohngeld__betrag_m_wthh <_gettsim.functions.all_functions_for_docs.wohngeld__betrag_m_wthh>`
  - Monthly housing benefit on household level
* - {func}`grundsicherung__im_alter__betrag_m_eg <_gettsim.functions.all_functions_for_docs.grundsicherung__im_alter__betrag_m_eg>`
  - Monthly subsistence payment for retirees on household level
```
