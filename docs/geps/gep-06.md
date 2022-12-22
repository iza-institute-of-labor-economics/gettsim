(gep-6)=

# GEP 6 — A unified architecture

```{list-table}
- * Author
  * [Hans-Martin von Gaudecker](https://github.com/hmgaudecker)
- * Status
  * Draft
- * Type
  * Standards Track
- * Created
  * <!-- <date created on, in yyyy-mm-dd format> -->
- * Resolution
  * <!-- One of [Accepted | Rejected | Withdrawn](<url>) once resolution has been found -->
```

## Abstract

This GEP outlines a unified architecture for GETTSIM based on a DAG that encompasses:

1. Namespaces for (policy) functions.
1. Decorators for including or excluding functions from the DAG, e.g., based on points
   in time.
1. Pre-processing of parameters.

Implementing this structure will make GETTSIM much more flexible and more natural to use
/ extend.

## Motivation and Scope

While GETTSIM's overall architecture has proven extremely useful, we are hitting limits
in at least three directions:

1. Names in the DAG are constantly hitting character limits because similar concepts are
   used across different domains
   ([example from PR 457](https://github.com/iza-institute-of-labor-economics/gettsim/pull/457#discussion_r1054643021):
   `anwartschaftszeit` in pensions and unemployment insurance — ).
1. Handling functions that change over the years is not robust (examples in
   [Issue 449](https://github.com/iza-institute-of-labor-economics/gettsim/issues/449)
1. Parameters files do not handle cases well when functions expect parameters in a
   different form than the law specifies them (example:
   [Issue 444](https://github.com/iza-institute-of-labor-economics/gettsim/issues/444)).

These issues severely limit the development of GETTSIM. We have been spending far too
much time finding names that adhere to our self-imposed character limits. Adding
parameters is sometimes awkward as there is no obvious way for pre-processing them.
functions with changing interfaces over the years is a constant pain. Specifying

The proposed changes will push the usage of a DAG to more domains in order to extend the
declarative approach to all components of the taxes and transfers system, not just the
part that applies to the (individual/household) data.

The proposed changes will affect all areas of GETTSIM

1. Namespaces will affect the column names in the input and output data.
1. Instead of a long list of if-statements in the `policy_functions` module, picking
   functions by year will be done in a more natural and more robust way.
1. A clear way to pre-process parameters will allow specifying parameters exactly as
   they are written into the law.

## Usage and Impact

1. The use of namespaces will have the usual benefits as in (Python) code:
   Disambiguation while keeping things that belong together in one place. We largely
   have this structure already for the parameters (think about each `params_[x]`
   dictionary as a namespace). As an example, take the (partly hypothetical) example of
   `anwartschaftszeit` mentioned above. Under the current structure, we may want to use:

   - `ges_rente_anwartschaftszeit`
   - `arbeitsl_geld_anwartschaftszeit`

   This is not possible because both names would be too long given the constraints we
   imposed on ourselves in order to accommodate Stata users.

   With namespaces, we would have:

   - `ges_rente___anwartschaftszeit`
   - `arbeitsl_geld___anwartschaftszeit`

   The precise character (sequence) used for namespace separation does not matter and
   can be determined down the road; the example uses triple underscores. The only
   restriction is that the result must be a valid Python identifier, so a dot will not
   work.

   Importantly, within a module or directory `arbeitsl_geld`, it will be possible to
   refer to `anwartschaftszeit` directly. This will allow keeping code short,
   self-contained, and clear.

1. A current example for functions changing over the years would be
   `midijob_bemessungsentgelt_m`. The relevant code in `policy_environment` is:

   ```python
   from _gettsim.social_insurance_contributions.eink_grenzen import (
       midijob_bemessungsentgelt_m_ab_10_2022,
   )
   from _gettsim.social_insurance_contributions.eink_grenzen import (
       midijob_bemessungsentgelt_m_bis_09_2022,
   )

   [...]

   if date >= datetime.date(year=2022, month=10, day=1):
       functions["midijob_bemessungsentgelt_m"] = midijob_bemessungsentgelt_m_ab_10_2022
   else:
       functions["midijob_bemessungsentgelt_m"] = midijob_bemessungsentgelt_m_bis_09_2022
   ```

   Adding a function that changes over time always means making changes in two
   completely unrelated places, it is very easy to get this wrong.

   A future implementation may look something like:

   ```py
   @dates_active(start="2003-04-01", end="2022-09-30", removesuffix="_some_spec")
   def midijob_bemessungsentgelt_m_some_spec():
       pass

   @dates_active(start="2022-10-01", removesuffix="_some_spec")
   def midijob_bemessungsentgelt_m_another_spec():
       pass
   ```

   If `@dates_active` evaluates to `False`, the function will not appear in the policy
   functions dictionary. Else, whatever is left after removing `removesuffix` will be
   placed as a key in the functions dictionary.

1. The yaml-files with parameters

   - Will live in the same directory as the other functions (=same namespace).

   - Will be parsed to dictionaries and that's it.

   - Might be used in a similar way as they are now (argument `params`, use
     `params["beitragssatz"]` to access elements) or get special treatment as arguments,
     e.g., `p_beitragssatz`.

     In both cases, the namespace makes clear we are talking about, say, `arbeitsl_v`.
     If we need parameters external to the current namespace, we will need the same
     verbose syntax as in 1. (`ges_rentenv___params` /
     `ges_rentenv___params___beitragssatz`).

     What we do will depend in part on how strict we will want to be about type
     checking; mypy does like very general dictionaries. But in general, it can be
     useful to see directly from the interface of a function what is being used inside.

## Backward compatibility

This section describes the ways in which the GEP breaks backward compatibility.

The [#GEPs] stream will contain the GEP up to and including this section. This is to
avoid losing users who are not interested in implementation details and instead focus
the discussion on usage and impact of the intended features.

The `compute_taxes_and_transfers` function will get an additional optional keyword
argument, `columns_mapping`. As the name suggests, it maps columns in the user-provided
data to those that GETTSIM expects. If there is demand, we will provide a code snippet
that maps the column names expected by GETTSIM v0.6 to column names in the updated
structure.

Other changes will impact primarily the development of GETTSIM or the replacement of
policy functions. These will be breaking changes, which seem necessary for the
above-cited reasons of extensibility and clarity.

## Detailed description

\[tbd\]

This section should provide a detailed description of the proposed change. It should
include examples of how the new functionality would be used, intended use-cases and
pseudo-code illustrating its use.

## Related Work

\[tbd\]

This section should list relevant and/or similar technologies, possibly in other
libraries. It does not need to be comprehensive, just list the major examples of prior
and relevant art.

## Implementation

\[tbd\]

This section lists the major steps required to implement the GEP. Where possible, it
should be noted where one step is dependent on another, and which steps may be
optionally omitted. Where it makes sense, each step should include a link to related
pull requests as the implementation progresses.

Any pull requests or development branches containing work on this GEP should be linked
to from here. (A GEP does not need to be implemented in a single pull request if it
makes sense to implement it in discrete phases).

## Alternatives

Continuing with the status quo does not seem to be an option to me. We learned so much
in the past three years that now seems to be a good time to put those lessons into code.

## Discussion

This section may just be a bullet list including links to any discussions regarding the
GEP:

- Links to relevant GitHub issues, pull requests.
- Discussion on Zulip

## References and Footnotes

## Copyright

This document has been placed in the public domain.

[#geps]: https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs
