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
| Updated    | 2021-12-XX                                                              |
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

  - for column names that are typically user-facing, there is a hard limit of 20
    characters;
  - for other column names, there is a hard limit of 25 characters.

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

We impose a hard limit of 20 characters for all column names that typically user-facing,
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

The default time unit is a year. If a column refers to a different time unit, an
underscore plus one of {``m``, ``w``, ``t``} will indicate the time unite.

The default unit a column refers to is an individual. In case a household or tax unit is
the relevant unit, an underscore plus one of {``hh``, ``tu``} will indicate the level of
aggregation.

Time unit identifier come before unit identifiers (e.g., ``arbeitsl_geld_2_m_hh``).



Parameters of the taxes and transfers system
--------------------------------------------

The structure of these parameters will be laid out in gep-3; we just note some
general naming considerations here.

* There is a hierarchical structure to these parameters in that each of them is
  associated with a group (e.g., ``arbeitsl_geld``, ``kinderzuschlag``). These groups or
  abbreviations thereof do not re-appear in the name of the parameter.



Python Identifiers (Functions, Variables)
-----------------------------------------

Python identifiers should generally be in English, unless they refer to a specific law
or set of laws, which is where the same reasoning applies as above.

Across variations that include the same identifier, this identifier should not be
changed, even if it leads to long variable names (e.g., ``kinderfreibetrag``,
``zu_verst_e_ohne_kinderfreibetrag``). This makes searching for that identifier easier
and less error-prone.

The length of an identifier name tends to be proportional to its scope. In a list
comprehension or a short loop, ``i`` might be an acceptable name for the running
variable. A function that is used in many different places should have a descriptive
name.

The name of variables should reflect the content or meaning of the variable and not the
type (i.e., int, dict, list, df, array ...). As for column names and parameters, in some
cases it might be useful to append an underscore plus one of {``m``, ``w``, ``t``} to
indicate the time unit and one of {``hh``, ``tu``} to indicate the unit of aggregation.


Examples
--------

As an example we can consider the naming of the parameter group ``arbeitsl_geld``. The
original name for this group of parameters was the abbreviation ``alg``. This will seem
like a suitable candidate for native speakers who are familiar with the German social
security system; the abbreviation is commonly used to refer to this type of unemployment
benefit. However, acronyms are generally not self-explanatory and users unfamiliar with
them will thus not be able to guess their meaning without looking them up.

More meaningful alternatives could be ``alo_geld`` or ``arb_los_geld``. These names use
abbreviations of the compounds of the term "Arbeitslosengeld", which the group name is
supposed to reflect, and connect them in a Pythonic manner through underscores. However,
``alo_geld`` still leaves much room for interpretation and ``arb_los_geld`` separates
the term "arbeitslosen" in an odd way.

The final choice ``arbeitsl_geld`` avoids all the disadvantages of the other options as
it is an unambivalent, natural, and minimal abbreviation of the original term it is
supposed to represent.


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


A final note
------------

No styleguide in the world can be complete or always be applicable. Python's  `PEP-8
<https://www.python.org/dev/peps/pep-0008/>`_ has the wonderful section called `A
Foolish Consistency is the Hobgoblin of Little Minds
<https://www.python.org/dev/peps/pep-0008/#a-foolish-consistency-is-the-hobgoblin-of-little-minds>`_
for that. Quoting from there:

    A style guide is about consistency. Consistency with this style guide is important.
    Consistency within a project is more important. Consistency within one module or
    function is the most important.

    However, know when to be inconsistent -- sometimes style guide recommendations just
    aren't applicable. When in doubt, use your best judgment. Look at other examples and
    decide what looks best. And don't hesitate to ask!

    In particular: do not break backwards compatibility just to comply with this PEP!

    Some other good reasons to ignore a particular guideline:

        1. When applying the guideline would make the code less readable, even for
           someone who is used to reading code that follows this PEP.
        2. To be consistent with surrounding code that also breaks it (maybe for
           historic reasons) -- although this is also an opportunity to clean up someone
           else's mess (in true XP style).
        3. Because the code in question predates the introduction of the guideline and
           there is no other reason to be modifying that code.
        4. When the code needs to remain compatible with older versions of Python that
           don't support the feature recommended by the style guide.


Discussion
----------

* GitHub PR: https://github.com/iza-institute-of-labor-economics/gettsim/pull/60
* Discussion on provisional acceptance: https://gettsim.zulipchat.com/#narrow/stream/212222-general/topic/GEPs/near/189539859
* GitHub PR for update: https://github.com/iza-institute-of-labor-economics/gettsim/pull/

Copyright
---------

This document has been placed in the public domain.
