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

    $ conda install -c gettsim -c conda-forge gettsim

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

+---------------------+--------------------------------------------------------+-------+
|    Variable         | Explanation                                            | Type  |
+=====================+========================================================+=======+
| hh_id               | Household identifier                                   | int   |
+---------------------+--------------------------------------------------------+-------+
| tu_id               | Tax Unit identifier                                    | int   |
+---------------------+--------------------------------------------------------+-------+
| p_id                | Personal identifier                                    | int   |
+---------------------+--------------------------------------------------------+-------+
| tu_vorstand         | Whether individual is head of tax unit                 | bool  |
+---------------------+--------------------------------------------------------+-------+
| anz_erwachsene_hh   | Number of adults in household                          | int   |
+---------------------+--------------------------------------------------------+-------+
| anz_minderj_hh      | Number of children between 0 and 18 in household       | int   |
+---------------------+--------------------------------------------------------+-------+
| vermögen_hh         | Wealth of household                                    | float |
+---------------------+--------------------------------------------------------+-------+
| bruttolohn_m        | Monthly wage of each individual                        | float |
+---------------------+--------------------------------------------------------+-------+
| alter               | Age of Individual                                      | int   |
+---------------------+--------------------------------------------------------+-------+
| selbstständig       | Whether individual is self-employed                    | bool  |
+---------------------+--------------------------------------------------------+-------+
| wohnort_ost         | Whether location in former east or west germany        | bool  |
+---------------------+--------------------------------------------------------+-------+
| hat_kinder          | Whether individual has kids                            | bool  |
+---------------------+--------------------------------------------------------+-------+
| eink_selbstst_m     | Monthly wage of selfemployment of each individual      | float |
+---------------------+--------------------------------------------------------+-------+
| ges_rente_m         | Monthly pension payments of each individual            | float |
+---------------------+--------------------------------------------------------+-------+
| prv_krankv_beit_m   | Whether individual is (only) privately health insured  | bool  |
+---------------------+--------------------------------------------------------+-------+
| prv_rente_beit_m    | Monthly contributions to private pension insurance     | float |
+---------------------+--------------------------------------------------------+-------+
| bruttolohn_vorj_m   | Average monthly earnings, previous year                | float |
+---------------------+--------------------------------------------------------+-------+
| arbeitsl_lfdj_m     | Months in unemployment, current year                   | float |
+---------------------+--------------------------------------------------------+-------+
| arbeitsl_vorj_m     | Months in unemployment, previous year                  | float |
+---------------------+--------------------------------------------------------+-------+
| arbeitsl_vor2j_m    | Months in unemployment, two years before               | float |
+---------------------+--------------------------------------------------------+-------+
| arbeitsstunden_w    | Weekly working hours of individual                     | int   |
+---------------------+--------------------------------------------------------+-------+
| anz_kinder_tu       | Number of children in tax unit                         | int   |
+---------------------+--------------------------------------------------------+-------+
| anz_erw_tu          | Number of adults in tax unit                           | int   |
+---------------------+--------------------------------------------------------+-------+
| geburtsjahr         | Year of birth                                          | int   |
+---------------------+--------------------------------------------------------+-------+
| j_arbeitserf        | Earning points for pension claim                       | float |
+---------------------+--------------------------------------------------------+-------+
| kind                | Dummy: Either below 18yrs, or below 25 and in          | bool  |
|                     | education                                              |       |
+---------------------+--------------------------------------------------------+-------+
| rentner             | Dummy: Pensioner employment status                     | bool  |
+---------------------+--------------------------------------------------------+-------+
| betreuungskost_m    | Monthly childcare expenses                             | float |
+---------------------+--------------------------------------------------------+-------+
| miete_unterstellt   | Monthly value of owner-occupied housing                | float |
+---------------------+--------------------------------------------------------+-------+
| kapital_eink_m      | Monthly capital income                                 | float |
+---------------------+--------------------------------------------------------+-------+
| vermiet_eink_m      | Monthly rental income                                  | float |
+---------------------+--------------------------------------------------------+-------+
| kaltmiete_m         | Monthly rent expenses (without heating)                | float |
+---------------------+--------------------------------------------------------+-------+
| heizkost_m          | Monthly heating expenses                               | float |
+---------------------+--------------------------------------------------------+-------+
| jahr_renteneintr    | Statutory retirement age (might be in the future)      | int   |
+---------------------+--------------------------------------------------------+-------+
| behinderungsgrad    | Handicap degree (between 0 and 100)                    | int   |
+---------------------+--------------------------------------------------------+-------+
| wohnfläche          | Size of dwelling in square meters                      | int   |
+---------------------+--------------------------------------------------------+-------+
| gem_veranlagt       | Dummy: Married couple filing jointly for income tax    | bool  |
+---------------------+--------------------------------------------------------+-------+
| in_ausbildung       | Dummy: Employment status "in education"                | bool  |
+---------------------+--------------------------------------------------------+-------+
| alleinerziehend     | Dummy: Single parent                                   | bool  |
+---------------------+--------------------------------------------------------+-------+
| bewohnt_eigentum    | Dummy: owner-occupied housing                          | bool  |
+---------------------+--------------------------------------------------------+-------+
| immobilie_baujahr   | Construction year of dwelling                          | int   |
|                     | (1: <1965,2:1966-2000,3:>2000)                         |       |
+---------------------+--------------------------------------------------------+-------+
| prv_transfers_m     | Sum of monthly public/private transfers not simulated. | int   |
|                     | E.g. transfers from parents, alimonies,                |       |
|                     | maternity leave payments                               |       |
+---------------------+--------------------------------------------------------+-------+


