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
  * 2025-02-17
- * Resolution
  * <!-- One of [Accepted | Rejected | Withdrawn](<url>) once resolution has been found -->
```

## Abstract

This GEP outlines a unified architecture for GETTSIM based on a DAG that encompasses:

1. Namespaces for (policy) functions.
1. Decorators for including or excluding functions from the DAG based on the evaluation
   date of the policy environment.
1. Pre-processing of parameters.

Implementing this structure will make GETTSIM much more flexible and more natural to use
/ extend.

## Motivation and Scope

While GETTSIM's overall architecture has proven extremely useful, we are hitting limits
in at least three directions:

1. GETTSIM follows a law-to-code approach, but function names often become artificially
   long to ensure uniqueness, thereby hitting self-imposed character limits. For
   example, `erziehungsgeld_eink_relev_kind_y` and `kinderzuschl_eink_relev_m_bg`
   represent similar concepts in a very different legal context. Excessive concatenation
   and abbreviations make these names difficult to understand and disconnect them from
   the legal framework. In most cases, such complexity is unnecessary, as the module in
   which a function resides already provides sufficient context—such as Arbeitslosengeld
   2 and Elterngeld in the examples above.
1. Handling functions that change over the years is not robust (examples in
   [Issue 449](https://github.com/iza-institute-of-labor-economics/gettsim/issues/449)
1. Parameters files do not handle cases well when functions expect parameters in a
   different form than the law specifies them (example:
   [Issue 444](https://github.com/iza-institute-of-labor-economics/gettsim/issues/444)).

These issues severely limit the development of GETTSIM. We have been spending far too
much time finding names that adhere to our self-imposed character limits. Adding
parameters is sometimes awkward as there is no obvious way for pre-processing them.
Functions with changing interfaces over the years are a constant pain.

The proposed changes will enhance GETTSIMs DAG in multiple dimensions. First, we extend
the DAG to the parameters of the taxes and transfers system, thereby allowing for
pre-processing of parameters. Second, building the DAG will depend on the date for which
the user wants to perform calculations. Third, the DAG will account for the namespace of
GETTSIMs policy functions, which allows for non-unqiue function names across GETTSIMs
modules.

The proposed changes will affect all areas of GETTSIM

1. Namespaces will affect how GETTSIM expects and returns input and output data.
1. Instead of a long list of if-statements in the `policy_functions` module, picking
   functions by year will be done in a more natural and more robust way.
1. A clear way to pre-process parameters will allow specifying parameters exactly as
   they are written into the law.

## Usage and Impact

1. The use of namespaces will have the usual benefits as in (Python) code:
   Disambiguation while keeping things that belong together in one place. We largely
   have this structure already for the parameters (think about each `[x]_param`
   dictionary as a namespace).

Currently, for example, `erziehungsgeld_eink_relev_kind_y` is used as the relevant
income for the pre-2009 parental leave benefit (Erziehungsgeld). Similarly,
`kinderzuschl_eink_relev_m_bg` is the income relevant for means-testing the additional
child benefit (Kinderzuschlag), and `arbeitsl_geld_2_eink_m` is the income used for
means-testing the monthly subsistence payment (Bürgergeld).

Having all of these concepts in the same namespace forces us to distinguish them by
including the name of the main transfer (e.g. `kinderzuschl_`) in the function's name.
Given the self-imposed character limit of 20 for user-facing columns, this requires
abbreviating words in the function name to a great extent, making it difficult for new
users of GETTSIM to read and understand. Even then `kinderzuschl_eink_relev_m_bg` is 8
characters too long.

These issues go beyond naming and could impact how future developers create tax and
transfer functions. Suppose you want to create a function that checks whether
`erziehungsgeld_eink_relev_kind_y` exceeds a certain threshold (see for example
`erziehungsgeld_ohne_abzug_m`). Given the strict 32-character limit for function names,
making the function's purpose clear would be challenging. This constraint may lead
developers to incorporate such checks in downstream functions of the DAG, potentially
violating our law-to-code approach.

With namespaces, we would have:

```
└── gettsim
 ├── kinderzuschlag
 │   ├── einkommen
 │       |── betrag_m_bg
 ├── arbeitslosengeld_2
 │   └── einkommen
 │       └── betrag_m_bg
 └── erziehungsgeld
     └── einkommen_kind
         └── betrag_m
