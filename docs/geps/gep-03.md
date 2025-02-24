(gep-3)=

# GEP 3 — Parameters of the taxes and transfers system

```{list-table}
- * Author
  * [Hans-Martin von Gaudecker](https://github.com/hmgaudecker)
- * Status
  * Provisional
- * Type
  * Standards Track
- * Created
  * 2022-03-28
- * Resolution
  * [Accepted](https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2003)
```

## Abstract

This GEP describes the structure of the parameters of the taxes and transfers system.
This includes the format of the yaml files (initial input) and storage of the processed
parameters.

## Motivation and Scope

The parameters of the taxes and transfers system are among the core elements of GETTSIM.
Along with the functions operating on them and the input data, they determine all
quantities of interest. Sensibly structuring and cleanly documenting the meaning and
sources of these parameters requires particular care.

## Usage and Impact

GETTSIM developers should closely look at the Section {ref}`gep-3-structure-yaml-files`
before adding new parameters.

(gep-3-structure-yaml-files)=

## Structure of the YAML files

Each YAML file contains a number of parameters at the outermost level of indentation.
Each of these parameters in turn is a dictionary with at least three keys: `name`,
`description`, and the `YYYY-MM-DD`-formatted date on which it first took effect. Values
usually change over time; each time a value is changed, another `YYYY-MM-DD` entry is
added.

Some keys at the outermost level refer to functions of the taxes and transfers system.
These work differently and they are
{ref}`treated separately below <gep-3-keys-referring-to-functions>`.

