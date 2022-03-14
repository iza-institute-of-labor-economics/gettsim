Changes
========

This is a record of all past ``gettsim`` releases and what went into them in reverse
chronological order. We follow `semantic versioning <https://semver.org/>`_ and all
releases are available on `Anaconda.org <https://anaconda.org/gettsim/gettsim>`_.

0.5.0 —
------------------

* :gh:`327` add behinderten_pauschbetrag for 1975-1986 (:ghuser:`lillyfischer`).
* :gh:`285` Set up bokeh dashboard to visualize tax-benefit parameters
   (:ghuser:`Si-Pf`, :ghuser:`Eric-Sommer`).
* :gh:`306` Add the possibility to load the value of a parameter of the previous
   year when calling `set_up_policy_environment` (:ghuser:`ChristianZimpelmann`).
* :gh:`275` Implement Grundrente. Implement Grundsicherung im Alter. Remove
   `ges_rente_m` as input. Rename `gettsim.renten_anspr` to `gettsim.transfers.rente`.
   Rename `gettsim.social_insurance` to `gettsim.social_insurance_contributions`
   (:ghuser:`davpahl`, :ghuser:`ChristianZimpelmann`).
* :gh:`307` Allow to specify order up to which ancestors and descendants are shown
   when plotting a dag (:ghuser:`ChristianZimpelmann`).
* :gh:`310` Added Mehrbedarf G to Implementation of Grundsicherung im Alter
   (:ghuser:`paulinaschroeder`).
* :gh:`311` Rename variable kaltmiete_m_hh to bruttokaltmiete_m_hh
   (:ghuser:`LauraGergeleit`).
* :gh:`319`:gh:`320` Implement changes for social assistance and social insurance
   becoming effective in 2022 (:ghuser:`Eric-Sommer`).
* :gh:`322` Add updated wohngeld parameters for 2022 (:ghuser:`mjbloemer`,
  :ghuser:`lillyfischer`).
* :gh:`312` Updated GEP-01 with effects on character limits, time and unit identifiers,
  adjustments for DAG backend (:ghuser:`hmgaudecker`).
* :gh:`314` Enforced character limits from GEP-01 for all function names and input
  variables. Make variable names more precise (e.g., `ges_` in front of all social
  insurance parameters that have private counterparts, `eink_st` everywhere the income
  tax is meant). Make variables consistent (e.g. `kinderfreibetrag` had different
  abbreviations, now `kinderfreib` everywhere). (:ghuser:`hmgaudecker`,
  :ghuser:`ChristianZimpelmann`)
* :gh:`343` New argument for `compute_taxes_and_transfers`: `rounding`. If set to False,
  rounding of outputs is disabled. Add rounding for `eink_st_tu`. Rounding for other
  functions will be introduced in future PRs. (:ghuser:`ChristianZimpelmann`).
* :gh:`349` Create parameters for several hard coded numbers in code.
  (:ghuser:`LauraGergeleit`).
* :gh:`355` Major renaming based on GEP 01, e.g.: correct use of ``_m``-suffix;
  ``alleinerziehend`` becomes ``alleinerz``; rename `ges_rentenv.yaml` to
  `ges_rente.yaml` (:ghuser:`hmgaudecker`, :ghuser:`ChristianZimpelmann`)

0.4.2 — 2022-01-25
------------------

* Ensure GETTSIM works with Pandas 1.4 (:gh:`337`)


0.4.1 — 2021-04-11
------------------

* :gh:`248` Implement 2021 increase in lump sum tax deductions for disabled.
   (:ghuser:`Eric-Sommer`).
* :gh:`254` Implement 2021 increase in unemployment benefits
    (:ghuser:`Eric-Sommer`).
* :gh:`253` Implement 2021 changes in health insurance contribution rates and
    other social insurance regulations (:ghuser:`Eric-Sommer`).
* :gh:`266` Adjust visualization.py to link nodes of DAGs to documentation
    properly (:ghuser:`davpahl`, :ghuser:`ChristianZimpelmann`).
* :gh:`267` Implement new calculation of Kinderzuschlag parameter
   (:ghuser:`Eric-Sommer`).
* :gh:`252` implement 2021 reforms to income tax tariff and family tax deductions
    (:ghuser:`Eric-Sommer`).
* :gh:`235` Module to create synthetic data
    (:ghuser:`Eric-Sommer`, :ghuser:`ChristianZimpelmann`).
