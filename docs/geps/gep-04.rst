=========================================
GEP 4 — A DAG—based Computational Backend
=========================================

+------------+---------------------------------------------------------------+
| Author     | `Max Blesch <https://github.com/MaxBlesch>`_                  |
+            +---------------------------------------------------------------+
|            | `Janos Gabler <https://github.com/janosg>`_                   |
+            +---------------------------------------------------------------+
|            | `Hans-Martin von Gaudecker <https://github.com/hmgaudecker>`_ |
+            +---------------------------------------------------------------+
|            | `Tobias Raabe <https://github.com/tobiasraabe>`_              |
+------------+---------------------------------------------------------------+
| Status     | Draft                                                         |
+------------+---------------------------------------------------------------+
| Type       | Standards Track                                               |
+------------+---------------------------------------------------------------+
| Created    | 2020-05-05                                                    |
+------------+---------------------------------------------------------------+
| Resolution | <url> (required for Accepted or Rejected or Withdrawn)        |
+------------+---------------------------------------------------------------+


Abstract
--------

This GEP explains the DAG-based computational backend for gettsim which does not only
increase performance, but, and more importantly, offers a way to make small changes to
an existing policy environment.


Motivation and Scope
--------------------

The change is motivated by two primary reasons.

1. A tax and transfer system is constantly evolving in many dimensions due to the
   decisions of policy makers. But, it is not enough to represent the state of the tax
   and transfer at any given point in time, because researchers want to study the
   effects of counterfactual scenarios. In these scenarios, they introduce their own
   changes which can be more local - changing the functional form of an existing policy
   - or more global - replacing the social benefits system with a universal basic
   income.

2. Computing taxes and transfers with gettsim takes a long time. The major reason is
   that the current implementation does not use vectorization. The second reason is that
   it is not possible to limit the computations to a set of target variables which the
   researcher is ultimately interested in.


Solution
--------

At the core of the solution is the following observation. To compute variables in the
tax and transfer system, the user starts with some input data. A variable in the tax and
transfer system can be computed by a function which receives the data and parameters as
inputs and yields the variable. Since a single function might become too complex, we
could split up the function into multiple functions which receive the data and
parameters and compute intermediate outcomes. Then, the task is to call the collection
of functions in the correct order and pass in the correct data and parameters. The last
function in this collection will receive the intermediate outcomes and calculate the
requested target variable.

Splitting complex calculations into smaller pieces has a lot of the usual advantages of
why we use functions in the first place: readability, simplicity, lower maintenance
costs (see single-responsibility principle). Another advantage is that each function is
a potential entrypoint for a researcher to change the tax and transfer system if she is
able to replace this function with her own version.

Two questions arise.

1. How do we know which data and parameters to pass to the functions?

To solve the first problem, we were inspired by `pytest and its fixtures
<https://docs.pytest.org/en/stable/fixture.html>`_. The idea is that every variable has
a name which is also a valid variable name in Python (cannot start with number,
alphanumeric, lower- and uppercase, underscores). Then, a function inside the tax and
transfer system uses this name as an input argument. See the following, intentionally
abstract and incorrect example.

.. code-block:: python

    def kindergeld(anz_kinder_hh, kindergeld_params):
        pass

The function :func:`kindergeld` requires the variable ``anz_kinder_hh`` which is the
number of children per household. When the function is called, a :class:`pandas.Series`
with the information is passed to this argument. The same happens to the parameters
where ``"kindergeld"`` is a single parameter-topic inside the collection of all
parameters and ``kindergeld_params`` is a dictionary.

The result of this function is again a :class:`pandas.Series` which has the name
``kindergeld``, the same name as the function. Another function, say

.. code-block:: python

    def benefits(kindergeld, arbeitsl_geld_2, params):
        pass

would need to have ``kindergeld`` as a name for an input argument to request this
:class:`pandas.Series`.

2. How do we ensure the order in which functions are called?

The second problem calls for a real classic of computer science. We can visualize the
relationship between functions and their input variables in a graph where nodes are
variables in the data or computed by functions. Edges are pointing from from input
variables to other variables which require them to be computed. See this `tutorial
<../visualize_the_system.ipynb>`_ for some graphics.

The resulting structure is a special kind of graph which is called a directed-acyclic
graph (DAG). Directed and acyclic means that there exist no path of vertices which
starts at some node :math:`\vega` and ends at the same node. Equivalently, a DAG has a
topological ordering which is a sequence of nodes ordered from earlier to later in the
sequence. The topological ordering is what defines the sequence in which the functions
in the tax and transfer system are evaluated. This ensures that the inputs are already
computed before a dependent function is called.


Usage and Impact
----------------

This GEP leads to a lot of changes which are best documented in the tutorials.

- The tutorial on the `interface <../tutorials/interface.ipynb>`_ offers a light
  introduction to the user interface.
- The tutorial on the `visualization <../tutorials/visualize_the_system.ipynb>`_ allows
  to inspect the tax and transfer system visually.


Backward compatibility
----------------------

The changes proposed by this GEP lead to a complete rewrite of gettsim.


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

There are multiple PRs which incrementally rewrote gettsim in version 0.3 and 0.4. See
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

.. [1] Each GEP must either be explicitly labeled as placed in the public domain (see
       this GEP as an example) or licensed under the `Open Publication License`_.

.. _Open Publication License: https://www.opencontent.org/openpub/

.. _#general/geps: https://gettsim.zulipchat.com/#narrow/stream/212222-general/topic/GEPs


Copyright
---------

This document has been placed in the public domain. [1]_
