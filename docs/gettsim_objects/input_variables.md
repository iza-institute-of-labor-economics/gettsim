(input_variables)=

# Basic input variables

The table below gives an overview of all variables needed to run GETTSIM completely.
Note that the variables with \_hh at the end, have to be constant over the whole
household.

(hh_id)=

## `hh_id`

Household identifier

Type: int

(kind)=

## `kind`

Dependent child living with parents

Type: bool

(bruttolohn_m)=

## `bruttolohn_m`

Monthly wage

Type: float

(alter)=

## `alter`

Individual's age.

Type: int

(weiblich)=

## `weiblich`

Female

Type: bool

(rentner)=

## `rentner`

Pensioner employment status

Type: bool

(alleinerz)=

## `alleinerz`

Single parent

Type: bool

(gemeinsam_veranlagt)=

## `gemeinsam_veranlagt`

Taxes are filed jointly

Type: bool

(p_id_elternteil_1)=

## `p_id_elternteil_1`

Identifier of the first parent

Type: int

(p_id_elternteil_2)=

## `p_id_elternteil_2`

Identifier of the second parent

Type: int

(p_id_ehepartner)=

## `p_id_ehepartner`

Identifier of married partner

Type: int

(p_id_einstandspartner)=

## `p_id_einstandspartner`

Identifier of Einstandspartner

Type: int

(p_id_einstandspartner)=

## `p_id_kindergeld_empf`

Identifier of person that claims Kindergeld for the particular child

Type: int

(wohnort_ost)=

## `wohnort_ost`

Living in former East Germany

Type: bool

(in_priv_krankenv)=

## `in_priv_krankenv`

In private health insurance

Type: bool

(priv_rentenv_beitr_m)=

## `priv_rentenv_beitr_m`

Monthly private pension contribution

Type: float

(in_ausbildung)=

## `in_ausbildung`

Employment status “in education”

Type: bool

(selbstständig)=

## `selbstständig`

Self-employed (main profession)

Type: bool

(hat_kinder)=

## `hat_kinder`

Has kids (incl. not in hh)

Type: bool

(betreuungskost_m)=

## `betreuungskost_m`

Monthly childcare expenses for a particular child under the age of 14

Type: float

(p_id_betreuungsk_träger)=

## `p_id_betreuungsk_träger`

Identifier of the person who paid childcare expenses.

Type: float

(sonstig_eink_m)=

## `sonstig_eink_m`

Additional income: includes private and public transfers that are not yet implemented in
GETTSIM (e.g., BAföG, Kriegsopferfürsorge)

Type: float

(eink_selbst_m)=

## `eink_selbst_m`

Monthly income from self-employment

Type: float

(eink_vermietung_m)=

## `eink_vermietung_m`

Monthly rental income net of deductions

Type: float

(kapitaleink_brutto_m)=

## `kapitaleink_brutto_m`

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

(wohnfläche_hh)=

## `wohnfläche_hh`

Size of household dwelling in square meters

Type: float

(bewohnt_eigentum_hh)=

## `bewohnt_eigentum_hh`

Owner-occupied housing

Type: bool

(arbeitsstunden_w)=

## `arbeitsstunden_w`

Weekly working hours of individual

Type: float

(bruttolohn_vorj_m)=

## `bruttolohn_vorj_m`

Monthly wage, previous year

Type: float

(geburtstag)=

## `geburtstag`

Day of birth (within month)

Type: int

(geburtsmonat)=

## `geburtsmonat`

Month of birth

Type: int

(geburtsjahr)=

## `geburtsjahr`

Year of birth

Type: int

(jahr_renteneintr)=

## `jahr_renteneintr`

Year of retirement

Type: int

(monat_renteneintr)=

## `monat_renteneintr`

Month of retirement

Type: int

(m_elterngeld)=

## `m_elterngeld`

Number of months hh received elterngeld

Type: int

(m_elterngeld_vat_hh)=

## `m_elterngeld_vat_hh`

Number of months father received elterngeld

Type: int

(m_elterngeld_mut_hh)=

## `m_elterngeld_mut_hh`

Number of months mother received elterngeld

Type: int

(behinderungsgrad)=

## `behinderungsgrad`

Handicap degree (between 0 and 100)

Type: int

(schwerbeh_g)=

## `schwerbeh_g`

Severerly handicapped, with flag "G"

Type: bool

(mietstufe)=

## `mietstufe`

Level of rents in city (1: low, 3: average)

Type: int

(immobilie_baujahr_hh)=

## `immobilie_baujahr_hh`

Construction year of dwelling

Type: int

(vermögen_bedürft)=

## `vermögen_bedürft`

Assets for means testing on individual
level.{ref}`See this page for more details. <means_testing>`

Type: float

(entgeltp_west)=

## `entgeltp_west`

Earnings points for pension claim accumulated in western states

Type: float

(entgeltp_ost)=

