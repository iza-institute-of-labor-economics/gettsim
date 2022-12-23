# Installation

You can install GETTSIM easily using [conda](https://conda.io/), the standard package
manager for scientific Python libraries. If conda is not installed on your machine,
please follow conda's
[installation instructions](https://docs.conda.io/projects/conda/en/latest/user-guide/install/).

With conda available on your path, installing GETTSIM is as simple as typing

```bash
conda install -c gettsim -c conda-forge gettsim
```

in a command shell.

To validate the installation, start the conda Python interpreter and type

```python
import gettsim

gettsim.test()
```
