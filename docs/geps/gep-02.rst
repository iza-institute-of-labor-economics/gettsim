.. _gep-2:

=======================================================
GEP 2 — Internal Representation of Data on Individuals
=======================================================

+------------+-------------------------------------------------------------------------+
| Author     | `Hans-Martin von Gaudecker <https://github.com/hmgaudecker>`_           |
+------------+-------------------------------------------------------------------------+
| Status     | Draft                                                                   |
+------------+-------------------------------------------------------------------------+
| Type       | Standards Track                                                         |
+------------+-------------------------------------------------------------------------+
| Created    | 2020-02-22                                                              |
+------------+-------------------------------------------------------------------------+
| Resolution | <url> (required for Accepted | Rejected | Withdrawn)                    |
+------------+-------------------------------------------------------------------------+


Abstract
--------

This GEP lays out how GETTSIM stores the user-provided data (be it from the SOEP, EVS,
example individuals, ...) and passes it around to the functions calculating taxes and
transfers.

Data will be stored as a collection of 1-d arrays, each of which corresponds to a column
in the data provided by the user (if it comes in the form of a DataFrame). All these
arrays have the same length, which corresponds to the number of individuals. Functions
operate on a single row of data. If a column name is ``[x]_id`` with `x` :math:`\in \{`
``hh``, ``tu`` :math:`\}`, it can be used to aggregate data within households, tax
units, or any other grouping of individuals specified in :ref:`GEP 1
<gep-1-column-names>`. Any other column name ending in ``_id`` indicates a link to a
different individual (e.g., child-parent relations could be ``parent_0_ind_id``,
``parent_1_ind_id``; receiver of child benefits would be ``kindergeldempf_id``).


Motivation and Scope
--------------------

Taxes and transfers are calculated at different levels of aggregation: Individuals,
couples, families, households. Sometimes, relations between individuals are important:
parents and children, payors/receivers of alimony payments, which parent receives the
`kindergeld` payments, etc..

Potentially, there are many ways of storing these data: Long form, wide form,
collections of tables adhering to :ref:`normal forms
<https://en.wikipedia.org/wiki/Database_normalization>`, N-dimensional arrays, etc.. As
usual, everything involves trade-offs, for example:

- Normal forms require many merge / join operations, which the tools we are using are
  not optimised for.
- One N-dimensional array is not possible because the aggregation dimensions are not
  necessarily nested
- Almost all functions are much easier to implement when working with a single row.
  This is most important for the typical user and increasing the number of developers.
- Modern tools for vectorization (e.g., Jax) scale best when working with
  single rows of data.

  Aggregation to groups of individuals (households, tax units) or referencing data from
  other rows (parents, receiver of child benefits) is not trivial with these tools.


Usage and Impact
----------------

This is primarily internal, i.e., only relevant for developers as the highest-level
interface can be easily adjusted. The default way to receive data will be one Pandas
DataFrame.

Users are affected only via the interface of lower-level functions. Under the proposed
implementation, they will always work on single rows of data. Many alternatives would
require users to write vectorised code, making filtering operations more cumbersome. For
aggregation or referencing other individuals' data, GETTSIM will provide functions that
allow abstracting from implementation details, see :ref:`below
<gep-2-aggregation-functions>`.


Detailed description
--------------------


.. _gep-2-aggregation-functions:

Aggregation functions
~~~~~~~~~~~~~~~~~~~~~

Often variables refer to units aggregating multiple individuals. All these will be
repeated for all individuals in a unit of aggregation.

Always require sorted arrays. Check during setup of the graph. Else go for slow
operations including re-sorting.

Different implementations depending on backend:

- Will need to swap to integer-count index for households internally for Jax'
  [segment_sum](https://jax.readthedocs.io/en/latest/_autosummary/jax.ops.segment_sum.html)
  etc. to work, then translate back
- For numpy, need indices of blocks (implement via
  [np.reduceat](https://numpy.org/doc/stable/reference/generated/numpy.ufunc.reduceat.html)


Implementation
--------------

TBD


Alternatives
------------

Versions 0.3 -- 0.4 (0.5) of GETTSIM used a collection of pandas Series. This proved
to be slow and cumbersome.

Adhering to normal forms (e.g., reducing the length of arrays to the number of
households like [here](https://www.tensorflow.org/api_docs/python/tf/math/segment_sum)
would have led to many merge-like operations in user functions.

Discussion
----------

This section may just be a bullet list including links to any discussions regarding the
GEP:

- Links to relevant GitHub issues, pull requests.
- Discussion on XXX


References and Footnotes
------------------------

.. [1] Each GEP must either be explicitly labeled as placed in the public domain (see
       this GEP as an example) or licensed under the `Open Publication License`_.

.. _Open Publication License: https://www.opencontent.org/openpub/

.. _#general/geps: https://gettsim.zulipchat.com/#narrow/stream/212222-general/topic/GEPs


Copyright
---------

This document has been placed in the public domain. [1]_
