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
   `anwartschaftszeit` in pensions and unemployment insurance).
1. Handling functions that change over the years is not robust (examples in
   [Issue 449](https://github.com/iza-institute-of-labor-economics/gettsim/issues/449)
1. Parameters files do not handle cases well when functions expect parameters in a
   different form than the law specifies them (example:
   [Issue 444](https://github.com/iza-institute-of-labor-economics/gettsim/issues/444)).

These issues severely limit the development of GETTSIM. We have been spending far too
much time finding names that adhere to our self-imposed character limits. Adding
parameters is sometimes awkward as there is no obvious way for pre-processing them.
Functions with changing interfaces over the years are a constant pain.

The proposed changes will push the usage of a DAG to more domains in order to extend the
declarative approach to all components of the taxes and transfers system, not just the
part that applies to the (individual/household) data.

The proposed changes will affect all areas of GETTSIM

1. Namespaces will affect the column names in the input and output data.
1. Instead of a long list of if-statements in the `policy_functions` module, picking
   functions by year will be done in a more natural and more robust way.
1. A clear way to pre-process parameters will allow specifying parameters exactly as
   they are written into the law.

```{note}
Not sure whether it will belong here, but it just occurred to me while browsing issues
that adding an interface to handle interactions between programmes might be a good idea.
There are (at least) three cases to distinguish:

1. **Vorrangprüfungen**: Legal ineligibility for one programme if eligible for another.

   *Example:* Receipt of `bürgergeld` if household also qualifies `wohngeld` and the
   latter pays at least as much (exception are transition periods like first half of
   2023).

1. **Günstigerprüfungen**: Automatic checks run by authorities whether one programme is
   more beneficial than another.

   *Example:* Tax authorities automatically check whether `kinderfreibetrag` or
   `kindergeld` is more beneficial for tax unit if tax declaration is handed in.

1. **Behavioral assumptions**: If individuals qualify for two mutual exclusive programmes
   but need to apply for either.

   *Example:* Receipt of `wohngeld` if person also qualifies for `bürgergeld`. There is
   no legal obligation to apply for `bürgergeld` in this case.

Currently, these three things seem to be mixed in a fairly ad-hoc way. E.g., "Vorrang"
of `wohngeld` over `bürgergeld` (example 1.) is correctly encoded in
`wohngeld_vorrang_hh` but the converse case (example 3.) is silently assumed in
`wohngeld_m_hh`.
```

## Usage and Impact

1. The use of namespaces will have the usual benefits as in (Python) code:
   Disambiguation while keeping things that belong together in one place. We largely
   have this structure already for the parameters (think about each `[x]_param`
   dictionary as a namespace). As an example, take the (partly hypothetical) example of
   `anwartschaftszeit` mentioned above. Under the current structure, we may want to use:

   - `ges_rente_anwartschaftszeit`
   - `arbeitsl_geld_anwartschaftszeit`

   This is not possible because both names would be too long given the constraints we
   imposed on ourselves in order to accommodate Stata users.

   With namespaces, we would have:

   - `ges_rente__anwartschaftszeit`
   - `arbeitsl_geld__anwartschaftszeit`

   The precise character (sequence) used for namespace separation does not matter and
   can be determined down the road; the example uses double underscores. The only
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


   @dates_active(start="2022-10-01", removesuffix="_another_spec")
   def midijob_bemessungsentgelt_m_another_spec():
       pass
   ```

   If `@dates_active` evaluates to `False`, the function will not appear in the policy
   functions dictionary. Else, whatever is left after removing `removesuffix` will be
   placed as a key in the functions dictionary.

   ```{todo}
   For functions that are changing names more than anything (like *Arbeitslosengeld 2* →
   *Bürgergeld*, which is a bad example only because it is at the namespace level), a
   `change_name` keyword may be useful. We should determine empirically whether it is
   worth it.)
   ```

1. The yaml-files with parameters

   - Will live in the same directory as the other functions (=same namespace).
   - Will be parsed to dictionaries and that's it.

   The keys from these dictionary can then be used as nodes in the DAG.

1. Functions will not have `[x]_params` arguments containing potentially large and
   unstructured dicts any more. Instead, functions will only use the arguments they
   require. In order to distinguish between arguments to be vectorised over (=data
   columns and outputs of policy functions) and arguments that do not vary with the data
   (e.g., parameters taken directly from the `yaml`-files or values derived from them,
   including structured short vectors like inputs for `piecewise_polynomial`), there
   will be a decorator `data_inputs`.

   ```{todo}
   TBD:
   - Name of decorator: `data_inputs` or something else? Might lead to confusion with
     actual data provided by the user.

     In any case, should be user-oriented rather than functionality-oriented like
     `vectorize_over`.

   - Just offer that one option or have something like `params_inputs` in addition?

     Trade-off between having only one way to achieve things and keeping things concise
     (some functions have lots of "data" inputs, others have a lot of "parameter"
     inputs).

   - Inputs assumed to be parameters by default? There will be quite a few functions
     with only parameters as inputs, but hardly any functions with only "data" inputs.
   ```

   The namespace makes clear we are talking about, say, the function `beitrag` in the
   namespace `arbeitsl_v` will have an input `beitragssatz`. If we need parameters which
   are external to the current namespace, we will need the same verbose syntax as in 1.
   (`ges_rentenv__beitragsbemessungsgrenze`).

   This approach will make the part of the DAG dealing with parameters of the taxes and
   transfers system more natural. E.g., we may have a function:

   ```py
   def parse_params_dict(params):
       pass
   ```

   which injects each of the top-level keys of its input (i.e., a `params` dictionary)
   into the DAG is passed in. E.g., in case of `soli_st`, this might be

   - `rate`
   - `freigrenze`
   - `max_rate`

   There might then be a function:

   ```py
   def params_piecewise_polynomial(rate, freigrenze, max_rate):
       pass
   ```

   which uses these values to return a structured dict with keys `thresholds`, `rates`,
   `intercepts_at_lower_thresholds`, i.e., what is required by `piecewise_polynomial`
   and which is the current content of `soli_st_params["soli_st"]`.

1. Because we will be expanding the scope of decorators, we will store function
   attributes in a more structured way than what is currently being done.

   E.g., currently the `add_rounding_spec` decorator will add an attribute
   `__rounding_params_key__` to a function.

   ```{todo}
   Understand how pytask is doing this and add explanation of implementation.
   ```

## Backward compatibility

This section describes the ways in which the GEP breaks backward compatibility.

The [#GEPs] stream will contain the GEP up to and including this section. This is to
avoid losing users who are not interested in implementation details and instead focus
the discussion on usage and impact of the intended features.

The `compute_taxes_and_transfers` function will get an additional optional keyword
argument, `columns_mapping`. As the name suggests, it maps names expected by GETTSIM to
columns in the user-provided data. If there is demand, we will provide a code snippet
that maps the column names expected by GETTSIM v0.6 to column names in the updated
structure.

This `columns_mapping` argument be particularly relevant for Stata users because some
names may become longer than the limit supported by Stata. It is also useful if one
prefers to have English variable names in one's data etc.. When calling from Stata, the
mapping could be specified in a yaml file that looks something like:

```yaml
---
ges_rente__anwartschaftszeit: pens_qual_per
arbeitsl_geld__anwartschaftszeit: ue_ins_qual_per
```

GETTSIM will then rename the columns internally (or create a duplicate column, the data
columns need not be unique).

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

### Separator to use for namespaces in DAG

\[tbd\]

This section lists the major steps required to implement the GEP. Where possible, it
should be noted where one step is dependent on another, and which steps may be
optionally omitted. Where it makes sense, each step should include a link to related
pull requests as the implementation progresses.

Any pull requests or development branches containing work on this GEP should be linked
to from here. (A GEP does not need to be implemented in a single pull request if it
makes sense to implement it in discrete phases).

Restriction: It must be a valid Python identifier, so `.` is impossible. It also should
be possible to parse it without too many case distinctions.

Alternatives might be (very open for discussion here):

1. double underscores

   - Pro:

     - Easy to type
     - Fits well with the rest

   - Con:

     - Somewhat easy to miss the doubling up
     - Names get even longer than they will be in the first place
     - Ambiguity when module names start **and** end with underscores (might just
       disallow / ignore special modules)

1. Some Greek letter, e.g. Ω (Unicode 0x3a9, Greek Capital Letter Omega)

   - Pro:

     - Easy to see purpose
     - Short

   - Con:

     - Hard to type
     - Unusual

### Distinguishing between different input arguments

The main issue for the extended DAG might be how to distinguish fairly automatically
between data to be vectorized over (input columns, policy functions) and arguments that
are be partialed in (parameters and values derived from those).

This currently works via matching `_params` at the end of an argument. If continuing to
work with dictionaries (pytrees) as arguments, we could keep that convention or think of
a similar one, e.g., the `p_` prefix as described above.

### Example

We distribute code across various private modules and keep one namespace per tax /
transfer / social insurance.

In main namespace (will be used to build the DAG):

```
ges_rente
|-- __init.py__
|   +-- from _gettsim.ges_rente._aufbau import *
|   +-- from _gettsim.ges_rente._auszahlung import *
|   +-- ...
|   +-- params = load_params("_gettsim/ges_rente/params.yaml")
```

Private namespace:

```
ges_rente
|-- _aufbau.py
|   +-- def beitrag()
|   +-- def entgeltp_update()
|-- _auszahlung.py
|   +-- def betrag()
|-- _langj_versicherte.py
|-- _grundrente.py
|-- ...
|-- params.yaml
|-- ...
```

## Alternatives

Continuing with the status quo does not seem to be an option. We learned so much in the
past three years that now seems to be a good time to put those lessons into code.

## Discussion

This section may just be a bullet list including links to any discussions regarding the
GEP:

- Links to relevant GitHub issues, pull requests.
- Discussion on Zulip

## References and Footnotes

## Copyright

This document has been placed in the public domain.

[#geps]: https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs
