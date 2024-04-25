# Relevant concepts of units of individuals

This is a collection of which units of individuals are relevant in which context,
originally resulting from a call on 27 Jan 2023. This may become a GEP.

Also see
[discussion on Zulip](https://gettsim.zulipchat.com/#narrow/stream/224837-High-Level-Architecture/topic/Update.20Data.20Structures/near/322500145)

## Taxes

### Joint taxation

#### Description

- Must be married or in a civil union

#### Relevant aggregation unit

- `sn_id` (endogenous)

### Kinderfreibeträge

#### Description

- Parents (max 2) and their children
- Don't have to be part of the same household
- Possibly claim on more than one Freibetrag for one child due to
  - no child support payed by other parent
  - other parent now known
  - Needs to be specified by the user currently

#### Relevant aggregation unit

- `sn_id` (endogenous)

## Kindergeld

#### Description

- Only one parent receives child allowances (specified via `p_id_kindergeld_empf`)
- Relevant for Unterhaltzahlung of the other parent

#### Relevant aggregation unit

- `p_id` (exogenous)

## Kinderzuschlag

#### Description

- Payed out on Bedarfsgemeinschaft level
- Parents outside of Bedarfsgemeinschaft (e.g. not in the same household) are not
  considered (besides of Unterhalts(vorschuss)zahlungen)

#### Relevant aggregation unit

- `bg_id` (endogenous)

## Elterngeld

#### Description

- Parents and their children
- Sum of months (across parents) parents can claim Elterngeld is capped.

#### Relevant aggregation unit

- `p_id` (exogenous)

## Unterhalt / Unterhaltsvorschuss

#### Description

- Parents and their children
- Parents necessarily in different households

#### Relevant aggregation unit

- `p_id` (exogenous)

## Pflegeversicherung

#### Description

- Contribution depends on the number of children
- Parents and their children
  - Can be in different households
  - No reference to age categories of children

#### Relevant aggregation unit

- `p_id` (exogenous)

## Rente

### Grundrente

#### Description

- Couples that are married or in a civil union

#### Relevant aggregation unit

- `ehe_id` (endogenous)

### Verwitwetenrente

#### Description

- Couples that were married or in a civil union

#### Relevant aggregation unit

- `ehe_id` (endogenous)

## Bürgergeld und Sozialhilfe

### SGB II (Bürgergeld)

#### Description

- Bedarfsgemeinschaft (Familiengemeinschaft after taking out children with income above
  a threshold)
  - Einstandsgemeinschaft (max 2 adults, marriage-like relationships)
  - Children under 18/25
- Note: A household may exist of several Bedarfsgemeinschaften
  - e.g. parents and adult children aged above 18/25
  - Income/wealth of related members of the household may be considered
    (Einstandsvermutung)

#### Relevant aggregation unit

- `bg_id` (endogenous)

### SGB XII (Hilfe zum Lebensunterhalt)

#### Description

Government expenditures: 1.5 Mrd €

- Relevant are
  - vertical relationships (parents/children)
    - No reference to shared household
    - No reference to age categories
  - Haushaltsgemeinschaft
  - Not necessarily limited to relatives

Regarding the household definition:

> wenn Personen, die zusammen wohnen, auch gemeinsam wirtschaften. Der Begriff der
> Haushaltsgemeinschaft wird gegenüber der Wohngemeinschaft gerade dadurch
> gekennzeichnet, dass ihre Mitglieder nicht nur vorübergehend in einer Wohnung
> zusammenleben, sondern einen gemeinsamen Haushalt in der Weise führen, dass sie „aus
> einem Topf“ wirtschaften. Das gemeinsame Wirtschaften geht über die gemeinsame Nutzung
> von Bad, Küche und ggf. Gemeinschaftsräumen sowie über einen gemeinsam organisierten
> Einkauf über eine Gemeinschaftskasse, wie dies regelmäßig in Wohngemeinschaften
> organisiert ist, hinaus.
> https://www.berlin.de/sen/soziales/service/berliner-sozialrecht/kategorie/rundschreiben/2014_04-572017.php

#### Relevant aggregation unit

- `hh_id` (endogenous)

### SGB XII (Grundsicherung im Alter / bei Erwerbsminderung)

#### Description

Government expenditures: 7 Mrd €

Relevant are vertical relationships (parents/children) - No reference to shared
household - No reference to age categories

### SGB XII (Eingliederungshilfe für Menschen mit Behinderung)

#### Description

Government expenditures: 20 Mrd €

### SGB XII (Hilfe zur Pflege)

#### Description

Government expenditures: 4 Mrd €

### Interactions between SGB II / SGB XII

- Partnerships where one partner falls under SGB II and one under SGB XII -> Whole
  household falls under SGB II
- Bedarfsgemeinschaft with child under 25 falling under SGB II -> ?

## Wohngeld

#### Description

- Household
  - Applicant
  - Spouse / registered partner / life partner (as long as in same household)
  - Parents (incl. step-, foster- and in-laws) (as long as in same household)
  - Children (incl. step-, foster- and adopted children) (as long as in same household)
  - "Einstandspartner": non-relatives living in the same household and sharing
    responsibility for each other (e.g. couples that are not married or in a civil
    union) (as long as in same household)
    - A community of responsibility or joint liability is regulated in § 7 Abs. 3a SGB
      II according to which at least one of the following conditions must be met
      - if partners live together for longer than 1 year
      - if partners live together with a child
      - if children or relatives are cared for or looked after in the household (not
        only occasionally)
      - if partners are mutually authorized to dispose of income and assets
    - The prerequisite for all household members is that they live with the applicant
      live in a shared apartment or house and are also registered there.
  - Other relatives

### Kinderwohngeld

#### Description

- E.g. single parent with one child
- Child cannot cover own needs with Unterhaltsleistungen, Kindergeld, Kinderzuschlag,
  Wohngeld
- Child drops out of Bedarfsgemeinschaft

## Modelling groupings

### Complete data

- Parent-child relationships via `p_id_elternteil_1` and `p_id_elternteil_2`
- Household concept of Wohngeld determines `hh_id`
  - A student flatshare would have different values for `hh_id`
- Bedarfsgemeinschaft from:
  - Einstandspartner `p_id_einstandspartner`
  - Children under 17/24, unless resolved
    - via own income
    - Kinderwohngeld

#### Limitations

- Within a Wohngeldhaushalt, no distinction can be made between persons without
  Einstandsverpflichtung according to SGB II or SGB XII and those with
  Einstandsverpflichtung

- Can only show the two extreme cases

  1. all non-vertical or partner relationships not a candidate for Haushaltsgemeinschaft
     according to SGB II / SGB XII
  1. all non-vertical or partner relationships are candidates for Haushaltsgemeinschaft
     according to SGB II / SGB XII

  Typically, 1. will be the solution (hurdles for joint economic activity are high).

- An alternative would be another ID variable that specifies Haushaltsgemeinschaft
  according to SGB II and SGB XII.

### Parts of the data not available

- Adult children exist, but not in the dataset
- Spouse that should pay child support is not in the dataset
- ...

Solution:

Add support for missing IDs in the data. Missing IDs are represented by negative IDs
(exact value doesn't matter for now).
