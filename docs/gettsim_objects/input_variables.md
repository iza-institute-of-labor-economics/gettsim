(input_variables)=

# Basic input variables

The table below gives an overview of all variables needed to run GETTSIM completely.
Note that the variables with \_hh at the end, have to be constant over the whole
household.

(demographics__hh_id)=

## `demographics__hh_id`

Household identifier following §5 WoGG

Type: int

(demographics__kind)=

## `demographics__kind`

Dependent child living with parents

Type: bool

(einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m)=

## `einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_m`

Monthly wage

Type: float

(demographics__alter)=

## `demographics__alter`

Individual's age.

Type: int

(demographics__weiblich)=

## `demographics__weiblich`

Female

Type: bool

(sozialversicherung__rente__bezieht_rente)=

## `sozialversicherung__rente__bezieht_rente`

Draws public pension benefits.

Type: bool

(demographics__alleinerziehend)=

## `demographics__alleinerziehend`

Single parent

Type: bool

(einkommensteuer__gemeinsam_veranlagt)=

## `einkommensteuer__gemeinsam_veranlagt`

Taxes are filed jointly

Type: bool

(demographics__p_id_elternteil_1)=

## `demographics__p_id_elternteil_1`

Identifier of the first parent

Type: int

(demographics__p_id_elternteil_2)=

## `demographics__p_id_elternteil_2`

Identifier of the second parent

Type: int

(demographics__p_id_ehepartner)=

## `demographics__p_id_ehepartner`

Identifier of married partner

Type: int

(arbeitslosengeld_2__p_id_einstandspartner)=

## `arbeitslosengeld_2__p_id_einstandspartner`

Identifier of Einstandspartner

Type: int

(arbeitslosengeld_2__p_id_einstandspartner)=

## `kindergeld__p_id_empfänger`

Identifier of person that claims Kindergeld for the particular child

Type: int

(demographics__wohnort_ost)=

## `demographics__wohnort_ost`

Living in former East Germany

Type: bool

(sozialversicherung__kranken__beitrag__privat_versichert)=

## `sozialversicherung__kranken__beitrag__privat_versichert`

In private health insurance

Type: bool

(einkommensteuer__abzüge__beitrag_private_rentenversicherung_m)=

## `einkommensteuer__abzüge__beitrag_private_rentenversicherung_m`

Monthly private pension contribution

Type: float

(kindergeld__in_ausbildung)=

## `kindergeld__in_ausbildung`

Employment status “in education”

Type: bool

(einkommensteuer__einkünfte__ist_selbstständig)=

## `einkommensteuer__einkünfte__ist_selbstständig`

Self-employed (main profession)

Type: bool

(sozialversicherung__pflege__beitrag__hat_kinder)=

## `sozialversicherung__pflege__beitrag__hat_kinder`

Has kids (incl. not in hh)

Type: bool

(einkommensteuer__abzüge__betreuungskosten_m)=

## `einkommensteuer__abzüge__betreuungskosten_m`

Monthly childcare expenses for a particular child under the age of 14

Type: float

(einkommensteuer__abzüge__p_id_betreuungskosten_träger)=

## `einkommensteuer__abzüge__p_id_betreuungskosten_träger`

Identifier of the person who paid childcare expenses.

Type: float

(einkommensteuer__einkünfte__sonstige__betrag_m)=

## `einkommensteuer__einkünfte__sonstige__betrag_m`

Additional income: includes private and public transfers that are not yet implemented in
GETTSIM (e.g., BAföG, Kriegsopferfürsorge)

Type: float

(einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m)=

## `einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_m`

Monthly income from self-employment

Type: float

(einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m)=

## `einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_m`

Monthly rental income net of deductions

Type: float

(einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_m)=

## `einkommensteuer__einkünfte__aus_kapitalvermögen__kapitalerträge_m`

Monthly capital income

Type: float

(wohnen__bruttokaltmiete_m_hh)=

## `wohnen__bruttokaltmiete_m_hh`

Monthly rent expenses for household

Type: float

(wohnen__heizkosten_m_hh)=

## `wohnen__heizkosten_m_hh`

Monthly heating expenses for household

Type: float

(wohnen__wohnfläche_hh)=

## `wohnen__wohnfläche_hh`

Size of household dwelling in square meters

Type: float

(wohnen__bewohnt_eigentum_hh)=

## `wohnen__bewohnt_eigentum_hh`

Owner-occupied housing

Type: bool

(demographics__arbeitsstunden_w)=

## `demographics__arbeitsstunden_w`

Weekly working hours of individual

Type: float

(elterngeld__claimed)=

## `elterngeld__claimed`

Individual claims Elterngeld

Type: bool

(elterngeld__nettoeinkommen_vorjahr_m)=

## `elterngeld__nettoeinkommen_vorjahr_m`

Approximation of the net wage in the 12 months before birth of youngest child (according
to simplified calculation rules). You may let GETTSIM compute this variable via the
`elterngeld__nettoeinkommen_approximation_m` target in a separate run, which would
typically be for the previous calendar year.

Type: float

