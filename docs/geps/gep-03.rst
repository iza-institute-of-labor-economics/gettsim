:download:`Download the template here <gep-template.rst>`.

.. _gep-3:

====================================================
GEP 3 — Parameters of the taxes and transfers system
====================================================

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

This GEP describes the structure of the parameters of the taxes and transfers system.
This includes the format of the yaml files (initial input) and storage of the processed
parameters (SQLite database? tbd)


Motivation and Scope
--------------------

In many ways, the parameters of the taxes and transfers system are the core of GETTSIM.
Along with the functions operating on them and the input data, they determine all
quantities of interest. Sensibly structuring and cleanly documenting the meaning and
sources of these parameters requires particular care.


Usage and Impact
----------------

* GETTSIM developers should closely look at the Section
  :ref:`gep-3-structure-yaml-files` before adding new variables.


.. _gep-3-structure-yaml-files:

Structure of the YAML files
---------------------------

Each YAML file contains a number of parameters at the outermost level of indentation.
Each of these parameters in turn is a dictionary with at least three keys: ``name``,
``description``, and the ``YYYY-MM-DD``-formatted date on which it first took effect.
Values usually change over time; each time a value is changed, another ``YYYY-MM-DD``
entry is added.

1. The ``name`` key has two sub-keys ``de`` and ``en``, which are

   * short names without re-stating the realm of the parameter (e.g.
     "Arbeitslosengeld II" or "Kinderzuschlag");
   * not sentences;
   * correctly capitalised.

   Example (from ``arbeitsl_geld_2``):

   .. code-block:: yaml

       e_anr_frei:
           name:
               de: Anrechnungsfreie Einkommensanteile
               en: Income shares not subject to transfer withdrawal

2. The ``description`` key has two sub-keys ``de`` and ``en``, which

   * are exhaustive explanations of the parameter;
   * show the § and Gesetzbuch of that parameter (including its entire history if the
     location has changed);
   * mention bigger amendments / Neufassungen and be as helpful as possible to
     make sense of that parameter.

     Example:

     .. code-block:: yaml

        description:
            de: >
                Einkommensanteile, aufgrund derer die Leistungen des Arbeitslosengelds
                II nicht vermindert werden. § 30 SGB II. Seit 01.10.2005 zudem definiert
                durch Freibetrag in § 11 SGB II, siehe auch § 67 SGB II. Seit 01.04.2011
                § 11b (2) SGB II (neugefasst durch B. v. 13.05.2011 BGBl. I S. 850.
                Artikel 2 G. v. 24.03.2011 BGBl. I S. 453).
            en: >
                Shares of income which do not lead to tapering of Arbeitslosengeld II
                benefits.

3. The ``unit`` key informs on the unit of the values (Euro or DM if monetary,
    or some share).

   * In rare cases (e.g. child benefit age threshold), it might be omitted.
   * possible values: ``euro``, ``dm``, ``share``, ``percentage``.

   Example:

   .. code-block:: yaml

    kgeld1:
      name:
        de: Kindergeld, Betrag für das erste Kind
        [...]
      unit: euro

4. The ``time`` key informs on the reference period of the values, if applicable

   * possible values: ``year``, ``month``, ``week``, ``day``.

   Example:

   .. code-block:: yaml

    kg_stunden:
      name:
        de: maximale Arbeitsstunden für Kindergeldanspruch
        [...]
      time: week

5. The YYYY-MM-DD key(s)

   * hold all historical values for a specific parameter or set of parameters in the
     ``value`` subkey;
   * is present with ``value: null`` if a parameter ceases to exist starting on a
     particular date;
   * contain a precise reference to the law in the ``reference`` subkey;
   * may add additional descriptions in the ``note`` key;
   * may give hints towards the type of function they refer to via the ``type`` subkey;
   * may include formulas if the law does;
   * may reference other parameters as described below.

   The remainder of this section explains this element in much more detail.


[YYYY-MM-DD].reference
++++++++++++++++++++++

* cites the law (Gesetz "G. v."), decree (Verordnung "V. v.") or proclamation
  (Bekanntmachung "B. v.") that changes the law
