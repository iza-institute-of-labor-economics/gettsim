.. _param_files:

Parameter files
===============

The parameters of the tax and transfer system are stored in compartment specific
dictionaries. The :code:`params` argument created in :func:`set_up_policy_environment`
and then used in :func:`compute_taxes_and_transfers` is a dictionary of these
compartment specific dictionaries. Thus it is a dictionary of dictionaries, where the
keys are the name of the compartment. The files from which
:func:`set_up_policy_environment` loads the default paramters for each year, can be
found `here <https://github.com/iza-institute-of-labor-economics/gettsim/tree/main
/gettsim/parameters>`_ and are named by the compartment. Our current guidlines on how
these files are set up can be found in the GEP-2.

Inside GETTSIM, functions don't operate with the full :code:`params` file and
instead just use each compartment specific parameter dictionary. The names of these
dictionaries are named by the structure :code:`compartment_name + _params`. The explicit
names can be found in the table below. GETTSIM reads the function arguments and
selects the corresponding part of the :code:`params` file. For GETTSIM to read and
process the arguments of functions correctly the :code:`compartment_name + _params`
variables have to be last inputs in the function signature.


+---------------------------+--------------------------------+
| Parameter file name       | Compartment of gettsim         |
+===========================+================================+
| _`soz_vers_beitr_params`  | Social insurance contributions |
+---------------------------+--------------------------------+
| _`eink_st_params`         | Income tax                     |
+---------------------------+--------------------------------+
| _`eink_st_abzüge_params` | Income tax deductions          |
+---------------------------+--------------------------------+
| _`soli_st_params`         | Solidarity surcharge           |
+---------------------------+--------------------------------+
| _`arbeitsl_geld_2_params` | Basic social insurance         |
+---------------------------+--------------------------------+
| _`arbeitsl_geld_params`   | Unemployment benefits          |
+---------------------------+--------------------------------+
| _`unterhalt_params`       | Alimony payments               |
+---------------------------+--------------------------------+
| _`abgelt_st_params`       | Capital income tax             |
+---------------------------+--------------------------------+
| _`wohngeld_params`        | Housing benefits               |
+---------------------------+--------------------------------+
| _`kinderzuschl_params`    | Child allowance                |
+---------------------------+--------------------------------+
| _`kindergeld_params`      | Child benefits                 |
+---------------------------+--------------------------------+
| _`elterngeld_params`      | Parental leave benefits        |
+---------------------------+--------------------------------+
| _`ges_rentenv_params`     | Pensions                       |
+---------------------------+--------------------------------+
