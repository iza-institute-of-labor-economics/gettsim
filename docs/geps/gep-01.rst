.. _gep-1:

==========================
GEP 1 — Naming Conventions
==========================

:Author: `Maximilian Blömer <https://github.com/mjbloemer>`_
:Author: `Hans-Martin von Gaudecker <https://github.com/hmgaudecker>`_
:Author: `Eric Sommer <https://github.com/Eric-Sommer>`_
:Status: Draft
:Type: Standards Track
:Created: 2019-11-04
:Resolution: <url> (required for Accepted | Rejected | Withdrawn)


Abstract
--------

This GEP pins down naming conventions for GETTSIM — general rules for what data columns,
parameters, Python identifiers (functions, variables), etc. should be called. In a
nutshell and without explanations, these conventions are:

* Names follow standard Python conventions (``lowercase_with_underscores``).
* Names should be long enough to be readable, but

  - for column names in the user-facing API, there is a hard limit of 15 characters;
  - for other column names, there is a soft limit of 15 and a hard limit of 25
    characters.

* The language should generally be English in all coding efforts and documentation.
  German should be used for all institutional features and directly corresponding
  names.
* German identifiers use correct spelling even if it is non-ASCII (this mostly concerns
  the letters ä, ö, ü, ß).

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

The scope of this GEP extends to some conventions for file formats; e.g. the rules for
documenting parameters of the taxes and transfers system.


General considerations
----------------------

Even though the working language of GETTSIM is English, all of 1. (column names) and 2.
(parameters of the taxes and transfers system) should be specified in German. Any
translation of detailed rules---e.g., distinguishing between Arbeitslosengeld 2 and
Sozialhilfe, or between Erziehungsgeld, Elterngeld, and Elterngeld+---is likely to lead
to more confusion than clarity. The main issue here is that often economic concepts
behind the different programmes are the same (in the examples, social assistance and
parental leave benefits, respectively), but often the names of laws change upon major
policy updates. Non-German speakers would need to look things up, anyhow.

Since Python natively supports UTF-8 characters, we use correct spelling everywhere and
do not make efforts to restrict ourselves to ASCII characters. This choice is made for
readability and uniqueness; e.g., it is not obvious whether an "ö" becomes "oe" or "o"
in English.


Column names (a.k.a. "variables" in Stata)
------------------------------------------

We impose a hard limit of 15 characters for all column names that are part of the API,
i.e., those that are an input to or an output of GETTSIM's main simulation functions.
This is for the benefit of Stata users, who face a strict limit of 32 characters for
their column names. Furthermore, where developers using other languages may store
different experiments in different variables, Stata users' only chance to distinguish
them is to append characters to the column names.

If a column is only present for internal use, it should start with an underscore.

Even though not implemented at the time of this writing, we plan to allow users to pass
in English column names and get English column names back. Potentially also standardised
variables like in `EUROMOD <https://www.euromod.ac.uk/>`_ or the `CNEF <https://cnef.ehe.osu.edu/data/>`_ standard.


Parameters of the taxes and transfers system
--------------------------------------------

In many ways, the parameters of the taxes and transfers system are the core of GETTSIM.
Along with the functions operating on them and the input data, they determine all
quantities of interest. Cleanly documenting the sources of these parameters requires
particular care. Hence, this is by far the longest section.

General rules
+++++++++++++

* The parameters are stored by group (e.g., ``arbeitsl_geld``, ``kinderzuschlag``).
  These groups or abbreviations thereof should not re-appear in the name of the
  parameter.
* The parameters make use of Python containers like tuples and namedtuples (the mutable
  versions of these, i.e., lists and dictionaries, might be better known) where
  relevant.
* The input of the parameters data via a set of
  [yaml](https://yaml.org/spec/1.2/spec.html)-files, which pin down these structures.


Structure of the YAML files
+++++++++++++++++++++++++++

Each YAML file contains a number of parameters at the outermost level of indentation.
Each of these parameters then has at least three keys: ``name``, ``description``, and
``value``. Values usually change over time; each time a value is introduced or changed
the respective law or regulation is referenced along with the numerical value.

1. The ``name`` key has two sub-keys ``de`` and ``en``, which are

   * short names without stating the realm (e.g. "Arbeitslosengeld II" or
     "Kinderzuschlag") again,
   * not sentences,
   * correctly capitalised.

   Example (from ``arbeitsl_geld_2``):

   .. code-block:: yaml

        name:
          de: Regelsatz
          en: Standard rate

2. The ``description`` key has two sub-keys ``de`` and ``en``, which

   * are good and full explanations of the parameter
   * show the § and Gesetzbuch/Paragraph (history) of that parameter
   * mention bigger amendments/Neufassungen and be as helpful as possible to
     make sense of that parameter

    Example:

   .. code-block:: yaml

        description:
          de: Einkommensanteil, der anrechnungsfrei bleibt, Intervall 2 [a2eg1, a2eg2]. § 30 SGB II. Seit 01.04.2011 § 11b SGB II.
          en: Income share not subject to transfer withdrawal, interval 2 [a2eg1, a2eg2]. § 30 SGB II. Since 01.04.2011 § 11b SGB II.


3. The ``value`` key

   * contains the value as defined in the law
   * values in percentages can alternatively be expressed to the base of one
   * add a leading zero for values smaller than 1 and greater than -1
   * DM values have to be converted to Euro using the excange rate 1:1.95583.

   Example 1:

   .. code-block:: yaml

        value:
            2005-01-01:
                value: 1500
                note: Artikel 1 G. v. 24.12.2003 BGBl. I S. 2954.
            2005-10-01:
                value: 1200
                note: Artikel 1 G. v. 14.08.2005 BGBl. I S. 2407.

   Example 2:

   .. code-block:: yaml

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


   Example:

   .. code-block:: yaml

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


Copyright
---------

This document has been placed in the public domain.