* :gh:`256` Implement 2021 housing benefit reform (:ghuser:`Eric-Sommer`).
* :gh:`283` Implement Kinderbonus in 2020 and 2021 (:ghuser:`ChristianZimpelmann`).


0.4.0 — 2020-11-11
------------------

* :gh:`241` renaming of directories: `gettsim.benefits` to `gettsim.transfers`;
   `gettsim.soz_vers` to `gettsim.social_insurance`; `gettsim.data` to
   `gettsim.parameters` (:ghuser:`MaxBlesch`, :ghuser:`ChristianZimpelmann`).
* :gh:`230` adds type hints and links all docstring variables to the documentation.
   Also all functions have a one liner docstring now (:ghuser:`MaxBlesch`,
   :ghuser:`FelixAhlbrecht`).
* :gh:`232` introduces beginner tutorials on how to use GETTSIM (:ghuser:`amageh`,
   :ghuser:`davpahl`, :ghuser:`Trichter33`).
* :gh:`185` adds the DAG code for renten_anspr_m (:ghuser:`MaxBlesch`). This is
   based on the pension simulation code by (:ghuser:`Eric-Sommer`).
* :gh:`184` adds visualization of the tax and transfer system as an interactive bokeh
  plot and documentation improvements (:ghuser:`tobiasraabe`).
* :gh:`198` enhances the loader of internal and user functions, adds a tutorial for how
  to pass functions to the interface and provides more tests (:ghuser:`tobiasraabe`).
* :gh:`213` changes ``compute_taxes_and_transfers`` such that it always returns a pandas
  DataFrame and removes the `return_dag` option (:ghuser:`tobiasraabe`).
* :gh:`219` refactors the DAG and makes it independent from the main interface
  (:ghuser:`tobiasraabe`). The PR also changes the names of interface arguments:
  ``functions`` instead of ``user_functions``, ``set_up_policy_environment`` instead of
  ``get_policy_for_date``, ``columns_overriding_functions`` instead of ``user_columns``
  and some more changes.
* :gh:`225` makes gettsim ready for Python 3.8 (:ghuser:`tobiasraabe`).



0.3.4 — 2020-07-30
------------------

* :gh:`222` Fix wohngeld coefficent. Add test for increasing wohngeld.
  (:ghuser:`hmgaudecker`, :ghuser:`MaxBlesch`)


0.3.3 — 2020-06-27
------------------

* :gh:`212` improves the error message when reduced series could not be expanded with an
  id variable and fixes a related error in the internal functions
  (:ghuser:`hmgaudecker`, :ghuser:`tobiasraabe`).
* :gh:`214` adds a check for missing root nodes (:ghuser:`tobiasraabe`).
* :gh:`215` adds a check for duplicate ``targets`` (:ghuser:`tobiasraabe`).
* :gh:`216` fixed calculation of kindergeldzuschlag and wohngeld. Changed check
  against arbeitsl_geld_2 (:ghuser:`tobiasraabe`).


0.3.2 — 2020-06-19
------------------

* :gh:`196` adds docstring to `policy_for_date.py` and improves its interface
  (:ghuser:`MaxBlesch`).
* :gh:`197` adds all functions which build the tax and transfer system to the
  documentation (:ghuser:`tobiasraabe`).
* :gh:`198` enhances the loader of internal and user functions, adds a tutorial for how
  to pass functions to the interface and provides more tests (:ghuser:`tobiasraabe`).
* :gh:`200` adds a debug mode to gettsim and documents the feature
  (:ghuser:`tobiasraabe`).
* :gh:`201` improves the calculation of ``hh_freib`` and renames it to
  ``alleinerziehend_freib`` (:ghuser:`MaxBlesch`, :ghuser:`tobiasraabe`).
* :gh:`202` fixes bugs that surfaced for negative incomes (:ghuser:`MaxBlesch`).
* :gh:`206` fixes several bugs in `arbeitsl_geld_2` and related transfers, calculating
  them at the appropriate (household) level (:ghuser:`MaxBlesch`).


0.3.1 — 2020-06-05
------------------

* :gh:`188` removes misleading code bits from the documentation and adds a copy-button
  (:ghuser:`tobiasraabe`).
* :gh:`191` adds a skip and a warning if `gettsim.test()` is repeatedly called
  (:ghuser:`tobiasraabe`).


0.3.0 — 2020-06-04
------------------