```

- Names are unique within a namespace. It will be possible to have an `betrag` function
  within the Kinderzuschlag Namespace and a similar-named function within
  `arbeitslosengeld_2`. Hence, there is no ambiguity about which income is meant.

- The namespace will generally be represented as a tuple in GETTSIMs internal
  infrastructure. This will be the node identifier in the DAG, the value is the
  function. Along with pytree terminology, we will call the tuple the "path" and the
  function the "leaf". The last element of the path will be called the "leaf name".

- GETTSIM will take data inputs in the form of nested dictionaries. This structure
  allows users to define the namespace of a given data leaf via the dictionary keys
  (which, taken together as a tuple, represent the path of GETTSIMs DAG). GETTSIM will
  return outputs as nested dictionaries as well.

- Within the code, it will be possible to refer to other functions residing in the same
  namespace without having to prefix them with the entire path. For functions residing
  in other modules, the namespace will be a prefix with the tuple elements separated by
  double underscores, e.g., `arbeitslosengeld_2__einkommen__betrag_m_bg`. _(Note that
  the most readable separator would be a dot, but that does not work. In order to use
  the identifier as a function argument, it must be a valid Python identifier)_

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
   @policy_function(
      start_date="2003-04-01",
      end_date="2022-09-30",
      leaf_name="midijob_bemessungsentgelt_m",
   )
   def midijob_bemessungsentgelt_m_bis_09_2022(...):
       pass

   @policy_function(start_date="2022-10-01", leaf_name="midijob_bemessungsentgelt_m")
   def midijob_bemessungsentgelt_m_ab_10_2022(...):
       pass
   ```

   The behavior will be such that if the evaluation date is between the start and end
   date, the name found under `leaf_name` will be used as the leaf name.

   The defaults of start_date and end_date are such that they will cover the entire
   period one may want to use GETTSIM for.

   If two or more functions with the same path are added to the DAG (i.e. there are
   overlapping start and end dates), an error will be raised.

1. The yaml-files with parameters

   - Will live in the same directory as the other functions (=same namespace).
   - Will be parsed to custom data classes, which will become nodes in the DAG.

   Parsing the parameters will happen much like how policy functions are parsed. There
   is a standard way mapping dictionary contents in the yaml-files to corresponding data
   classes. Dates are selected by the `policy_environment` date. If there are changes in
   the structure of the parameters over time, a similar mechanism like the `start_date`
   and `end_date` for the policy functions can be used. The data classes will all
   inherit from a base class `PolicyParameter`.

   Functions will not have `[x]_params` arguments containing potentially large and
   unstructured dicts any more. Instead, functions will only use the `PolicyParameters`
   they require. These could be scalars or structured objects, e.g., the inputs for
   `piecewise_polynomial`.

   The namespace makes clear we are talking about, say, the function `beitrag` in the
   namespace `arbeitsl_v` will have an input `beitragssatz`. If we need parameters which
   are external to the current namespace, we will need the same verbose syntax as in 1.
   (`ges_rentenv__beitragsbemessungsgrenze`).

## Backward compatibility

The interface will get a complete overhaul, parts of which will be described in a
separate GEP. The most important direct consequence is that the structure of the input
data will be generated for each application, which can then be filled by the user. The
format of that will be a nested dictionary (or yaml-file) with the paths as keys and
values left empty. The user may then fill in the values with the column names in her
dataset. A similar renaming functionality will be added to the target data. Because of
this, we will not need to work around character limits anymore — users will never need
to access the internal structure of GETTSIM.

## Alternatives

Continuing with the status quo does not seem to be an option. We learned so much in the
past five years that now seems to be a good time to put those lessons into code.

## Discussion

There have been various discussions and preliminary implementations of some parts of
this GEP:

- Pull requests:
  - [#787](https://github.com/iza-institute-of-labor-economics/gettsim/pulls/787) Model
    classes for policy functions and policy environments
  - [#720](https://github.com/iza-institute-of-labor-economics/gettsim/pulls/720)
    Combined decorator for policy information,
  - [#638](https://github.com/iza-institute-of-labor-economics/gettsim/pulls/638) Don’t
    use functions in compute_taxes_and_transfers that are not active
  - [#804](https://github.com/iza-institute-of-labor-economics/gettsim/pulls/804)
    Namespaces for policy functions
- Issues:
  - [#781](https://github.com/iza-institute-of-labor-economics/gettsim/issues/781):
    Summary of interface discussion from 2024 GETTSIM workshop
- Zulip:
  - TBD

## Copyright

This document has been placed in the public domain.
