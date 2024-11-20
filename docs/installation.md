# Installation

You can install GETTSIM easily using [conda](https://conda.io/) or
[pixi](https://pixi.sh/latest/). If these are not installed on your machine, please
follow conda's
[installation instructions](https://docs.conda.io/projects/conda/en/latest/user-guide/install/)
or pixi's
[installation instructions](https://prefix.dev/docs/pixi/overview#installation).

With one of these available on your path, installing GETTSIM is as simple as typing

```shell-session
$ conda install -c conda-forge gettsim
```

or

```shell-session
$ pixi add gettsim
```

in a command shell.

To validate the installation, start the Python interpreter and type

```python
import gettsim

gettsim.test()
```
