.. _gep-2:

=====================================================================
GEP 2 — Internal Representation of Data on Individuals and Households
=====================================================================

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
a DataFrame. All these arrays have the same length, which corresponds to the number of
individuals. Unless marked in a specific way, functions operate on a single row of data.
Column names ending in ``_id`` can be used to aggregate data within households, tax
units, etc..


Motivation and Scope
--------------------

Taxes and transfers are calculated at different levels of aggregation: Individuals,
couples, families, households. Potentially, there are many ways of storing these data:
Long form, wide form, collections of tables, n-dimensional arrays, etc..

Trade-offs:

- Normal forms lead to irregular data.

- Modern tools for vectorization (e.g., Numba or Jax) scale best when working with
  single rows of data.

- Almost all functions are much easier to implement when working with a single row.
  This is most important for the typical user and increasing the number of developers.




Usage and Impact
----------------

* Primarily internal / relevant for developers — highest-level interface can be easily
  adjusted

* Affects users only via the interface of lower-level functions (they might want to
  call those or override them)



Detailed description
--------------------

Will need to swap to integer-count index for households internally for Jax'
[segment_sum](https://www.tensorflow.org/api_docs/python/tf/math/segment_sum) etc. to work,
then translate back


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
