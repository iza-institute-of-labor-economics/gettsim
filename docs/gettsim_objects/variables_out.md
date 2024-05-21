# Typical output variables

The table below gives an overview of typical variables selected by users to simulate
with GETTSIM. You can simulate them by defining them as target in
{func}`compute_taxes_and_transfers <_gettsim.interface.compute_taxes_and_transfers>`.
You can find their individual calculation in the documentation of all {ref}`functions`.

```{list-table}
* - Variables
  - Description
* - {func}`ges_rentenv_beitr_arbeitnehmer_m <_gettsim.functions.ges_rentenv_beitr_arbeitnehmer_m>`
  - Monthly amount employee old-age pensions contributions
* - {func}`arbeitsl_v_beitr_m <_gettsim.functions.arbeitsl_v_beitr_m>`
  - Monthly amount employee unempl. insurance contributions
* - {func}`ges_krankenv_beitr_m <_gettsim.functions.ges_krankenv_beitr_m>`
  - Monthly amount employee health insurance contributions
* - {func}`ges_pflegev_beitr_m <_gettsim.functions.ges_pflegev_beitr_m>`
  - Monthly amount of long term care insurance
* - {func}`arbeitsl_geld_m <_gettsim.functions.arbeitsl_geld_m>`
  - Monthly amount of unemployment assistance
* - {func}`entgeltp_update <_gettsim.functions.entgeltp_update>`
  - Updated earning points for pension claim
* - {func}`abgelt_st_y_sn <_gettsim.functions.abgelt_st_y_sn>`
  - Capital income tax on Steuernummer level
* - {func}`soli_st_y_sn <_gettsim.functions.soli_st_y_sn>`
  - Solidarity surcharge on Steuernummer level
* - {func}`kindergeld_m <_gettsim.functions.kindergeld_m>`
  - Monthly child benefit
* - {func}`eink_st_y_sn <_gettsim.functions.eink_st_y_sn>`
  - Income Tax on Steuernummer level
* - {func}`lohnst_m` <_gettsim.functions.lohnst_m>`
  - Withholding tax
* - {func}`soli_st_lohnst_m <_gettsim.functions.soli_st_lohnst_m>`
  - Solidarity surcharge on withholding tax
* - {func}`unterhaltsvors_m <_gettsim.functions.unterhaltsvors_m>`
  - Alimony advance payment
* - {func}`arbeitsl_geld_2_m_bg <_gettsim.functions.arbeitsl_geld_2_m_bg>`
  - Monthly subsistence payment on household level
* - {func}`kinderzuschl_m_bg <_gettsim.functions.kinderzuschl_m_bg>`
  - Monthly additional child benefit, household sum
* - {func}`elterngeld_m <_gettsim.functions.elterngeld_m>`
  - Monthly parental leave benefit
* - {func}`wohngeld_m_hh <_gettsim.functions.wohngeld_m_hh>`
  - Monthly housing benefit on household level
* - {func}`grunds_im_alter_m_eg <_gettsim.functions.grunds_im_alter_m_eg>`
  - Monthly subsistence payment for retirees on household level
```
