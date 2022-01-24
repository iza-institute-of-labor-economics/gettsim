.. _input_variables:

Basic input variables
=====================

The table below gives an overview of all variables needed to run GETTSIM completely.
Note that the variables with _hh at the end, have to be constant over the whole
household.

+-------------------------+----------------------------------------------+-------------+
| Variable name           | Description                                  | Type        |
+=========================+==============================================+=============+
| _`hh_id`                | Household identifier                         | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`tu_id`                | Tax Unit identifier (married couples + kids) | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`kind`                 | Dummy: Dependent child living with parents   | BoolSeries  |
+-------------------------+----------------------------------------------+-------------+
| _`bruttolohn_m`         | Monthly wage                                 | FloatSeries |
+-------------------------+----------------------------------------------+-------------+
| _`alter`                | Age of Individual                            | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`rentner`              | Dummy: Pensioner employment status           | BoolSeries  |
+-------------------------+----------------------------------------------+-------------+
| _`alleinerziehend`      | Dummy: Single parent                         | BoolSeries  |
+-------------------------+----------------------------------------------+-------------+
| _`wohnort_ost`          | Dummy: Living in former East Germany         | BoolSeries  |
+-------------------------+----------------------------------------------+-------------+
| _`in_priv_krankenv`     | Dummy: In private health insurance           | BoolSeries  |
+-------------------------+----------------------------------------------+-------------+
| _`priv_rentenv_beitr_m` | Monthly private pension contribution         | FloatSeries |
+-------------------------+----------------------------------------------+-------------+
| _`in_ausbildung`        | Dummy: Employment status “in education”      | BoolSeries  |
+-------------------------+----------------------------------------------+-------------+
| _`selbstständig`        | Dummy: Individual is self-employed           | BoolSeries  |
+-------------------------+----------------------------------------------+-------------+
| _`hat_kinder`           | Dummy: Individual has kids (incl. not in hh) | BoolSeries  |
+-------------------------+----------------------------------------------+-------------+
| _`betreuungskost_m`     | Monthly childcare expenses                   | FloatSeries |
+-------------------------+----------------------------------------------+-------------+
| _`sonstig_eink_m`       | Additional income                            | FloatSeries |
+-------------------------+----------------------------------------------+-------------+
| _`eink_selbst_m`        | Monthly income from self-employment          | FloatSeries |
+-------------------------+----------------------------------------------+-------------+
| _`vermiet_eink_m`       | Monthly rental income                        | FloatSeries |
+-------------------------+----------------------------------------------+-------------+
| _`kapital_eink_m`       | Monthly capital income                       | FloatSeries |
+-------------------------+----------------------------------------------+-------------+
| _`bruttokaltmiete_m_hh` | Monthly rent expenses for household          | FloatSeries |
+-------------------------+----------------------------------------------+-------------+
| _`heizkosten_m_hh`      | Monthly heating expenses for household       | FloatSeries |
+-------------------------+----------------------------------------------+-------------+
| _`wohnfläche_hh`        | Size of household dwelling in square meters  | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`bewohnt_eigentum_hh`  | Dummy: Owner-occupied housing                | BoolSeries  |
+-------------------------+----------------------------------------------+-------------+
| _`arbeitsl_lfdj_m`      | Months in unemployment, current year         | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`arbeitsl_vorj_m`      | Months in unemployment, previous year        | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`arbeitsl_vor2j_m`     | Months in unemployment, two years before     | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`arbeitsstunden_w`     | Weekly working hours of individual           | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`bruttolohn_vorj_m`    | Monthly wage, previous year                  | FloatSeries |
+-------------------------+----------------------------------------------+-------------+
| _`geburtstag`           | Day of birth                                 | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`geburtsmonat`         | Month of birth                               | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`geburtsjahr`          | Year of birth                                | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`jahr_renteneintr`     | Year of retirement                           | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`m_elterngeld`         | Number of months hh received elterngeld      | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`m_elterngeld_vat`     | Number of months father received elterngeld  | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`m_elterngeld_mut`     | Number of months mother received elterngeld  | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`behinderungsgrad`     | Handicap degree (between 0 and 100)          | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`mietstufe`            | Level of rents in city (1: low, 3: average)  | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`immobilie_baujahr_hh` | Construction year of dwelling                | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`vermögen_hh`          | Wealth of household                          | FloatSeries |
+-------------------------+----------------------------------------------+-------------+
| _`entgeltpunkte`        | Earning points for pension claim             | FloatSeries |
+-------------------------+----------------------------------------------+-------------+
| _`gr_bewertungszeiten`  | Months with > 30% of average income          | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`entgeltp_grundr`      | Entgeltpunkte in Grundrentenbewertungszeiten | FloatSeries |
+-------------------------+----------------------------------------------+-------------+
| _`grundrentenzeiten`    | Number of months considered for Grundrente   | IntSeries   |
+-------------------------+----------------------------------------------+-------------+
| _`prv_rente_m`          | Amount of monthly private pension            | FloatSeries |
+-------------------------+----------------------------------------------+-------------+
| _`schwerbe_ausweis_g`   | Dummy: Schwerbehindertenausweis Merkzeichen G| BoolSeries  |
+-------------------------+----------------------------------------------+-------------+
