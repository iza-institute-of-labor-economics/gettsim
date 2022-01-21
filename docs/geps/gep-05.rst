.. _gep-5:

=============================================
GEP 5 — Optional Rounding of Variables
=============================================

+------------+------------------------------------------------------------------+
| Author     | `Christian Zimpelmann <https://github.com/ChristianZimpelmann>`_ |
+            +------------------------------------------------------------------+
|            | `Janos Gabler <https://github.com/janosg>`_                      |
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

1. Some applications require the exact, rounded, amount as specified in the law. This
   is also helpful for creating test cases.
2. Other applications require smooth functions and the non-rounding error does not
   matter much.

This document describes how we go about supporting both use cases.


Implementation
--------------

GETTSIM allows for optional rounding of functions' results. Rounding parameters
are specified in the ``.yaml``-files.

The law on the public pension insurance specifies that the maximum possible
Grundrentenzuschlag ``höchstwert_grundr_zuschlag_m`` be rounded to the nearest
fourth decimal point (§76g SGB VI: Zuschlag an Entgeltpunkten für langjährige
Versicherung). The example below contains GETTSIM's encoding of this fact.

The snippet is taken from ``ges_rentenv.yaml``, which contains the following
code:

.. code-block:: yaml

    rounding:
      höchstwert_grundr_zuschlag_m:
        2020-01-01:
          base: 0.0001
          direction: nearest
          reference: §76g SGB VI Abs. 4 Nr. 4

The specification of the rounding parameters starts with the key ``rounding`` at
the outermost level of indentation. The keys are names of functions.

At the next level, the ``YYYY-MM-DD`` key(s) indicate when rounding was
introduced and/or changed. This is done in in the same way as for other policy
parameters as described in :ref:`gep-3`. Those ``YYYY-MM-DD`` key(s) are
associated with a dictionary of the following elements:

- The parameter ``base`` determines the base to which the variables is rounded.
  It has to be a floating point number.
- The parameter ``direction`` has to be one of ``up``, ``down``, or ``nearest``.
- The reference must contain the reference to the law, which specifies the
  rounding.

In the same way as other policy parameters, the rounding parameters become part
of the dictionary ``policy_params``.

At the definition of the function ``höchstwert_grundr_zuschlag_m`` the decorator
``add_rounding_spec`` indicates that the respective output should be rounded and
in which parameter file the rounding parameters are specified.

.. code-block:: python

    @add_rounding_spec(params_file="ges_rentenv")
    def höchstwert_grundr_zuschlag_m(
        grundrentenzeiten: IntSeries, ges_rentenv_params: dict
    ) -> FloatSeries:
        ...
        return out

The decorator adds the attribute ``__rounding_parameter_file__`` to the
function. When calling ``compute_taxes_and_transfers`` with ``rounding=True``,
GETTSIM loops over all functions. If a function has a rounding attribute, the
rounding is applied based on the specification in the argument
``policy_params``. In the example above, the rounding would be based on
``policy_params["ges_rentenv"]["rounding"]["höchstwert_grundr_zuschlag_m"]``.

Note that GETTSIM only allows for optional rounding of functions' results. In
case one is tempted to write a function requiring an intermediate variable to be
rounded, the function should be split up so that another function returns the
quantity to be rounded.

Error handling
~~~~~~~~~~~~~~

In case a function has a ``__rounding_parameter_file__``, but the respective
parameters are missing in ``policy_params``, an error is raised.

In case rounding parameters are specified and the function does not have
``__rounding_parameter_file__`` attribute of the functions is missing does not
lead to an error during execution. This will never happen in the GETTSIM
codebase, however, due to a suitable test.

User-specified rounding
~~~~~~~~~~~~~~~~~~~~~~~

If one wants to add rounding ...

.. For self-written functions, the user needs to add the rounding parameters to
.. ``policy_params`` and decorate the respective functions with
.. ``add_rounding_spec``.

.. Suppose one would like to specify a reform in which
.. ``höchstwert_grundr_zuschlag_m`` is rounded to the next-lowest fourth decimal
.. point instead of to the nearest.

.. The only change  needed to change the rounding parameters by setting

.. .. code-block:: python

..        policy_params["ges_rentenv"]["rounding"]["höchstwert_grundr_zuschlag_m"][
..            "direction"
..        ] = "down"


.. Secondly, you needed to specify the new function calculating
.. ``höchstwert_grundr_zuschlag_m`` and decorate it with the decorator:

.. .. code-block:: python

..     @add_rounding_spec(params_file="ges_rentenv")
..     def höchstwert_grundr_zuschlag_m(
..         grundrentenzeiten: IntSeries, ges_rentenv_params: dict
..     ) -> FloatSeries:
..         ...
..         return out

.. Alternatively to the decorator, one could set the attribute directly:

.. .. code-block:: python

..     höchstwert_grundr_zuschlag_m.__rounding_parameter_file__ = "ges_rentenv"


Advantages of this implementation
---------------------------------

This implementation was chosen over alternatives (e.g., specifying the rounding
parameters in the ``.py`` files directly) for the following reason:

- How a variable is rounded is a feature of the taxes and transfers system.
  Hence, the best place to define it is alongside its other features.
- Rounding parameters might change over time. In this case, the rounding
  parameters for each period can be specified in the parameter file using a
  well-established machinery.
- Optional rounding can be easily specified for user-written functions.
- At the definition of a function, it is clearly visible whether it is
  optionally rounded and where the rounding parameters are found.


Discussion
----------

- Zulip: https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs
- PR: https://github.com/iza-institute-of-labor-economics/gettsim/pull/324
- PR Implementation: https://github.com/iza-institute-of-labor-economics/gettsim/pull/316


Copyright
---------

This document has been placed in the public domain.
