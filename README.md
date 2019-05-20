# DYNAMOD - Dynamic Modelling of the German Tax Transfer System #

## Technical Remarks
- In order to clone including submodules, please clone via `git clone --recurse-submodules https://git.econ.tools/dynamod/dynamod.git` .
- The data for the test cases are prepared in Excel as we make use of formulas. When opening these files in Libreoffice Calc, boolean values (e.g. for `child` oder `east`) might be displayed as `0/1` instead of `TRUE/FALSE`. 
Changing the tests with calc might hence lead to failure, as the function requires the `pandas` boolean type. **Remedy:** Change the format in Calc to *booelan* by selecting the respective cells and hitting `Ctrl+1`.
- The data preparation is outsourced into separate repositories. In order to work smoothly, place these repos into the same root folder as this repo. 
Alternatively, you may change the respective path (`SOEP_PATH`, `SIAB_PATH`, etc.) in `wscript`. 

## Assumptions in SOEP data preparation
- A household member is defined as a child if (under 18) or (under 25 and in education). Unless it's the household head or his/her partner
- Earnings:
  - Monthly earnings are summed up from earnings from all jobs. This is a simplification as the 2nd job might be tax-free if it's paid below 450€. 
  - To this, other wage components (13th salary, bonus payments) are added. Since this information stems from the previous year, it is divided by the number of months in work.
  - If "stellung im Beruf" is self-employed, these earnings count as self-employed income `m_self`. Otherwise, it's labor income `m_wage`.
- Non-workers are assigned a potential hourly wage via Heckman Imputation. (function `heckman()` in `2_prepare_data.py`)
- `m_transfers` encompasses all private transfers (alimony mainly) and public transfers which we do not simulate (e.g. Parental Benefit, BaföG)
- Renting costs `hgrent` and heating costs `hgheat` exhibit many missings. Missing values are imputed in order to have some idea on benefit claim. It's better to be somewhat off than to assume no renting costs.

## Implicit Assumptions in Tax-Benefit calculations ##

- Calculation of taxable income (`zve()`): 
  - In lack of more detailed information, we always deduct the lumpsum amount `werbung` (currently € 1000) which is the lower bound
  - The same holds for Sonderausgaben (`sonder` = € 36)
- Income Tax Calculation:
  - married couples are assumed to file jointly. This is not a brave assumption; they are always better off that way.
- Housing Benefit (Wohngeld):
  - There is an upper threshold `tg["wgmax?p_m"], (? = [1,2,4,5,plus5])` up to which rents are considered in the wohngeld formula. These values differ by *Mietstufe* (I: Eifel village , V: Bonn, VI: Köln).
We don't know the municipality and hence the Mietstufe. We assume instead Mietstufe III for *everyone*, which is supposed to capture a medium level. This leads to undercoverage of housing benefit in large, expensive cities.
- Unemployment Benefit (ALG 2):
  - Housing costs are paid if *appropriate*.
    - We cap rents to €10 per square meter. In 2017, actual acknowledged cost of ALG2 recipients were in average between €8 and €9.
    - There is a *Faustregel* on the maximum size of the flat:
	  - For Renters: 45 sqm plus 15 sqm for each additional person
	  - For Owners: 80 sqm plus 20 sqm for each additional person after third
    - *Kosten der Unterkunft* (`alg2_kdu`) are hence calculated by maximum 10€ per sqm, multiplied by minimum of actual flat size and Faustregel.
  - For the Asset Test, we impute assets via capital income and some average interest rate (tb['r_assets']). This should be replaced by either imputed wealth from EVS, or wealth observed in SOEP wave 2017.

## Necessary input for tax_transfer() elements ##

### soc_ins_contrib() ###
- `pid`: Personal Identifier
- `m_wage`: Monthly earnings from Employment
- `m_self`: Monthly Self-Employment Income
- `m_pensions`: Monthly old-age pensions
- `east` (boolean): East Germany
- `age`
- `selfemployed` (boolean): Self-Employment Status
- `haskids` (boolean): Person has kids (in and outside the household!)
- `pkv` (boolean): Person has private health insurance

### ui() ###
- `pid`: Personal Identifier
- `m_wage_l1`: Monthly Earnings from previous year
- `east` (boolean): East Germany
- `child` (boolean)
- `months_ue`: Months in unemployment, current year
- `months_ue_l`: Month in unemployment, previous year
- `months_ue_l2`: Month in unemployment, two years ago
- `m_pensions`: Monthly old-age pensions
- `w_hours`: Weekly working hours
- `child_num_tu`: Number of children in Tax Unit
- `age`

