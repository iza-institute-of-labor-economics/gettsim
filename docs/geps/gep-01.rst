.. _gep-1:

==========================
GEP 1 — Naming Conventions
==========================

:Author: `Eric Sommer <https://github.com/Eric-Sommer>`_
:Author: `Hans-Martin von Gaudecker <https://github.com/hmgaudecker>`_
:Status: Draft
:Type: Standards Track
:Created: 2019-11-04
:Resolution: <url> (required for Accepted | Rejected | Withdrawn)


Abstract
--------

This GEP pins down naming conventions for GETTSIM — general rules for what data columns,
parameters, Python identifiers (functions, variables), etc. should be called. In a
nutshell and without explanations, these conventions are:

* Names follow standard Python conventions (``lowercase_with_underscores``)
* Names should be long enough to be readable, but

  - For column names in the user-facing API, there is a hard limit of 15 characters
  - For other column names, there is a soft limit of 15 and a hard limit of 20 characters

* The language should generally be English in all coding efforts and documentation.
  German should be used for all institutional features for precision.

We explain the background for these choices below.


Motivation and Scope
--------------------

Naming conventions are important in order to build and maintain GETTSIM as a coherent
library. Since many people with different backgrounds and tastes work on it, it is
particularly important to clearly document our rules for naming things.

There are three basic building blocks of the code:

1. The input and output data, including any values stored intermediately.
2. The parameters of the tax transfer system, as detailed in the YAML files.
3. Python identifiers, that is, variables and functions.

The general rules and considerations apply in the same way to similar concepts, e.g.,
groups of parameters.


General considerations
----------------------

Even though the working language of GETTSIM is English, all of 1. (column names) and 2.
(parameters of the taxes and transfers system) should be specified in German. Any
translation of detailed rules---e.g., ....---is likely to lead to more confusion than
clarity. Non-German speakers would need to look things up, anyhow.


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
variables like in `EUROMOD <https://www.euromod.ac.uk/>`_ or the ... standard.

Parameters of the taxes and transfers system
--------------------------------------------

