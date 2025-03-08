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

(einkommen__bruttolohn_m)=

## `einkommen__bruttolohn_m`

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

(rente__altersrente__rentner)=

## `rente__altersrente__rentner`

Pensioner employment status

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

(demograpics__p_id_ehepartner)=

## `demograpics__p_id_ehepartner`

Identifier of married partner

Type: int

(demograpics__p_id_einstandspartner)=

## `demograpics__p_id_einstandspartner`

Identifier of Einstandspartner

Type: int

(demograpics__p_id_einstandspartner)=

## `kindergeld__p_id_empfänger`

Identifier of person that claims Kindergeld for the particular child

Type: int

(demographics__wohnort_ost)=

## `demographics__wohnort_ost`

Living in former East Germany

Type: bool

(sozialversicherungsbeitraege__krankenversicherung__privat_versichert)=

## `sozialversicherungsbeitraege__krankenversicherung__privat_versichert`

In private health insurance

Type: bool

(einkommensteuer__einkommen__beitrag_private_rentenversicherung_m)=

## `einkommensteuer__einkommen__beitrag_private_rentenversicherung_m`

Monthly private pension contribution

Type: float

(kindergeld__in_ausbildung)=

## `kindergeld__in_ausbildung`

Employment status “in education”

Type: bool

(einkommen__ist_selbstständig)=

## `einkommen__ist_selbstständig`

Self-employed (main profession)

Type: bool

(sozialversicherungsbeitraege__pflegeversicherung__hat_kinder)=

## `sozialversicherungsbeitraege__pflegeversicherung__hat_kinder`

Has kids (incl. not in hh)

Type: bool

(einkommensteuer__freibetraege__betreuungskosten_m)=

## `einkommensteuer__freibetraege__betreuungskosten_m`

Monthly childcare expenses for a particular child under the age of 14

Type: float

(einkommensteuer__freibetraege__p_id_betreuungskosten_träger)=

## `einkommensteuer__freibetraege__p_id_betreuungskosten_träger`

Identifier of the person who paid childcare expenses.

Type: float

(einkommen__sonstige_m)=

## `einkommen__sonstige_m`

Additional income: includes private and public transfers that are not yet implemented in
GETTSIM (e.g., BAföG, Kriegsopferfürsorge)

Type: float

(einkommen__aus_selbstständigkeit_m)=

## `einkommen__aus_selbstständigkeit_m`

Monthly income from self-employment

Type: float

(einkommen__aus_vermietung_m)=

## `einkommen__aus_vermietung_m`

Monthly rental income net of deductions

Type: float

(einkommen__bruttokapitaleinkommen_m)=

## `einkommen__bruttokapitaleinkommen_m`

Monthly capital income

Type: float

(bruttokaltmiete_m_hh)=

## `bruttokaltmiete_m_hh`

Monthly rent expenses for household

Type: float

(heizkosten_m_hh)=

## `heizkosten_m_hh`

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
`elterngeld__nettoerwerbseinkommen_approximation_m` target in a separate run, which
would typically be for the previous calendar year.

Type: float

(elterngeld__zu_versteuerndes_einkommen_vorjahr_y_sn)=

## `elterngeld__zu_versteuerndes_einkommen_vorjahr_y_sn`

Taxable income in the 12 months before birth of youngest child. You may let GETTSIM
compute this variable via the
`einkommensteuer__einkommen__zu_versteuerndes_einkommen_mit_kinderfreibetrag_y_sn`
target in a separate run, which would typically be for the previous calendar year.

Type: float

(einkommen__bruttolohn_vorjahr_m)=

## `einkommen__bruttolohn_vorjahr_m`

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

(rente__jahr_renteneintritt)=

## `rente__jahr_renteneintritt`

Year of retirement

Type: int

(rente__monat_renteneintritt)=

## `rente__monat_renteneintritt`

Month of retirement

Type: int

(elterngeld__bisheriger_bezug_m)=

## `elterngeld__bisheriger_bezug_m`

Number of months the individual received Elterngeld for the current youngest child.

Type: int

(demographics__behinderungsgrad)=

