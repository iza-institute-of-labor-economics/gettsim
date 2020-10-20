Basic input variables
=====================

+-------------------------+---------------------------------------------------------+-------------+
| Variable name           | Description                                             | Type        |
+=========================+=========================================================+=============+
| _`hh_id`                | Household identifier                                    | IntSeries   |
+-------------------------+---------------------------------------------------------+-------------+
| _`tu_id`                | Tax Unit identifier                                     | IntSeries   |
+-------------------------+---------------------------------------------------------+-------------+
| _`kind`                 | Dummy: Either below 18yrs, or below 25 and in education | BoolSeries  |
+-------------------------+---------------------------------------------------------+-------------+
| _`anz_minderj_hh`       | Number of children between 0 and 18 in household        | IntSeries   |
+-------------------------+---------------------------------------------------------+-------------+
| _`bruttolohn_m`         | Monthly wage of each individual                         | FloatSeries |
+-------------------------+---------------------------------------------------------+-------------+
| _`alter`                | Age of Individual                                       | IntSeries   |
+-------------------------+---------------------------------------------------------+-------------+
| _`rentner`              | Dummy: Pensioner employment status                      | BoolSeries  |
+-------------------------+---------------------------------------------------------+-------------+
| _`alleinerziehend`      | Dummy: Single parent                                    | BoolSeries  |
+-------------------------+---------------------------------------------------------+-------------+
| _`wohnort_ost`          | Dummy: Living in former East Germany                    | BoolSeries  |
+-------------------------+---------------------------------------------------------+-------------+
| _`prv_krankenv`         | Dummy: Private health insured                           | BoolSeries  |
+-------------------------+---------------------------------------------------------+-------------+
| _`prv_rente_beitr_m`    | Monthly contributions to private pension insurance      | FloatSeries |
+-------------------------+---------------------------------------------------------+-------------+
| _`in_ausbildung`        | Dummy: Employment status “in education”                 | BoolSeries  |
+-------------------------+---------------------------------------------------------+-------------+
| _`selbstständig`        | Whether individual is self-employed                     | BoolSeries  |
+-------------------------+---------------------------------------------------------+-------------+
| _`hat_kinder`           | Whether individual has kids                             | BoolSeries  |
+-------------------------+---------------------------------------------------------+-------------+
| _`betreuungskost_m`     | Monthly childcare expenses                              | FloatSeries |
+-------------------------+---------------------------------------------------------+-------------+
| _`sonstig_eink_m`       | Sum of monthly public/private transfers not simulated.  | FloatSeries |
+-------------------------+---------------------------------------------------------+-------------+
| _`eink_selbst_m`        | Monthly wage of selfemployment of each individual       | FloatSeries |
+-------------------------+---------------------------------------------------------+-------------+
| _`vermiet_eink_m`       | Monthly rental income                                   | FloatSeries |
+-------------------------+---------------------------------------------------------+-------------+
| _`kapital_eink_m`       | Monthly capital income                                  | FloatSeries |
+-------------------------+---------------------------------------------------------+-------------+
| _`ges_rente_m`          | Monthly pension payments of each individual             | FloatSeries |
+-------------------------+---------------------------------------------------------+-------------+
| _`kaltmiete_m_hh`       | Monthly rent expenses for household (without heating)   | FloatSeries |
+-------------------------+---------------------------------------------------------+-------------+
| _`heizkosten_m_hh`      | Monthly heating expenses for houesehold                 | FloatSeries |
+-------------------------+---------------------------------------------------------+-------------+
| _`wohnfläche_hh`        | Size of household dwelling in square meters             | IntSeries   |
+-------------------------+---------------------------------------------------------+-------------+
| _`bewohnt_eigentum_hh`  | Dummy: Owner-occupied housing                           | BoolSeries  |
+-------------------------+---------------------------------------------------------+-------------+
| _`arbeitsl_lfdj_m`      | Months in unemployment, current year                    | IntSeries   |
+-------------------------+---------------------------------------------------------+-------------+
| _`arbeitsl_vorj_m`      | Months in unemployment, previous year                   | IntSeries   |
+-------------------------+---------------------------------------------------------+-------------+
| _`arbeitsl_vor2j_m`     | Months in unemployment, two years before                | IntSeries   |
+-------------------------+---------------------------------------------------------+-------------+
| _`arbeitsstunden_w`     | Weekly working hours of individual                      | IntSeries   |
+-------------------------+---------------------------------------------------------+-------------+
| _`bruttolohn_vorj_m`    | Weekly working hours of individual                      | FloatSeries |
+-------------------------+---------------------------------------------------------+-------------+
| _`geburtstag`           | Day of birth                                            | IntSeries   |
+-------------------------+---------------------------------------------------------+-------------+
| _`geburtsmonat`         | Month of birth                                          | IntSeries   |
+-------------------------+---------------------------------------------------------+-------------+
| _`geburtsjahr`          | Year of birth                                           | IntSeries   |
+-------------------------+---------------------------------------------------------+-------------+
| _`m_elterngeld`         | Number of months received elterngeld                    | IntSeries   |
+-------------------------+---------------------------------------------------------+-------------+
| _`m_elterngeld_vat`     | Number of months father received elterngeld             | IntSeries   |
+-------------------------+---------------------------------------------------------+-------------+
| _`m_elterngeld_mut`     | Number of months mother received elterngeld             | IntSeries   |
+-------------------------+---------------------------------------------------------+-------------+
| _`behinderungsgrad`     | Handicap degree (between 0 and 100)                     | IntSeries   |
+-------------------------+---------------------------------------------------------+-------------+
| _`mietstufe`            | Level of rents in city                                  | IntSeries   |
+-------------------------+---------------------------------------------------------+-------------+
| _`immobilie_baujahr_hh` | Construction year of dwelling                           | IntSeries   |
+-------------------------+---------------------------------------------------------+-------------+
| _`vermögen_hh`          | Wealth of household                                     | FloatSeries |
+-------------------------+---------------------------------------------------------+-------------+
| _`entgeltpunkte`        | Earning points for pension claim                        | FloatSeries |
+-------------------------+---------------------------------------------------------+-------------+
