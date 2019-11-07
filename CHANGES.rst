Changes
=======

This is a record of all past ``gettsim`` releases and what went into them in reverse
chronological order. We follow `semantic versioning <https://semver.org/>`_ and all
releases are available on `Anaconda.org <https://anaconda.org/gettsim/gettsim>`_.

0.2.0 - 2019-11-06
------------------

This will be the initial release of ``gettsim``.

- Set up as a package installable via conda (`@tobiasraabe
  <https://github.com/tobiasraabe>`_) 
- Migration of the parameter database from xls to yaml (`@mjbloemer <https://github.com/mjbloemer>`_, `@MaxBlesch
  <https://github.com/MaxBlesch>`_)
- Migration of test parameters from xls to csv (via some time as ods...) (`@MaxBlesch
  <https://github.com/MaxBlesch>`_, `@tobiasraabe
  <https://github.com/tobiasraabe>`_)
- Many changes to the interface of the package by `@MaxBlesch
  <https://github.com/MaxBlesch>`_, `@janosg <https://github.com/janosg>`_,
  `@Eric-Sommer <https://github.com/Eric-Sommer>`_, `@hmgaudecker
  <https://github.com/hmgaudecker>`_ and `@tobiasraabe
  <https://github.com/tobiasraabe>`_
- Tax and transfer module uses apply instead of loops (@MaxBlesch
  <https://github.com/MaxBlesch>`_, `@hmgaudecker
  <https://github.com/hmgaudecker>`_ 
- Correct tax treatment of child care costs (`@Eric-Sommer <https://github.com/Eric-Sommer>`_)
- Improved calculation of housing allowance (`@Eric-Sommer <https://github.com/Eric-Sommer>`_)


0.1 and prior work - 2019-09-30
-------------------------------

Most code is written by `@Eric-Sommer <https://github.com/Eric-Sommer>`_ based on
`IZAΨMOD <https://www.iza.org/publications/dp/8553/
documentation-izapsmod-v30-the-iza-policy-simulation-model>`_, a policy microsimulation
model developed at `IZA <https://www.iza.org>`_.