## `demographics__behinderungsgrad`

Handicap degree (between 0 and 100)

Type: int

(rente__altersrente__schwerbehindert_grad_g)=

## `rente__altersrente__schwerbehindert_grad_g`

Severerly handicapped, with flag "G"

Type: bool

(wohngeld__mietstufe)=

## `wohngeld__mietstufe`

Level of rents in city (1: low, 3: average)

Type: int

(wohngeld__baujahr_immobilie_hh)=

## `wohngeld__baujahr_immobilie_hh`

Construction year of dwelling

Type: int

(demographics__vermögen)=

## `demographics__vermögen`

Assets for means testing on individual
level.{ref}`See this page for more details. <means_testing>`

Type: float

(rente__altersrente__entgeltpunkte_west)=

## `rente__altersrente__entgeltpunkte_west`

Earnings points for pension claim accumulated in western states

Type: float

(rente__altersrente__entgeltpunkte_ost)=

## `rente__altersrente__entgeltpunkte_ost`

Earnings points for pension claim accumulated in eastern states

Type: float

(rente__grundrente__grundrentenzeiten_m)=

## `rente__grundrente__grundrentenzeiten_m`

Number of months determining Grundrenteeligibility

Type: int

(rente__grundrente__bewertungszeiten_m)=

## `rente__grundrente__bewertungszeiten_m`

Number of months determining Grundrentepayments

Type: int

(rente__grundrente__entgeltpunkte)=

## `rente__grundrente__entgeltpunkte`

Average `entgeltp` during`rente__grundrente__bewertungszeiten_m`

Type: float

(rente__private_rente_m)=

## `rente__private_rente_m`

Amount of monthly private pension

Type: float

(rente__altersrente__pflichtbeitragszeiten_m)=

## `rente__altersrente__pflichtbeitragszeiten_m`

Total months of mandatory pensioninsurance contributions

Type: float

(rente__altersrente__freiwillige_beitragszeiten_m)=

## `rente__altersrente__freiwillige_beitragszeiten_m`

Total months of voluntary pensioninsurance contributions

Type: float

(rente__altersrente__mutterschutzzeiten_m)=

## `rente__altersrente__mutterschutzzeiten_m`

Total months of maternal protections

Type: float

(rente__altersrente__arbeitsunfähigkeitszeiten_m)=

## `rente__altersrente__arbeitsunfähigkeitszeiten_m`

Total months of sickness, rehabilitation,measures for worklife participation(Teilhabe)

Type: float

(rente__altersrente__krankheitszeiten_ab_16_bis_24_m)=

## `rente__altersrente__krankheitszeiten_ab_16_bis_24_m`

Months of sickness between age 16 and 24

Type: float

(rente__altersrente__arbeitslosigkeitszeiten_m)=

## `rente__altersrente__arbeitslosigkeitszeiten_m`

Total months of unemployment (registered)

Type: float

(rente__altersrente__ausbildungssuche_m)=

## `rente__altersrente__ausbildungssuche_m`

Total months of apprenticeship search

Type: float

(rente__altersrente__schulausbildung_m)=

## `rente__altersrente__schulausbildung_m`

Months of schooling (incl college, unifrom age 17, max. 8 years)

Type: float

(rente__altersrente__entgeltersatzleistungen_arbeitslosigkeit_m)=

## `rente__altersrente__entgeltersatzleistungen_arbeitslosigkeit_m`

Total months of unemployment (only timeof Entgeltersatzleistungen, not ALGII),i.e.
Arbeitslosengeld, Unterhaltsgeld, Übergangsgeld

Type: float

(rente__altersrente__zeiten_geringfügiger_beschäftigung_m)=

## `rente__altersrente__zeiten_geringfügiger_beschäftigung_m`

Total months of marginal employment (w/o mandatory contributions)

Type: float

(rente__altersrente__ersatzzeiten_m)=

## `rente__altersrente__ersatzzeiten_m`

Total months during military, persecution/escape, internment, and consecutive sickness

Type: float

(rente__altersrente__kinderberücksichtigungszeiten_m)=