* in German
* follows the style ``Artikel [n] [G./V./B.] v. [DD.MM.YYYY] BGBl. I S. [SSSS].``
* do not add information "geändert durch" (it is always a change) or the date the law
  comes into force (this is exactly the date key one level above)
* the page should be the first page of the law/decree/proclamation, not the exact page
  of the parameter

Example:

.. code-block:: yaml

    reference: G. v. 24.12.2003 BGBl. I S. 2964.


[YYYY-MM-DD].value
++++++++++++++++++

The general idea is to make the replication of the laws very obvious. If the law
includes a table, we will have a dictionary with keys 0, 1, 2, .... If the law includes
a formula, it should be included. Etc.

The following walks through several cases.

.. todo::

    Make these cases close to exhaustive.

* The simplest case is a single parameter, which should be specified as:

  .. code-block:: yaml

      value: 520

* Values may reference another parameter if that is fixed by law in a given year. That
  is, it must not depend on anything else or individual-level data. So this would not
  work, for example, for income tax schedules. Example:

  .. code-block:: yaml

      value: arbeitsl_geld_2.regelbedarf * 0.6


* More complex: A piecewise linear function

    .. code-block:: yaml

        type: piecewise_linear
        value:
            0:
                lower_threshold: 0
                upper_threshold: 400
                rate: 0.15
                intercept_at_lower_threshold: 0
            1:
                upper_threshold: 800
                rate: 0.3
            2:
                upper_threshold: 1200
                rate: 0.15
            3:
                upper_threshold: inf
                rate: 0
                note: Making this explicit.

* Formulas: We want to allow for something like this if the law is specified that way
  (e.g. the Steuertarif, IIRC):

  .. code-block:: yaml

      value: (2000 + 0.5 * x) * x

  Still need to think this through, depends on implementation. Will require that a
  function is specified in the ``type`` keyword so that we can get standard
  representations via SymPy or the like.

* If a parameter ceases to be relevant, is superseded by something else, ... there must
  be a ``YYYY-MM-DD`` key with an entry ``value: null`` regardless of the previous
  strucuture of the ``value``. Ideally, there would be a ``reference`` and potentially a
  ``note`` key. Example:

  .. code-block:: yaml

      value: null
      note: Arbeitslosenhilfe is superseded by arbeitsl_geld_2


.. todo::

    Add more examples as we gather more experience. E.g. wohngeld (#144)

.. todo::

    Decide on this:

    * values in percentages can alternatively be expressed to the base of one
    * DM values have to be converted to Euro using the exchange rate 1:1.95583.

    HMG: If we allow for both % and fractions, we must add a ``unit`` key. Then we can
    trivially allow for DM values, which would be nice for being close to the laws. I
    would be all for that ``unit`` key, but want to throw it out here first.


[YYYY-MM-DD].note
+++++++++++++++++

This optional key may contain a free-form note holding any information that may be
relevant for the interpretation of the parameter, the implementer, user, ...


[YYYY-MM-DD].deviation_from
+++++++++++++++++++++++++++

Often laws change only part of a parameter. To avoid error-prone code duplication, we
allow for such cases via the ``deviation_from`` key. This is the reason why lists are to
be avoided in the value key (see the ``piecewise_linear`` function above).

The key could either reference another value explicitly:

.. code-block:: yaml

    deviation_from: arbeitsl_geld_2.e_anr_frei
    2:
        upper_threshold: 1500

A special case is the value ``previous``, which just refers to the previous law change's
set of values:

.. code-block:: yaml

    deviation_from: previous
    value:
        1:
            upper_threshold: 1000


Implementation
--------------

This section lists the major steps required to implement the GEP.  Where possible, it
should be noted where one step is dependent on another, and which steps may be
optionally omitted.  Where it makes sense, each step should include a link to related
pull requests as the implementation progresses.

Any pull requests or development branches containing work on this GEP should be linked
to from here.  (A GEP does not need to be implemented in a single pull request if it
makes sense to implement it in discrete phases).



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