(elterngeld__zu_versteuerndes_einkommen_vorjahr_y_sn)=

## `elterngeld__zu_versteuerndes_einkommen_vorjahr_y_sn`

Taxable income in the calendar year prior to the youngest child's birth year. You may
let GETTSIM compute this variable via the
`einkommensteuer__zu_versteuerndes_einkommen_y_sn` target in a separate run, which would
typically be for the previous calendar year.

Type: float

(einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_vorjahr_m)=

## `einkommensteuer__einkünfte__aus_nichtselbstständiger_arbeit__bruttolohn_vorjahr_m`

Gross wage in the previous year

Type: float

(demographics__geburtstag)=

## `demographics__geburtstag`

Day of birth (within month)

Type: int

(demographics__geburtsmonat)=

## `demographics__geburtsmonat`

Month of birth

Type: int

(demographics__geburtsjahr)=

## `demographics__geburtsjahr`

Year of birth

Type: int

(sozialversicherung__rente__jahr_renteneintritt)=

## `sozialversicherung__rente__jahr_renteneintritt`

Year of retirement

Type: int

(sozialversicherung__rente__monat_renteneintritt)=

## `sozialversicherung__rente__monat_renteneintritt`

Month of retirement

Type: int

(elterngeld__bisherige_bezugsmonate)=

## `elterngeld__bisherige_bezugsmonate`

Number of months the individual received Elterngeld for the current youngest child.

Type: int

(demographics__behinderungsgrad)=

## `demographics__behinderungsgrad`

Handicap degree (between 0 and 100)

Type: int

(demographics__schwerbehindert_grad_g)=

## `demographics__schwerbehindert_grad_g`

Severerly handicapped, with flag "G"

Type: bool

(wohngeld__mietstufe)=

## `wohngeld__mietstufe`

Level of rents in city (1: low, 3: average)

Type: int

(wohnen__baujahr_immobilie_hh)=

## `wohnen__baujahr_immobilie_hh`

Construction year of dwelling

Type: int

(demographics__vermögen)=

## `demographics__vermögen`

Assets for means testing on individual
level.{ref}`See this page for more details. <means_testing>`

Type: float

(sozialversicherung__rente__entgeltpunkte_west)=

## `sozialversicherung__rente__entgeltpunkte_west`

Earnings points for pension claim accumulated in western states

Type: float

(sozialversicherung__rente__entgeltpunkte_ost)=

## `sozialversicherung__rente__entgeltpunkte_ost`

Earnings points for pension claim accumulated in eastern states

Type: float

(sozialversicherung__rente__grundrente__grundrentenzeiten_monate)=

## `sozialversicherung__rente__grundrente__grundrentenzeiten_monate`

Number of months determining eligibility for Grundrente.

Type: int

(sozialversicherung__rente__grundrente__bewertungszeiten_monate)=

## `sozialversicherung__rente__grundrente__bewertungszeiten_monate`

Number of months determining Grundrentepayments

Type: int

(sozialversicherung__rente__grundrente__mean_entgeltpunkte)=

## `sozialversicherung__rente__grundrente__mean_entgeltpunkte`

Average `entgeltpunkte` during
`sozialversicherung__rente__grundrente__bewertungszeiten_monate`

Type: float

(sozialversicherung__rente__private_rente_betrag_m)=

## `sozialversicherung__rente__private_rente_betrag_m`

Amount of monthly private pension

Type: float

(sozialversicherung__rente__pflichtbeitragsmonate)=

## `sozialversicherung__rente__pflichtbeitragsmonate`

Total months of mandatory pension insurance contributions

Type: float

(sozialversicherung__rente__freiwillige_beitragsmonate)=

## `sozialversicherung__rente__freiwillige_beitragsmonate`

Total months of voluntary pensioninsurance contributions

Type: float

(sozialversicherung__rente__monate_in_mutterschutz)=

## `sozialversicherung__rente__monate_in_mutterschutz`

Total months of maternal protections

Type: float

(sozialversicherung__rente__monate_in_arbeitsunfähigkeit)=

## `sozialversicherung__rente__monate_in_arbeitsunfähigkeit`

Total months of sickness, rehabilitation,measures for worklife participation(Teilhabe)

Type: float

(sozialversicherung__rente__krankheitszeiten_ab_16_bis_24_monate)=

## `sozialversicherung__rente__krankheitszeiten_ab_16_bis_24_monate`

Months of sickness between age 16 and 24

Type: float

(sozialversicherung__rente__monate_in_arbeitslosigkeit)=

## `sozialversicherung__rente__monate_in_arbeitslosigkeit`

Total months of unemployment (registered)

Type: float

(sozialversicherung__rente__monate_in_ausbildungssuche)=

## `sozialversicherung__rente__monate_in_ausbildungssuche`

Total months of apprenticeship search

Type: float

(sozialversicherung__rente__monate_in_schulausbildung)=

## `sozialversicherung__rente__monate_in_schulausbildung`

Months of schooling (incl college, unifrom age 17, max. 8 years)

Type: float

(sozialversicherung__rente__monate_mit_bezug_entgeltersatzleistungen_wegen_arbeitslosigkeit)=

