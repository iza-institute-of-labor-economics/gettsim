(gep-4)=

# GEP 4 — A DAG—based Computational Backend

```{list-table}
- * Author
  * [Max Blesch](https://github.com/MaxBlesch),
    [Janos Gabler](https://github.com/janosg),
    [Hans-Martin von Gaudecker](https://github.com/hmgaudecker),
    [Tobias Raabe](https://github.com/tobiasraabe),
    [Christian Zimpelmann](https://github.com/ChristianZimpelmann)
- * Status
  * Provisional
- * Type
  * Standards Track
- * Created
  * 2022-03-28
- * Resolution
  * [Accepted](https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2004)
```

## Abstract

This GEP explains the directed acyclic graph (DAG)-based computational backend for
GETTSIM.

The graph operates on columns of data. Stringified function names and their inputs
correspond to columns in the data, i.e., nodes in the graph.

Unless functions perform aggregations, they are written in terms of scalars and
vectorized during DAG setup.

## Motivation

The implementation choice to use a DAG to represent the taxes and transfers system is
motivated by two main reasons.

1. The taxes and transfers system is constantly evolving in many dimensions, flexibility
   is thus needed internally. Additionally, it is not enough to represent the state of
   the system at any given point in time, but users need to be able to introduce their
   own changes. Being able to change or replace any part of the taxes and transfers
   system is crucial. Put differently, there is no meaningful distinction between parts
   of the system only ever touched by developers and parts that are modifiable by users.
   A DAG implementation allows to eliminate this usual boundary for almost all use
   cases.

1) The DAG allows a user to limit computations to generate a set of target variables,
   which she is ultimately interested in. Doing so allows cutting down on the number of
   input variables, it prevents unnecessary calculations, and it increases computation
   speed.

## Basic idea