.. _returned_cols:

Columns returned by the simulator
---------------------------------

Note that if one of these columns exists, it will be overwritten.

+-------------------------+----------------------------------------------------+-------+
|    Variable             | Explanation                                        | type  |
+=========================+====================================================+=======+
| rentenv_beit_m          | Monthly amount employee old-age pensions contrib.  | float |
+-------------------------+----------------------------------------------------+-------+
| arbeitsl_v_beit_m       | Monthly amount employee unempl. insurance contrib. | float |
+-------------------------+----------------------------------------------------+-------+
| ges_krankv_beit_m       | Monthly amount employee health insurance contrib.  | float |
+-------------------------+----------------------------------------------------+-------+
| pflegev_beit_m          | Monthly amount of long term care insurance         | float |
+-------------------------+----------------------------------------------------+-------+
| arbeitsl_geld_m         | Monthly amount of unemployment assistance          | float |
+-------------------------+----------------------------------------------------+-------+
| rente_anspr_m           | Monthly amount of old-age pensions                 | float |
+-------------------------+----------------------------------------------------+-------+
| abgelt_st               | Monthly capital income tax due, individual         | float |
+-------------------------+----------------------------------------------------+-------+
| soli_st                 | Monthly solidarity surcharge due, individual       | float |
+-------------------------+----------------------------------------------------+-------+
| kindergeld_m            | Monthly child Benefit, individual                  | float |
+-------------------------+----------------------------------------------------+-------+
| eink_st                 | Monthly income Tax Due, individual                 | float |
+-------------------------+----------------------------------------------------+-------+
| eink_st_tu              | Monthly income Tax Due, couple sum                 | float |
+-------------------------+----------------------------------------------------+-------+
| unterhaltsvors_m        | Alimony advance payment, individual                | float |
+-------------------------+----------------------------------------------------+-------+
| regelsatz_m             | Household socio-economic *need*, lump-sum          | float |
+-------------------------+----------------------------------------------------+-------+
| kost_unterk_m           | Housing cost covered by social assistance          | float |
+-------------------------+----------------------------------------------------+-------+
| kinderzuschlag_m        | Monthly additional child benefit, household sum    | float |
+-------------------------+----------------------------------------------------+-------+
| wohngeld_m              | Monthly housing benefit, household sum             | float |
+-------------------------+----------------------------------------------------+-------+
| arbeitsl_geld_2_m       | Monthly social assistance, household sum           | float |
+-------------------------+----------------------------------------------------+-------+
| verfüg_eink_m           | Monthly disposable income, individual              | float |
+-------------------------+----------------------------------------------------+-------+
| verfüg_eink_hh_m        | Monthly disposable income including household      | float |
|                         | level benefits, household sum                      |       |
+-------------------------+----------------------------------------------------+-------+