## `sozialversicherung__rente__monate_mit_bezug_entgeltersatzleistungen_wegen_arbeitslosigkeit`

Total months of unemployment (only timeof Entgeltersatzleistungen, not ALGII),i.e.
Arbeitslosengeld, Unterhaltsgeld, Übergangsgeld

Type: float

(sozialversicherung__rente__monate_geringfügiger_beschäftigung)=

## `sozialversicherung__rente__monate_geringfügiger_beschäftigung`

Total months of marginal employment (w/o mandatory contributions)

Type: float

(sozialversicherung__rente__ersatzzeiten_monate)=

## `sozialversicherung__rente__ersatzzeiten_monate`

Total months during military, persecution/escape, internment, and consecutive sickness

Type: float

(sozialversicherung__rente__kinderberücksichtigungszeiten_monate)=

## `sozialversicherung__rente__kinderberücksichtigungszeiten_monate`

Total months of childcare till age 10

Type: float

(sozialversicherung__rente__pflegeberücksichtigungszeiten_monate)=

## `sozialversicherung__rente__pflegeberücksichtigungszeiten_monate`

Total months of home care provision (01.01.1992-31.03.1995)

Type: float

(sozialversicherung__rente__altersrente__für_frauen__pflichtsbeitragsjahre_ab_alter_40)=

## `sozialversicherung__rente__altersrente__für_frauen__pflichtsbeitragsjahre_ab_alter_40`

Total years of mandatory contributions after age 40

Type: float

(sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__pflichtbeitragsjahre_8_von_10)=

## `sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__pflichtbeitragsjahre_8_von_10`

Has at least 8 contribution years in past 10 years

Type: bool

(sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__arbeitslos_für_1_jahr_nach_alter_58_ein_halb)=

## `sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__arbeitslos_für_1_jahr_nach_alter_58_ein_halb`

Has been unemployed at least 1 year after age 58.5

Type: bool

(sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__vertrauensschutz_1997)=

## `sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__vertrauensschutz_1997`

Is covered by Vertrauensschutz rules for the Altersrente wegen Arbeitslosigkeit
implemented in 1997 (§ 237 SGB VI Abs. 4).

Type: bool

(sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__vertrauensschutz_2004)=

## `sozialversicherung__rente__altersrente__wegen_arbeitslosigkeit__vertrauensschutz_2004`

Is covered by Vertrauensschutz rules for the Altersrente wegen Arbeitslosigkeit enacted
in July 2004 (§ 237 SGB VI Abs. 5).

Type: bool

(sozialversicherung__rente__altersrente__höchster_bruttolohn_letzte_15_jahre_vor_rente_y)=

## `sozialversicherung__rente__altersrente__höchster_bruttolohn_letzte_15_jahre_vor_rente_y`

Highest gross income from regular employment in the last 15 years before pension benefit
claiming. Relevant to determine pension benefit deductions for retirees in early
retirement.

(arbeitslosengeld_2__arbeitslosengeld_2_bezug_im_vorjahr)=

## `arbeitslosengeld_2__arbeitslosengeld_2_bezug_im_vorjahr`

Received Bürgergeld in previous year

Type: bool

(sozialversicherung__arbeitslosen__anwartschaftszeit)=

## `sozialversicherung__arbeitslosen__anwartschaftszeit`

At least 12 months of unemployment contributions in the 30 months before claiming
unemployment insurance

Type: bool

(sozialversicherung__arbeitslosen__arbeitssuchend)=

## `sozialversicherung__arbeitslosen__arbeitssuchend`

Looking for employment

Type: bool

(sozialversicherung__arbeitslosen__monate_durchgängigen_bezugs_von_arbeitslosengeld)=

## `sozialversicherung__arbeitslosen__monate_durchgängigen_bezugs_von_arbeitslosengeld`

Number of months the individual already receives Arbeitslosengeld without interruption.

Type: float

(sozialversicherung__arbeitslosen__monate_sozialversicherungspflichtiger_beschäftigung_in_letzten_5_jahren)=

## `sozialversicherung__arbeitslosen__monate_sozialversicherungspflichtiger_beschäftigung_in_letzten_5_jahren`

Months of subjection to compulsory insurance in the 5 years before claiming unemployment
insurance

Type: float

## `unterhalt__anspruch_m`

Monthly gross child alimony payments to be received by the child as determined by the
court.

Type: float

## `unterhalt__tatsächlich_erhaltener_betrag_m`

Child alimony payments the child actually receives.

Type: float

(lohnsteuer__steuerklasse)=

## `lohnsteuer__steuerklasse`

Tax Bracket (1 to 5) for withholding tax

Type: int

## `erziehungsgeld__budgetsatz`

Applied for "Budgetsatz" of parental leave benefit

Type: bool

## `sozialversicherung__rente__erwerbsminderung__voll_erwerbsgemindert`

Unable to provide more than 3 hours of market labor per day.

Type: bool

## `sozialversicherung__rente__erwerbsminderung__teilweise_erwerbsgemindert`

Able to provide at least 3 but no more than 6 hours of market labor per day.

Type: bool
