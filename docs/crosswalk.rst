Crosswalk of data column names v0.2 ↔ v0.3
==========================================

The 0.2 versions still had column names for the user-provided data that were very
close to IZAΨMOD. Almost all of them were renamed in v0.3. This page provides a
crosswalk for users / developers who are familiar with the IZAΨMOD codebase.


Required input columns
----------------------

+-----------------+-------------------+------------------------------------------------+
| v0.2            | v0.3              | Explanation                                    |
| (≈IZAΨMOD)      |                   |                                                |
+=================+===================+================================================+
| hid             | hh_id             | Household identifier                           |
+-----------------+-------------------+------------------------------------------------+
| tu_id           | tu_id             | Tax Unit identifier                            |
+-----------------+-------------------+------------------------------------------------+
| pid             | p_id              | Personal identifier                            |
+-----------------+-------------------+------------------------------------------------+
| head_tu         | tu_vorstand       | Whether individual is head of tax unit         |
+-----------------+-------------------+------------------------------------------------+
| adult_num       | anz_erwachsene_hh | Number of adults in household                  |
+-----------------+-------------------+------------------------------------------------+
| child0_18_num   | anz_minderj_hh    | Number of children between 0 and 18 in         |
|                 |                   | household                                      |
+-----------------+-------------------+------------------------------------------------+
| hh_wealth       | vermögen_hh       | Wealth of household                            |
+-----------------+-------------------+------------------------------------------------+
| m_wage          | bruttolohn_m      | Monthly wage of each individual                |
+-----------------+-------------------+------------------------------------------------+
| age             | alter             | Age of Individual                              |
+-----------------+-------------------+------------------------------------------------+
| selfemployed    | selbstständig     | Whether individual is self-employed            |
+-----------------+-------------------+------------------------------------------------+
| east            | wohnort_ost       | Whether location in former East or West        |
|                 |                   | Germany                                        |
+-----------------+-------------------+------------------------------------------------+
| haskids         | hat_kinder        | Whether individual has kids                    |
+-----------------+-------------------+------------------------------------------------+
| m_self          | eink_selbstst_m   | Monthly wage of selfemployment of each         |
|                 |                   | individual                                     |
+-----------------+-------------------+------------------------------------------------+
| m_pensions      | ges_rente_m       | Monthly pension payments of each individual    |
+-----------------+-------------------+------------------------------------------------+
| pkv             | prv_krankv_beit_m | Whether individual is (only) privately health  |
|                 |                   | insured                                        |
+-----------------+-------------------+------------------------------------------------+
| priv_pens_contr | prv_rente_beit_m  | Monthly contributions to private pension       |
|                 |                   | insurance                                      |
+-----------------+-------------------+------------------------------------------------+
| m_wage_l1       | bruttolohn_vorj_m | Average monthly earnings, previous year        |
+-----------------+-------------------+------------------------------------------------+
| months_ue       | arbeitsl_lfdj_m   | Months in unemployment, current year           |
+-----------------+-------------------+------------------------------------------------+
| months_ue_l1    | arbeitsl_vorj_m   | Months in unemployment, previous year          |
+-----------------+-------------------+------------------------------------------------+
| months_ue_l2    | arbeitsl_vor2j_m  | Months in unemployment, two years before       |
+-----------------+-------------------+------------------------------------------------+
| w_hours         | arbeitsstunden_w  | Weekly working hours of individual             |
+-----------------+-------------------+------------------------------------------------+
| child_num_tu    | anz_kinder_tu     | Number of children in tax unit                 |
+-----------------+-------------------+------------------------------------------------+
| adult_num_tu    | anz_erw_tu        | Number of adults in tax unit                   |
+-----------------+-------------------+------------------------------------------------+
| byear           | geburtsjahr       | Year of birth                                  |
+-----------------+-------------------+------------------------------------------------+
| EP              | entgeltpunkte     | Earning points for pension claim               |
+-----------------+-------------------+------------------------------------------------+
| child           | kind              | Dummy: Either below 18yrs, or below 25 and in  |
|                 |                   | education                                      |
+-----------------+-------------------+------------------------------------------------+
| pensioner       | rentner           | Dummy: Pensioner employment status             |
+-----------------+-------------------+------------------------------------------------+
| m_childcare     | betreuungskost_m  | Monthly childcare expenses                     |
+-----------------+-------------------+------------------------------------------------+
| m_imputedrent   | miete_unterstellt | Monthly value of owner-occupied housing        |
+-----------------+-------------------+------------------------------------------------+
| m_kapinc        | kapital_eink_m    | Monthly capital income                         |
+-----------------+-------------------+------------------------------------------------+
| m_vermiet       | vermiet_eink_m    | Monthly rental income                          |
+-----------------+-------------------+------------------------------------------------+
| miete           | kaltmiete_m       | Monthly rent expenses (without heating)        |
+-----------------+-------------------+------------------------------------------------+
| heizkost        | heizkost_m        | Monthly heating expenses                       |
+-----------------+-------------------+------------------------------------------------+
| renteneintritt  | jahr_renteneintr  | Statutory retirement age (might be dropped in  |
|                 |                   | the future)                                    |
+-----------------+-------------------+------------------------------------------------+
| handcap_degree  | behinderungsgrad  | Handicap degree (between 0 and 100)            |
+-----------------+-------------------+------------------------------------------------+
| wohnfl          | wohnfläche        | Size of dwelling in square meters              |
+-----------------+-------------------+------------------------------------------------+
| zveranl         | gem_veranlagt     | Dummy: Married couple filing jointly for       |
|                 |                   | income tax                                     |
+-----------------+-------------------+------------------------------------------------+
| ineducation     | in_ausbildung     | Dummy: Employment status "in education"        |
+-----------------+-------------------+------------------------------------------------+
| alleinerz       | alleinerziehend   | Dummy: Single parent                           |
+-----------------+-------------------+------------------------------------------------+
| eigentum        | bewohnt_eigentum  | Dummy: owner-occupied housing                  |
+-----------------+-------------------+------------------------------------------------+
| cnstyr          | immobilie_baujahr | Construction year of dwelling                  |
|                 |                   | (1: <1965,2:1966-2000,3:>2000)                 |
+-----------------+-------------------+------------------------------------------------+
| m_transfers     | sonstig_eink_m    | Sum of monthly public/private transfers not    |
|                 |                   | simulated. E.g. transfers from parents,        |
|                 |                   | alimonies, maternity leave payments. Will be   |
|                 |                   | split up in future releases.                   |
+-----------------+-------------------+------------------------------------------------+



