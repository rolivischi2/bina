# Eine nicht-technische Anleitung zur Zürcher Velozählstellen-Analyse

Das ist, was wir gemacht haben, in einfacher Sprache, über zwei Phasen hinweg: **Bereinigung der Rohdaten** und **Analyse der Wachstums-Hotspots**.

---

## Teil 1: Datenbereinigung (Notebook 02)

Stell dir vor, du bekommst sechs Kisten mit handschriftlichen Verkehrszählungen — eine Kiste pro Jahr (2020–2025). Einige Zähler standen auf Velowegen, andere auf Fussgängerwegen. Manche Seiten sind verschmiert, manche fehlen, einige zeigen offensichtliche Fehler (wie "minus 15 Velofahrer"). Bevor wir irgendeine sinnvolle Frage beantworten können, müssen wir die Kisten in eine saubere, vertrauenswürdige Datei zusammenführen.

### Schritt 1 — Alle sechs Jahre in eine Tabelle zusammenführen
Jedes Jahr war in einer separaten Datei gespeichert. Wir haben sie zu einer grossen Tabelle zusammengefügt, damit wir den gesamten Zeitraum 2020–2025 auf einmal sehen können. Wir haben auch die Spaltenüberschriften (die kryptisch waren wie `FK_STANDORT`) in lesbare Namen wie `station_id` umbenannt.

### Schritt 2 — Fussgänger-Zählstellen aussortieren
Die Zähler messen sowohl Velos als auch Fussgänger, aber unser Projekt dreht sich nur um Velos. Wir haben nur die Stationen behalten, die tatsächlich Velodaten aufgezeichnet haben, und die Fussgänger-Spalten komplett gelöscht.

### Schritt 3 — Datumsangaben prüfen und auf Duplikate kontrollieren
Jede Zeile hat einen Zeitstempel (z.B. "14. März 2022, 08:15"). Wir haben sichergestellt, dass Python diese als echte Datumsangaben versteht (nicht nur als Text), und überprüft, dass keine Station zwei Zeilen für denselben Zeitpunkt hat — was eine Doppelzählung bedeuten würde.

### Schritt 4 — Einbahn- vs. Zweibahn-Zählstellen unterscheiden
Einige Zähler stehen auf einem Einbahn-Veloweg (sie messen nur Velos in eine Richtung). Andere stehen auf einem Zweibahn-Veloweg (sie messen "rein" *und* "raus"). Wenn wir naiv "rein + raus" für eine Einbahn-Station addieren würden, würden wir null zu einer echten Zahl addieren — kein Problem. Aber wenn wir vergessen, sie für eine Zweibahn-Station zu addieren, würden wir den echten Verkehr **halbieren**. Wir haben deshalb identifiziert, welche Art welche war, und für jede Station ein korrektes **Gesamtvolumen** berechnet.

### Schritt 5 — Defekte Sensoren erkennen
Ein echter Zähler zeigt um 3 Uhr morgens im Januar null Velos — das ist plausibel. Aber wenn ein Zähler **sechs Stunden am Stück mitten an einem Wochentag null Velos** zeigt, war der Sensor kaputt, nicht die Stadt. Wir haben jede Serie von Nullen, die länger als 6 Stunden dauerte, als Sensor-Ausfall markiert und diese Messungen als "fehlend" gekennzeichnet (damit sie Durchschnittswerte nicht nach unten ziehen).

### Schritt 6 — Unmögliche Werte entfernen
Es kann keine "-5 Velofahrer" geben. Negative Zahlen sind Dateneingabefehler, also haben wir diese auf "fehlend" gesetzt.

### Schritt 7 — Prüfen, welche Stationen konsistente Abdeckung haben
**Das ist der wichtigste Bereinigungsschritt für unsere Wachstumsanalyse.**

Zürich hat viele alte Zähler rund um 2022–2023 ersetzt. Wenn wir also einfach schauen würden "welche Station ist seit 2020 am meisten gewachsen", würde ein Zähler, der 2023 installiert wurde, so aussehen, als wäre er von **null** gewachsen — offensichtlich Unsinn. Wir haben jede Station mit einem "is_consistent"-Flag markiert: grünes Licht, wenn sie in jedem Jahr der Studie mindestens 60% Abdeckung hat.