Based on the two requirements above we split the taxes and transfers system into a set
of small functions. Each function calculates one clearly defined variable (identical to
the function's stringified name) and returns a 1d-array.

```{note}
The function code itself will typically work on scalars and is vectorized by
GETTSIM; this is irrelevant for the DAG.
```

Function arguments can be of three kinds:

- User-provided input variables (e.g., `bruttolohn_m`).
- Outputs of other functions in the taxes and transfers system (e.g., `eink_st_y_tu`).
- Parameters of the taxes and transfers system, which are pre-defined and always end in
  `_params` (e.g., `ges_rentenv_params`).

GETTSIM will calculate the variables a researcher is interested in by starting with the
input variables and calling the required functions in a correct order. This is
accomplished via a DAG (see below).

Splitting complex calculations into smaller pieces has a lot of the usual advantages of
why we use functions when programming: readability, simplicity, lower maintenance costs
(single-responsibility principle). Another advantage is that each function is a
potential entry point for a researcher to change the taxes and transfers system if she
is able to replace this function with her own version.

See the following example for capital income taxes.

```python
def abgelt_st_y_tu(zu_verst_kapitaleink_y_tu: float, abgelt_st_params: dict) -> float:
    """Calculate Abgeltungssteuer on tax unit level.

    Parameters
    ----------
    zu_verst_kapitaleink_y_tu
        See :func:`zu_verst_kapitaleink_y_tu`.
    abgelt_st_params
        See params documentation :ref:`abgelt_st_params <abgelt_st_params>`.

    Returns
    -------

    """
    return abgelt_st_params["satz"] * zu_verst_kapitaleink_y_tu
```

The function {func}`abgelt_st_y_tu` requires the variable `zu_verst_kapital_eink_y_tu`,
which is the amount of taxable capital income on tax unit level (the latter is implied
by the `_tu` suffix, see {ref}`gep-1`). `zu_verst_kapital_eink_y_tu` must be provided by
the user as a column of the input data or it has to be the name of another function.
`abgelt_st_params` is a dictionary of parameters related to the calculation of
`abgelt_st_y_tu`.

Another function, say

```python
def soli_st_y_tu(
    eink_st_mit_kinderfreib_y_tu: float,
    anz_erwachsene_tu: int,
    abgelt_st_y_tu: float,
    soli_st_params: dict,
) -> float: ...
```

may use `abgelt_st_y_tu` as an input argument. The DAG backend ensures that the function
`abgelt_st_y_tu` will be executed first.

Note that the type annotations (e.g. `float`) indicate the expected type of each input
and the output of a function, see {ref}`gep-2`.

## Directed Acyclic Graph

The relationship between functions and their input variables is a graph where nodes
represent columns in the data. These columns must either be present in the data supplied
to GETTSIM or they are computed by functions. Edges are pointing from input columns to
variables, which require them to be computed.

```{note}
GETTSIM allows to visualize the graph, see this [guide](../how_to_guides/visualizing_the_system.ipynb).
```

The resulting structure is a special kind of graph, called a directed acyclic graph
(DAG). It is directed because there are clearly inputs and outputs, i.e., there is a
sense of direction. Acyclic means that there exist no path along the direction of the
edges, where you start at some node and end up at the same node. Equivalently, a DAG has
a topological ordering which is a sequence of nodes ordered from earlier to later in the
sequence. The topological ordering is what defines the sequence in which the functions
in the taxes and transfers system are evaluated. This ensures that the inputs are
already computed before a function that requires them is called.

In order to calculate a set of taxes and transfers, GETTSIM builds a DAG based on three
inputs provided by the user:

> - Input data.
>
> - A set of functions representing the taxes and transfers system, which consist of the
>   ones pre-implemented in GETTSIM and potentially user-written additional functions.
>
>   Parameters of the taxes and transfers system can be ignored in the following (they
>   amount to collections of constants; in practice they will already be partialled into
>   these functions). These functions need to be written for scalars; they will be
>   vectorised during the set up of the DAG.
>
> - A set of dictionaries specifying aggregation functions, calculating, for example,
>   household-level averages.
>
> - The target columns of interest.

The DAG is then used to call all required functions in the right order and to calculate
the requested targets.

### Level of the DAG and limitations

In principle, GETTSIM will import all functions defined in the modules describing the
taxes and transfers system. In principle, these functions refer to all years in
GETTSIM's scope. There has to be some discretion in order to allow for the interface of
functions to change over time, new functions to appear, or old ones to disappear.

Some examples include:

1. `arbeitsl_hilfe` being replaced by `arbeitsl_geld_2`.
1. `kinderbonus` being active only in a few years.
1. The introduction of `kinderzuschl`.
1. Capital income entering `sum_brutto_eink` or not.

The goal is that the graph for any particular point in time is minimal in the sense that
`arbeitsl_geld_2` does not appear before it was conceived, it is apparent from the
interface of `sum_brutto_eink` whether it includes capital income or not, etc..

In the yaml-files corresponding to a particular tax / transfer, functions not present in
all years will need to be listed with along with the dates for when they are active. See
:gep-3-keys-referring-to-functions: for the precise syntax. That mechanism should be
used for:

1. Functions that are newly introduced.

1. Functions that cease to be relevant.

1. Functions whose interface changes over time.

1. Functions whose body changes so much that

   - it is useful to signal that things have changed and/or
   - it would be awkward to program the different behaviors in one block with case
     distinctions.

Needless to say, the different reasons may appear at different points in time for the
same function.

## Additional functionalities

We implemented a small set of additional features that simplify the specification of
certain types of functions of the taxes and transfers system.

(gep-4-aggregation-by-group-functions)=

### Group summation and other aggregation functions

Many taxes or transfers require group-level variables. \<GEP-2 describes
`gep-2-aggregation-functions`> how reductions are handled in terms of the underlying
data. This section describes how to specify them.

In order to inject aggregation functions at the group level into the graph, scripts with
functions of the taxes and transfer system should define a dictionary
`aggregate_by_group_[script_name]` at the module level. This dictionary must specify the
aggregated columns as keys and a dictionary with keys `source_col` and `aggr` as values.
If `aggr` is `count`, `source_col` is not needed.

For example, in `demographic_vars.py`, we could have:

```
aggregate_by_group_demographic_vars = {
    "anz_erwachsene_tu": {"source_col": "erwachsen", "aggr": "sum"},
    "haushaltsgröße_hh": {"aggr": "count"},
}
```

The group identifier (`tu_id`, `hh_id`) will be automatically included as an argument;
for `count` no other variable is necessary.

The output type will be the same as the input type. Exceptions:

- Input type `bool` and aggregation `sum` leads to output type `int`.
- Input type `int` and aggregation {math}`\in \{` `any`, `all` {math}`\}` leads to
  output type `bool`
- Aggregation `count` will always result in an `int`.

The most common operation are sums of individual measures. GETTSIM adds the following
syntactic sugar: In case an individual-level column `my_col` exists, the graph will be
augmented with a node including a group sum like `my_col_hh` should that be requested.
Requests can be either inputs in a downstream function or explicit targets of the
calculation.

Automatic summation will only happen in case no column `my_col_hh` is explicitly set.
Using a different reduction function than the sum is as easy as explicitly specifying
`my_col_hh`.

Consider the following example: the function `kindergeld_m` calculates the
individual-level child benefit payment. `arbeitsl_geld_2_m_bg` calculates
Arbeitslosengeld 2 on the Bedarfsgemeinschaft (bg) level (as indicated by the suffix).
One necessary input of this function is the sum of all child benefits on the
Bedarfsgemeinschaft level. There is no function or input column `kindergeld_m_bg`.

By including `kindergeld_m_bg` as an argument in the definition of
`arbeitsl_geld_2_m_bg` as follows:

```python
def arbeitsl_geld_2_m_bg(kindergeld_m_bg, other_arguments): ...
```

a node `kindergeld_m_bg` containing the Bedarfsgemeinschaft-level sum of `kindergeld_m`
will be automatically added to the graph. Its parents in the graph will be
`kindergeld_m` and `bg_id`. This is the same as specifying:

```
aggregate_by_group_kindergeld =  = {
    "kindergeld_m_bg": {
        "source_col": "kindergeld_m",
        "aggr": "sum"
    }
}
```

(gep-4-aggregation-by-p-id-functions)=

### Aggregation based on person-to-person pointers

For some taxes and transfers, one person may establish a claim for another person. A
parent, for example, has a claim on the basic child allowance (Kindergeld) because their
child is eligible for it. Similarly, parents receive a tax allowance because their child
satisfies the criteria for it. These aggregation operations are based on the `p_id`
column. This section describes how to specify such taxes and transfers.

The implementation is similar to aggregations to the level of groupings: In order to specify new aggregation
functions, scripts with functions of the taxes and transfer system should define a
dictionary `aggregate_by_p_id_[script_name]` at the module level. This dictionary must
specify the aggregated columns as keys and a dictionary with keys `source_col`,
`p_id_to_aggregate_by` and `aggr` as values. If `aggr` is `count`, `source_col` is not
needed.

The key `source_col` specifies which column is the source of the aggregation operation.
The key `p_id_to_aggregate_by` specifies the column that indicates to which `p_id` the
values in `source_col` should be ascribed to. The key `aggr` gives the aggregation
method.

For example, in `kindergeld.py`, we could have:

```
aggregate_by_p_id_kindergeld = {
    "kindergeld_anz_ansprüche": {
        "p_id_to_aggregate_by": "p_id_kindergeld_empf",
        "source_col": "kindergeld_anspruch",
        "aggr": "sum",
    },
}
```

This dict creates a target function `kindergeld_anz_ansprüche` which gives the amount of
claims that a person has on Kindergeld, based on the `kindergeld_anspruch` function
which returns Booleans, which show whether a child is a reason for a Kindergeld claim.

The output type will be the same as the input type. Exceptions:

- Input type `bool` and aggregation `sum` leads to output type `int`.
- Input type `int` and aggregation {math}`\in \{` `any`, `all` {math}`\}` leads to
  output type `bool`
- Aggregation `count` will always result in an `int`.

(gep-4-time-unit-conversion)=

### Conversion between reference periods

Similarly to summations to the group level, GETTSIM will automatically convert values
referring to different reference periods defined in {ref}`gep-1` (years (default, no
suffix), months `_m`, weeks `_w`, and days `_d`).

In case a column with annual values `[column]` exists, the graph will be augmented with
a node including monthly values like `[column]_m` should that be requested. Requests can
be either inputs in a downstream function or explicit targets of the calculation. In
case the column refers to a different level of aggregation, say `[column]_hh`, the same
applies to `[column]_m_hh`.

Automatic summation will only happen in case no column `[column]_m` is explicitly set.
Using a different conversion function than the sum is as easy as explicitly specifying
`[column]_m`.

Conversion goes both ways and uses the following formulas:

```{eval-rst}
| time unit | suffix | factor     |
| Year      |        | 1          |
| Month     | ``_m`` | 12         |
| Week      | ``_w`` | 365.25 / 7 |
| Day       | ``_d`` | 365.25     |
```

These values average over leap years. They ensure that conversion is always possible
both ways without changing quantities. In case more complex conversions are needed (for
example to account for irregular days per month, leap years, or the like), explicit
functions for, say, `[column]_w` need to be set.

## Related Work

- The [OpenFisca](https://github.com/openfisca) project uses an internal DAG as well.
- Scheduling computations on data with task graphs is how [Dask](https://docs.dask.org/)
  splits and distributes computations.
- Based on GETTSIM and many other projects, the
  [dags](https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2004)
  project combines the core ideas in one spot. GETTSIM will likely use it to implement
  functionality at some point.

## Alternatives

We have not found any alternatives which offer the same amount of flexibility and
computational advantages.

## Discussion

- <https://github.com/iza-institute-of-labor-economics/gettsim/pull/178>
- <https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2004>

## Copyright

This document has been placed in the public domain.
