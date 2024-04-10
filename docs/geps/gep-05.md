(gep-5)=

# GEP 5 — Optional Rounding of Variables

```{list-table}
- * Author
  * [Janos Gabler](https://github.com/janosg), [Christian Zimpelmann](https://github.com/ChristianZimpelmann)
- * Status
  * Provisional
- * Type
  * Standards Track
- * Created
  * 2022-02-02
- * Resolution
  * [Accepted](https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2005/near/270427530)
```

## Abstract

This GEP describes the implementation of optional rounding of variables in GETTSIM.

## Motivation and Scope

For several taxes and transfers, German law specifies that these be rounded in specific
ways. This leads to different use cases for GETTSIM.

1. Some applications require the exact, rounded, amount as specified in the law. This is
   also helpful for creating test cases.
1. Other applications benefit if functions are mostly smooth and the non-rounding error
   relative to the law does not matter much.

GETTSIM's default will be 1. This document describes how we support both use cases.

(gep-5-rounding-spec-yaml)=

## Implementation

GETTSIM allows for optional rounding of functions' results. Rounding parameters are
specified in the `.yaml`-files. The following goes through the details using an example
from the basic pension allowance (Grundrente).

The law on the public pension insurance specifies that the maximum possible
Grundrentenzuschlag `grundr_zuschlag_höchstwert_m` be rounded to the nearest fourth
decimal point (§76g SGB VI: Zuschlag an Entgeltpunkten für langjährige Versicherung).
The example below contains GETTSIM's encoding of this fact.

The snippet is taken from `ges_rente.yaml`, which contains the following code:

```yaml
rounding:
  grundr_zuschlag_höchstwert_m:
    2020-01-01:
      base: 0.0001
      direction: nearest
      reference: §76g SGB VI Abs. 4 Nr. 4
```

The specification of the rounding parameters starts with the key `rounding` at the
outermost level of indentation. The keys are names of functions.

At the next level, the `YYYY-MM-DD` key(s) indicate when rounding was introduced and/or
changed. This is done in in the same way as for other policy parameters, see
{ref}`gep-3`. Those `YYYY-MM-DD` key(s) are associated with a dictionary containing the
following elements:

- The parameter `base` determines the base to which the variables is rounded. It has to
  be a floating point number.
- The parameter `direction` has to be one of `up`, `down`, or `nearest`.
- The `reference` must contain the reference to the law, which specifies the rounding.

In the same way as other policy parameters, the rounding parameters become part of the
dictionary `policy_params`.

A function to be rounded must be decorated with `policy_info`. Set the `rounding_key`
parameter to point to the key of the policy parameters dictionary containing the
rounding parameters relating to the function that is decorated. In the above example,
the rounding specification for `grundr_zuschlag_höchstwert_m` will be found in
`policy_params["ges_rente"]` after {func}`set_up_policy_environment()` has been called
(since it was specified in `ges_rente.yaml`). Hence, the `rounding_key` argument of
`policy_info` has to be `"ges_rente"`:

```python
@policy_info(rounding_key="ges_rente")
def grundr_zuschlag_höchstwert_m(grundr_zeiten: int) -> float:
    ...
    return out
```

The decorator adds the attribute `__rounding_params_key__` to the function. When calling
{func}`compute_taxes_and_transfers <_gettsim.interface.compute_taxes_and_transfers>`
with `rounding=True`, GETTSIM will look for a key `"rounding"` in
`policy_params["params_key"]` and within that, for another key containing the decorated
function's name (here: `"grundr_zuschlag_höchstwert_m"`). That is, by the machinery
outlined in {ref}`GEP 3 <gep-3>`, the following indexing of the `policy_params`
dictionary

```python
policy_params["ges_rente"]["rounding"]["grundr_zuschlag_höchstwert_m"]
```

needs to be possible and yield the `"base"` and `"direction"` keys as described above.

Note that GETTSIM only allows for optional rounding of functions' results. In case one
is tempted to write a function requiring an intermediate variable to be rounded, the
function should be split up so that another function returns the quantity to be rounded.

### Error handling

In case a function has a `__rounding_params_key__`, but the respective parameters are
missing in `policy_params`, an error is raised.

Note that if the results have to be rounded in some years, but not in others (e.g. after
a policy reform) the rounding parameters (both `"base"` and `"direction"`) must be set
to `None`. This allows that the rounding parameters are found and no error is raised,
but still no rounding is applied.

In case rounding parameters are specified and the function does not have a
`__rounding_params_key__` attribute, execution will not lead to an error. This will
never happen in the GETTSIM codebase, however, due to a suitable test.

### User-specified rounding

If a user wants to change rounding of a specified function, she will need to adjust the
rounding parameters in `policy_params`.

Suppose one would like to specify a reform in which `grundr_zuschlag_höchstwert_m` is
rounded to the next-lowest fourth decimal point instead of to the nearest. In that case,
the rounding parameters will need to be changed as follows

```python
policy_params["ges_rente"]["rounding"]["grundr_zuschlag_höchstwert_m"][
    "direction"
] = "down"
```

This will be done after the policy environment has been set up and it is exactly the
same as for other parameters of the taxes and transfers system, see {ref}`gep-3`.

If a user would like to add user-written functions which should be rounded, she will
need to decorate the respective functions with `policy_info` and adjust `policy_params`
accordingly.

## Advantages of this implementation

This implementation was chosen over alternatives (e.g., specifying the rounding
parameters in the `.py` files directly) for the following reason:

- How a variable is rounded is a feature of the taxes and transfers system. Hence, the
  best place to define it is alongside its other features.
- Rounding parameters might change over time. In this case, the rounding parameters for
  each period can be specified in the parameter file using a well-established machinery.
- Optional rounding can be easily specified for user-written functions.
- At the definition of a function, it is clearly visible whether it is optionally
  rounded and where the rounding parameters are found.

## Discussion

- Zulip: <https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs>
- PR: <https://github.com/iza-institute-of-labor-economics/gettsim/pull/324>
- PR Implementation:
  <https://github.com/iza-institute-of-labor-economics/gettsim/pull/316>

## Copyright

This document has been placed in the public domain.
