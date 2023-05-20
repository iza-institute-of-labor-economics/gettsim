# Relevant concepts of units of individuals

This is a collection of which units of individuals are relevant in which context,
originally resulting from a call on 27 Jan 2023. This may become a GEP.

Also see
[discussion on Zulip](https://gettsim.zulipchat.com/#narrow/stream/224837-High-Level-Architecture/topic/Update.20Data.20Structures/near/322500145)

## Steuern

### Veranlagung

- gemeinsam veranlagt (max 2, muss verheiratet sein / eingetragene Partnerschaft) oder
  nicht

### Kinderfreibeträge

- Elternteil(e) (max 2) / Kind
- Keine Referenz zu gemeinsamen Haushalt
- ggf. endogener Anspruch wegen
  - fehlender Unterhaltszahlung
  - unbekanntem Elternteil

## Kindergeld

- Elternteil(e) (max 2) / Kind
- Keine Referenz zu gemeinsamen Haushalt
- Auszahlung nur an 1 Person, aber betrifft anderen Elternteil bzgl. Unterhalt

## Kinderzuschlag

- Eine Bedarfsgemeinschaft + Eltern-/Kindbeziehung
- Elternteil(e) außerhalb des Haushalts spielen keine Rolle außer über
  Unterhalts(vorschuss)zahlungen

## Elterngeld

- Eltern-/Kindbeziehung

## Unterhalt / Unterhaltsvorschuss

- Eltern-/Kindbeziehung
  - Eltern zwangsläufig nicht Teil einer Haushaltsgemeinschaft

## Pflegeversicherung

- Eltern-/Kindbeziehung
  - Keine Referenz zu gemeinsamen Haushalt
  - Keine Referenz zu Alterskategorien der Kinder

## Rente

### Grundrente

- Ehepartner

### Verwitwetenrente

- (ehem.) Ehepartner

## Bürgergeld und Sozialhilfe

### SGB II (Bürgergeld)

- Eine Bedarfsgemeinschaft
  - Einstandsgemeinschaft (max 2 Erwachsene, eheähnliche Verhältnisse)
  - Kinder unter 18/25
- Eine Haushaltsgemeinschaft kann aus mehreren Bedarfsgemeinschaften bestehen
  - Eltern + erwachsene Kinder ab 18/25
  - Es kann sein, dass Einkommen/Vermögen von verwandten/verschwägerten Mitgliedern der
    Haushaltsgemeinschaft berücksichtigt wird (Einstandsvermutung)

### SGB XII (Hilfe zum Lebensunterhalt)

(1,5 Mrd €)

- Relevant sind
  - vertikale Beziehungen (Eltern / Kinder)
    - Keine Referenz zu gemeinsamen Haushalt
    - Keine Referenz zu Alterskategorien
  - Haushaltsgemeinschaft
  - Nicht zwangsläufig auf Verwandte beschränkt
  - _wenn Personen, die zusammen wohnen, auch gemeinsam wirtschaften. Der Begriff der_
    _Haushaltsgemeinschaft wird gegenüber der Wohngemeinschaft gerade dadurch_
    _gekennzeichnet, dass ihre Mitglieder nicht nur vorübergehend in einer Wohnung_
    _zusammenleben, sondern einen gemeinsamen Haushalt in der Weise führen, dass sie_
    _„aus einem Topf“ wirtschaften. Das gemeinsame Wirtschaften geht über die_
    _gemeinsame Nutzung von Bad, Küche und ggf. Gemeinschaftsräumen sowie über einen_
    _gemeinsam organisierten Einkauf über eine Gemeinschaftskasse, wie dies regelmäßig_
    _in Wohngemeinschaften organisiert ist, hinaus._
    https://www.berlin.de/sen/soziales/service/berliner-sozialrecht/kategorie/rundschreiben/2014_04-572017.php

### SGB XII (Grundsicherung im Alter / bei Erwerbsminderung)

- Relevant sind vertikale Beziehungen (Eltern / Kinder)
  - Keine Referenz zu gemeinsamen Haushalt
  - Keine Referenz zu Alterskategorien

(7 Mrd €)

### SGB XII (Eingliederungshilfe für Menschen mit Behinderung)

(20 Mrd €)

### SGB XII (Hilfe zur Pflege)

(4 Mrd €)

### Interaktion SGB II / SGB XII

- Partnerschaften, in denen ein Partner unter SGB II und einer unter SGB XII fällt →
  ganze Gemeinschaft fällt unter SGB II
- Bedarfsgemeinschaft mit Kind unter 25, welches unter SGB II fällt → ?

## Wohngeld

- Haushaltsgemeinschaft
  - Antragsteller selbst

  - Ehegatte/ eingetragener Lebenspartner/ Lebensgefährte

  - Eltern (auch Stief-, Pflege- und Schwiegereltern)

  - Kinder (auch Pflege- und Adoptivkinder)

  - "Einstandspartner": nicht Verwandte, die aber mit dem Antragsteller in
    Verantwortungs- und Einstehensgemeinschaft leben

    _Eine Verantwortungs- bzw. Einstehensgemeinschaft ist im § 7 Abs. 3a SGB II_
    _geregelt, demnach muss mindestens eine der folgenden Bedingungen erfüllt sein:_

    - _wenn Partner länger als 1 Jahr zusammenleben_
    - _wenn Partner mit einem gemeinsamen Kind zusammenleben_
    - _wenn Kinder oder Angehörige im Haushalt versorgt oder betreut werden (nicht nur_
      _gelegentlich)_
    - _wenn Partner gegenseitig befugt sind, über Einkommen und Vermögen zu verfügen_

    _Voraussetzung für alle Haushaltsmitglieder ist, dass sie mit dem dem Antragsteller_
    _in einer gemeinsamen Wohnung oder Haus leben und auch dort gemeldet sind._

  - sonstige Verwandte

### Kinderwohngeld

Bsp:

- Alleinerziehend, ein Kind
- Kind kann eigenen Bedarf decken mit Unterhaltsleistungen, Kindergeld, Kinderzuschlag,
  Wohngeld
- Kind fällt aus Bedarfsgemeinschaft heraus

## Modellierung

### Vollerhebung

#### Ansatz

- Eltern-Kind-Beziehungen über `id_eltern`
- Haushaltskonzept aus Wohngeld bestimmt `id_haushalt`
  - Eine Studierenden-WG hätte unterschiedliche Werte für `id_haushalt`
- Bedarfsgemeinschaft aus:
  - Einstandspartner `id_einstandspartner`
  - Kinder bis 17/24 von mir und meinem Einstandspartner. Es sei denn herausgelöst
    - über eigenes Einkommen
    - Kinderwohngeld

#### Limitierung

- Innerhalb eines Wohngeldhaushalts kann nicht unterschieden werden zwischen Personen
  ohne Einstandsverpflichtung nach SGB II bzw. SGB XII und mit einer solchen

- Kann nur die beiden Extremfälle abbilden

  1. alle nicht-vertikalen bzw. Partnerbeziehungen kein Kandidat für
     Haushaltsgemeinschaft nach SGB II / SGB XII
  1. alle nicht-vertikalen bzw. Partnerbeziehungen sind Kandidat für
     Haushaltsgemeinschaft nach SGB II / SGB XII

  Typischerweise wird 1. die Lösung sein (Hürden für gemeinsames Wirtschaften sind
  hoch).

- Alternative wäre eine weitere ID-Variable, die Haushaltsgemeinschaften nach SGB II und
  SGB XII spezifiziert.

### Teile der Daten nicht vorhanden

- Erwachsene Kinder da, aber nicht im Datensatz
- Unterhaltspflichtiger Ehepartner da, aber nicht im Datensatz
- ...

Optionen:

- Datenzeilen hinzufügen (seitens Nutzer:in, ggf. Hilfsfunktionen zum Auffüllen von
  Datensätzen), diese müssten aber wohl wieder aus Berechnung herausfallen
- Personen-ID mit negativem Wert (o.Ä.) zu Datensatz hinzugeben.
