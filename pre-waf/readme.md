# IZADYNMOD: DYNAMIC IZAMOD #

## General remarks ##
* Start a simulation run by running *izamod.py*
* All settings are done in *settings.py*
* The data basis is SOEPlong

## Remarks on Tax Transfer Simulation ##
* The tax transfer parameters (tax rates, benefit amounts etc.) can be found in /data/params/params.xlsx
This is also where you find the corresponding law. The content of this will be loaded into a
year-specific dictionary called *tb*
* The implementation of tax transfer rules before 2005 is not complete as of now.
* Each reform (specified in settings.py) requires a different tax_transfer module. The counterfactual
tax transfer module might however call functions (soc_ins_contrib, tax_sched ,...)
from tax_transfer.py. Then, one has several choices
1. don't change anything, just call the baseline function
2. hand over an adjusted tb dictionary, allowing for differential parameters
3. hand over the string 'ref' (empty by default), allowing for slight changes in calculations. If
new functions differ only by a few lines, this should be OK.
4. write a new function yourself

## Open issues ##
* too many recipients for ALG1 and wohngeld



