====================================
GEP 1 - Convention on Variable Names
====================================

:Author: `Eric Sommer <https://github.com/Eric-Sommer>`
:Status: Provisional
:Type: Standards
:Created: 2019-11-04


This GEP specifies a framework on how to name variables bearing information on persons or
households. These usually come as columns in dataframes or, sometimes, as standard python
variables. They should therefore not be confused with *parameters* or other variables 
needed during run-time. A convention on variable names should make the code easier to 
understand and to maintain. In addition, it should lower the requirement to consult
the documentation.

There are three types of variables:
1. Input variables: what the user feeds into the model.
2. Intermediate variables: variables calculated during run-time in `gettsim`, but which 
   are not returned by default.
3. Output variables.

General Guidelines
^^^^^^^^^^^^^^^^^^ 
- lower case letters only. Exceptions are specified below.
- longer names should be interrupted with underscores, e.g. `alg2_anzurechnendes_ek`
- use of booelan type for dummy variables rather than integer. Boolean variables can be negated easily 
  (mind the difference between `~` and `not` in pandas vs. core python) and make the code easier to read.


Input Variables
^^^^^^^^^^^^^^^

First letter specifies type of variable
----------------------------------------
In the spirit of the Euromod_ framework, I suggest that the type of a variable is indicated by its first letter


+--------------+-----------------------------------+----------------------------------------------------------+
| First letter | Type of Variable                  | Examples                                                 |
+==============+===================================+==========================================================+
| d            | demographic                       | dage, dchild, dnchildren, dsex, deast, dmarried, dhhsize |
+--------------+-----------------------------------+----------------------------------------------------------+
| y            | market income                     | ywage, yself, ycap, yrent                                |
+--------------+-----------------------------------+----------------------------------------------------------+
| l            | labor market                      |  lhrs, lstatus                                           |
+--------------+-----------------------------------+----------------------------------------------------------+
| b            | benefits (i.e. non-market income) | balim, boldagepen, bsocass                               |
+--------------+-----------------------------------+----------------------------------------------------------+
| h            | housing                           | hsize, hrent, hheat                                      |
+--------------+-----------------------------------+----------------------------------------------------------+
| x            | expenses                          | xchildcare                                               |
+--------------+-----------------------------------+----------------------------------------------------------+
| a            | assets/wealth                     |  afinancial, aproperty                                   |
+--------------+-----------------------------------+----------------------------------------------------------+

The table above demonstrates the virtue of the first letter identification. `hsize` can easily be misunderstood as the household size, which is a demographic variable. The first letter `h` avoids this misinterpretation.

Identifiers (`pid`, `hid`, `tu_id`) constitute a special form of input variables, along with pointers to ids within the household.

If applicable, the last UPPERCASE letter specifies the time frame
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When modelling the tax-ben system, it is easy to lose track on which period a particular variable is defined (e.g. wage is defined on the monthly or yearly level). For this reason, we could indicate by the last letter the reference time frame for this variable. This applies both to input (incomes) as well as intermediate variables (taxable income, relevant income for some benefit).


+-------------+------------+----------------+
| Last Letter | Time Frame | Example        |
+=============+============+================+
| D           | Day        |                |
+-------------+------------+----------------+
| W           | Week       | lhrsW          |
+-------------+------------+----------------+
| M           | Month      | hrentM, ywageM |
+-------------+------------+----------------+
| Y           | Year       | zveY           |
+-------------+------------+----------------+


Intermediate Variables
^^^^^^^^^^^^^^^^^^^^^^

As there are many intermediate variables which greatly differ in their type and which are often only useful within the particular function, there is no need to specify too detailed conventions. However,

1. use names which reflect the legal issue in *German*
2. explain the variable in a comment *above* its definition
3. maximum variable length: ??

Output Variables
^^^^^^^^^^^^^^^^

**All output is in monthly terms!**


+-------------------------------+----------------------------------+-------------+------------------+
| Type                          | Variable                         | Name        | attributed to    |
+===============================+==================================+=============+==================+
| Income Aggregates             | Gross Income                     | inc_gross   | household_head   |
+                               +----------------------------------+-------------+------------------+
|                               | Disp. Income                     | inc_disp    | household_head   |
+                               +----------------------------------+-------------+------------------+
|                               | Net Income                       | inc_net     | household_head   |
+-------------------------------+----------------------------------+-------------+------------------+
| Market Incomes                | *identical to input data*        |             | individual       |
+-------------------------------+----------------------------------+-------------+------------------+
| Taxes                         | All income-related taxes         | tax_total   | household_head   |
+                               +----------------------------------+-------------+------------------+
|                               | Income Tax                       | tax_inc     | household_head   |
+                               +----------------------------------+-------------+------------------+
|                               | Solidarity Surcharge             | tax_soli    | household_head   |
+                               +----------------------------------+-------------+------------------+
|                               | Capital Income Tax               | tax_capinc  | household_head   |
+-------------------------------+----------------------------------+-------------+------------------+
| Social Security Contributions | All (no employer contributions!) | ssc_total   | individual       |
+                               +----------------------------------+-------------+------------------+
|                               | Old-Age Pension                  | ssc_pens    | individual       |
+                               +----------------------------------+-------------+------------------+
|                               | Health Care                      | ssc_health  | individual       |
+                               +----------------------------------+-------------+------------------+
|                               | Unemployment Insurance           | ssc_ue      | individual       |
+                               +----------------------------------+-------------+------------------+
|                               | Care                             | ssc_care    | individual       |
+-------------------------------+----------------------------------+-------------+------------------+
| Benefits                      | All                              | ben_total   | household head   |
+                               +----------------------------------+-------------+------------------+
|                               | Child Benefit                    | ben_ch      | individual child |
+                               +----------------------------------+-------------+------------------+
|                               | Unemployment Benefit (ALG II)    | ben_alg2    | household head   |
+                               +----------------------------------+-------------+------------------+
|                               | Unemployment Insurance           | ben_ui      | individual       |
+                               +----------------------------------+-------------+------------------+
|                               | Alimony Advance Payment          | ben_uhv     | individual child |
+                               +----------------------------------+-------------+------------------+
|                               | Social Assistance                | ben_sa      | household head   |
+                               +----------------------------------+-------------+------------------+
|                               | Additional Child Benefit         | ben_addch   | household head   |
+-------------------------------+----------------------------------+-------------+------------------+


**Issues to clarify:**

1. How do we deal with tax-benefit items which we don't simulate but take from the input data? (e.g. pensions, alimony payments)
2. The output returns data as one row per person. We have to think on how to attribute outputs in a meaningful manner. At the same time, calculation of income aggregates should be straightforward.

Documentation
^^^^^^^^^^^^^ 

In the medium-term, or along with this GEP, we need a list with the definition for input and output variables. It should contain

1. variable name
2. description
3. range of allowed values

.. _Euromod: https://www.euromod.ac.uk/sites/default/files/working-papers/EMTN-1.1.pdf