1. The `name` key has two sub-keys `de` and `en`, which are

   - short names without re-stating the realm of the parameter (e.g. "Arbeitslosengeld
     II" or "Kinderzuschlag");
   - not sentences;
   - correctly capitalised.

   Example (from `arbeitsl_geld_2`):

   ```yaml
   eink_anr_frei:
     name:
       de: Anrechnungsfreies Einkommen
       en: Income shares not subject to transfer withdrawal
   ```

1. The `description` key has two sub-keys `de` and `en`, which

   - are exhaustive explanations of the parameter;

   - show the § and Gesetzbuch of that parameter (including its entire history if the
     location has changed);

   - mention bigger amendments / Neufassungen and be as helpful as possible to make
     sense of that parameter.

     Example:

     ```yaml
     eink_anr_frei:

       description:
         de: >-
           Einkommensanteile, die anrechnungsfrei bleiben. § 30 SGB II. Seit 01.10.2005 zudem
           definiert durch Freibetrag in § 11 SGB II, siehe auch § 67 SGB II. Seit 01.04.2011
           § 11b (2) SGB II (neugefasst durch B. v. 13.05.2011 BGBl. I S. 850. Artikel 2
           G. v. 24.03.2011 BGBl. I S. 453).
         en: >-
           Income shares which do not lead to tapering of benefits.
     ```

1. The `unit` key informs on the unit of the values (Euro or DM if monetary, share of
   some other value, ...).

   - In rare cases (e.g. child benefit age threshold), it might be omitted.
   - It should be capitalised.
   - Some values used at this point: `Euro`, `DM`, `Share`, `Percent`, `Factor`, `Year`,
     `Month`, `Hour`, `Square Meter`, `Euro / Square Meter`.
   - The `unit` key may be overridden at lower levels. For example, the unit will
     typically be `Euro` for monetary quantities. For the years prior to its
     introduction, it may be specified as `DM`.

   Example:

   ```yaml
   kindergeld:
     name:
       de: Kindergeld, Betrag je nach Reihenfolge der Kinder.
     unit: Euro
   ```

1. The (optional) `type` key may contain a reference to a particular function that is
   implemented. Examples are `piecewise_linear` or `piecewise_quadratic`

1. The (optional) `reference_period` key informs on the reference period of the values,
   if applicable

   Possible values: - `Year` - `Month` - `Week` - `Day`

   Example:

   ```yaml
   kindergeld_stundengrenze:
     name:
       de: Wochenstundengrenze für Kindergeldanspruch
       [...]
     reference_period: Week
   ```

(gep-3-access_prior_parameters)=

6. The (optional) `access_prior_parameters` can be used to make the parameter of a
   previous point in time (relative to the date specified in
   {func}`set_up_policy_environment <_gettsim.policy_environment.set_up_policy_environment>`)
   available within GETTSIM functions. It requires the `reference_period` (one of
   `Year`, `Month`, `Week`, `Day`) and the `number_of_lags`.

   Example:

   ```yaml
   rentenwert:
     name:
       de: Rentenwerte alte und neue Bundesländer.
         [...]
     access_prior_parameters:
       - reference_period: Year
       - number_of_lags: 1
   ```

1. The YYYY-MM-DD key(s)

   - hold all historical values for a specific parameter or set of parameters in the
     `value` subkey;
   - is present with `value: null` if a parameter ceases to exist starting on a
     particular date;
   - contain a precise reference to the law in the `reference` subkey;
   - may add additional descriptions in the `note` key;
   - may give hints towards the type of function they refer to via the `type` subkey;
   - may include formulas if the law does;
   - may reference other parameters as described below.
   - may contain a `unit` subkey, which overrides the `unit` key mentioned in 3. (mostly
     relevant for DM / Euro)

   The remainder of this section explains this element in much more detail.

### The `reference` key of \[YYYY-MM-DD\]

- cites the law (Gesetz "G. v."), decree (Verordnung "V. v.") or proclamation
  (Bekanntmachung "B. v.") that changes the law
- uses German language
- follows the style `Artikel [n] [G./V./B.] v. [DD.MM.YYYY] BGBl. I S. [SSSS].`
- does not add information "geändert durch" (it is always a change) or the date the law
  comes into force (this would just repeat the date key one level above)
- the page should be the first page of the law/decree/proclamation, not the exact page
  of the parameter

Example:

```yaml
eink_anr_frei:
  name:
    de: Anrechnungsfreie Einkommensanteile
  2005-01-01:
    reference: Artikel 1. G. v. 24.12.2003 BGBl. I S. 2954.
```

### The `note` key of \[YYYY-MM-DD\]

This optional key may contain a free-form note holding any information that may be
relevant for the interpretation of the parameter, the implementer, user, ...

(gep-3-deviation_from)=

### The `deviation_from` key of \[YYYY-MM-DD\]

Often laws change only part of a parameter. To avoid error-prone code duplication, we
allow for such cases via the `deviation_from` key. This is the reason why lists are to
be avoided in the value key (see the `piecewise_linear` function above).

The key could either reference another value explicitly:

```yaml
eink_anr_frei_kinder:
  name:
    de: Abweichende anrechnungsfreie Einkommensanteile falls Kinder im Haushalt
  2005-10-01:
    deviation_from: arbeitsl_geld_2.eink_anr_frei
    3:
      upper_threshold: 1500
```

A special keyword is `previous`, which just refers to the set of values in the previous
law change.

```yaml
eink_anr_frei:
  name:
    de: Anrechnungsfreie Einkommensanteile
  2011-04-01:
    deviation_from: previous
    2:
      upper_threshold: 1000
```

### The values of \[YYYY-MM-DD\]

The general idea is to make the replication of the laws very obvious. If the law
includes a table, we will have a dictionary with keys 0, 1, 2, .... If the law includes
a formula, the formula should be included and its parameters referenced. Etc..

The following walks through several cases.

- The simplest case is a single parameter, which should be specified as:

  ```yaml
  kindergeld_stundengrenze:
    name:
      de: Wochenstundengrenze für Kindergeldanspruch
    2012-01-01:
      scalar: 20
  ```

- There could be a dictionary, potentially nested:

  ```yaml
  exmin:
    name:
      de: Höhen des Existenzminimums, festgelegt im Existenzminimumsbericht der Bundesregierung.
    2005-01-01:
      regelsatz:
        single: 4164
        paare: 7488
        kinder: 2688
      kosten_der_unterkunft:
        single: 2592
        paare: 3984
        kinder: 804
      heizkosten:
        single: 600
        paare: 768
        kinder: 156
  ```

- In some cases, a dictionary with numbered keys makes sense. It is important to use
  these, not lists!

  ```yaml
  kindergeld:
    name:
      de: Kindergeld, Betrag je nach Reihenfolge der Kinder.
    1975-01-01:
      1: 26
      2: 36
      3: 61
      4: 61
  ```

- Another example would be referring to the parameters of a piecewise linear function:

  > ```yaml
  > eink_anr_frei:
  >   name:
  >     de: Anrechnungsfreie Einkommensanteile
  >     en: Income shares not subject to transfer withdrawal
  >   type: piecewise_linear
  >   2005-01-01:
  >     0:
  >       lower_threshold: -inf
  >       upper_threshold: 0
  >       rate: 0
  >       intercept_at_lower_threshold: 0
  > ```

- In general, a parameter should appear for the first time that it is mentioned in a
  law, becomes relevant, etc..

  Only in exceptional cases it might be useful to set a parameter to some value
  (typically zero) even if it does not exist yet.

- If a parameter ceases to be relevant, is superseded by something else, etc., there
  must be a `YYYY-MM-DD` key with a note on this.

  Generally, this `YYYY-MM-DD` key will have an entry `scalar: null` regardless of the
  previous structure. Ideally, there would be a `reference` and potentially a `note`
  key. Example:

  ```yaml
  value: null
  note: arbeitsl_hilfe is superseded by arbeitsl_geld_2
  ```

  Only in exceptional cases it might be useful to set a parameter to some value
  (typically zero) even if it is not relevant any more.

  In any case, it **must** be the case that it is obvious from the `YYYY-MM-DD` entry
  that the (set of) parameter(s) is not relevant any more, else the previous ones will
  linger on.

(gep-3-keys-referring-to-functions)=

## Keys referring to functions

### The `rounding` key

See {ref}`GEP-5 <gep-5>` for the entire scope of rounding, here we reproduce the
{ref}`relevant section referring to YAML-files <gep-5-rounding-spec-yaml>`,

The following goes through the details using an example from the basic pension allowance
(Grundrente).

The law on the public pension insurance specifies that the maximum possible
Grundrentenzuschlag `rente__grundrente__höchstbetrag_m` be rounded to the nearest fourth
decimal point (§76g SGB VI: Zuschlag an Entgeltpunkten für langjährige Versicherung).
The example below contains GETTSIM's encoding of this fact.

The snippet is taken from `ges_rente.yaml`, which contains the following code:

```yaml
rounding:
  rente__grundrente__höchstbetrag_m:
    2020-01-01:
      base: 0.0001
      direction: nearest
      reference: §76g SGB VI Abs. 4 Nr. 4
```

The specification of the rounding parameters starts with the key `rounding` at the
outermost level of indentation. The keys are names of functions.

At the next level, the `YYYY-MM-DD` key(s) indicate when rounding was introduced and/or
changed. This is done in in the same way as for other policy parameters. Those
`YYYY-MM-DD` key(s) are associated with a dictionary containing the following elements:

- The parameter `base` determines the base to which the variables is rounded. It has to
  be a floating point number.
- The parameter `direction` has to be one of `up`, `down`, or `nearest`.
- The `reference` must contain the reference to the law, which specifies the rounding.

### The `dates_active` key

Some functions should not be present at certain times. For example, `arbeitsl_geld_2`
and all its ancestors should not appear in DAGs referring to years prior to 2005.

Other functions have different interfaces in different years or undergo very large
changes in their body.

The `dates_active` key can be used to include certain functions only in certain years
and to switch between different implementations of other functions.

(gep-3-storage-of-parameters)=

## Storage of parameters

The contents of the YAML files become part of the `policy_params` dictionary. Its keys
correspond to the names of the YAML files. Each value will be a dictionary that follows
the structure of the YAML file. These values can be used in policy functions as
`[key]_params`.

The contents mostly follow the content of the YAML files. The main difference is that
all parameters are present in their required format; no further parsing shall be
necessary inside the functions. The important changes include:

- In the YAML files, parameters may be specified as deviations from other values,
  {ref}`see above <gep-3-deviation_from>`. All these are converted so that the relevant
  values are part of the dictionary.
- Similarly, values from other points in time (via `access_prior_parameters`,
  {ref}`see above <gep-3-access_prior_parameters>`) of `[param]` will be available as:
  `[param]_t_minus_[number_of_lags]_[reference_period[0].lower()]`.
- Parameters for piecewise polynomials are parsed.
- Parameters that are derived from other parameters are calculated (examples include
  `kinderzuschlag_max` starting in 2021 or calculating the phasing in of
  `vorsorgeaufwand_alter` over the 2005-2025 period).

These functions will be avaiable to users en bloque or one-by-one so they can specify
parameters as in the YAML file for their own policy parameters.

## Discussion

- <https://github.com/iza-institute-of-labor-economics/gettsim/pull/148>
- <https://gettsim.zulipchat.com/#narrow/stream/309998-GEPs/topic/GEP.2003>

## Copyright

This document has been placed in the public domain.
