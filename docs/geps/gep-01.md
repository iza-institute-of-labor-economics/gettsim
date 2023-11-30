(gep-1)=

# GEP 1 — Naming Conventions

```{list-table}
- * Author
  * [Maximilian Blömer](https://github.com/mjbloemer),
    [Hans-Martin von Gaudecker](https://github.com/hmgaudecker),
    [Eric Sommer](https://github.com/Eric-Sommer)
- * Status
  * Provisional
- * Type
  * Standards Track
- * Created
  * 2019-11-04
- * Updated
  * 2022-03-28
- * Resolution
  * [Accepted](https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2001)
```

## Abstract

This GEP pins down naming conventions for GETTSIM — i.e., general rules for how data
columns, parameters, Python identifiers (functions, variables), etc. should be named. In
a nutshell and without explanations, these conventions are:

1. Names follow standard Python conventions (`lowercase_with_underscores`).
   Abbreviations of words that form a part of these names are always followed by an
   underscore, unless it is the last word.

1. Names should be long enough to be readable. However, we impose limits in order to
   make GETTSIM usable in languages, which place limits on characters (Stata, in
   particular).

   - Column names that are typically user-facing have a hard limit of 20 characters.
     These columns are documented in `DEFAULT_TARGETS` in `gettsim/config.py`.
   - Other column names that users might potentially be interested in have a hard limit
     of 32 characters.
   - Columns geared at internal use (e.g., helper variables before applying a
     favorability check) start with an underscore and there are no restrictions.
     Internal variables should be used sparingly.

1. If names need to be concatenated for making clear what a column name refers to (e.g.,
   `arbeitsl_geld_2_vermög_freib_bg` vs. `grunds_im_alter_vermög_freib_vg`), the group
   (i.e., the tax or transfer) that a variable refers to appears first.

1. Because of the necessity of concatenated column names, there will be conflicts
   between readability (1.) and variable length (2.). If such conflicts arise, they need
   to be solved on a case by case basis. Consistency across different variants of a
   variable names always has to be kept.

1. The language should generally be English in all coding efforts and documentation.
   German should be used for all institutional features and directly corresponding
   names.

1. German identifiers use correct spelling even if it is non-ASCII (this mostly concerns
   the letters ä, ö, ü, ß).

We explain the background for these choices below.

## Motivation and Scope

Naming conventions are important in order to build and maintain GETTSIM as a coherent
library. Since many people with different backgrounds and tastes work on it, it is
particularly important to clearly document our rules for naming things.

There are three basic building blocks of the code:

1. The input and output data, including any values stored intermediately.
1. The parameters of the tax transfer system, as detailed in the YAML files.
1. Python identifiers, that is, variables and functions.

The general rules and considerations apply in the same way to similar concepts, e.g.,
groups of parameters of filenames.

## General considerations

Even though the working language of GETTSIM is English, all of 1. (column names) and 2.
(parameters of the taxes and transfers system) should be specified in German. Any
translation of detailed rules---e.g., distinguishing between Arbeitslosengeld 2 and
Sozialhilfe; or between Erziehungsgeld, Elterngeld, and Elterngeld Plus---is likely to
lead to more confusion than clarity. The main issue here is that often economic concepts
behind the different programmes are the same (in the examples, social assistance and
parental leave benefits, respectively), but often the names of laws change upon major
policy updates. Non-German speakers would need to look things up, anyhow.

Since Python natively supports UTF-8 characters, we use correct spelling everywhere and
do not make efforts to restrict ourselves to ASCII characters. This choice is made for
readability and uniqueness; e.g., it is not obvious whether an "ö" becomes "oe" or "o"
in English. For column names, we always allow a pure ASCII option, see the next point.

(gep-1-column-names)=

## Column names (a.k.a. "variables" in Stata)

We impose a hard limit of 20 characters for all column names that typically user-facing.
This is for the benefit of Stata users, who face a strict limit of 32 characters for
their column names. Furthermore, where developers using other languages may store
different experiments in different variables, Stata users' only chance to distinguish
them is to append characters to the column names.

For the same reason, there is a hard limit of 32 characters for variables that users may
reasonably request.

If a column is only present for internal use, it starts with an underscore and there is
no restriction on the number of characters. Internal columns should be used sparingly.

Across variations that include the same identifier, this identifier should not be
changed, even if it leads to long variable names (e.g., `kinderfreib`,
`_zu_verst_eink_ohne_kinderfreib_y_sn`). This makes searching for identifiers easier and
less error-prone.

If names need to be concatenated for making clear what a column name refers to (e.g.,
`arbeitsl_geld_2_vermög_freib_bg` vs. `grunds_im_alter_vermög_freib_vg`), the group
(i.e., the tax or transfer) that a variable refers to appears first.

If a column has a reference to a time unit (i.e., any flow variable like earnings or
transfers), a column is indicated by an underscore plus one of {`y`, `m`, `w`, `d`}.

The default unit a column refers to is an individual. In case a household or tax unit is
the relevant unit, an underscore plus one of {`sn`, `vg`, `fg`, `bg`} will indicate the
level of aggregation.

GETTSIM knows about the following units:

- `p_id`: person identifier
- `sn_id`: Steuernummer (same for spouses filing taxes jointly, not the same as the
  Germany-wide Steuer-ID)
- `vg_id`: Haushalt, the relevant unit for Wohngeld. `vg` derives from Verantwortungs-
  und Einstehensgemeinschaft. Encompasses more people than the Bedarfsgemeinschaft
  (e.g., possibly more than 2 generations). *(might be misnomer)* Currently also used in
  SGB XII.
