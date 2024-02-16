(gep-2)=

# GEP 2 — Internal Representation of Data on Individuals

```{list-table}
- * Author
  * [Hans-Martin von Gaudecker](https://github.com/hmgaudecker)
- * Status
  * Provisional
- * Type
  * Standards Track
- * Created
  * 2022-03-28
- * Resolution
  * [Accepted](https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2002)
```

## Abstract

This GEP lays out how GETTSIM stores the user-provided data (be it from the SOEP, EVS,
example individuals, ...) and passes it around to the functions calculating taxes and
transfers.

Data will be stored as a collection of 1-d arrays, each of which corresponds to a column
in the data provided by the user (if it comes in the form of a DataFrame) or calculated
by GETTSIM. All these arrays have the same length. This length corresponds to the number
of individuals. Functions operate on a single row of data.

If a column name is `[x]_id` with `x` {math}`\in \{` `hh`, `tu` {math}`\}`, it will be
the same for all households, tax units, or any other grouping of individuals specified
in {ref}`GEP 1 <gep-1-column-names>`.

Any other column name ending in `_id` indicates a link to a different individual (e.g.,
child-parent relations could be `parent_0_ind_id`, `parent_1_ind_id`; receiver of child
benefits would be `kindergeldempf_id`).

## Motivation and Scope

Taxes and transfers are calculated at different levels of aggregation: Individuals,
couples, families, households. Sometimes, relations between individuals are important:
parents and children, payors/receivers of alimony payments, which parent receives the
`kindergeld` payments, etc..

Potentially, there are many ways of storing these data: Long form, wide form,
collections of tables adhering to
[database normal forms](https://en.wikipedia.org/wiki/Database_normalization),
N-dimensional arrays, etc.. As usual, everything involves trade-offs, for example:

- Normal forms require many merge / join operations, which the tools we are using are
  not optimised for.

- One N-dimensional array is not possible because groups are not necessarily nested

- Almost all functions are much easier to implement when working with a single row. This
  is most important for the typical user and increasing the number of developers.

- Modern tools for vectorization (e.g., Jax) scale best when working with single rows of
  data.

  Aggregation to groups of individuals (households, tax units) or referencing data from
  other rows (parents, receiver of child benefits) is not trivial with these tools.

## Usage and Impact

This is primarily internal, i.e., only relevant for developers as the highest-level
interface can be easily adjusted. The default way to receive data will be one Pandas
DataFrame.

Users are affected only via the interface of lower-level functions. Under the proposed
implementation, they will always work on single rows of data. Many alternatives would
require users to write vectorised code, making filtering operations more cumbersome. For
aggregation or referencing other individuals' data, GETTSIM will provide functions that
allow abstracting from implementation details, see
{ref}`below <gep-2-aggregation-functions>`.

## Detailed description

The following discussion assumes that data is passed in as a Pandas DataFrame. It will
be possible to pass data directly in the form that GETTSIM requires it internally. In
that case, only the relevant steps apply.

- GETTSIM will first make a check that all identifiers pointing to other individuals
  (e.g., `kindergeldempf_id`) are valid.

- GETTSIM will then create internal identifiers for individuals, households, and tax
  units. GETTSIM will also generate appropriate columns with identifiers pointing to
  other individuals. Columns with the original values are stored.

  All internal identifiers are integers starting at 0 and counting in increments of 1.
  For individuals, they are sorted, implying they can be used to index into the arrays.
  It also means that identifiers pointing to other individuals can be used directly for
  indexing.

  Because groups of individuals are not necessarily nested (e.g., joint taxation during
  separation phase but living in different households), they cannot be sorted in
  general. In case users know their data allows sorting on all groups (i.e., all groups
  have a nesting structure), they will be able to provide a `data_is_sorted` flag, which
  defaults to `False`.

- The core of GETTSIM works with a collection of 1-d arrays, all of which have the same
  length as the number of individuals.

  These arrays form the nodes of its DAG computation engine (see {ref}`GEP 4 <gep-4>`).

- GETTSIM returns an object of the same type and with the same identifiers that was
  passed by the user.

- GETTSIM strives to show errors along with the original indices, but this may not
  always be possible.

(gep-2-aggregation-functions)=

### Grouped values and aggregation functions

Often columns refer to groups of individuals. Such columns have a suffix indicating the
group (see {ref}`GEP 1 <gep-1-column-names>`, currently `_hh` or `_tu`). These columns'
values will be repeated for all individuals who form part of a group.

By default, GETTSIM will check consistency on input columns in this respect. Users will
be able to turn this check off.

Aggregation functions will be provided by GETTSIM.

- Aggregation will always start from the individual level. If aggregation from, say, tax
  unit to household is required (and possible), users will first need to provide an
  appropriate individual-level column (e.g., by dividing some tax unit-level aggregate
  by the number of members in the tax unit)

- As outlined in {ref}`GEP 4 <gep-4-aggregation-by-group-functions>` users will need to
  specify:

  - The stringified name of the aggregated variable. This **must** end with a feasible
    unit of aggregation, i.e., `_hh` or `_tu`
  - The stringified name of the original variable.
  - The type of aggregation {math}`\in \{` `sum`, `mean`, `max`, `min`, `any` {math}`\}`

  Note that as per {ref}`GEP 4 <gep-4-aggregation-by-group-functions>`, sums will be
  calculated implicitly if the graph contains a column `my_col` and an aggregate such as
  `my_col_hh` is requested somewhere.

Note that the groups `tu` and `hh` may change in the future. Some might also be
calculated via relations between household members, see
[discussion](https://gettsim.zulipchat.com/#narrow/stream/224837-High-Level-Architecture/topic/Update.20Data.20Structures/near/180917151)
on Zulip in this respect.

## Alternatives

Versions 0.3 -- 0.4 of GETTSIM used a collection of pandas Series. This proved to be
cumbersome because case distinctions had to be made in vectorized code (e.g., picking
different values from the parameter database depending on a child's age).

Adhering to normal forms (e.g., reducing the length of arrays to the number of
households like
\[here\](<https://www.tensorflow.org/api_docs/python/tf/math/segment_sum>) would have
led to many merge-like operations in user functions.

## Discussion

- Some
  [discussion on Zulip](https://gettsim.zulipchat.com/#narrow/stream/224837-High-Level-Architecture/topic/Update.20Data.20Structures/near/180917151)
  re data structures.
- Zulip stream for
  [GEP 2](https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2001/near/189539859).

## Copyright

This document has been placed in the public domain.
