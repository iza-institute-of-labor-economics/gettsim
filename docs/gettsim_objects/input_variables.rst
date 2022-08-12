.. _input_variables:

Basic input variables
=====================

The table below gives an overview of all variables needed to run GETTSIM completely.
Note that the variables with _hh at the end, have to be constant over the whole
household.

+-------------------------+---------------------------------------------+--------------+
| Variable name           | Description                                 | Type         |
+=========================+=============================================+==============+
| _`hh_id`                | Household identifier                        | int          |
+-------------------------+---------------------------------------------+--------------+
| _`tu_id`                | Tax Unit identifier (married couples + kids)| int          |
+-------------------------+---------------------------------------------+--------------+
| _`kind`                 | Dummy: Dependent child living with parents  | bool         |
+-------------------------+---------------------------------------------+--------------+
| _`bruttolohn_m`         | Monthly wage                                | float        |
+-------------------------+---------------------------------------------+--------------+
| _`alter`                | Age of Individual                           | int          |
+-------------------------+---------------------------------------------+--------------+
| _`rentner`              | Dummy: Pensioner employment status          | bool         |
+-------------------------+---------------------------------------------+--------------+
| _`alleinerz`            | Dummy: Single parent                        | bool         |
+-------------------------+---------------------------------------------+--------------+
| _`wohnort_ost`          | Dummy: Living in former East Germany        | bool         |
+-------------------------+---------------------------------------------+--------------+
| _`in_priv_krankenv`     | Dummy: In private health insurance          | bool         |
+-------------------------+---------------------------------------------+--------------+
| _`priv_rentenv_beitr_m` | Monthly private pension contribution        | float        |
+-------------------------+---------------------------------------------+--------------+
| _`in_ausbildung`        | Dummy: Employment status “in education”     | bool         |
+-------------------------+---------------------------------------------+--------------+
| _`selbstständig`        | Dummy: Individual is self-employed          | bool         |
+-------------------------+---------------------------------------------+--------------+
| _`hat_kinder`           | Dummy: Individual has kids (incl. not in hh)| bool         |
+-------------------------+---------------------------------------------+--------------+
| _`betreuungskost_m`     | Monthly childcare expenses                  | float        |
+-------------------------+---------------------------------------------+--------------+
| _`sonstig_eink_m`       | Additional income                           | float        |
+-------------------------+---------------------------------------------+--------------+
| _`eink_selbst_m`        | Monthly income from self-employment         | float        |
+-------------------------+---------------------------------------------+--------------+
| _`eink_vermietung_m`    | Monthly rental income                       | float        |
+-------------------------+---------------------------------------------+--------------+
| _`kapitaleink_brutto_m` | Monthly capital income                      | float        |
+-------------------------+---------------------------------------------+--------------+
| _`bruttokaltmiete_m_hh` | Monthly rent expenses for household         | float        |
+-------------------------+---------------------------------------------+--------------+
| _`heizkosten_m_hh`      | Monthly heating expenses for household      | float        |
+-------------------------+---------------------------------------------+--------------+
| _`wohnfläche_hh`        | Size of household dwelling in square meters | int          |
+-------------------------+---------------------------------------------+--------------+
| _`bewohnt_eigentum_hh`  | Dummy: Owner-occupied housing               | bool         |
+-------------------------+---------------------------------------------+--------------+
| _`arbeitsl_monate_lfdj` | Months in unemployment, current year        | int          |
+-------------------------+---------------------------------------------+--------------+
| _`arbeitsl_monate_vorj` | Months in unemployment, previous year       | int          |
+-------------------------+---------------------------------------------+--------------+
| _`arbeitsl_monate_v2j`  | Months in unemployment, two years before    | int          |
+-------------------------+---------------------------------------------+--------------+
| _`arbeitsstunden_w`     | Weekly working hours of individual          | int          |
+-------------------------+---------------------------------------------+--------------+
| _`bruttolohn_vorj_m`    | Monthly wage, previous year                 | float        |
+-------------------------+---------------------------------------------+--------------+
| _`geburtstag`           | Day of birth                                | int          |
+-------------------------+---------------------------------------------+--------------+
| _`geburtsmonat`         | Month of birth                              | int          |
+-------------------------+---------------------------------------------+--------------+
| _`geburtsjahr`          | Year of birth                               | int          |
+-------------------------+---------------------------------------------+--------------+
| _`jahr_renteneintr`     | Year of retirement                          | int          |
+-------------------------+---------------------------------------------+--------------+
| _`m_elterngeld`         | Number of months hh received elterngeld     | int          |
+-------------------------+---------------------------------------------+--------------+
| _`m_elterngeld_vat_hh`  | Number of months father received elterngeld | int          |
+-------------------------+---------------------------------------------+--------------+
| _`m_elterngeld_mut_hh`  | Number of months mother received elterngeld | int          |
+-------------------------+---------------------------------------------+--------------+
| _`behinderungsgrad`     | Handicap degree (between 0 and 100)         | int          |
+-------------------------+---------------------------------------------+--------------+
| _`schwerbeh_g`          | Severerly handicapped, with flag "G"        | bool         |
+-------------------------+---------------------------------------------+--------------+
| _`mietstufe`            | Level of rents in city (1: low, 3: average) | int          |
+-------------------------+---------------------------------------------+--------------+
| _`immobilie_baujahr_hh` | Construction year of dwelling               | int          |
+-------------------------+---------------------------------------------+--------------+
| _`vermögen_hh`          | Wealth of household                         | float        |
+-------------------------+---------------------------------------------+--------------+
| _`entgeltp`             | Earnings points for pension claim           | float        |
+-------------------------+---------------------------------------------+--------------+
|| _`grundr_zeiten`       || Number of months determining Grundrente    || int         |
||                        || eligibility                                ||             |
+-------------------------+---------------------------------------------+--------------+
|| _`grundr_bew_zeiten`   || Number of months determining Grundrente    || int         |
||                        || payments                                   ||             |
+-------------------------+---------------------------------------------+--------------+
|| _`grundr_entgeltp`     || Average `entgeltp` during                  || float       |
||                        || `grundr_bew_zeiten`                        ||             |
+-------------------------+---------------------------------------------+--------------+
| _`priv_rente_m`         | Amount of monthly private pension           | float        |
+-------------------------+---------------------------------------------+--------------+
| _`weiblich`             | True if female                              | bool         |
+-------------------------+---------------------------------------------+--------------+
| _`pflichtbeitragszeit`  | Months of mandatory contributions           | float        |
+-------------------------+---------------------------------------------+--------------+
| _`freiw_beitragszeit`   | Months of voluntary contributions           | float        |
+-------------------------+---------------------------------------------+--------------+
| _`zeit_mutterschutz`    | Months of maternal protections              | float        |
+-------------------------+---------------------------------------------+--------------+
||_`zeit_au_reha_teilh`   || Months of sickness, rehabilitation,        || float       |
||                        || measures for worklife participation        ||             |
+-------------------------+---------------------------------------------+--------------+
| _`zeit_krank_17_25`     | Months of sickness between age 16 and 24    | float        |
+-------------------------+---------------------------------------------+--------------+
| _`zeit_arbeitslos`      | Months of unemployment (registered)         | float        |
+-------------------------+---------------------------------------------+--------------+
| _`zeit_ausbild_suche`   | Months of apprenticeship search             | float        |
+-------------------------+---------------------------------------------+--------------+
||_`zeit_schul_ausbild`   || Months of schooling (incl college, uni     || float       |
||                        || from age 17, max. 8 years)                 ||             |
+-------------------------+---------------------------------------------+--------------+
|| _`zeit_rente_erwmind`  || Months of retirement benefits if included  || float       |
||                        || in Zurechnungszeiten (insurance retirement)||             |
+-------------------------+---------------------------------------------+--------------+
|| _`zeit_alg1_übergang`  || Months of unemployment (only time          || float       |
||                        || of Entgeltersatzleistungen, not ALGII),    ||             |
||                        || i.e. Arbeitslosengeld, Unterhaltsgeld,     ||             |
||                        || Übergangsgeld                              ||             |
+-------------------------+---------------------------------------------+--------------+
|| _`zeit_marg_employment`|| Month of marginal employment (w/o          || float       |
||                        || mandatory contributions) (computed after   ||             |
||                        || § 244a SGB VI - earningspoints/0,0313)     ||             |
+-------------------------+---------------------------------------------+--------------+
|| _`ersatzzeit`          || Months during military, persecution/escape,|| float       |
||                        || internment and consecutive sickness        ||             |
+-------------------------+---------------------------------------------+--------------+
| _`kinder_berücks_zeit`  | Months of childcare till age 10             | float        |
+-------------------------+---------------------------------------------+--------------+
| _`pfl9295_berücks_zeit` | Months of home care (01.01.1992-31.03.1995)| float        |
+-------------------------+---------------------------------------------+--------------+
| _`jahre_beitr_nach40`   | Years of mandat. contributions after age 40 | float        |
+-------------------------+---------------------------------------------+--------------+
