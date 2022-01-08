=============================================
GEP 5 — Optional Rounding of Variables
=============================================

+------------+------------------------------------------------------------------+
| Author     | `Christian Zimpelmann <https://github.com/ChristianZimpelmann>`_ |
+------------+------------------------------------------------------------------+
| Status     | Draft                                                            |
+------------+------------------------------------------------------------------+
| Type       | Discussion                                                       |
+------------+------------------------------------------------------------------+
| Created    | 2021-12-dd                                                       |
+------------+------------------------------------------------------------------+
| Resolution | <url> (required for Accepted or Rejected or Withdrawn)           |
+------------+------------------------------------------------------------------+



Abstract
--------

This GEP discusses three ways how optional rounding of variables could be implemented
in GETTSIM.


Motivation and Scope
--------------------

When transfers and taxes are calculated, in some cases intermediate results or the
final amount need to be rounded based on German law. For some applications, it is
beneficial to also round these variables. These exact results can, for example, be
directly compared to test cases.

However, the rounding leads to non-smooth functions which can hamper numerical
optimization. For these applications, the rounding can be disabled.

User Interface
--------------
GETTSIM only allows for optional rounding of the results of functions. If an
intermediate variable needs to be rounded, the programmer can just split up the code
and create a new function returning exactly this (potentially rounded) result.

In the code, we specify all functions that are potentially rounded and how they are
rounded (``base`` and ``direction``). When calling ``compute_taxes_and_transfers``, the
user can specify if the results should be rounded or not.

Options for Implementation
--------------------------

We discussed three ways how this functionality could be implemented:

1) Decorators
~~~~~~~~~~~~~

Use decorators within ``.py``-files to add attribute ``__roundingspec__`` to the
functions that should be rounded.

.. code-block:: python

       @add_rounding_spec(base=0.01, direction="nearest")
       def grundr_zuschlag_m(
           grundr_zuschlag_vor_eink_anr_m: FloatSeries, anrechenbares_eink_gr_m: FloatSeries
       ) -> FloatSeries:
           pass

``grundr_zuschlag_m`` should be rounded to the second decimal point.

When calling ``compute_taxes_and_transfers`` with ``rounding=True``, GETTSIM loops over
all functions and applies the rounding specified in the attribute if the attribute
exists.

2) Rounding as parameter in parameter file -- no attribute
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify rounding in ``.yaml``-files. Set no attribute ``__roundingspec__``.

.. code-block:: yaml

       rounding:
       - grundr_zuschlag_m:
         - direction: nearest
         - base: 0.01
         - reference: Whatever law

``grundr_zuschlag_m`` should be rounded to the second decimal point.

When calling ``compute_taxes_and_transfers`` with ``rounding=True``, GETTSIM loops over
all functions that are specified in the parameter files as being rounded and applies
the rounding.

3) Rounding as parameter in parameter file -- with attribute
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Specify rounding in ``.yaml``-files as in option 2. Set attribute ``__roundingspec__``
based on ``.yaml``-files.

Implementation could look similar to:

.. code-block:: python

       @add_rounding_spec(
           params_file="ges_renten_vers_params", function_name="grundr_zuschlag_m"
       )
       def grundr_zuschlag_m(
           grundr_zuschlag_vor_eink_anr_m: FloatSeries, anrechenbares_eink_gr_m: FloatSeries
       ) -> FloatSeries:
           pass

After the decorator is applied, ``grundr_zuschlag_m`` would then get a new input
parameter ``ges_renten_vers_params``. Not sure yet, how this can be implemented.

When calling ``compute_taxes_and_transfers`` with ``rounding=True``, GETTSIM loops over
all functions and applies the rounding specified in the attribute if the attribute
exists.


Advantages and Disadvantages
----------------------------

Advantages option 1 over option 2
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

*  Decorator allows to specify function and associated rounding in the same file.
   Hence, function name is only defined once:

   *  Easier to associate the definition of a function and rounding when trying to
      understand how a variable is calculated (otherwise, at the function definition
      there is no sign that the function is rounded)
   *  Less error prone in case function name changes

*  Easier to apply optional rounding to self-written functions (not clear how often
   this is relevant).

Advantages option 2 and 3 over option 1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Strictly speaking, how a variable is rounded is a parameter of the tax and transfer
  system. Hence, it seems a better fit to define it there.
- Rounding parameters can be changed, e.g. if they change over time in the law.

Option 3
~~~~~~~~~~~~~~~~~~~~~

- Adds additional complexity.
- Unclear if and how implementation could look like.
- But could be the best of both worlds?



Discussion
----------

- PR: https://github.com/iza-institute-of-labor-economics/gettsim/pull/316


References and Footnotes
------------------------

.. [1] Each GEP must either be explicitly labeled as placed in the public domain (see
       this GEP as an example) or licensed under the `Open Publication License`_.

.. _Open Publication License: https://www.opencontent.org/openpub/

.. _#general/geps: https://gettsim.zulipchat.com/#narrow/stream/212222-general/topic/GEPs


Copyright
---------

This document has been placed in the public domain. [1]_