## `entgeltp_ost`

Earnings points for pension claim accumulated in eastern states

Type: float

(grundr_zeiten)=

## `grundr_zeiten`

Number of months determining Grundrenteeligibility

Type: int

(grundr_bew_zeiten)=

## `grundr_bew_zeiten`

Number of months determining Grundrentepayments

Type: int

(grundr_entgeltp)=

## `grundr_entgeltp`

Average `entgeltp` during`grundr_bew_zeiten`

Type: float

(priv_rente_m)=

## `priv_rente_m`

Amount of monthly private pension

Type: float

(m_pflichtbeitrag)=

## `m_pflichtbeitrag`

Total months of mandatory pensioninsurance contributions

Type: float

(m_freiw_beitrag)=

## `m_freiw_beitrag`

Total months of voluntary pensioninsurance contributions

Type: float

(m_mutterschutz)=

## `m_mutterschutz`

Total months of maternal protections

Type: float

(m_arbeitsunfähig)=

## `m_arbeitsunfähig`

Total months of sickness, rehabilitation,measures for worklife participation(Teilhabe)

Type: float

(m_krank_ab_16_bis_24)=

## `m_krank_ab_16_bis_24`

Months of sickness between age 16 and 24

Type: float

(m_arbeitsl)=

## `m_arbeitsl`

Total months of unemployment (registered)

Type: float

(m_ausbild_suche)=

## `m_ausbild_suche`

Total months of apprenticeship search

Type: float

(m_schul_ausbild)=

## `m_schul_ausbild`

Months of schooling (incl college, unifrom age 17, max. 8 years)

Type: float

(m_alg1_übergang)=

## `m_alg1_übergang`

Total months of unemployment (only timeof Entgeltersatzleistungen, not ALGII),i.e.
Arbeitslosengeld, Unterhaltsgeld,Übergangsgeld

Type: float

(m_geringf_beschäft)=

## `m_geringf_beschäft`

Total months of marginal employment (w/o mandatory contributions)

Type: float

(m_ersatzzeit)=

## `m_ersatzzeit`

Total months during military, persecution/escape, internment, and consecutive sickness

Type: float

(m_kind_berücks_zeit)=

## `m_kind_berücks_zeit`

Total months of childcare till age 10

Type: float

(m_pfleg_berücks_zeit)=

## `m_pfleg_berücks_zeit`

Total months of home care provision (01.01.1992-31.03.1995)

Type: float

(y_pflichtbeitr_ab_40)=

## `y_pflichtbeitr_ab_40`

Total years of mandatory contributions after age 40

Type: float

(pflichtbeitr_8_in_10)=

## `pflichtbeitr_8_in_10`

Has at least 8 contribution years in past 10 years

Type: bool

(arbeitsl_1y_past_585)=

## `arbeitsl_1y_past_585`

Has been unemployed at least 1 year after age 58.5

Type: bool

(vertra_arbeitsl_1997)=

## `vertra_arbeitsl_1997`

Is covered by Vertrauensschutz rules for the Altersrente wegen Arbeitslosigkeit
implemented in 1997 (§ 237 SGB VI Abs. 4).

Type: bool

(vertra_arbeitsl_2006)=

## `vertra_arbeitsl_2006`

Is covered by Vertrauensschutz rules for the Altersrente wegen Arbeitslosigkeit
implemented in 2006 (§ 237 SGB VI Abs. 5).

Type: bool

(bürgerg_bezug_vorj)=

## `bürgerg_bezug_vorj`

Received Bürgergeld in previous year

Type: bool

(anwartschaftszeit)=

## `anwartschaftszeit`

At least 12 months of unemployment contributions in the 30 months before claiming
unemployment insurance

Type: bool

(arbeitssuchend)=

## `arbeitssuchend`

Looking for employment

Type: bool

(m_durchg_alg1_bezug)=

## `m_durchg_alg1_bezug`

Months the individual already uninterruptedly receives Arbeitslosengeld

Type: float

(sozialv_pflicht_5j)=

## `sozialv_pflicht_5j`

Months of subjection to compulsory insurance in the 5 years before claiming unemployment
insurance

Type: float

## `kind_unterh_anspr_m`

Monthly gross child alimony payments to be received as determined by the court

Type: float

## `kind_unterh_erhalt_m`

Monthly actual child alimony payments received

Type: float

(steuerklasse)=

## `steuerklasse`

Tax Bracket (1 to 5) for withholding tax

Type: int

## `anz_eig_kind_bis_24`

Number of own children below the age of 25 (incl. not in hh)

Type: int

## `budgetsatz_erzieh`

Applied for "Budgetsatz" of parental leave benefit

Type: bool

## `voll_erwerbsgemind`

Unable to provide more than 3 hours of market labor per day.

Type: bool

## `teilw_erwerbsgemind`

Able to provide at least 3 but no more than 6 hours of market labor per day.

Type: bool
