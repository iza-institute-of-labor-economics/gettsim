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

    import pandas as pd
    from gettsim.tax_transfer import tax_transfer
    from gettsim.policy_for_date import load_tax_data
    from gettsim.policy_for_date import get_policies_for_date

    raw_tax_data = load_tax_data("param.yaml")  # This is the standard tax data
    year_of_policy = 2015  # We cover 1985 to 2019
    tax_data = get_policies_for_date(tax_policy_data, year=year)
    tax_data_pensions = pd.read_excel(ROOT_DIR / "data" / "pensions.xlsx").set_index("var")
    tax_transfer(dataset, tax_policy, tax_policy_pensions)


Where dataset is some DataFrame containing the following variables for each observation:
