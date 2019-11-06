Getting Started
===============

Installation
------------

We distribute GETTSIM via the package manager `conda <https://conda.io/>`_. If it is not
installed on your machine, follow the `user guide
<https://docs.conda.io/projects/conda/en/latest/user-guide/index.html>`_ on the topics
installation and getting started.

Then, install GETTSIM with

.. code-block:: bash

    $ conda install -c gettsim gettsim

Usage
-----

To validate the installation, start a Python shell or a Jupyter notebook and type

.. code-block:: python

    from gettsim.tax_transfer import calculate_tax_and_transfers

    year_of_policy = 2015  # We cover 1985 to 2019
    calculate_tax_and_transfers(dataset, year_of_policy)


Where dataset is some DataFrame containing the following variables for each observation:

+-------------+------------------------------------------------------------------------+
|   Variable  |Explanation                                               | Type        +
+=============+========================================================================+
|hid          |Household identifier                                      | Int         |
+-------------+------------------------------------------------------------------------+
|tu_id        |Tax Unit identifier                                       | Int         |
+-------------+------------------------------------------------------------------------+
|pid          |Personal identifier                                       | Int         |
+-------------+------------------------------------------------------------------------+
|head_tu      |Head of tax unit                                          | Bool        |
+-------------+------------------------------------------------------------------------+
|head         |Head of Household                                         | Bool        |
+-------------+------------------------------------------------------------------------+
|hhtyp        |                                                          | Int         |
+-------------+------------------------------------------------------------------------+
|hhsize       |Size of household                                         | Int         |
+-------------+------------------------------------------------------------------------+
|hhsize_tu    |Size of tax unit                                          | Int         |
+-------------+------------------------------------------------------------------------+
|adult_num    |Number of adults in household                             | Int         |
+-------------+------------------------------------------------------------------------+
|child0_18_num|Number of children between 0 and 18 in household          | Int         |
+-------------+------------------------------------------------------------------------+
|hh_wealth    |Wealth of household                                       | Float       |
+-------------+------------------------------------------------------------------------+
|m_wage       |Monthly wage of each individual                           | Float       |
+-------------+------------------------------------------------------------------------+
|age          |Age if Individual                                         | Int         |
+-------------+------------------------------------------------------------------------+
|selfemployed |Self-employment of Individual                             | Bool        |
+-------------+------------------------------------------------------------------------+
|east         |Location in former east or west germany                   | Bool        |
+-------------+------------------------------------------------------------------------+
|haskids      |Individual has kids                                       | Bool        |
+-------------+------------------------------------------------------------------------+
|m_self       |Monthly wage of selfemployment of each individual         | Float       |
+-------------+------------------------------------------------------------------------+
|m_pensions   |Monthly pension payments of each individual               | Float       |
+-------------+------------------------------------------------------------------------+
|pkv          |Individual is private health insured                      | Bool        |
+-------------+------------------------------------------------------------------------+