- `fg_id`: Familiengemeinschaft. Maximum of two generations, the relevant unit for
  Bürgergeld / Arbeitslosengeld 2. Another way to think about this is the potential
  Bedarfsgemeinschaft before making checks for whether children have enough income fend
  for themselves. Subset of `vg`.
- `bg_id`: Bedarfsgemeinschaft, i.e., Familiengemeinschaft plus for whether children
  have enough income to fend for themselves. Subset of `fg_id`.

Note that households do not include flat shares etc.. Such broader definition are
currently not relevant in GETTSIM but may be added in the future (e.g., capping rules
for costs of dwelling in SGB II depend on this).

Open questions:

- Can we use bg_id for both SGB II and SGB XII at the same time or do we need to
  differentiate once we add serious support for SGB XII?

Time unit identifiers always appear before unit identifiers (e.g.,
`arbeitsl_geld_2_m_bg`).

## Parameters of the taxes and transfers system

The structure of these parameters are laid out in \<GEP-3 `gep-3`>; we just note some
general naming considerations here.

- There is a hierarchical structure to these parameters in that each of them is
  associated with a group (e.g., `arbeitsl_geld`, `kinderzuschlag`). These groups or
  abbreviations thereof do not re-appear in the name of the parameter.
- Parameter names should be generally be aligned with relevant column names. However,
  since the group is not repeated for the parameter, it is often better not to
  abbreviate them (e.g., `wohngeld_params["vermögensgrundfreibetrag"]` for the parameter
  and `wohngeld_nach_vermög_check_m_vg` for a column derived from it).

## Other Python identifiers (Functions, Variables)

Python identifiers should generally be in English, unless they refer to a specific law
or set of laws, which is where the same reasoning applies as above.

The length of an identifier name tends to be proportional to its scope. In a list
comprehension or a short loop, `i` might be an acceptable name for the running variable.
A function that is used in many different places should have a descriptive name.

The name of variables should reflect the content or meaning of the variable and not the
type (i.e., float, int, dict, list, df, array ...). As for column names and parameters,
in some cases it might be useful to append an underscore plus one of {`m`, `w`, `d`} to
indicate the time unit and one of {`sn`, `vg`, `fg`, `bg`} to indicate the unit of
aggregation.

## Examples

As an example we can consider the naming of the parameter group `arbeitsl_geld`. The
original name for this group of parameters was the abbreviation `alg`. This will seem
like a suitable candidate for native speakers who are familiar with the German social
security system; the abbreviation is commonly used to refer to this type of unemployment
benefit. However, acronyms are generally not self-explanatory and users unfamiliar with
them will thus not be able to guess their meaning without looking them up.

More meaningful alternatives could be `alo_geld` or `arb_los_geld`. These names use
abbreviations of the compounds of the term "Arbeitslosengeld", which the group name is
supposed to reflect, and connect them in a Pythonic manner through underscores. However,
`alo_geld` still leaves much room for interpretation and `arb_los_geld` separates the
term "Arbeitslosen" in an odd way.

The final choice `arbeitsl_geld` avoids all the disadvantages of the other options as it
is an unambivalent, natural, and minimal abbreviation of the original term it is
supposed to represent.

## Alternatives

- We considered using more English identifiers, but opted against it because of the lack
  of precision and uniqueness (see the example above: How to distinguish between
  Erziehungsgeld, Elterngeld, and Elterngeld Plus in English?).
- Use one of the standards for column identifiers. They are not precise enough and
  sometimes rather cryptic.
- Do something like EUROMOD and include some hierarchy in column names (e.g. start with
  `d_` for demographics). Should not be necessary if column names have clear enough
  names. If anything, we would achieve this via a MultiIndex for the columns.

## A final note

No styleguide in the world can be complete or always be applicable. Python's
[PEP-8](https://www.python.org/dev/peps/pep-0008/) has the wonderful section called
[A Foolish Consistency is the Hobgoblin of Little Minds](https://www.python.org/dev/peps/pep-0008/#a-foolish-consistency-is-the-hobgoblin-of-little-minds)
for that. Quoting from there:

> A style guide is about consistency. Consistency with this style guide is important.
> Consistency within a project is more important. Consistency within one module or
> function is the most important.
>
> However, know when to be inconsistent -- sometimes style guide recommendations just
> aren't applicable. When in doubt, use your best judgment. Look at other examples and
> decide what looks best. And don't hesitate to ask!
>
> In particular: do not break backwards compatibility just to comply with this PEP!
>
> Some other good reasons to ignore a particular guideline:
>
> > 1. When applying the guideline would make the code less readable, even for someone
> >    who is used to reading code that follows this PEP.
> > 1. To be consistent with surrounding code that also breaks it (maybe for historic
> >    reasons) -- although this is also an opportunity to clean up someone else's mess
> >    (in true XP style).
> > 1. Because the code in question predates the introduction of the guideline and there
> >    is no other reason to be modifying that code.
> > 1. When the code needs to remain compatible with older versions of Python that don't
> >    support the feature recommended by the style guide.

## Discussion

- GitHub PR: <https://github.com/iza-institute-of-labor-economics/gettsim/pull/60>
- Discussion on provisional acceptance:
  <https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2001/near/189539859>
- GitHub PR for first update (character limits, time and unit identifiers, DAG
  adjustments): <https://github.com/iza-institute-of-labor-economics/gettsim/pull/312>
- GitHub PR for second update (concatenated column names, dealing with conflicting
  objectives, names for columns vs parameters):
  <https://github.com/iza-institute-of-labor-economics/gettsim/pull/342>

## Copyright

This document has been placed in the public domain.
