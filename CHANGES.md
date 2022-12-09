# Changes

This is a record of all past `gettsim` releases and what went into them
in reverse chronological order. We follow [semantic
versioning](https://semver.org/) and all releases are available on
[Anaconda.org](https://anaconda.org/gettsim/gettsim).

## 0.5.2 —

-   ```{github} 323``` Health care contribution parameters are better aligned with
    law. Restructure calculation of ges\_krankenv, minor changes to
    ges\_pflegev. (`Eric-Sommer`, `ChristianZimpelmann`).

-   `392` Fix relative tolerance which was set too high for some tests.
    Rename <span class="title-ref">vorsorge</span> to <span
    class="title-ref">vorsorgeaufw</span> (`LauraGergeleit`,
    `ChristianZimpelmann`).

-   `385` Make altersentlastungsbetrag dependent on age not on current
    date (`m-pannier`, `lillyfischer`).

-   `393` normal retirement age adjustment aligned with the rules.
    (`TeBackh`).

-   `396` Implement pension for (very) long term insured, including eligibility criteria,
    i.e. "Wartezeiten". Implement pension for women (`TeBackh`).

-   `403` Replace <span class="title-ref">Bokeh</span> with <span
    class="title-ref">plotly</span> for visualization.
    (`effieHAN`,`sofyaakimova`).

-   `380` Implement an automatic type conversion of imported variables.
    Adding test cases in <span
    class="title-ref">test\_interface.py</span>. (`LauraGergeleit`,
    `ChristianZimpelmann`)

-   `406` Changed variable name from <span
    class="title-ref">vermögen\_hh</span> to <span
    class="title-ref">vermögen\_bedürft\_hh</span>. Add test cases for
    several transfers (`LauraGergeleit`).

-   `415` Define supported groupings in <span
    class="title-ref">config.py</span>. (`LauraGergeleit`,
    `ChristianZimpelmann`)

-   `416` Added documentation page for Vermögensbegriff for transfers.
    (`LauraGergeleit`)

-   `423` Modeled marginal employment rules reform from 10/2022.
    (`Eric-Sommer`, `LauraGergeleit`)

-   `399` Use dags package to create the DAG. (`ChristianZimpelmann`)

-   `440` Implemented Bürgergeld, which reforms <span
    class="title-ref">arbeitsl_geld_2</span> from 01/01/2023.
    (`LauraGergeleit`)

## 0.5.1 — 2022-04-21

-   `377` Fix wrong parameter value for <span
    class="title-ref">ges\_pflegev</span> contribution
    (`JuergenWiemers`).
-   `383` Remove ä, ö, ü from file names (`ChristianZimpelmann`).

## 0.5.0 — 2022-04-01

-   `327` add behinderten\_pauschbetrag for 1975-1986 (`lillyfischer`).

-   `285` Set up bokeh dashboard to visualize tax-benefit parameters
    (`Si-Pf`, `Eric-Sommer`).

-   `306` Add the possibility to load the value of a parameter of the previous
    year when calling <span
    class="title-ref">set\_up\_policy\_environment</span>
    (`ChristianZimpelmann`).

-   `275` Implement Grundrente. Implement Grundsicherung im Alter. Remove
    <span class="title-ref">ges\_rente\_m</span> as input. Rename <span
    class="title-ref">gettsim.renten\_anspr</span> to <span
    class="title-ref">gettsim.transfers.rente</span>. Rename <span
    class="title-ref">gettsim.social\_insurance</span> to <span
    class="title-ref">gettsim.social\_insurance\_contributions</span>
    (`davpahl`, `ChristianZimpelmann`).

-   `307` Allow to specify order up to which ancestors and descendants are shown
    when plotting a dag (`ChristianZimpelmann`).

-   `310` Added Mehrbedarf G to Implementation of Grundsicherung im Alter
    (`paulinaschroeder`).

-   `311` Rename variable kaltmiete\_m\_hh to bruttokaltmiete\_m\_hh
    (`LauraGergeleit`).

-   `319``320` Implement changes for social assistance and social insurance
    becoming effective in 2022 (`Eric-Sommer`).

-   `322` Add updated wohngeld parameters for 2022 (`mjbloemer`,
    `lillyfischer`).

-   `312` Updated GEP-01 with effects on character limits, time and unit
    identifiers, adjustments for DAG backend (`hmgaudecker`).

-   `314` Enforced character limits from GEP-01 for all function names
    and input variables. Make variable names more precise (e.g., <span
    class="title-ref">ges\_</span> in front of all social insurance
    parameters that have private counterparts, <span
    class="title-ref">eink\_st</span> everywhere the income tax is
    meant). Make variables consistent (e.g. <span
    class="title-ref">kinderfreibetrag</span> had different
    abbreviations, now <span class="title-ref">kinderfreib</span>
    everywhere). (`hmgaudecker`, `ChristianZimpelmann`)

-   `343` New argument for \`compute\_taxes\_and\_transfers\`: <span
    class="title-ref">rounding</span>. If set to False, rounding of
    outputs is disabled. Add rounding for <span
    class="title-ref">eink\_st\_tu</span>. Rounding for other functions
    will be introduced in future PRs. (`ChristianZimpelmann`).

-   `349` Create parameters for several hard coded numbers in code.
    (`LauraGergeleit`).

-   `355` Major renaming based on GEP 01, e.g.: correct use of
    `_m`-suffix; `alleinerziehend` becomes `alleinerz`; rename <span
    class="title-ref">ges\_rentenv.yaml</span> to <span
    class="title-ref">ges\_rente.yaml</span> (`hmgaudecker`,
    `ChristianZimpelmann`)

-   `356` Define functions on scalars and have them vectorised.
    Implement aggregation functions on group levels. (`LauraGergeleit`,
    `ChristianZimpelmann`)

## 0.4.2 — 2022-01-25

-   Ensure GETTSIM works with Pandas 1.4 (`337`)

## 0.4.1 — 2021-04-11

-   `248` Implement 2021 increase in lump sum tax deductions for disabled.
    (`Eric-Sommer`).

-   `254` Implement 2021 increase in unemployment benefits
    (`Eric-Sommer`).

-   `253` Implement 2021 changes in health insurance contribution rates and
    other social insurance regulations (`Eric-Sommer`).

-   `266` Adjust visualization.py to link nodes of DAGs to documentation
    properly (`davpahl`, `ChristianZimpelmann`).

-   `267` Implement new calculation of Kinderzuschlag parameter
    (`Eric-Sommer`).

-   `252` implement 2021 reforms to income tax tariff and family tax deductions
    (`Eric-Sommer`).

-   `235` Module to create synthetic data
    (`Eric-Sommer`, `ChristianZimpelmann`).

-   `256` Implement 2021 housing benefit reform (`Eric-Sommer`).

-   `283` Implement Kinderbonus in 2020 and 2021
    (`ChristianZimpelmann`).

## 0.4.0 — 2020-11-11

-   `241` renaming of directories: <span class="title-ref">gettsim.benefits</span> to <span class="title-ref">gettsim.transfers</span>;
    <span class="title-ref">gettsim.soz\_vers</span> to <span
    class="title-ref">gettsim.social\_insurance</span>; <span
    class="title-ref">gettsim.data</span> to <span
    class="title-ref">gettsim.parameters</span> (`MaxBlesch`,
    `ChristianZimpelmann`).

-   `230` adds type hints and links all docstring variables to the documentation.
    Also all functions have a one liner docstring now (`MaxBlesch`,
    `FelixAhlbrecht`).

-   `232` introduces beginner tutorials on how to use GETTSIM (`amageh`,
    `davpahl`, `Trichter33`).

-   `185` adds the DAG code for renten\_anspr\_m (`MaxBlesch`). This is
    based on the pension simulation code by (`Eric-Sommer`).

-   `184` adds visualization of the tax and transfer system as an
    interactive bokeh plot and documentation improvements
    (`tobiasraabe`).

-   `198` enhances the loader of internal and user functions, adds a
    tutorial for how to pass functions to the interface and provides
    more tests (`tobiasraabe`).

-   `213` changes `compute_taxes_and_transfers` such that it always
    returns a pandas DataFrame and removes the <span
    class="title-ref">return\_dag</span> option (`tobiasraabe`).

-   `219` refactors the DAG and makes it independent from the main
    interface (`tobiasraabe`). The PR also changes the names of
    interface arguments: `functions` instead of `user_functions`,
    `set_up_policy_environment` instead of `get_policy_for_date`,
    `columns_overriding_functions` instead of `user_columns` and some
    more changes.

-   `225` makes gettsim ready for Python 3.8 (`tobiasraabe`).

## 0.3.4 — 2020-07-30

-   `222` Fix wohngeld coefficent. Add test for increasing wohngeld.
    (`hmgaudecker`, `MaxBlesch`)

## 0.3.3 — 2020-06-27

-   `212` improves the error message when reduced series could not be
    expanded with an id variable and fixes a related error in the
    internal functions (`hmgaudecker`, `tobiasraabe`).
-   `214` adds a check for missing root nodes (`tobiasraabe`).
-   `215` adds a check for duplicate `targets` (`tobiasraabe`).
-   `216` fixed calculation of kindergeldzuschlag and wohngeld. Changed
    check against arbeitsl\_geld\_2 (`tobiasraabe`).

## 0.3.2 — 2020-06-19

-   `196` adds docstring to <span
    class="title-ref">policy\_for\_date.py</span> and improves its
    interface (`MaxBlesch`).
-   `197` adds all functions which build the tax and transfer system to
    the documentation (`tobiasraabe`).
-   `198` enhances the loader of internal and user functions, adds a
    tutorial for how to pass functions to the interface and provides
    more tests (`tobiasraabe`).
-   `200` adds a debug mode to gettsim and documents the feature
    (`tobiasraabe`).
-   `201` improves the calculation of `hh_freib` and renames it to
    `alleinerziehend_freib` (`MaxBlesch`, `tobiasraabe`).
-   `202` fixes bugs that surfaced for negative incomes (`MaxBlesch`).
-   `206` fixes several bugs in <span
    class="title-ref">arbeitsl\_geld\_2</span> and related transfers,
    calculating them at the appropriate (household) level (`MaxBlesch`).

## 0.3.1 — 2020-06-05

-   `188` removes misleading code bits from the documentation and adds a
    copy-button (`tobiasraabe`).
-   `191` adds a skip and a warning if <span
    class="title-ref">gettsim.test()</span> is repeatedly called
    (`tobiasraabe`).

## 0.3.0 — 2020-06-04

-   Cleanup of ALG II parameters and documentation (`mjbloemer`)
-   Break up params.yaml into group-level files (`MaxBlesch`)
-   Corrected income deductions for additional child benefit
    (`Eric-Sommer`)
-   Implemented "Starke-Familien-Gesetz" from July 2019 on child
    benefits (`Eric-Sommer`)
-   Remove child specific ALG II withdrawal and refactoring of ALG II
    (`MaxBlesch`, `mjbloemer`)
-   Add ALG II transfer withdrawal 2005-01-01 to 2005-09-30
    (`mjbloemer`, `MaxBlesch`)
-   Child tax allowance modelled as two separate items. (`Eric-Sommer`)
-   Alimony advance payment (*Unterhaltsvorschuss*) now modelled more in
    line with the law (`Eric-Sommer`)
-   Implement Art. 3 of *Familienentlastungsgesetz* on income tax tariff
    and child tax allowance becoming effective in 2020 (`Eric-Sommer`)
-   Implement parity in health care contributions since 2019 and 2020
    contribution rates (`Eric-Sommer`)
-   Add *Elterngeld* calculation (`MaxBlesch`, `boryana-ilieva`)
-   Fix Soli 1991 calculation, improve Soli 1995 calculation, add 2021
    Soli parameters and add Soli tests (`mjbloemer`, `MaxBlesch`)
-   Implement pre-2010 ruling on *Vorsorgeaufwendungen* (`Eric-Sommer`)
-   `gettsim` is released as a conda noarch package (`tobiasraabe`)
-   Implement 2020 reform increasing housing benefit
    (*Wohngeldstärkungsgesetz*) and complete parameters on past benefits
    (`Eric-Sommer`)
-   Regroup wohngeld parameters according to GEP-3 (`MaxBlesch`)
-   Renamed all data columns to German names (`amageh`, `MaxBlesch`)
-   Renamed and regrouped all param files (`Eric-Sommer`, `MaxBlesch`)
-   Added generic/piecewise functions (`johannesgoldbeck`,
    `ppoepperling`, `MaxBlesch`)
-   A series of pull requests established the new DAG-based backend and
    refactored the calculation of benefits, taxes, and social insurance
    (`MaxBlesch`, `tobiasraabe`)
-   Error messages for the new interface (`hmgaudecker`, `tobiasraabe`).

## 0.2.1 — 2019-11-20

-   Fix error with real SOEP data and "Wohngeld" for households with
    more than 12 household members (`Eric-Sommer`, `MaxBlesch`)
-   Better description of required input and output columns
    (`MaxBlesch`, `Eric-Sommer`)
-   Fix dependencies for conda package (`tobiasraabe`)
-   Fill changelog and include in docs (`tobiasraabe`, `hmgaudecker`)
-   Add maintenance section to website (`tobiasraabe`)

## 0.2.0 — 2019-11-06

Initial release of `gettsim`.

-   Set up as a conda-installable package (`tobiasraabe`)
-   Migration of the parameter database from xls to yaml (`mjbloemer`,
    `MaxBlesch`)
-   Migration of test parameters from xls to csv (`MaxBlesch`,
    `tobiasraabe`)
-   Get the main entry point to work, change interface (`MaxBlesch`,
    janosg, `Eric-Sommer`, `hmgaudecker`, `tobiasraabe`)
-   Tax and transfer module uses apply instead of loops (`MaxBlesch`,
    `hmgaudecker`)
-   Correct tax treatment of child care costs (`Eric-Sommer`)
-   Improve calculation of housing allowance (`Eric-Sommer`)

## 0.1 and prior work — 2019-09-30

Most code written by `Eric-Sommer` based on [IZAΨMOD](https://www.iza.org/publications/dp/8553/documentation-izapsmod-v30-the-iza-policy-simulation-model&gt),
a policy microsimulation model developed at [IZA](https://www.iza.org).
