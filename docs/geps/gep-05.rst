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

This GEP describes the implementation of optional rounding of variables in GETTSIM.


Motivation and Scope
--------------------

When transfers and taxes are calculated, in some cases intermediate results or the
final amount need to be rounded based on German law. For some applications, it is
beneficial to also round these variables. These exact results can, for example, be
directly compared to test cases.

However, the rounding leads to non-smooth functions which can hamper numerical
optimization. For these applications, the rounding can be disabled.

Implementation
--------------

GETTSIM only allows for optional rounding of the results of functions. If an
intermediate variable needs to be rounded, the programmer can just split up the code
and create a new function returning exactly this (potentially rounded) result.

Within the code base, rounding parameters are specified in the ``.yaml``-files. The
example below determines that ``grundr_zuschlag_m`` is by law rounded to the second
decimal point. The parameter ``base`` determines the base to which the variables is
rounded and ``direction`` has to be one of ``up``, ``down``, ``nearest``. The rounding
parameters become part of the dictionary ``policy_params`` once
``set_up_policy_environment`` is called -- in the same way as other policy parameters
do.

.. code-block:: yaml

       rounding:
         grundr_zuschlag_m:
           2020-01-01:
             direction: nearest
             base: 0.01
             reference: Whatever law

At the definition of ``grundr_zuschlag_m`` the decorator
``add_rounding_spec_by_params_file`` indicates that the respective output should be
rounded and in which parameter file the rounding parameters are specified.

.. code-block:: python

       @add_rounding_spec(params_file="ges_renten_vers")
       def grundr_zuschlag_m(
           grundr_zuschlag_vor_eink_anr_m: FloatSeries, anrechenbares_eink_gr_m: FloatSeries
       ) -> FloatSeries:
           pass

The decorator adds the attribute ``__rounding_parameter_file__`` to the function. When
calling ``compute_taxes_and_transfers`` with ``rounding=True``, GETTSIM loops over all
functions. If a function has a rounding attribute, the rounding is applied based on the
specification in the argument ``policy_params``. In the example above, the rounding
would be based on ``policy_params["ges_renten_vers"]["rounding"]["grundr_zuschlag_m"]``.

User-written functions
~~~~~~~~~~~~~~~~~~~~~~

For self-written functions, the user needs to add the rounding parameters to
``policy_params`` and decorate the respective functions with ``add_rounding_spec`` in
the same way as demonstrated above.



Advantages of this implementation
---------------------------------

This implementation was chosen over alternatives (e.g. specifying the rounding
parameters in the ``.py`` files directly) for the following reason:

- Rounding parameters might change over time in the law. In this case, the rounding
  parameters for each time period can be specified in the parameter file.
- How a variable is rounded, is strictly speaking a parameter of the tax and transfer
  system. Hence, it seems a better fit to define it there.
- Optional rounding can be easily specified for user-written functions.
- At the definition of a function, it is clearly visible if it is optionally rounded
  and where the rounding parameters are found.

Discussion
----------

- PR: https://github.com/iza-institute-of-labor-economics/gettsim/pull/324
- PR Implementation: https://github.com/iza-institute-of-labor-economics/gettsim/pull/316


References and Footnotes
------------------------

.. [1] Each GEP must either be explicitly labeled as placed in the public domain (see
       this GEP as an example) or licensed under the `Open Publication License`_.

.. _Open Publication License: https://www.opencontent.org/openpub/

.. _#general/geps: https://gettsim.zulipchat.com/#narrow/stream/212222-general/topic/GEPs


Copyright
---------

This document has been placed in the public domain. [1]_