Columns returned by the simulator
---------------------------------

+-----------------+-------------------+------------------------------------------------+
| v0.2            | v0.3              | Explanation                                    |
| (≈IZAΨMOD)      |                   |                                                |
+=================+===================+================================================+
| svbeit          | —                 |                                                |
+-----------------+-------------------+------------------------------------------------+
| rvbeit          | rentenv_beit_m    | Monthly amount employee old-age pensions       |
|                 |                   | contributions                                  |
+-----------------+-------------------+------------------------------------------------+
| avbeit          | arbeitsl_v_beit_m | Monthly amount employee unempl. insurance      |
|                 |                   | contributions                                  |
+-----------------+-------------------+------------------------------------------------+
| gkvbeit         | ges_krankv_beit_m | Monthly amount employee health insurance       |
|                 |                   | contributions                                  |
+-----------------+-------------------+------------------------------------------------+
| pvbeit          | pflegev_beit_m    | Monthly amount of long term care insurance     |
+-----------------+-------------------+------------------------------------------------+
| m_alg1          | arbeitsl_geld_m   | Monthly amount of unemployment assistance      |
+-----------------+-------------------+------------------------------------------------+
| pensions_sim    | rente_anspr_m     | Monthly amount of old-age pensions             |
+-----------------+-------------------+------------------------------------------------+
| EP              | entgeltpunkte     | Updated earning points for pension claim       |
+-----------------+-------------------+------------------------------------------------+
| gross_e1        | —                 |                                                |
+-----------------+-------------------+------------------------------------------------+
| gross_e5        | —                 |                                                |
+-----------------+-------------------+------------------------------------------------+
| gross_e6        | —                 |                                                |
+-----------------+-------------------+------------------------------------------------+
| gross_e7        | —                 |                                                |
+-----------------+-------------------+------------------------------------------------+
| abgst           | abgelt_st_m       | Monthly capital income tax due, individual     |
+-----------------+-------------------+------------------------------------------------+
| soli            | soli_st_m         | Monthly solidarity surcharge due, individual   |
+-----------------+-------------------+------------------------------------------------+
| kindergeld      | kindergeld_m      | Monthly child Benefit, individual              |
+-----------------+-------------------+------------------------------------------------+
| incometax       | eink_st_m         | Monthly income Tax Due, individual             |
+-----------------+-------------------+------------------------------------------------+
| incometax_tu    | eink_st_m_tu      | Monthly income Tax Due, couple sum             |
+-----------------+-------------------+------------------------------------------------+
| uhv             | unterhaltsvors_m  | Alimony advance payment, individual            |
+-----------------+-------------------+------------------------------------------------+
| regelbedarf     | —                 |                                                |
+-----------------+-------------------+------------------------------------------------+
| regelsatz       | regelsatz_m       | Household socio-economic *need*, lump-sum      |
+-----------------+-------------------+------------------------------------------------+
| alg2_kdu        | kost_unterk_m     | Housing cost covered by social assistance      |
+-----------------+-------------------+------------------------------------------------+
| kiz             | kinderzuschlag_m  | Monthly additional child benefit, household    |
|                 |                   | sum                                            |
+-----------------+-------------------+------------------------------------------------+
| —               | elterngeld_m      | Monthly elterngeld, individual                 |
+-----------------+-------------------+------------------------------------------------+
| wohngeld        | wohngeld_m        | Monthly housing benefit, household sum         |
+-----------------+-------------------+------------------------------------------------+
| m_alg2          | arbeitsl_geld_2_m | Monthly social assistance, household sum       |
+-----------------+-------------------+------------------------------------------------+
| dpi_ind         | verfügb_eink_m    | Monthly disposable income, individual          |
+-----------------+-------------------+------------------------------------------------+
| —               | verfügb_eink_hh_m | Monthly disposable income including household  |
|                 |                   | level benefits, household sum                  |
+-----------------+-------------------+------------------------------------------------+
| gross           | —                 |                                                |
+-----------------+-------------------+------------------------------------------------+
