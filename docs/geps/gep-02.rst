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
example indidviduals...) and passes it around to the functions calculating taxes and
transfers.


Motivation and Scope
--------------------

This section describes the need for the proposed change. It should describe the existing
problem, who it affects, what it is trying to solve, and why. This section should
explicitly address the scope of and key requirements for the proposed change.


Usage and Impact
----------------

* Primarily internal / relevant for developers — highest-level interface can be easily
  adjusted
* Affects users only via the interface of lower-level functions (they might want to
  call those or override them)



Detailed description
--------------------

Main idea: adhere to normal forms (see pages https://www.wiwi.uni-bonn.de/gaudecker/_static/prog_econ/2019/09_data_management.pdf).

1. Values do not have any internal structure
2. Tables do not contain redundant information
3. No structure in variable names (always use "long" format, not "wide" format)

1. and 3. should be uncontroversial, for 2., there are two potential ways forward, see
below.

Some things that will be the case for sure:

* Anything variable that exists at a level that is above the lowe

.. note::

    We might get by without steuersubjekt (tax unit) by just tracing out relations
    between people and eligibility; I leave it in for now.


A: Strict adherence to 2nd normal form
---------------------------------------

* 3+ different tables (bedarfsgemeinschaft, steuersubjekt, person, ?).
* Indexes would be ``jahr`` :math:`\times` {``bedarfsgemeinschaft``, ``steuersubjekt``,
  ``person``}


B: One table with MultiIndex
----------------------------

* Index would be ``jahr`` :math:`\times` ``bedarfsgemeinschaft`` :math:`\times`
  ``steuersubjekt`` :math:`\times` ``person``
* Any variable relevant at a level higher than ``person`` will be filled in the same
  way for all persons belonging to that unit.


Pro A:

* Very obvious what is the correct level for a particular variable
* Never a need to append anything like ``_hh`` to a variable as this is encoded in the
  table name
* Less need to work with MultiIndex, which might not be straightforward.

Pro B:

* Most of the time, calculations at ``higher-up`` levels require information from the
  person level (as opposed to aggregates only). E.g., for a lot of Arbeitslosengeld II -
  stuff we have to check person-by person. One might as well just work with that
  directly and avoid lots of merges.
* More natural for people not used to the SQL-like way of doing things.



Related Work
------------

This section should list relevant and/or similar technologies, possibly in other
libraries. It does not need to be comprehensive, just list the major examples of prior
and relevant art.


Implementation
--------------

This section lists the major steps required to implement the GEP.  Where possible, it
should be noted where one step is dependent on another, and which steps may be
optionally omitted.  Where it makes sense, each step should include a link to related
pull requests as the implementation progresses.

Any pull requests or development branches containing work on this GEP should be linked
to from here.  (A GEP does not need to be implemented in a single pull request if it
makes sense to implement it in discrete phases).


Backward compatibility
----------------------

This section describes the ways in which the GEP breaks backward compatibility.


Alternatives
------------

If there were any alternative solutions to solving the same problem, they should be
discussed here, along with a justification for the chosen approach.


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
