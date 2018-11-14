# IZADYNMOD: DYNAMIC IZAMOD #

## General remarks ##
* Start a simulation run by running *izamod.py*
* Basic settings are done in *settings.py*
* The data basis is SOEPlong
* Each reform (specified in settings.py) requires a different tax_transfer module

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


