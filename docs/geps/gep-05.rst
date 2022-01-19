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
| Created    | 2022-01-08                                                       |
+------------+------------------------------------------------------------------+
| Resolution | <url> (required for Accepted or Rejected or Withdrawn)           |
+------------+------------------------------------------------------------------+


Abstract
--------

This GEP describes the implementation of optional rounding of variables in GETTSIM.


Motivation and Scope
--------------------

For several taxes and transfers, German law specifies that these be rounded in specific
ways. This leads to different use cases.

1. Some applications require the exact, rounded, amount as specified in the law. This is
   also helpful for creating test cases.
2. Other applications require smooth functions and the non-rounding error does not
   matter much.

This document describes how we go about supporting both use cases.


Implementation
--------------

GETTSIM allows for optional rounding of functions' results. Rounding parameters are
specified in the ``.yaml``-files.

The example below contains GETTSIM's encoding of the fact that the [XXX] law specifies
that ``grundr_zuschlag_m`` be rounded to the nearest second decimal point.

- The key has to be a function name, in this case ``grundr_zuschlag_m``
- The parameter ``base`` determines the base to which the variables is rounded. It has
  to be a floating point number.
- The parameter ``direction`` has to be one of ``up``, ``down``, or ``nearest``.
- The reference must contain the reference to the law, which specifies the rounding.

The rounding parameters become part of the dictionary ``policy_params`` once
``set_up_policy_environment`` is called in the same way as other policy parameters.

.. code-block:: yaml

       rounding:
         grundr_zuschlag_m:
           2020-01-01:
             base: 0.01
             direction: nearest
             reference: Whatever law

At the definition of the function ``grundr_zuschlag_m`` the decorator
``add_rounding_spec_by_params_file`` indicates that the respective output should be
rounded and in which parameter file the rounding parameters are specified.

.. code-block:: python

       @add_rounding_spec(params_file="ges_renten_vers")
       def grundr_zuschlag_m(
           grundr_zuschlag_vor_eink_anr_m: FloatSeries, anrechenbares_eink_gr_m: FloatSeries
       ) -> FloatSeries:
           ...
           return out

The decorator adds the attribute ``__rounding_parameter_file__`` to the function. When
calling ``compute_taxes_and_transfers`` with ``rounding=True``, GETTSIM loops over all
functions. If a function has a rounding attribute, the rounding is applied based on the
specification in the argument ``policy_params``. In the example above, the rounding
would be based on ``policy_params["ges_renten_vers"]["rounding"]["grundr_zuschlag_m"]``.

Note that GETTSIM only allows for optional rounding of functions' results. In case you
happened to write a function that requires an intermediate variable to be rounded, split
it up and create a new function returning exactly the potentially rounded value.


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
- How a variable is rounded is a feature of the taxes and transfers system. Hence, it
  seems a better fit to define it there.
- Optional rounding can be easily specified for user-written functions.
- At the definition of a function, it is clearly visible whether it is optionally
  rounded and where the rounding parameters are found.


Discussion
----------

- Zulip: https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs
- PR: https://github.com/iza-institute-of-labor-economics/gettsim/pull/324
- PR Implementation: https://github.com/iza-institute-of-labor-economics/gettsim/pull/316


Copyright
---------

This document has been placed in the public domain.