### Schritt 8 — Bereinigte Daten speichern
Wir haben zwei Dateien gespeichert:
- **`velo_15min_clean.parquet`** — die bereinigten Zählungen, alle 15 Minuten, für jede Velostation
- **`station_metadata.csv`** — eine Zusammenfassung jeder Station (Standort, Einbahn vs. Zweibahn, Konsistenz-Flag)

Denk daran als: chaotischer Stapel Papierkram → eine ordentliche Tabelle + ein Stations-Verzeichnis.

---

## Teil 2: Wachstums-Hotspots (Notebook 03)

Die Frage, die dieses Notebook beantwortet: **Welche Velozähler zeigen den stärksten Aufwärtstrend von 2020–2025? Und bei aktuellem Tempo, welche werden ihren Verkehr innerhalb von 5 Jahren verdoppeln?**

### Schritt 1 — Bereinigte Daten laden
Wir haben die beiden Dateien aus Teil 1 wieder geladen.

### Schritt 2 — Nur konsistente Stationen behalten
Mit dem "is_consistent"-Flag von vorher. Von 46 Stationen insgesamt hatten nur **12** zuverlässige Daten in jedem Jahr. Die anderen 34 wurden aus dieser Analyse ausgeschlossen — nicht weil sie schlecht sind, sondern weil man keinen fairen "2020–2025 Trend" für eine Station berechnen kann, die erst 2023 existierte.

### Schritt 3 — Verbleibende Lücken entfernen
Die letzten fehlenden Werte entfernen, damit sie die Jahressummen nicht verfälschen.

### Schritt 4 — Prüfen, wie vollständig jedes Jahr pro Station ist
Ein normales Jahr hat etwa 35'000 Fünfzehn-Minuten-Intervalle. Wir haben pro Station und pro Jahr berechnet, welcher Prozentsatz dieser Intervalle tatsächlich vorhanden ist. Das ist einfach eine Transparenzprüfung: "Station 2991 hat 62% von 2021 und 99% von 2024" — nützlicher Kontext.

### Schritt 5 — Mit dem unvollständigen Jahr 2025 umgehen
2025 war noch nicht abgeschlossen, als diese Analyse gemacht wurde. Wenn Station X in der Hälfte von 2025 500'000 Fahrten gezählt hat, können wir das nicht direkt mit 2'000'000 Fahrten für ganze Jahre vergleichen. Die Lösung: **Hochrechnen** — Teiljahres-Summen auf eine Ganzjahres-Schätzung skalieren, basierend auf dem Anteil des Jahres, den wir haben. (500'000 ÷ 50% = 1'000'000 geschätzt.)

### Schritt 6 — Saisoneffekt überprüfen
Veloverkehr ist stark saisonal (viel mehr im Sommer als im Winter). Wenn 2025 nur Jan–März (Winter) abdeckt, würde eine lineare Hochrechnung das echte Jahrestotal *unterschätzen*. Wir haben das monatliche Saisonmuster geplottet und geprüft, ob die abgedeckten Monate von 2025 ausgewogen sind. Wenn nicht, hätten wir 2025 aus der Trendberechnung ausgeschlossen.

### Schritt 7 — Finale Jahrestotale-Tabelle erstellen
Eine saubere Zahl pro Station pro Jahr, bereit für die Analyse.

### Schritt 8 — Jährliche Wachstumsraten berechnen (Year-over-Year)
Einfache Arithmetik: "Dieses Jahr im Vergleich zum letzten Jahr, geht es rauf oder runter, und um welchen Prozentsatz?" Das gab uns einen ersten Bauchgefühls-Check, wer wächst und wer schrumpft.

### Schritt 9 — Trendlinie für jede Station anpassen
Für jede Station haben wir die "beste gerade Linie" durch die Jahrestotale gezogen. Diese Linie gibt uns drei Zahlen:
- **Slope (Steigung)** — wie viele Fahrten die Station pro Jahr gewinnt (oder verliert)
- **R²** — wie gut eine gerade Linie überhaupt zu den Daten passt (näher an 1 = sehr konsistenter Trend; näher an 0 = unregelmässig schwankend)
- **p-Wert** — die Wahrscheinlichkeit, dass der Trend nur zufälliges Rauschen ist (tiefer = vertrauenswürdiger)

