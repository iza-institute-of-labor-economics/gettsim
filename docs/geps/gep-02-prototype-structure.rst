

- Need to decide on backend only when graph is constructed

- Three backends:
  - numpy
  - jax


__init__.py:

try imports, store variable ``has_jax``

when graph is requested,

- fail if requested backend is not around

- import based on importlib.inspect from modules ``vectorize_jax``, ``vectorize_numpy``

  maybe can do with one module for numpy in case syntax is very similar

- These modules add decorators to all functions in the graph

- They will also include generic aggregation functions (including sorting and
  without)
