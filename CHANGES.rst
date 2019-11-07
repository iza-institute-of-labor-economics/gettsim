Changes
=======

This is a record of all past ``gettsim`` releases and what went into them in reverse
chronological order. We follow `semantic versioning <https://semver.org/>`_ and all
releases are available on `Anaconda.org <https://anaconda.org/gettsim/gettsim>`_.

0.2.0 - 2019-11-06
------------------

This will be the initial release of ``gettsim``.

- Set up as a conda-installable package (tobiasraabe)
- Migration of the parameter database from xls to yaml (mjbloemer, MaxBlesch)
- Migration of test parameters from xls to csv (MaxBlesch, tobiasraabe)
- Get the main entry point to work, change interface (MaxBlesch, janosg,
  Eric-Sommer, hmgaudecker, tobiasraabe)
- Tax and transfer module uses apply instead of loops (MaxBlesch, hmgaudecker)
- Correct tax treatment of child care costs (Eric-Sommer)
- Improve calculation of housing allowance (Eric-Sommer)


0.1 and prior work - 2019-09-30
-------------------------------

Most code written by Eric-Sommer based on
`IZAΨMOD <https://www.iza.org/publications/dp/8553/
documentation-izapsmod-v30-the-iza-policy-simulation-model>`_, a policy microsimulation
model developed at `IZA <https://www.iza.org>`_.