### Schritt 10 — Compound Annual Growth Rate (CAGR) und Verdopplungszeit berechnen
Die **CAGR** ist die durchschnittliche jährliche Wachstumsrate mit Berücksichtigung von Zinseszins (so wie bei einem Sparkonto). Aus der CAGR können wir direkt berechnen: "Bei diesem Tempo, wie viele Jahre bis sich der Verkehr verdoppelt?"

Ergebnis: **Keine Station ist auf Kurs, sich innerhalb von 5 Jahren zu verdoppeln.** Der schnellste Wachser (Station 3003, +13.4%/Jahr) würde sich in etwa 5.5 Jahren verdoppeln.

### Schritt 11 — Jede Station mit 5-Jahres-Projektion visualisieren
Ein kleines Diagramm pro Station, das die tatsächlichen Datenpunkte, die Trendlinie und eine gestrichelte Projektion 5 Jahre in die Zukunft zeigt. Wichtiger Vorbehalt: Das ist **keine Prognose** — es ist eine "Was wenn nichts geändert wird?"-Darstellung für Planer.

### Schritt 12 — Alle Stationen rangieren
Zwei Balkendiagramme nebeneinander:
- **Absolutes Wachstum** (wer fügt am meisten Fahrten in Rohzahlen hinzu?)
- **Relatives Wachstum** (wer wächst am schnellsten *prozentual* zum bestehenden Verkehr?)

Die können sich unterscheiden — eine grosse Station, die 2% hinzufügt, kann in absoluten Zahlen mehr Fahrten hinzufügen als eine kleine Station, die 15% wächst.

### Schritt 13 — Auf statistisch belastbare Trends filtern
Nicht jeder Trend ist zuverlässig. Einige Stationen haben schwankende Daten, die zufällig nach oben zeigen. Wir haben sie in drei Kategorien sortiert:
- **Stark** — der Trend ist eindeutig real (3 Stationen: 3003, 4242, 732)
- **Moderat** — ein Trend ist wahrscheinlich vorhanden (2 Stationen: 4249, 2989)
- **Schwach** — zu unregelmässig, um darauf zu vertrauen

### Schritt 14 — Empfehlung an die Stadt formulieren
Wir haben geprüft: Ist das Wachstum auf wenige Strassen konzentriert oder gleichmässig über Zürich verteilt? Antwort: **Die Top 3 wachsenden Stationen machen 80% des gesamten Wachstums aus** — sehr konzentriert. Die praktische Empfehlung: **Präventiv Kapazität an diesen spezifischen Korridoren ausbauen**, anstatt zu versuchen, das gesamte Netz gleichmässig zu verbessern.

### Schritt 15 — Stationen auf Karte darstellen
Wir haben jede Station auf einer Zürich-Karte eingezeichnet. Grüne Kreise = wachsend, rote Kreise = schrumpfend, grössere Kreise = stärkerer Trend. Durch Klick auf eine Station werden alle Statistiken angezeigt. Das ist das Bild, das ein Stadtplaner Entscheidungsträgern vorlegen kann.

### Schritt 16 — Ergebnisse exportieren
Zwei CSV-Dateien gespeichert, damit spätere Notebooks die Wachstumsdaten wiederverwenden können, ohne die ganze Analyse neu zu rechnen.

---

## Fazit

**Bereinigung** hat 6 chaotische Jahresdateien mit gemischten Fussgänger- und Velodaten, defekten Sensoren und inkonsistenter Stationsabdeckung in einen einzigen vertrauenswürdigen Datensatz verwandelt — mit Flags für alles, was wir über Datenqualität wissen müssen.

**Analyse** hat dann gefragt: "Von den 12 Zählern, die wir über den gesamten Zeitraum zuverlässig verfolgen können, welche zeigen echtes Wachstum?" Die Antwort: Drei Stationen (3003, 4242, 732) haben eindeutige, statistisch solide Aufwärtstrends, und sie sind konzentriert genug, dass Zürich dort Kapazität ausbauen sollte — statt Investitionen gleichmässig über die Stadt zu verteilen.
