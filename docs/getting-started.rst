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
columns specified below in :ref:`returned_cols`.


.. _required_cols:

Required columns in input data
-------------------------------

+--------------+---------------------------------------------------------+-------------+
|   Variable   |Explanation                                              | Type        +
+==============+=========================================================+=============+
|hid           |Household identifier                                     | Int         |
+--------------+---------------------------------------------------------+-------------+
|tu_id         |Tax Unit identifier                                      | Int         |
+--------------+---------------------------------------------------------+-------------+
|pid           |Personal identifier                                      | Int         |
+--------------+---------------------------------------------------------+-------------+
|head_tu       |Whether individual is head of tax unit                   | Bool        |
+--------------+---------------------------------------------------------+-------------+
|head          |Whether individual is head of household                  | Bool        |
+--------------+---------------------------------------------------------+-------------+
|adult_num     |Number of adults in household                            | Int         |
+--------------+---------------------------------------------------------+-------------+
|child0_18_num |Number of children between 0 and 18 in household         | Int         |
+--------------+---------------------------------------------------------+-------------+
|hh_wealth     |Wealth of household                                      | Float       |
+--------------+---------------------------------------------------------+-------------+
|m_wage        |Monthly wage of each individual                          | Float       |
+--------------+---------------------------------------------------------+-------------+
|age           |Age of Individual                                        | Int         |
+--------------+---------------------------------------------------------+-------------+
|selfemployed  |Whether individual is self-employed                      | Bool        |
+--------------+---------------------------------------------------------+-------------+
|east          |Whether location in former east or west germany          | Bool        |
+--------------+---------------------------------------------------------+-------------+
|haskids       |Whether individual has kids                              | Bool        |
+--------------+---------------------------------------------------------+-------------+
|m_self        |Monthly wage of selfemployment of each individual        | Float       |
+--------------+---------------------------------------------------------+-------------+
|m_pensions    |Monthly pension payments of each individual              | Float       |
+--------------+---------------------------------------------------------+-------------+
|pkv           |Whether individual is (only) privately health insured    | Bool        |
+--------------+---------------------------------------------------------+-------------+
|m_wage_l1     |Average monthly earnings, previous year                  | Float       |
+--------------+---------------------------------------------------------+-------------+
|months_ue     |Months in unemployment, current year                     | Float       |
+--------------+---------------------------------------------------------+-------------+
|months_ue_l1  |Months in unemployment, previous year                    | Float       |
+--------------+---------------------------------------------------------+-------------+
|months_ue_l2  |Months in unemployment, two years before                 | Float       |
+--------------+---------------------------------------------------------+-------------+
|w_hours       |Weekly working hours of individual                       | Int         |
+--------------+---------------------------------------------------------+-------------+
|child_num_tu  |Number of children in tax unit                           | Int         |
+--------------+---------------------------------------------------------+-------------+
|adult_num_tu  |Number of adults in tax unit                             | Int         |
+--------------+---------------------------------------------------------+-------------+
|byear         |Year of Birth                                            | Int         |
+--------------+---------------------------------------------------------+-------------+
|exper         |Labor Market Experience, in years                        | Int         |
+--------------+---------------------------------------------------------+-------------+
|EP            |Earning points for pension claim                         | Float       |
+--------------+---------------------------------------------------------+-------------+
|child         |Dummy: Either below 18yrs, or below 25 and in education  | Bool        |
+--------------+---------------------------------------------------------+-------------+
|pensioner     |Dummy: Pensioner employment status                       | Bool        |
+--------------+---------------------------------------------------------+-------------+
|m_childcare   |Monthly childcare expenses                               | Float       |
+--------------+---------------------------------------------------------+-------------+
|m_imputedrent |Monthly value of owner-occupied housing                  | Float       |
+--------------+---------------------------------------------------------+-------------+
|m_kapinc      |Monthly capital income                                   | Float       |
+--------------+---------------------------------------------------------+-------------+
|m_vermiet     |Monthly rental income                                    | Float       |
+--------------+---------------------------------------------------------+-------------+
|miete         |Monthly rent expenses (without heating)                  | Float       |
+--------------+---------------------------------------------------------+-------------+
|heizkost      |Monthly heating expenses                                 | Float       |
+--------------+---------------------------------------------------------+-------------+
|renteneintritt|Retirement age                                           | Int         |
+--------------+---------------------------------------------------------+-------------+
|handcap_degree|Handicap Degree (between 0 and 100                       | Int         |
+--------------+---------------------------------------------------------+-------------+
|wohnfl        |Size of dwelling in square meters                        | Int         |
+--------------+---------------------------------------------------------+-------------+
|zveranl       |Dummy: Married couple filing jointly for income tax      | Bool        |
+--------------+---------------------------------------------------------+-------------+
|ineducation   |Dummy: Employment status "in education"                  | Bool        |
+--------------+---------------------------------------------------------+-------------+
|alleinerz     |Dummy: Single parent                                     | Bool        |
+--------------+---------------------------------------------------------+-------------+
|eigentum      |Dummy: Owner-occupied housing                            | Bool        |
+--------------+---------------------------------------------------------+-------------+
|cnstyr        |Constr. year of dwelling (1: <1965,2:1966-2000,3:>2000)  | Int         |
+--------------+---------------------------------------------------------+-------------+
|m_transfers   |Sum of monthly public/private transfers not simulated    | Int         |
+--------------+---------------------------------------------------------+-------------+


.. _returned_cols:

Columns returned by the simulator
---------------------------------

Note that if one of these columns exists, it will be overwritten.

+-------------------+----------------------------------------------------+-------------+
|   Variable        |Explanation                                         | Type        +
+===================+====================================================+=============+
|svbeit             |Monthly amount employee soc. sec. contributions      | Float      |
+-------------------+-----------------------------------------------------+------------+
|rvbeit             |Monthly amount employee old-age pensions contrib.    | Float      |
+-------------------+-----------------------------------------------------+------------+
|avbeit             |Monthly amount employee unempl. insurance contrib.   | Float      |
+-------------------+-----------------------------------------------------+------------+
|gkvbeit            |Monthly amount employee health insurance contrib.    | Float      |
+-------------------+-----------------------------------------------------+------------+
|m_alg1             |Monthly amount of unemployment assistance            | Float      |
+-------------------+-----------------------------------------------------+------------+
|pensions_sim       |Monthly amount of old-age pensions                   | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross_e1           |Taxable inc. from self-employment, individual        | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross_e5           |Taxable inc. from capital, individual                | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross_e6           |Taxable inc. from rents, individual                  | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross_e7           |Taxable inc. from pensions, individual               | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross_e1_tu        |Taxable inc. from self-employment, couple sum        | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross_e4_tu        |Taxable inc. from earnings, couple sum               | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross_e5_tu        |Taxable inc. from capital, couple sum                | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross_e6_tu        |Taxable inc. from rents, couple sum                  | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross_e7_tu        |Taxable inc. from pensions, couple sum               | Float      |
+-------------------+-----------------------------------------------------+------------+
|abgst_tu           |Monthly capital income tax burden, couple sum        | Float      |
+-------------------+-----------------------------------------------------+------------+
|abgst              |Monthly capital income tax burden, individual        | Float      |
+-------------------+-----------------------------------------------------+------------+
|soli               |Monthly solidarity surcharge tax burden, individual  | Float      |
+-------------------+-----------------------------------------------------+------------+
|soli_tu            |Monthly solidarity surcharge tax due, couple sum     | Float      |
+-------------------+-----------------------------------------------------+------------+
|kindergeld         |Monthly child benefit, assigned to the child         | Float      |
+-------------------+-----------------------------------------------------+------------+
|kindergeld_tu      |Monthly child benefit, sum of tax unit               | Float      |
+-------------------+-----------------------------------------------------+------------+
|incometax          |Monthly income tax burden, individual                | Float      |
+-------------------+-----------------------------------------------------+------------+
|incometax_tu       |Monthly income tax burden, couple sum                | Float      |
+-------------------+-----------------------------------------------------+------------+
|uhv                |Alimony advance payment, assigned to the child       | Float      |
+-------------------+-----------------------------------------------------+------------+
|uhv_hh             |Alimony advance payment, household sum               | Float      |
+-------------------+-----------------------------------------------------+------------+
|regelbedarf        |Household socio-economic *need*, incl. housing cost  | Float      |
+-------------------+-----------------------------------------------------+------------+
|regelsatz          |Household socio-economic *need*, lump-sum            | Float      |
+-------------------+-----------------------------------------------------+------------+
|alg2_kdu           |Appropriate housing costs for a family in *need*     | Float      |
+-------------------+-----------------------------------------------------+------------+
|kiz                |Monthly additional child benefit, household sum      | Float      |
+-------------------+-----------------------------------------------------+------------+
|wohngeld           |Monthly housing benefit, household sum               | Float      |
+-------------------+-----------------------------------------------------+------------+
|m_alg2             |Monthly social assistance, household sum             | Float      |
+-------------------+-----------------------------------------------------+------------+
|dpi_ind            |Monthly disposable income, individual                | Float      |
+-------------------+-----------------------------------------------------+------------+
|dpi                |Monthly disposable income, household sum             | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross              |Monthly market income                                | Float      |
+-------------------+-----------------------------------------------------+------------+