## `rente__altersrente__kinderberücksichtigungszeiten_m`

Total months of childcare till age 10

Type: float

(rente__altersrente__pflegeberücksichtigungszeiten_m)=

## `rente__altersrente__pflegeberücksichtigungszeiten_m`

Total months of home care provision (01.01.1992-31.03.1995)

Type: float

(rente__altersrente__für_frauen__jahre_pflichtbeiträge_ab_40)=

## `rente__altersrente__für_frauen__jahre_pflichtbeiträge_ab_40`

Total years of mandatory contributions after age 40

Type: float

(rente__altersrente__wegen_arbeitslosigkeit__pflichtbeitrag_8_in_10)=

## `rente__altersrente__wegen_arbeitslosigkeit__pflichtbeitrag_8_in_10`

Has at least 8 contribution years in past 10 years

Type: bool

(rente__altersrente__wegen_arbeitslosigkeit__arbeitslos_für_1_jahr_nach_585)=

## `rente__altersrente__wegen_arbeitslosigkeit__arbeitslos_für_1_jahr_nach_585`

Has been unemployed at least 1 year after age 58.5

Type: bool

(rente__altersrente__wegen_arbeitslosigkeit__vertrauensschutz_1997)=

## `rente__altersrente__wegen_arbeitslosigkeit__vertrauensschutz_1997`

Is covered by Vertrauensschutz rules for the Altersrente wegen Arbeitslosigkeit
implemented in 1997 (§ 237 SGB VI Abs. 4).

Type: bool

(rente__altersrente__wegen_arbeitslosigkeit__vertrauensschutz_2006)=

## `rente__altersrente__wegen_arbeitslosigkeit__vertrauensschutz_2006`

Is covered by Vertrauensschutz rules for the Altersrente wegen Arbeitslosigkeit
implemented in 2006 (§ 237 SGB VI Abs. 5).

Type: bool

(rente__altersrente__höchster_bruttolohn_letzte_15_jahre_vor_rente_y)=

## `rente__altersrente__höchster_bruttolohn_letzte_15_jahre_vor_rente_y`

Highest gross income from regular employment in the last 15 years before pension benefit
claiming. Relevant to determine pension benefit deductions for retirees in early
retirement.

(arbeitslosengeld_2__in_vorjahr_bezogen)=

## `arbeitslosengeld_2__in_vorjahr_bezogen`

Received Bürgergeld in previous year

Type: bool

(arbeitslosengeld__anwartschaftszeit)=

## `arbeitslosengeld__anwartschaftszeit`

At least 12 months of unemployment contributions in the 30 months before claiming
unemployment insurance

Type: bool

(arbeitslosengeld__arbeitssuchend)=

## `arbeitslosengeld__arbeitssuchend`

Looking for employment

Type: bool

(arbeitslosengeld__monate_durchgängiger_alg1_bezug)=

## `arbeitslosengeld__monate_durchgängiger_alg1_bezug`

Months the individual already uninterruptedly receives Arbeitslosengeld

Type: float

(arbeitslosengeld__war_5_jahre_sozialversicherungspflichtig)=

## `arbeitslosengeld__war_5_jahre_sozialversicherungspflichtig`

Months of subjection to compulsory insurance in the 5 years before claiming unemployment
insurance

Type: float

## `unterhalt__kind_anspruch_m`

Monthly gross child alimony payments to be received as determined by the court on child
level

Type: float

## `unterhalt__kind_betrag_m`

Monthly actual child alimony payments received on child level

Type: float

(lohnsteuer__steuerklasse)=

## `lohnsteuer__steuerklasse`

Tax Bracket (1 to 5) for withholding tax

Type: int

## `erziehungsgeld__budgetsatz`

Applied for "Budgetsatz" of parental leave benefit

Type: bool

## `rente__erwerbsminderung__voll_erwerbsgemindert`

Unable to provide more than 3 hours of market labor per day.

Type: bool

## `rente__erwerbsminderung__teilweise_erwerbsgemindert`

Able to provide at least 3 but no more than 6 hours of market labor per day.

Type: bool
