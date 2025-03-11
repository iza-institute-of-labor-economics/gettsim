# Typical output variables

The table below gives an overview of typical variables selected by users to simulate
with GETTSIM. You can simulate them by defining them as target in
{func}`compute_taxes_and_transfers <_gettsim.interface.compute_taxes_and_transfers>`.
You can find their individual calculation in the documentation of all {ref}`functions`.

```{list-table}
* - Variables
  - Description
* - {func}`sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_m <_gettsim.functions.all_functions_for_docs.sozialversicherungsbeitraege__rentenversicherung__betrag_arbeitnehmer_m>`
  - Monthly amount employee old-age pensions contributions
* - {func}`sozialversicherungsbeitraege__arbeitslosenversicherung__betrag_arbeitnehmer_m <_gettsim.functions.all_functions_for_docs.sozialversicherungsbeitraege__arbeitslosenversicherung__betrag_arbeitnehmer_m>`
  - Monthly amount employee unempl. insurance contributions
* - {func}`sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_m <_gettsim.functions.all_functions_for_docs.sozialversicherungsbeitraege__krankenversicherung__betrag_arbeitnehmer_m>`
  - Monthly amount employee health insurance contributions
* - {func}`sozialversicherungsbeitraege__pflegeversicherung__betrag_arbeitnehmer_m <_gettsim.functions.all_functions_for_docs.sozialversicherungsbeitraege__pflegeversicherung__betrag_arbeitnehmer_m>`
  - Monthly amount of long term care insurance
* - {func}`arbeitslosengeld__betrag_m <_gettsim.functions.all_functions_for_docs.arbeitslosengeld__betrag_m>`
  - Monthly amount of unemployment assistance
* - {func}`entgeltp_update <_gettsim.functions.all_functions_for_docs.entgeltp_update>`
  - Updated earning points for pension claim
* - {func}`abgeltungssteuer__betrag_y_sn <_gettsim.functions.all_functions_for_docs.abgeltungssteuer__betrag_y_sn>`
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
