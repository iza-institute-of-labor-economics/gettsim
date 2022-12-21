(params_files)=

# Parameter files

The parameters of the tax and transfer system are stored in compartment specific
dictionaries. The {code}`params` argument created in
{func}`set_up_policy_environment <_gettsim.policy_environment.set_up_policy_environment>`
and then used in
{func}`compute_taxes_and_transfers <_gettsim.interface.compute_taxes_and_transfers>` is
a dictionary of these compartment specific dictionaries. Thus it is a dictionary of
dictionaries, where the keys are the name of the compartment. The files from which
{func}`set_up_policy_environment <_gettsim.policy_environment.set_up_policy_environment>`
loads the default parameters for each year, can be found
[here](https://github.com/iza-institute-of-labor-economics/gettsim/tree/main/gettsim/parameters)
and are named by the compartment. Our current guidlines on how these files are set up
can be found in the GEP-2.

Inside GETTSIM, functions don't operate with the full {code}`params` file and instead
just use each compartment specific parameter dictionary. The names of these dictionaries
are named by the structure {code}`compartment_name + _params`. The explicit names can be
found in the table below. GETTSIM reads the function arguments and selects the
corresponding part of the {code}`params` file. For GETTSIM to read and process the
arguments of functions correctly the {code}`compartment_name + _params` variables have
to be last inputs in the function signature.

(soz_vers_beitr_params)=

## `soz_vers_beitr_params`

Social insurance contributions

(eink_st_params)=

## `eink_st_params`

Income tax

(eink_st_abzuege_params)=

## `eink_st_abzuege_params`

Income tax deductions

(soli_st_params)=

## `soli_st_params`

Solidarity surcharge

(arbeitsl_geld_2_params)=

## `arbeitsl_geld_2_params`

Basic social insurance

(arbeitsl_geld_params)=

## `arbeitsl_geld_params`

Unemployment benefits

(unterhalt_params)=

## `unterhalt_params`

Alimony payments

(abgelt_st_params)=

## `abgelt_st_params`

Capital income tax

(wohngeld_params)=

## `wohngeld_params`

Housing benefits

(kinderzuschl_params)=

## `kinderzuschl_params`

Child allowance

(kindergeld_params)=

## `kindergeld_params`

Child benefits

(elterngeld_params)=

## `elterngeld_params`

Parental leave benefits

(ges_rente_params)=

## `ges_rente_params`

Pensions

(grunds_im_alter_params)=

## `grunds_im_alter_params`

Old-age basic income support
