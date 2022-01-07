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

1. The taxes and transfers system is constantly evolving in many dimensions, flexibility
   is thus needed internally. Additionally, it is not enough to represent the state of
   the system at any given point in time, but users need to be able to introduce their
   own changes. Being able to change or replace any part of the taxes and transfers
   system is crucial. Put differently, there is no meaningful distinction between parts
   of the system only ever touched by developers and parts that are modifiable by users.
   A DAG implementation allows to eliminate this usual boundary for almost all use
   cases.

1. By using a DAG the user is able to limit computations to a set of target variables,
   which she is ultimately interested in. This prevents unnecessary calculations and
   increases computation speed.


Basic idea
----------

Based on the two requirements above we split the tax and transfer system into a set of
small functions. Each function calculates one clearly defined variable (identical to the
function's name) and returns it as a :class:`Series`. All input variables of a function
are either a user-provided input variables (e.g. `bruttolohn_m`) or the output of
another function. The only other potential additional arguments are parameters of the
tax and transfer system, which are pre-defined.

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


would need to have ``kindergeld`` as a name for an input argument to request this
:class:`pandas.Series`.

Note that the type annotations (e.g. `FloatSeries`) indicate the expected type of each
input and the output of a function.


Directed Acyclic Graph
~~~~~~~~~~~~~~~~~~~~~~

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


However, all functions will be present in all years in principle.
This is not satisfactory; ideally, functions would only be present in years where they actually exist.

.. todo::

    Brainstorm to look for a sensible solution. Ideally want:

    - Minimal set of functions for a given policy year
    - Users putting together their policy environment based on functions from different years
    - ...



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
