Installation
============

The recommended way to install GETTSIM is via `conda <https://conda.io/>`_, the standard
package manager for scientific Python libraries. If conda is not installed on your
machine, please follow the `installation instructions
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
