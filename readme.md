# IZADYNMOD: DYNAMIC IZAMOD #

## General remarks ##
* Start a simulation run by running *izamod.py*
* All settings are done in *settings.py*
* The data basis is SOEPlong

## Remarks on Data preparation ##

* The SOEP households are divided into separate *tax units*, which contain either one or two adults only.
Example: A household consists of a couple and three kids aged 25, 17 and 14. The grandmother is also
part of the household. Then, the couple, together with the two younger kids, consitutes the first tax
unit. The adult kid is the second one, the grandmother the third one.
The few households for which this division fails are deleted.
* This household splitting implies that one has to mind the difference between e.g. the number of
kids in the SOEP household (*child_num*) and the the number of kids in the tax unit (*child_num_tu*)

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


