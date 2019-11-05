Installation
============

We distribute GETTSIM via the package manager `conda <https://conda.io/>`_. If it is not
installed on your machine, follow the `user guide
<https://docs.conda.io/projects/conda/en/latest/user-guide/index.html>`_ on the topics
installation and getting started.

Then, install GETTSIM with

.. code-block:: bash

    $ conda install -c gettsim gettsim


To validate the installation, start a Python shell or a Jupyter notebook and type

.. code-block:: python

    import gettsim

    gettsim.test()
