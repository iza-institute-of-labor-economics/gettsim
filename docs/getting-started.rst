Getting Started
===============

Installation
------------

The recommended way to install GETTSIM is via `conda <https://conda.io/>`_, the
standard package manager for scientific Python libraries. If conda is not installed on
your machine, please follow the `installation instructions
<https://docs.conda.io/projects/conda/en/latest/user-guide/install/>`_ of its user
guide.

With conda available on your path, installing GETTSIM is as simple as typing

.. code-block:: bash

    $ conda install -c gettsim gettsim

in a command shell.

To validate the installation, start a Python shell and type

.. code-block:: python

    import gettsim

    gettsim.test()


.. _usage:

Usage
-----

Say you have a dataset for the year 2019 that you store in a
`pandas <https://pandas.pydata.org/>`_ DataFrame using the variable name ``data``.
Your dataset needs to adhere to a particular format; all the columns specified in
:ref:`required_cols` below need to be present.

To calculate the taxes and transfers for the households / tax units / individuals in
the dataset, you can use the following Python code:

.. code-block:: python

    from gettsim.tax_transfer import calculate_tax_and_transfers


    calculate_tax_and_transfers(dataset=data, year_of_policy=2019)


The function ``calculate_tax_and_transfers`` will update your dataset ``data`` with the
columns specified below in :ref:`returned_cols`. Note that the dataset needs to be in
long format, i.e. each person no matter what age has his/her own row.


.. _required_cols:

Required columns in input data
-------------------------------

+--------------------+---------------------------------------------------------+-------+
|   Variable         |Explanation                                              | Type  |
+====================+=========================================================+=======+
|hid                 |Household identifier                                     | int   |
+--------------------+---------------------------------------------------------+-------+
|tu_id               |Tax Unit identifier                                      | int   |
+--------------------+---------------------------------------------------------+-------+
|pid                 |Personal identifier                                      | int   |
+--------------------+---------------------------------------------------------+-------+
|head_tu             |Whether individual is head of tax unit                   | bool  |
+--------------------+---------------------------------------------------------+-------+
|head                |Whether individual is head of household                  | bool  |
+--------------------+---------------------------------------------------------+-------+
|adult_num           |Number of adults in household                            | int   |
+--------------------+---------------------------------------------------------+-------+
|child0_18_num       |Number of children between 0 and 18 in household         | int   |
+--------------------+---------------------------------------------------------+-------+
|hh_wealth           |Wealth of household                                      | float |
+--------------------+---------------------------------------------------------+-------+
|m_wage              |Monthly wage of each individual                          | float |
+--------------------+---------------------------------------------------------+-------+
|age                 |Age of Individual                                        | int   |
+--------------------+---------------------------------------------------------+-------+
|selfemployed        |Whether individual is self-employed                      | bool  |
+--------------------+---------------------------------------------------------+-------+
|east                |Whether location in former east or west germany          | bool  |
+--------------------+---------------------------------------------------------+-------+
|haskids             |Whether individual has kids                              | bool  |
+--------------------+---------------------------------------------------------+-------+
|m_self              |Monthly wage of selfemployment of each individual        | float |
+--------------------+---------------------------------------------------------+-------+
|m_pensions          |Monthly pension payments of each individual              | float |
+--------------------+---------------------------------------------------------+-------+
|pkv                 |Whether individual is (only) privately health insured    | bool  |
+--------------------+---------------------------------------------------------+-------+
|priv_pens_contr     |Monthly contributions to private pension insurance       | float |
+--------------------+---------------------------------------------------------+-------+
|m_wage_l1           |Average monthly earnings, previous year                  | float |
+--------------------+---------------------------------------------------------+-------+
|months_ue           |Months in unemployment, current year                     | float |
+--------------------+---------------------------------------------------------+-------+
|months_ue_l1        |Months in unemployment, previous year                    | float |
+--------------------+---------------------------------------------------------+-------+
|months_ue_l2        |Months in unemployment, two years before                 | float |
+--------------------+---------------------------------------------------------+-------+
|w_hours             |Weekly working hours of individual                       | int   |
+--------------------+---------------------------------------------------------+-------+
|child_num_tu        |Number of children in tax unit                           | int   |
+--------------------+---------------------------------------------------------+-------+
|adult_num_tu        |Number of adults in tax unit                             | int   |
+--------------------+---------------------------------------------------------+-------+
|byear               |Year of birth                                            | int   |
+--------------------+---------------------------------------------------------+-------+
|exper               |Labor market experience, in years                        | int   |
+--------------------+---------------------------------------------------------+-------+
|EP                  |Earning points for pension claim                         | float |
+--------------------+---------------------------------------------------------+-------+
|child               |Dummy: Either below 18yrs, or below 25 and in education  | bool  |
+--------------------+---------------------------------------------------------+-------+
|pensioner           |Dummy: Pensioner employment status                       | bool  |
+--------------------+---------------------------------------------------------+-------+
|m_childcare         |Monthly childcare expenses                               | float |
+--------------------+---------------------------------------------------------+-------+
|m_imputedrent       |Monthly value of owner-occupied housing                  | float |
+--------------------+---------------------------------------------------------+-------+
|m_kapinc            |Monthly capital income                                   | float |
+--------------------+---------------------------------------------------------+-------+
|m_vermiet           |Monthly rental income                                    | float |
+--------------------+---------------------------------------------------------+-------+
|miete               |Monthly rent expenses (without heating)                  | float |
+--------------------+---------------------------------------------------------+-------+
|heizkost            |Monthly heating expenses                                 | float |
+--------------------+---------------------------------------------------------+-------+
|renteneintritt      |Statutory retirement age (might be in the future)        | int   |
+--------------------+---------------------------------------------------------+-------+
|handcap_degree      |Handicap degree (between 0 and 100)                      | int   |
+--------------------+---------------------------------------------------------+-------+
|wohnfl              |Size of dwelling in square meters                        | int   |
+--------------------+---------------------------------------------------------+-------+
|zveranl             |Dummy: Married couple filing jointly for income tax      | bool  |
+--------------------+---------------------------------------------------------+-------+
|ineducation         |Dummy: Employment status "in education"                  | bool  |
+--------------------+---------------------------------------------------------+-------+
|alleinerz           |Dummy: Single parent                                     | bool  |
+--------------------+---------------------------------------------------------+-------+
|eigentum            |Dummy: owner-occupied housing                            | bool  |
+--------------------+---------------------------------------------------------+-------+
|cnstyr              |Construction year of dwelling                            | int   |
|                    |(1: <1965,2:1966-2000,3:>2000)                           |       |
+--------------------+---------------------------------------------------------+-------+
|m_transfers         |Sum of monthly public/private transfers not simulated.   | int   |
|                    |E.g. transfers from parents, alimonies,                  |       |
|                    |maternity leave payments                                 |       |
+--------------------+---------------------------------------------------------+-------+


