.. _gep-1:

==========================
GEP 1 — Naming Conventions
==========================

+------------+-------------------------------------------------------------------------+
| Author     | `Maximilian Blömer <https://github.com/mjbloemer>`_                     |
+            +-------------------------------------------------------------------------+
|            | `Hans-Martin von Gaudecker <https://github.com/hmgaudecker>`_           |
+            +-------------------------------------------------------------------------+
|            | `Eric Sommer <https://github.com/Eric-Sommer>`_                         |
+------------+-------------------------------------------------------------------------+
| Status     | Draft                                                                   |
+------------+-------------------------------------------------------------------------+
| Type       | Standards Track                                                         |
+------------+-------------------------------------------------------------------------+
| Created    | 2019-11-04                                                              |
+------------+-------------------------------------------------------------------------+
| Resolution | <url> (required for Accepted | Rejected | Withdrawn)                    |
+------------+-------------------------------------------------------------------------+


Abstract
--------

This GEP pins down naming conventions for GETTSIM — i.e., general rules for how data
columns, parameters, Python identifiers (functions, variables), etc. should be named. In
a nutshell and without explanations, these conventions are:

* Names follow standard Python conventions (``lowercase_with_underscores``).
  Abbreviations of words that form a part of these names are always followed by an
  underscore, unless it is the last word.
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
groups of parameters of filenames.


General considerations
----------------------

Even though the working language of GETTSIM is English, all of 1. (column names) and 2.
(parameters of the taxes and transfers system) should be specified in German. Any
translation of detailed rules---e.g., distinguishing between Arbeitslosengeld 2 and
Sozialhilfe, or between Erziehungsgeld, Elterngeld, and Elterngeld Plus---is likely to
lead to more confusion than clarity. The main issue here is that often economic concepts
behind the different programmes are the same (in the examples, social assistance and
parental leave benefits, respectively), but often the names of laws change upon major
policy updates. Non-German speakers would need to look things up, anyhow.

Since Python natively supports UTF-8 characters, we use correct spelling everywhere and
do not make efforts to restrict ourselves to ASCII characters. This choice is made for
readability and uniqueness; e.g., it is not obvious whether an "ö" becomes "oe" or "o"
in English. For column names, we always allow a pure ASCII option, see the next point.


Column names (a.k.a. "variables" in Stata)
------------------------------------------

We impose a hard limit of 15 characters for all column names that are part of the API,
i.e., those that are an input to or an output of GETTSIM's main simulation functions.
This is for the benefit of Stata users, who face a strict limit of 32 characters for
their column names. Furthermore, where developers using other languages may store
different experiments in different variables, Stata users' only chance to distinguish
them is to append characters to the column names.

If a column is only present for internal use, it starts with an underscore.

Even though not implemented at the time of this writing, we plan to allow users to pass
in English column names and get English column names back. Similarly, there will be a
pure ASCII option in German (this should always be fulfilled in the English version). If
there is demand, we could also support standardised variables like in `EUROMOD
<https://www.euromod.ac.uk/>`_ or the `CNEF <https://cnef.ehe.osu.edu/data/>`_ standard.

It might be useful to append an underscore plus one of {``j``, ``m``, ``w``, ``t``} to
indicate the time unit.



Parameters of the taxes and transfers system
--------------------------------------------

The structure of these parameters will be laid out in :ref:`gep-3`; we just note some
general naming considerations here.

* There is a hierarchical structure to these parameters in that each of them is
  associated with a group (e.g., ``arbeitsl_geld``, ``kinderzuschlag``). These groups or
  abbreviations thereof do not re-appear in the name of the parameter.



Python Identifiers (Functions, Variables)
-----------------------------------------

Python identifiers should generally be in English, unless they refer to a specific law
or set of laws, which is where the same reasoning applies as above.

The length of a variable name tends to be proportional to its scope. In a list
comprehension or a short loop, ``i`` might be an acceptable name for the running
variable. Variables that are used at many different places should have descriptive
names.

The name of variables should reflect the content or meaning of the variable and not the
type (i.e., int, dict, list, ...). As for column names and parameters, in some cases it
might be useful to append an underscore plus one of {``j``, ``m``, ``w``, ``t``} to
indicate the time unit.

Across variations that include the same identifier, this identifier should not be
changed, even if it leads to long variable names (e.g., ``kinderfreibetrag``,
``zu_verst_e_ohne_kinderfreibetrag``). This makes searching for that identifier easier
and less error-prone.

Function names should contain a verb. Moreover, the length of a function name is
typically inversely proportional to its scope. The public functions like maximize and
minimize can have very short names. At a lower level of abstraction you typically need
more words to describe what a function does.


Examples
--------

As an example we can consider the naming of the parameter group ``arbeitsl_geld``. The
original name for this group of parameters was the abbreviation ``alg``. This will seem
like a suitable candidate for native speakers who are familiar with the German social
security system, as the abbreviation is commonly used to refer to this type of
unemployment benefit. However, acronyms are generally not self-explanatory and users
unfamiliar with them will thus not be able to guess their meaning without looking it up.
More meaningful alternatives could be ``alo_geld`` or ``arb_los_geld``. These names
uses abbreviations of the compounds of the term "Arbeitslosengeld" that the group name is
supposed to reflect, and connect them in a pythonic manner through underscores. However,
``alo_geld`` still leaves much room for interpretation and ``arb_los_geld`` separates
the term in an odd way. The final choice ``arbeitsl_geld`` avoids all the disadvantages
of the other options as it is an unambivalent, natural, and minimal abbreviation of the
original term it is supposed to represent.


Alternatives
------------

* We considered using more English identifiers, but opted against it because of the
  lack of precision and uniqueness (see the example above: How to distinguish between
  Erziehungsgeld, Elterngeld, and Elterngeld Plus in English?). In
* Use one of the standards for column identifiers. They are not precise enough and
  sometimes rather cryptic.
* Do something like EUROMOD and include some hierarchy in column names (e.g. start with
  ``d_`` for demographics). Should not be necessary if column names have clear enough
  names. If anything, we would achieve this via a MultiIndex for the columns.


Discussion
----------

GitHub PR

Zulip discussion


Copyright
---------

This document has been placed in the public domain.