* Cleanup of ALG II parameters and documentation (:ghuser:`mjbloemer`)
* Break up params.yaml into group-level files (:ghuser:`MaxBlesch`)
* Corrected income deductions for additional child benefit (:ghuser:`Eric-Sommer`)
* Implemented "Starke-Familien-Gesetz" from July 2019 on child benefits
  (:ghuser:`Eric-Sommer`)
* Remove child specific ALG II withdrawal and refactoring of ALG II
  (:ghuser:`MaxBlesch`, :ghuser:`mjbloemer`)
* Add ALG II transfer withdrawal 2005-01-01 to 2005-09-30
  (:ghuser:`mjbloemer`, :ghuser:`MaxBlesch`)
* Child tax allowance modelled as two separate items. (:ghuser:`Eric-Sommer`)
* Alimony advance payment (*Unterhaltsvorschuss*) now modelled more in line
  with the law (:ghuser:`Eric-Sommer`)
* Implement Art. 3 of *Familienentlastungsgesetz* on income tax tariff and child tax
  allowance becoming effective in 2020 (:ghuser:`Eric-Sommer`)
* Implement parity in health care contributions since
  2019 and 2020 contribution rates (:ghuser:`Eric-Sommer`)
* Add *Elterngeld* calculation (:ghuser:`MaxBlesch`, :ghuser:`boryana-ilieva`)
* Fix Soli 1991 calculation, improve Soli 1995 calculation, add 2021 Soli
  parameters and add Soli tests (:ghuser:`mjbloemer`, :ghuser:`MaxBlesch`)
* Implement pre-2010 ruling on *Vorsorgeaufwendungen* (:ghuser:`Eric-Sommer`)
* ``gettsim`` is released as a conda noarch package (:ghuser:`tobiasraabe`)
* Implement 2020 reform increasing housing benefit (*Wohngeldstärkungsgesetz*) and
  complete parameters on past benefits (:ghuser:`Eric-Sommer`)
* Regroup wohngeld parameters according to GEP-3 (:ghuser:`MaxBlesch`)
* Renamed all data columns to German names (:ghuser:`amageh`, :ghuser:`MaxBlesch`)
* Renamed and regrouped all param files (:ghuser:`Eric-Sommer`, :ghuser:`MaxBlesch`)
* Added generic/piecewise functions (:ghuser:`johannesgoldbeck`,
  :ghuser:`ppoepperling`, :ghuser:`MaxBlesch`)
* A series of pull requests established the new DAG-based backend and refactored the
  calculation of benefits, taxes, and social insurance (:ghuser:`MaxBlesch`,
  :ghuser:`tobiasraabe`)
* Error messages for the new interface (:ghuser:`hmgaudecker`, :ghuser:`tobiasraabe`).


0.2.1 — 2019-11-20
------------------

* Fix error with real SOEP data and "Wohngeld" for households with more than 12
  household members (:ghuser:`Eric-Sommer`, :ghuser:`MaxBlesch`)
* Better description of required input and output columns (:ghuser:`MaxBlesch`,
  :ghuser:`Eric-Sommer`)
* Fix dependencies for conda package  (:ghuser:`tobiasraabe`)
* Fill changelog and include in docs (:ghuser:`tobiasraabe`, :ghuser:`hmgaudecker`)
* Add maintenance section to website (:ghuser:`tobiasraabe`)


0.2.0 — 2019-11-06
------------------

This will be the initial release of ``gettsim``.

* Set up as a conda-installable package (:ghuser:`tobiasraabe`)
* Migration of the parameter database from xls to yaml (:ghuser:`mjbloemer`,
  :ghuser:`MaxBlesch`)
* Migration of test parameters from xls to csv (:ghuser:`MaxBlesch`,
  :ghuser:`tobiasraabe`)
* Get the main entry point to work, change interface (:ghuser:`MaxBlesch`, janosg,
  :ghuser:`Eric-Sommer`, :ghuser:`hmgaudecker`, :ghuser:`tobiasraabe`)
* Tax and transfer module uses apply instead of loops (:ghuser:`MaxBlesch`,
  :ghuser:`hmgaudecker`)
* Correct tax treatment of child care costs (:ghuser:`Eric-Sommer`)
* Improve calculation of housing allowance (:ghuser:`Eric-Sommer`)


0.1 and prior work — 2019-09-30
-------------------------------

Most code written by :ghuser:`Eric-Sommer` based on `IZAΨMOD <https://www.iza.org/
publications/dp/8553/documentation-izapsmod-v30-the-iza-policy-simulation-model>`_, a
policy microsimulation model developed at `IZA <https://www.iza.org>`_.
