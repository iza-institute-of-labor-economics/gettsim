.. _gep-4:

=========================================
GEP 4 — A DAG—based Computational Backend
=========================================

+------------+------------------------------------------------------------------+
| Author     | `Max Blesch <https://github.com/MaxBlesch>`_                     |
+            +------------------------------------------------------------------+
|            | `Janos Gabler <https://github.com/janosg>`_                      |
+            +------------------------------------------------------------------+
|            | `Hans-Martin von Gaudecker <https://github.com/hmgaudecker>`_    |
+            +------------------------------------------------------------------+
|            | `Tobias Raabe <https://github.com/tobiasraabe>`_                 |
+            +------------------------------------------------------------------+
|            | `Christian Zimpelmann <https://github.com/ChristianZimpelmann>`_ |
+------------+------------------------------------------------------------------+
| Status     | Draft                                                            |
+------------+------------------------------------------------------------------+
| Type       | Standards Track                                                  |
+------------+------------------------------------------------------------------+
| Created    | 2021-12-xx                                                       |
+------------+------------------------------------------------------------------+
| Resolution | <url> (required for Accepted or Rejected or Withdrawn)           |
+------------+------------------------------------------------------------------+


Abstract
--------

This GEP explains the directed acyclic graph (DAG)-based computational backend for
GETTSIM.


Motivation
----------

The implementation choice to use a DAG to represent the taxes and transfers system is
motivated by two main reasons.

1. The taxes and transfers system is constantly evolving in many dimensions,
   flexibility is thus needed internally. Additionally, it is not enough to represent
   the state of the system at any given point in time, but users need to be able to
   introduce their own changes. Being able to change or replace any part of the taxes
   and transfers system is crucial. Put differently, there is no meaningful distinction
   between parts of the system only ever touched by developers and parts that are
   modifiable by users. A DAG implementation allows to eliminate this usual boundary
   for almost all use cases.

1. By using a DAG the user is able to limit computations to a set of target variables,
   which she is ultimately interested in. This prevents unnecessary calculations and
   increases computation speed.


Basic idea
----------