.. _returned_cols:

Columns returned by the simulator
---------------------------------

Note that if one of these columns exists, it will be overwritten.

+------------------------+-----------------------------------------------------+-------+
|   Variable             |Explanation                                          | type  |
+========================+=====================================================+=======+
|svbeit                  |Monthly amount employee soc. sec. contributions      | float |
+------------------------+-----------------------------------------------------+-------+
|rvbeit                  |Monthly amount employee old-age pensions contrib.    | float |
+------------------------+-----------------------------------------------------+-------+
|avbeit                  |Monthly amount employee unempl. insurance contrib.   | float |
+------------------------+-----------------------------------------------------+-------+
|gkvbeit                 |Monthly amount employee health insurance contrib.    | float |
+------------------------+-----------------------------------------------------+-------+
|m_alg1                  |Monthly amount of unemployment assistance            | float |
+------------------------+-----------------------------------------------------+-------+
|pensions_sim            |Monthly amount of old-age pensions                   | float |
+------------------------+-----------------------------------------------------+-------+
|gross_e1                |Inc. from self-employment subject to tax, individual | float |
+------------------------+-----------------------------------------------------+-------+
|gross_e5                |Inc. from Capital subject to tax, individual         | float |
+------------------------+-----------------------------------------------------+-------+
|gross_e6                |Inc. from Rents subject to tax, individual           | float |
+------------------------+-----------------------------------------------------+-------+
|gross_e7                |Inc. from Pensions subject to tax, individual        | float |
+------------------------+-----------------------------------------------------+-------+
|gross_e1_tu             |Inc. from Self-Employment subject to tax, couple sum | float |
+------------------------+-----------------------------------------------------+-------+
|gross_e4_tu             |Inc. from Earnings subject to tax, couple sum        | float |
+------------------------+-----------------------------------------------------+-------+
|gross_e5_tu             |Inc. from Capital subject to tax, couple sum         | float |
+------------------------+-----------------------------------------------------+-------+
|gross_e6_tu             |Inc. from Rents subject to tax, couple sum           | float |
+------------------------+-----------------------------------------------------+-------+
|gross_e7_tu             |Inc. from Pensions subject to tax, couple sum        | float |
+------------------------+-----------------------------------------------------+-------+
|abgst_tu                |Monthly capital cncome tax due, couple sum           | float |
+------------------------+-----------------------------------------------------+-------+
|abgst                   |Monthly capital cncome tax due, individual           | float |
+------------------------+-----------------------------------------------------+-------+
|soli                    |Monthly solidarity surcharge due, individual         | float |
+------------------------+-----------------------------------------------------+-------+
|soli_tu                 |Monthly solidarity surcharge due, couple sum         | float |
+------------------------+-----------------------------------------------------+-------+
|kindergeld              |Monthly child Benefit, individual                    | float |
+------------------------+-----------------------------------------------------+-------+
|kindergeld_tu           |Monthly child Benefit, household sum                 | float |
+------------------------+-----------------------------------------------------+-------+
|incometax               |Monthly income Tax Due, individual                   | float |
+------------------------+-----------------------------------------------------+-------+
|incometax_tu            |Monthly income Tax Due, couple sum                   | float |
+------------------------+-----------------------------------------------------+-------+
|uhv                     |Alimony advance payment, individual                  | float |
+------------------------+-----------------------------------------------------+-------+
|regelbedarf             |Household socio-economic *need*, incl. housing cost  | float |
+------------------------+-----------------------------------------------------+-------+
|regelsatz               |Household socio-economic *need*, lump-sum            | float |
+------------------------+-----------------------------------------------------+-------+
|alg2_kdu                |Housing cost covered by social assistance            | float |
+------------------------+-----------------------------------------------------+-------+
|uhv_hh                  |Alimony advance payment, household sum               | float |
+------------------------+-----------------------------------------------------+-------+
|kiz                     |Monthly additional child benefit, household sum      | float |
+------------------------+-----------------------------------------------------+-------+
|wohngeld                |Monthly housing benefit, household sum               | float |
+------------------------+-----------------------------------------------------+-------+
|m_alg2                  |Monthly social assistance, household sum             | float |
+------------------------+-----------------------------------------------------+-------+
|dpi_ind                 |Monthly disposable income, individual                | float |
+------------------------+-----------------------------------------------------+-------+
|dpi                     |Monthly disposable income, household sum             | float |
+------------------------+-----------------------------------------------------+-------+
|gross                   |Monthly market income                                | float |
+------------------------+-----------------------------------------------------+-------+