### zve() ###
- `tu_id`: Tax Unit Identifier
- `pid`: Personal Identifier
- `m_wage`: Monthly Earnings
- `m_self`: Monthly Self-Employment Income
- `m_kapinc`: Monthly capital income
- `m_vermiet`: Monthly rental income
- `renteneintritt`: Year of entering old-age retirement. **can easily be calculated within the function**
- `m_pensions`: Monthly old-age pensions
- `east` (booelan): East Germany
- `zveranl` (boolean): Adults within a married couple who file jointly
- `child` (boolean)
- `handcap_degree` [0,100]: Degree of disability
- `rvbeit`: Monthly old-age pension contributions, output from `soc_ins_contrib()`
- `avbeit`: Monthly unemployment insurance contributions, output from `soc_ins_contrib()`
- `gkvbeit`: Monthly statutory health insurance contributions, output from `soc_ins_contrib()`
- `pvbeit`: Monthly long-term care insurance contributions, output from `soc_ins_contrib()`
- `alleinerz` (boolean): Single Parent
- `age`
- `child_num_tu`: Number of children in tax unit

### tax_sched() ###
- `tu_id`: Tax Unit Identifier
- `zve_x_y`: taxable income... (output from `zve()`)
    - x = ["", abg]: without and with capital income included
    - y = [nokfb, kfb]: without and with child tax allowance
- `gross_e5`: **annual** capital income (5th type of taxable incomes), output from `zve()`
- `gross_e5_tu`: annual capital income, sum within the tax unit, output from `zve()`
- `zveranl` (boolean): Adults within a married couple who file jointly

### kindergeld() ###
- `tu_id`: Tax Unit Identifier
- `pid`: Personal Identifer
- `age`
- `w_hours`: Weekly working hours
- `ineducation` (boolean)
- `m_wage`: Monthly Earnings

### favorability_check() ###
- `tu_id`: Tax Unit Identifier
- `pid`: Personal Identifier
- `zveranl` (boolean): Adults within a married couple who file jointly
- `child` (boolean)
- `tax_x_y`: income tax for different tax bases (output from `tax_sched()`):
    - x = ["", abg]: without and with capital income included
    - y = [nokfb, kfb]: without and with child tax allowance
- `abgst_tu`: Capital income tax (Abgeltungssteuer), sum within tu_id.
- `kindergeld_basis`: Output from `kindergeld()`
- `kindergeld_basis`: Output from `kindergeld()`, **can be calculated within function**

### soli() ###
- `tu_id`: Tax Unit Identifier
- `pid`: Personal Identifier
- `zveranl` (boolean): Adults within a married couple who file jointly
- `child` (boolean)
- `incometax_tu`: optimal income tax, output from `favorability_check()`.
- `tax_kfb_tu`: Income tax with child tax allowance, output from `tax_sched()`
- `tax_kfb_abg_tu`: As above, but with capital income included, needed before 2009. Output from `tax_sched()`
- `abgst_tu`: Capital income tax, output from `tax_sched()`

### uhv() ###
- `tu_id`: Tax Unit Identifier
- `pid`: Personal Identifier
- `zveranl` (boolean): Adults within a married couple who file jointly
- `age`
- `alleinerz` (boolean): Single Parent
- `m_wage, m_transfers, m_self, m_vermiet, m_kapinc, m_pensions, m_alg1`: Income from various sources

### wg() ###
- `hid`: Household Identifier
- `tu_id`: Tax Unit Identifier
- `head_tu` (boolean): Dummy for Head of Tax Unit
- `hhsize`: Size of Household
- `hhsize_tu`: Size of Tax Unit
- `hh_korr`: `hhsize` / `hhsize_tu`. ** can be calculated within function **
- `child` (boolean)
- `miete`: monthly rent without heating
- `heizkost`: monthly heating costs
- `alleinerz` (boolean): Single Parent
- `child11_num_tu`: number of children below 11 in tax unit ** can be calculated within function **
- `cnstyr` [1,2,3]: Indicator for construction year of house; relevant before 2009. Set it to `2` if in doubt.
- `m_wage`: Monthly Earnings
- `m_pensions`: Monthly old-age pensions
- `ertragsanteil`: Taxable Share of pensions, output from `zve()`.
- `uhv`: Monthly alimony payments, output from `uhv()`.
- `m_alg1`: Monthly unemployment benefits, output from `ui()`
- `m_transfers`: Monthly private and public transfers that are not simulated. 
- `gross_e1, gross_e4, gross_e5, gross_e6`: Annual income from self-employment, employment (incl. werbungskosten), capital and rental
- `incometax`: monthyl income Tax payments, output from `soli()`.
- `rvbeit`, `gkvbeit`: monthly contributions, output from `soc_ins_contrib()`
- `handcap_degree`: Degree of disability
- `divdy`: annual capital income.