[merge this with @mjbloemer's parts below]

* The parameters are stored by group (e.g., ``arbeitsl_geld``, ``kinderzuschlag``).
  These groups or their abbreviations should not re-appear in the name.
* Use Python containers like tuples and namedtuples (the mutable versions of these,
  i.e., lists and dictionaries, might be better known) where relevant.

E.g., instead of ``kgeld1: 204``, ``kgeld2: 204``, ``kgeld3: 210``, and ``kgeld4: 235`` in the file ``kindergeld.yaml``, use

    .. code-block:: yaml

        beträge:
          - 204
          - 204
          - 210
          - 235


  ``steuer_tarif_stufe_0_max = 15000``, ..., ``steuer_tarif_stufe_3_max = 60000`` and
  ``steuer_tarif_rate_0 = 0``, ..., ``steuer_tarif_stufe_4 = 0.55``, use::

      steuer_tarif: {
          15000: 0,
          25000: 0.15,
          40000: 0.3,
          60000: 0.45,
          infty: 0.55
      }


Parameter Documentation
-----------------------

Parameters stored in the parameter database have basic documentation provided by a
``name`` and a ``descripion`` key. Furthermore, every introduction of a new parameter or
value change has a reference to a law or a source.

The ``name`` key has two sub-keys `de` and `en`, which are

* short names without stating the realm (e.g. "ALG II" or "Kinderzuschlag") again
* not sentences
* Correctly capitalised

Example::

      name:
        de: Regelsatz
        en: Standard rate

The `description` key has two sub-keys `de` and `en`, which

* are good and full explanations of the parameter
* show the § and Gesetzbuch/Paragraph (history) of that parameter
* mention bigger amendments/Neufassungen and be as helpful as possible to
  make sense of that parameter

Example::

      description:
        de: Einkommensanteil, der anrechnungsfrei bleibt, Intervall 2 [a2eg1, a2eg2]. § 30 SGB II. Seit 01.04.2011 § 11b SGB II.
        en: Income share not subject to transfer withdrawal, interval 2 [a2eg1, a2eg2]. § 30 SGB II. Since 01.04.2011 § 11b SGB II.


The `values` key

* contains the value as defined in the law
* values in percentages can alternatively be expressed to the base of one
* add a leading zero for values smaller than 1 and greater than -1
* DM values have to be converted to Euro using the excange rate 1:1.95583.

Example 1::

      values:
        2005-01-01:
          value: 1500
          note: Artikel 1 G. v. 24.12.2003 BGBl. I S. 2954.
        2005-10-01:
          value: 1200
          note: Artikel 1 G. v. 14.08.2005 BGBl. I S. 2407.

Example 2::

      values:
        1995-01-01:
          value: 681
          note: Artikel 31 G. v. 23.06.1993 BGBl. I S. 944. Wert in Euro. Der Betrag im Gesetz lautet 1332 DM.
        1998-01-01:
          value: 939
          note: Artikel 1 G. v. 21.11.1997 BGBl. I S. 2743. Wert in Euro. Der Betrag im Gesetz lautet 1836 DM.
        2002-01-01:
          value: 972
          note: B. v. 15.10.2002 BGBl. I S. 4130.
        2021-01-01:
          value: 16956
          note: Artikel 1 G. v. 10.12.2019 BGBl. I S. 2115.


the `note` key:

* cites the law (Gesetz "G. v."), decree (Verordnung "V. v.") or proclamation (Bekanntmachung "B. v.") that changes the law
* in German
* follows the style ``Artikel [n] [G./V./B.] v. [DD.MM.YYYY] BGBl. I S. [SSSS]. [optional note].``
* do not add information "geändert durch" (it is always a change) or the date the law comes into force (this is exactly the date key in the previous line)
* the page should be the first page of the law/decree/proclamation, not the exact page of the parameter
* ``[optional note]`` can be added. In some rare cases you can add a date/value for a parameter that did not change the parameter. This is usually the case when a whole block of parameters is changed but one of the parameters did not change (by coincidence or not). In these cases there the same value is still listed in the BGBl. Add a "Betrag unverändert." to the note. This is also to signal that the BGBl. has been taken into account. If a parameter is calculated the note will also give information on the calculation. If the value has been converted from DM to Euro the original DM value should be added to the note key.


Example::

      values:
        2005-01-01:
          value: 338
          note: Artikel 1 G. v. 24.12.2003 BGBl. I S. 2954. Der tatsächliche Wert unterscheidet sich zwischen Ost und West. Korrekte Werte sind in den alten Bundesländern einschließlich Berlin (Ost) 345 Euro, in den neuen Bundesländern 331 Euro.
        2005-07-01:
          value: 338
          note: B. v. 01.09.2005 BGBl. I S. 2718. Betrag unverändert. Der tatsächliche Wert unterscheidet sich zwischen Ost und West. Hier wurde vereinfachend 338 Euro als ungewichteter Mittelwert genommen. Korrekte Werte für die Zeit ab 1. Juli 2005 sind in den alten Bundesländern einschließlich Berlin (Ost) 345 Euro, in den neuen Bundesländern 331 Euro.
        2006-07-01:
          value: 345
          note: B. v. 20.07.2006 BGBl. I S. 1702.
        2007-07-01:
          value: 347
          note: B. v. 18.06.2007 BGBl. I S. 1139.
        2008-07-01:
          value: 351
          note: B. v. 26.06.2008 BGBl. I S. 1102.
        2009-07-01:
          value: 359
          note: B. v. 17.06.2009 BGBl. I S. 1342.
        2010-07-01:
          value: 359
          note: B. v. 07.06.2010 BGBl. I S. 820. Betrag unverändert.
        2011-01-01:
          value: 364
          note: Artikel 1 G. v. 24.03.2011 BGBl. I S. 453.
        2012-01-01:
          value: 374
          note: B. v. 20.10.2011 BGBl. I S. 2093.


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


Examples
--------

.. todo::

    Add an example. E.g. our discussion on the parameter group ``arbeitsl_geld``


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
