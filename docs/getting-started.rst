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
|hhtyp         |                                                         | Int         |
+--------------+---------------------------------------------------------+-------------+
|hhsize        |Size of household                                        | Int         |
+--------------+---------------------------------------------------------+-------------+
|hhsize_tu     |Size of tax unit                                         | Int         |
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
|avg_ep        |                                                         | Float       |
+--------------+---------------------------------------------------------+-------------+
|EP            |                                                         | Float       |
+--------------+---------------------------------------------------------+-------------+
|child         |Dummy: either below 18yrs, or below 25 and in education  | Bool        |
+--------------+---------------------------------------------------------+-------------+
|pensioner     |Dummy: pensioner employment status                       | Bool        |
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
|divdy         |Yearly capital income                                    | Float       |
+--------------+---------------------------------------------------------+-------------+
|heizkost      |Monthly heating expenses                                 | Float       |
+--------------+---------------------------------------------------------+-------------+
|renteneintritt|retirement age                                           | Int         |
+--------------+---------------------------------------------------------+-------------+
|handcap_degree|Handicap Degree (between 0 and 100                       | Int         |
+--------------+---------------------------------------------------------+-------------+
|wohnfl        |size of dwelling in sqm                                  | Int         |
+--------------+---------------------------------------------------------+-------------+
|zveranl       |Dummy: married couple filing jointly for income tax      | Bool        |
+--------------+---------------------------------------------------------+-------------+
|ineducation   |Dummy: employment status "in education"                  | Bool        |
+--------------+---------------------------------------------------------+-------------+
|alleinerz     |Dummy: Single Parent                                     | Bool        |
+--------------+---------------------------------------------------------+-------------+
|eigentum      |Dummy: Owner-occupied housing                            | Bool        |
+--------------+---------------------------------------------------------+-------------+
|cnstyr        |Constr. Yr of Dwelling (1: <1965,2:1966-2000,3:>2000)    | Int         |
+--------------+---------------------------------------------------------+-------------+
|m_transfers   |Sum of monthly public/pricate transfers not simulated    | Int         |
+--------------+---------------------------------------------------------+-------------+
|hh_korr       |                                                         | Int         |
+--------------+---------------------------------------------------------+-------------+


.. _returned_cols:

Columns returned by the simulator
---------------------------------

Note that if one of these columns exists, it will be overwritten.

+-------------------+----------------------------------------------------+-------------+
|   Variable        |Explanation                                         | Type        +
+===================+====================================================+=============+
|svbeit             |Monthly Amount Employee Soc. Sec. Contributions      | Float      |
+-------------------+-----------------------------------------------------+------------+
|rvbeit             |Monthly Amount Employee Old-Age Pensions Contrib.    | Float      |
+-------------------+-----------------------------------------------------+------------+
|avbeit             |Monthly Amount Employee Unempl. Insurance Contrib.   | Float      |
+-------------------+-----------------------------------------------------+------------+
|gkvbeit            |Monthly Amount Employee Health Insurance Contrib.    | Float      |
+-------------------+-----------------------------------------------------+------------+
|m_alg1             |Monthly Amount of Unemployment Assistance            | Float      |
+-------------------+-----------------------------------------------------+------------+
|pensions_sim       |Monthly amount of old-age pensions                   | Float      |
+-------------------+-----------------------------------------------------+------------+
|zve_abg_nokfb      |Annual taxable income, no child allowance            | Float      |
+-------------------+-----------------------------------------------------+------------+
|zve_abg_kfb        |Annual taxable income, including child allowance     | Float      |
+-------------------+-----------------------------------------------------+------------+
|kifreib            |Child Allowance                                      | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross_e1           |Taxable Inc. from Self-Employment, individual        | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross_e5           |Taxable Inc. from Capital, individual                | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross_e6           |Taxable Inc. from Rents, individual                  | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross_e7           |Taxable Inc. from Pensions, individual               | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross_e1_tu        |Taxable Inc. from Self-Employment, couple sum        | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross_e4_tu        |Taxable Inc. from Earnings, couple sum               | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross_e5_tu        |Taxable Inc. from Capital, couple sum                | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross_e6_tu        |Taxable Inc. from Rents, couple sum                  | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross_e7_tu        |Taxable Inc. from Pensions, couple sum               | Float      |
+-------------------+-----------------------------------------------------+------------+
|ertragsanteil      |                                                     | Float      |
+-------------------+-----------------------------------------------------+------------+
|sonder             |                                                     | Float      |
+-------------------+-----------------------------------------------------+------------+
|hhfreib            |                                                     | Float      |
+-------------------+-----------------------------------------------------+------------+
|altfreib           |                                                     | Float      |
+-------------------+-----------------------------------------------------+------------+
|vorsorge           |                                                     | Float      |
+-------------------+-----------------------------------------------------+------------+
|tax_kfb            |Monthly Income Tax Due, individual, child allow.     | Float      |
+-------------------+-----------------------------------------------------+------------+
|tax_nokfb          |Monthly Income Tax Due, individual, no child allow.  | Float      |
+-------------------+-----------------------------------------------------+------------+
|tax_kfb_tu         |Monthly Income Tax Due, couple sum, child allow.     | Float      |
+-------------------+-----------------------------------------------------+------------+
|tax_nokfb_tu       |Monthly Income Tax Due, couple sum, no child allow.  | Float      |
+-------------------+-----------------------------------------------------+------------+
|abgst_tu           |Monthly Capital Income Tax Due, couple sum           | Float      |
+-------------------+-----------------------------------------------------+------------+
|abgst              |Monthly Capital Income Tax Due, individual           | Float      |
+-------------------+-----------------------------------------------------+------------+
|soli               |Monthly Solidarity Surcharge due, individual         | Float      |
+-------------------+-----------------------------------------------------+------------+
|soli_tu            |Monthly Solidarity Surcharge due, couple sum         | Float      |
+-------------------+-----------------------------------------------------+------------+
|kindergeld_basis   |Monthly Child Benefit, individual to the child       | Float      |
+-------------------+-----------------------------------------------------+------------+
|kindergeld_tu_basis|Monthly Child Benefit, household sum                 | Float      |
+-------------------+-----------------------------------------------------+------------+
|incometax_tu       |Monthly Income Tax Due, couple sum                   | Float      |
+-------------------+-----------------------------------------------------+------------+
|incometax          |Monthly Income Tax Due, individual                   | Float      |
+-------------------+-----------------------------------------------------+------------+
|kindergeld         |                                                     | Float      |
+-------------------+-----------------------------------------------------+------------+
|kindergeld_hh      |                                                     | Float      |
+-------------------+-----------------------------------------------------+------------+
|kindergeld_tu      |                                                     | Float      |
+-------------------+-----------------------------------------------------+------------+
|uhv                |Alimony Advance payment, individual to the child     | Float      |
+-------------------+-----------------------------------------------------+------------+
|wohngeld_basis     |                                                     | Float      |
+-------------------+-----------------------------------------------------+------------+
|wohngeld_basis_hh  |                                                     | Float      |
+-------------------+-----------------------------------------------------+------------+
|ar_alg2_ek_hh      |                                                     | Float      |
+-------------------+-----------------------------------------------------+------------+
|alg2_grossek_hh    |                                                     | Float      |
+-------------------+-----------------------------------------------------+------------+
|mehrbed            |                                                     | Float      |
+-------------------+-----------------------------------------------------+------------+
|regelbedarf        |Household socio-economic *need*, incl. housing cost  | Float      |
+-------------------+-----------------------------------------------------+------------+
|regelsatz          |Household socio-economic *need*, lump-sum            | Float      |
+-------------------+-----------------------------------------------------+------------+
|alg2_kdu           |Household Appropriate Housing Cost                   | Float      |
+-------------------+-----------------------------------------------------+------------+
|uhv_hh             |Alimony Advance payment, household sum               | Float      |
+-------------------+-----------------------------------------------------+------------+
|ekanrefrei         |                                                     | Float      |
+-------------------+-----------------------------------------------------+------------+
|kiz_temp           |                                                     | Float      |
+-------------------+-----------------------------------------------------+------------+
|kiz_incrange       |                                                     | Float      |
+-------------------+-----------------------------------------------------+------------+
|kiz                |Monthly additional child benefit, household sum      | Float      |
+-------------------+-----------------------------------------------------+------------+
|wohngeld           |Monthly housing benefit, household sum               | Float      |
+-------------------+-----------------------------------------------------+------------+
|m_alg2             |Monthly social assistance, household sum             | Float      |
+-------------------+-----------------------------------------------------+------------+
|dpi_ind            |Monthly disposable income, individual                | Float      |
+-------------------+-----------------------------------------------------+------------+
|dpi                |Monthly disposable income, household                 | Float      |
+-------------------+-----------------------------------------------------+------------+
|gross              |Monthly market income                                | Float      |
+-------------------+-----------------------------------------------------+------------+
