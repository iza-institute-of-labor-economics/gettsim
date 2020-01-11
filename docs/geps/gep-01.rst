==========================
GEP 1 — Naming Conventions
==========================

:Author: `Eric Sommer <https://github.com/Eric-Sommer>`_
:Author: `Hans-Martin von Gaudecker <https://github.com/hmgaudecker>`_
:Status: Provisional
:Type: Standards
:Created: 2019-11-04


Abstract
--------

This GEP pins down naming conventions for GETTSIM — general rules for what data columns,
parameters, Python identifiers (functions, variables), etc. should be called. In a
nutshell and without explanations, these conventions are:

* Names follow standard Python conventions (``lowercase_with_underscores``)
* Names should be long enough to be readable, but
  * For column names in the user-facing API, there is a hard limit of 15 characters
  * For others, there is a soft limit of 15 and a hard limit of 20 characters
* The language should generally be German

We explain the background for these choices below


Motivation and Scope
--------------------

Naming conventions are important in order to build and maintain GETTSIM as a coherent
library. Since many people with different backgrounds and tastes work on it, it is
particularly important to clearly document our rules for naming things.

There are three basic building blocks of the code:

1. The input and output data, including any values stored intermediately. The scope of
   this GEP are the column identifiers. The index and the variable contents are defined
   elsewhere (could link if we have something).
2. The parameters of the tax transfer system, as detailed in the YAML files.
3. Python identifiers, that is, variables and functions.


General considerations
----------------------

Even though the working language of GETTSIM is English, all of 1. (column names) and 2.
(parameters of the taxes and transfers system) should be specified in German. Any
translation of detailed rules---e.g., ....---is doomed to fail is likely to lead to more
confusion than clarity. Non-German speakers would need to look things up, anyhow.


Column names (a.k.a. "variables" in Stata)
------------------------------------------

We impose a hard limit of 15 characters for all column names that are part of the API,
i.e., those that are an input to or an output of GETTSIM's main simulation functions.
This is for the benefit of Stata users, who face a strict limit of 32 characters for
their column names. Furthermore, where developers using other languages may store
different experiments in different variables, Stata users' only chance to distinguish
them is to append characters to the column names.

If a column is only for internal use, it should start with an underscore.

Even though not implemented at the time of this writing, we plan to allow users to pass
in English column names and get English column names back. Potentially also standardised
variables...

Parameters of the taxes and transfers system
--------------------------------------------

* Stored by group. This group should not re-appear in the name.
* Use Python containers like tuples and namedtuples (the mutable versions of these,
  i.e., lists and dictionaries, might be better known) where relevant. E.g., instead of
  ``steuer_tarif_stufe_0_max = 15000``, ..., ``steuer_tarif_stufe_3_max = 60000`` and
  ``steuer_tarif_rate_0 = 0``, ..., ``steuer_tarif_stufe_4 = 0.55``, use::

      steuer_tarif: {
          15000: 0,
          25000: 0.15,
          40000: 0.3,
          60000: 0.45,
          infty: 0.55
      }


Python Identifiers (Functions, Variables)
-----------------------------------------

The length of a variable name should be proportional to its scope. In a list
comprehension or short loop, it might be an acceptable name for the running variable,
but variables that are used at many different places should have descriptive names.

The name of variables should reflect the content or meaning of the variable and not the
type. As for column names and parameters, in some casees it might be useful to append an
underscore plus either of {``y``, ``m``, ``w``, ``d``} to indicate the timeframe.

Function names should contain a verb. Moreover, the length of a function name is
typically inversely proportional to its scope. The public functions like maximize and
minimize can have very short names. At a lower level of abstraction you typically need
more words to describe what a function does.


Alternatives
------------

* More English
* More info
* Use standard

Discussion
----------


References and Footnotes
------------------------

.. _Euromod: https://www.euromod.ac.uk/sites/default/files/working-papers/EMTN-1.1.pdf

Copyright
---------

This document has been placed in the public domain.
