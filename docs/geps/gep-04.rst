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

This GEP explains the DAG-based computational backend for GETTSIM, which does not only
increase performance, but, and more importantly, offers a way to make changes to an
existing policy environment.


Motivation and Scope
--------------------

The implementation choice to use a DAG to represent the tax and transfers is motivated
by two primary reasons.

1. A tax and transfer system is constantly evolving in many dimensions due to the
   decisions of policy makers. Additionally, it is not enough to represent the state of
   the tax and transfer at any given point in time, but users need to be able to
   introduce their own changes. It is, hence, crucial to easily replace single
   functions or a set of functions within the tax and transfer system.

2. By using a DAG the user is able to limit the computations to a set of target
   variables, which the researcher is ultimately interested in. This prevents
   unnecessary calculations and increases the computation speed of GETTSIM.


Basic idea
----------

Based on the two requirements above we split the tax and transfer system into a set of
small functions. Each function calculates one clearly defined variable and returns it
as a :class:`pandas.Series`. All input variables are either the output of another
function or an input variable that the user provided (e.g. `bruttolohn_m`)

GETTSIM is able to calculate all requested variables by starting with the input
variables and calling the functions in the right order. This is accomblished via a
directed acyclic graph (DAG).

Splitting complex calculations into smaller pieces has a lot of the usual advantages of
why we use functions in the first place: readability, simplicity, lower maintenance
costs (see single-responsibility principle). Another advantage is that each function is
a potential entry point for a researcher to change the tax and transfer system if she
is able to replace this function with her own version.

See the following, intentionally abstract and incorrect example.

.. code-block:: python

    def kindergeld(anz_kinder_hh: IntSeries, kindergeld_params: dict) -> FloatSeries:
        return anz_kinder_hh * kindergeld_params["kindergeld"]

The function :func:`kindergeld` requires the variable ``anz_kinder_hh`` which is the
number of children per household. When the function is called, a :class:`pandas.Series`
with the information is passed to this argument. ``anz_kinder_hh`` has to be provided
by the user as input variable or has to be the name of another function.
``kindergeld_params`` is a dictionary of parameters related to the calculation of
kindergeld.

The result of this function is again a :class:`pandas.Series` which has the name
``kindergeld``, the same name as the function. Another function, say

.. code-block:: python

    def benefits(
        kindergeld: FloatSeries, arbeitsl_geld_2: FloatSeries, params: dict
    ) -> FloatSeries:
        pass

would need to have ``kindergeld`` as a name for an input argument to request this
:class:`pandas.Series`.

Mention:
- type annotations
- interface of `compute_taxes_and_transfers` (e.g. `override_columns`)?
-

Directed Acyclic Graph
~~~~~~~~~~~~~~~~~~~~~~

We can visualize the relationship between functions and their input variables in a graph
where nodes are variables in the data or computed by functions. Edges are pointing from
from input variables to other variables which require them to be computed. See this
`tutorial <../visualize_the_system.ipynb>`_ for some graphics.

The resulting structure is a special kind of graph which is called a directed-acyclic
graph (DAG). Directed and acyclic means that there exist no path of vertices which
starts at some node and ends at the same node. Equivalently, a DAG has a
topological ordering which is a sequence of nodes ordered from earlier to later in the
sequence. The topological ordering is what defines the sequence in which the functions
in the tax and transfer system are evaluated. This ensures that the inputs are already
computed before a dependent function is called.

When `compute_taxes_and_transfers` is called, GETTSIM builds a DAG based on the
requested targets and the provided input variables. Afterwards, all required functions
are called in the right order and the requested targets are calculated.


Usage and Impact
----------------

This GEP leads to a lot of changes which are best documented in the tutorials.

- The tutorial on the `interface <../tutorials/interface.ipynb>`_ offers a light
  introduction to the user interface.
- The tutorial on the `visualization <../tutorials/visualize_the_system.ipynb>`_ allows
  to inspect the tax and transfer system visually.


Detailed description
--------------------

The detailed descriptions and examples are provided in the tutorials.


Related Work
------------

- The `openfisca <https://github.com/openfisca/>`_ project uses an internal DAG as well.
- Scheduling computations on data with task graphs is how `Dask
  <https://docs.dask.org/>`_ splits and distributes computations.


Implementation
--------------

There are multiple PRs which incrementally rewrote GETTSIM for versions 0.3 and 0.4. See
the `release notes <../changes.rst>`_ for the linked PRs.


Alternatives
------------

We have not found any alternatives which offer the same amount of flexibility and
computational advantages.


Discussion
----------

*Not applicable.*


References and Footnotes
------------------------


Copyright
---------

This document has been placed in the public domain.