Based on the two requirements above we split the tax and transfer system into a set of
small functions. Each function calculates one clearly defined variable (identical to
the function's name) and returns it as a :class:`Series`. Typically, function arguments
are either user-provided input variables (e.g. `bruttolohn_m`) or outputs of other
functions in the taxes and transfers system. The only other potential additional
arguments are parameters of the taxes and transfers system, which are pre-defined.

GETTSIM is able to calculate the variables a researcher is interested in by starting
with the input variables and calling the required functions in a correct order. This is
accomplished via a DAG (see below).

Splitting complex calculations into smaller pieces has a lot of the usual advantages of
why we use functions when programming: readability, simplicity, lower maintenance costs
(see single-responsibility principle). Another advantage is that each function is a
potential entry point for a researcher to change the taxes and transfers system if she
is able to replace this function with her own version.

See the following example for capital income taxes.

.. code-block:: python

    def abgelt_st_tu(
        zu_verst_kapital_eink_tu: FloatSeries, abgelt_st_params: dict
    ) -> FloatSeries:
        """Calculate abgeltungssteuer per tax unit.

        Parameters
        ----------
        zu_verst_kapital_eink_tu
            See :func:`zu_verst_kapital_eink_tu`.
        abgelt_st_params
            See params documentation :ref:`abgelt_st_params <abgelt_st_params>`.

        Returns
        -------

        """
        return abgelt_st_params["abgelt_st_satz"] * zu_verst_kapital_eink_tu

The function :func:`abgelt_st_tu` requires the variable ``zu_verst_kapital_eink_tu``
which is the amount of taxable capital income per tax unit (the latter is implied by the
``_tu`` suffix, see :ref:`gep-1`). ``zu_verst_kapital_eink_tu``  has to be provided by
the user as an input variable or it has to be the name of another function. In any case,
it needs to be a :class:`pandas.Series` with an appropriate index. ``abgelt_st_params``
is a dictionary of parameters related to the calculation of ``abgelt_st_tu``.

The result of this function is again a :class:`pandas.Series` which has the name
``abgelt_st_tu``, the same name as the function. Another function, say

.. code-block:: python

    def soli_st_tu(
        st_kind_freib_tu: FloatSeries,
        anz_erwachsene_tu: IntSeries,
        abgelt_st_tu: FloatSeries,
        soli_st_params: dict,
    ) -> FloatSeries:
        ...


would need to have ``abgelt_st_tu`` as a name for an input argument to request this
:class:`pandas.Series`.

Note that the type annotations (e.g. `FloatSeries`) indicate the expected type of each
input and the output of a function.


Directed Acyclic Graph
----------------------

The relationship between functions and their input variables is a graph where nodes are
variables. These variables must either be present in the data supplied to GETTSIM or
they are computed by functions. Edges are pointing from input variables to variables,
which require them to be computed. See this `tutorial <../visualize_the_system.ipynb>`_
for how to visualize this.

The resulting structure is a special kind of graph, called a directed acyclic graph
(DAG). It is directed because there are clearly inputs and outputs, i.e., a sense of
direction. Acyclic means that there exist no path along the direction of the edges,
where you start at some node and end up at the same node. Equivalently, a DAG has a
topological ordering which is a sequence of nodes ordered from earlier to later in the
sequence. The topological ordering is what defines the sequence in which the functions
in the taxes and transfers system are evaluated. This ensures that the inputs are
already computed before a function that requires them is called.

When ``compute_taxes_and_transfers`` is called, GETTSIM builds a DAG based on three
inputs provided by the user:

 - A set of functions of the tax and transfer system, which consist of the ones
   pre-implemented in GETTSIM and potentially user-written additional functions.
 - The targets of interest.
 - The input variables.

 The DAG is then used to call all required functions in the right order and to
 calculate the requested targets.


Level of the DAG and limitations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The DAG sketched above allows for great flexibility at any given point in time. It also
allows the user to override any function easily. However, it does not allow the
interface of functions to change over time, new functions to appear, or old ones to
disappear.

Some examples include:

1. `arbeitsl_hilfe` being replaced by `arbeitsl_geld_2`
1. `kinderbonus` being active only in a few years
1. The introduction of `kinderzuschlag`
1. Capital income entering `sum_brutto_eink` or not.

The current solution handles the case of changing interfaces like this (example 4.):

.. code-block:: python

    if year < 2009:
        functions["sum_brutto_eink"] = sum_brutto_eink_mit_kapital
    else:
        functions["sum_brutto_eink"] = sum_brutto_eink_ohne_kapital


However, all functions will be present in all years in principle. This is not
satisfactory; ideally, functions would only be present in years where they actually
exist.

.. todo::

    Brainstorm to look for a sensible solution. Ideally want:

    - Minimal set of functions for a given policy year
    - Users putting together their policy environment based on functions from different years
    - ...

Additional functionalities
--------------------------

We implemented a small set of additional features that simplify the specification of
certain types of functions of the tax and transfer system.


.. _gep-4-group-sums:

Group summation of variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Individual-level measures often need to be summed up to a group level. GETTSIM automates
this process for groups of individuals defined in :ref:`gep-1` (households ``_hh`` and
tax units ``_tu``).

In case an individual-level column `[column]` exists, the graph will be augmented with a
node including a group sum like `[column]_hh` should that be requested. Requests can be
either inputs in a downstream function or explicit targets of the calculation.

Automatic summation will only happen in case no column `[column]_hh` is explicitly set.
Using a different reduction function than the sum is as easy as explicitly specifying
`[column]_hh`.

Consider the following example: the function ``kindergeld_m`` calculates the
individual-level child benefit payment. ``arbeitsl_geld_2_m_hh`` calculates
Arbeitslosengeld 2 on the household level (as indicated by the suffix). One necessary
input of this function is the sum of all child benefits on the household level. There is
no function or input column ``kindergeld_m_hh``.

By including ``kindergeld_m_hh`` as an argument in the definition of
``arbeitsl_geld_2_m_hh`` as follows:

.. code-block:: python

    def arbeitsl_geld_2_m_hh(
        kindergeld_m_hh: FloatSeries, other_arguments: FloatSeries
    ) -> FloatSeries:
        ...

a node ``kindergeld_m_hh`` containing the household-level sum of ``kindergeld_m`` will
be automatically added to the graph. Its parents in the graph will be ``kindergeld_m``
and ``hh_id``.


.. _gep-4-time-unit-conversion:

Conversion between reference periods
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Similarly to :ref:`gep-4-group-sums`, GETTSIM will automatically convert values
referring to different reference periods defined in :ref:`gep-1` (years (default, no
suffix), months ``_m``, weeks ``_w``, and days ``_t``).

In case a column with annual values `[column]` exists, the graph will be augmented with
a node including monthly values like `[column]_m` should that be requested. Requests can
be either inputs in a downstream function or explicit targets of the calculation. In
case the column refers to a different level of aggregation, say ``[column]_hh``, the
same applies to ``[column]_m_hh``.

Automatic summation will only happen in case no column `[column]_m` is explicitly set.
Using a different conversion function than the sum is as easy as explicitly specifying
`[column]_m`.

Conversion goes both ways and uses the following formulas:

+-----------+--------+------------+
| time unit | suffix | factor     |
+-----------+--------+------------+
| year      |        | 1          |
+-----------+--------+------------+
| month     | `_m`   | 12         |
+-----------+--------+------------+
| week      | `_w`   | 365.25 / 7 |
+-----------+--------+------------+
| day       | `_t`   | 365.25     |
+-----------+--------+------------+

These values average over leap years. They ensure that conversion is always possible
both ways without changing quantities. In case more complex conversions are needed (for
example to account for irregular days per month, leap years, or the like), explicit
functions for, say, ``[column]_w`` need to be set.


Functions defined only for a subset of years
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. todo::

    Describe current solution of the future implementation once we decide on a better
    solution.

Related Work
------------

- The `openfisca <https://github.com/openfisca/>`_ project uses an internal DAG as well.
- Scheduling computations on data with task graphs is how `Dask
  <https://docs.dask.org/>`_ splits and distributes computations.


Alternatives
------------

We have not found any alternatives which offer the same amount of flexibility and
computational advantages.



Copyright
---------

This document has been placed in the public domain.
