# Regeln für Claude-Sessions in diesem Verzeichnis

Dieses Dokument hält Konventionen fest, die eine einzelne Session sonst
leicht erfindet, ohne sie zu prüfen - und die dabei objektiv falsch sein
können (siehe Edit-Version unten). Vor Arbeiten an `index.html`: diese
Datei lesen. Nach dem Etablieren einer neuen, wiederholbaren Regel: hier
ergänzen.

## Edit-Version im Info-Popover

`index.html` enthält nahe des Scriptanfangs:

```js
const EDIT_VERSION = "v214";
const EDIT_STAMP = "2026-08-20 19:46 UTC";
```

Angezeigt im Header-Info-Popover als "Bearbeitungsstand". Zweck: dem
Nutzer unabhängig vom GitHub-Pages-Deploy-Stand (`deploy-info.json`,
siehe `loadDeployInfo()`) zeigen, welcher Bearbeitungsstand tatsächlich
im Quelltext steckt - auch direkt nach einem Push, bevor Pages neu
gebaut hat.

**Falsch gemacht in einer früheren Session:** `EDIT_VERSION` einfach bei
1 begonnen und pro eigener Session hochgezählt ("v1", "v2", "v3", ...) -
das ist eine reine Erfindung ohne Bezug zur echten Historie und nach nur
drei Bearbeitungen bereits sichtbar absurd, da das Repo zu dem Zeitpunkt
schon über 200 echte Commits hatte.

**Richtig:** die Zahl muss aus der echten Commit-Historie kommen, nicht
aus einem Session-lokalen Zähler.

```bash
git rev-list --count HEAD
```

liefert die Anzahl Commits bis zum aktuellen `HEAD` (also *ohne* den
Commit, der gerade erst erstellt wird). Da dieser eigene Commit die
Historie um genau 1 verlängert, ist der korrekte Wert für
`EDIT_VERSION`:

```
"v" + (git rev-list --count HEAD) + 1
```

Beispiel: `git rev-list --count HEAD` liefert `213` → `EDIT_VERSION =
"v214"`, weil der gleich folgende Commit selbst die Nummer 214 sein
wird. `EDIT_STAMP` ist die aktuelle UTC-Zeit (`date -u "+%Y-%m-%d %H:%M
UTC"`), nicht ein geschätzter oder erfundener Zeitpunkt.

Beides bei **jedem** Edit, der committet wird, neu berechnen und
aktualisieren - nicht nur gelegentlich, und nicht per Kopfrechnung.

## Ship-Workflow

Etablierter Ablauf für's Live-Schalten eines Batches (mehrfach in dieser
Session verwendet, vom Nutzer bestätigt):

1. `git add`/`git commit` mit aussagekräftiger Message (Warum, nicht nur
   Was).
2. `git push -u origin claude/<branch-name>`
3. `mcp__github__create_pull_request` gegen `main`
4. `mcp__github__merge_pull_request` mit `merge_method:"squash"`
5. Branch resyncen, damit die nächste Session/der nächste Batch auf dem
   echten `main`-Stand aufsetzt:
   ```bash
   git fetch origin main && git reset --hard origin/main \
     && git push --force-with-lease origin claude/<branch-name>
   ```

Der Nutzer kann eine Zwischenversion nicht bewerten, solange sie nur auf
dem Feature-Branch liegt - bei ausdrücklichem Wunsch ("push auf main,
sonst kann ich es nicht bewerten") direkt mergen, nicht auf den
Abschluss des ganzen Batches warten.

## Testen vor dem Ship

- Lokaler Server: `python3 -m http.server 8791` im Verzeichnis
  `mvrv-dashboard`.
- Playwright-Tests routen `community-api.coinmetrics.io` → 403 und
  `raw.githubusercontent.com` → 200 mit `real_snapshot.json`, um
  deterministisch den echten Snapshot-Fallback-Pfad zu erzwingen (siehe
  vorhandene `test_*.js`-Skripte im Scratchpad-Verzeichnis als Vorlage).
- Nach jeder Änderung an gemeinsam genutztem Code (`buildLineChart`,
  `animateMatrix`, `computeZoomMatrix` usw.) die bestehende
  Regressionssuite laufen lassen, nicht nur den unmittelbar betroffenen
  Chart - mehrere Charts teilen sich dieselbe Zoom-/Crosshair-Maschinerie.

## Qualitätskontrolle vor jedem Ship (Pflicht)

**Anlass:** PR #242 (Fullscreen-Buttons für den Marktzyklen-Chart) hat mit
"0 Konsolenfehler" getestet gemerged, war aber trotzdem kaputt - die neuen
Buttons haben ihr eigenes kleines Icon-`<svg>` vor das echte Chart-`<svg>`
gesetzt, wodurch mehrere ungezielte `"#cycleChartPanel svg"`-Abfragen ab
sofort das Icon-SVG statt des Charts trafen. Die Log/Linear-Achsen-
Animation lief dadurch komplett leer (keine Elemente gefunden, aber auch
kein Fehler geworfen), der Chart sprang beim Umschalten nur noch sofort in
den Endzustand. Das ist erst dem Nutzer aufgefallen, nicht mir - das darf
nicht nochmal passieren.

**Kernlektion:** "Keine Konsolenfehler" beweist nur Abwesenheit von
Crashes, nicht Korrektheit. Ein Selector, der das falsche (aber
existierende) Element trifft, wirft nie einen Fehler - er liefert einfach
ein leeres/falsches Ergebnis. Genau solche Bugs sind es, die durchrutschen,
wenn nur auf `pageerrors.length === 0` geprüft wird.

Deshalb vor **jedem** Merge an `index.html`, nicht nur für das gerade
gebaute Feature:

1. **DOM-Struktur-Diff prüfen**, sobald Elemente in einem bestehenden Panel
   neu hinzugefügt, entfernt oder umsortiert wurden:
   `grep -n "#<panelId>" index.html` laufen lassen und **jeden Treffer
   einzeln** durchgehen - trifft ein dortiger `querySelector`/
   `querySelectorAll` nach der Änderung noch das ursprünglich gemeinte
   Element (DOM-Reihenfolge!), oder jetzt versehentlich ein neu
   eingefügtes? Ein unscoped `"#panel svg"`/`"#panel button"` usw. ist ein
   Alarmsignal, sobald das Panel mehr als ein Element dieser Art enthält -
   im Zweifel auf einen spezifischeren Vorfahren scopen (Vorbild: das
   bereits vorhandene `"#cycleChartPanel .chart-wrap svg"`).
2. **Verhalten testen, nicht nur Fehlerfreiheit**: für jede berührte
   Animation/Interaktion eine echte Zustands-Assertion schreiben (z. B.
   `path.getAttribute("d")`, eine Transform-Matrix, eine Bounding-Box) -
   nie nur `pageerrors.length === 0` als alleinigen Erfolgsnachweis werten.
3. **Zwischenzustände sampeln, nicht nur Vorher/Nachher**: bei jeder
   Animation mindestens zwei Frames *mitten* in der Transition abgreifen
   und prüfen, dass sich der Wert zwischen den Frames tatsächlich ändert
   (`mid !== start` UND `mid !== end`). Ein Bug, der die Animation komplett
   leerlaufen lässt, ist an Start-/Endzustand allein unsichtbar, weil die
   sofortige DOM-Neuerstellung (`renderCycleChart()` o. ä.) diese ohnehin
   schon korrekt liefert.
4. **Volle Regressions-Checkliste** für jeden Chart, der von der Änderung
   betroffen sein könnte (siehe unten) - nicht nur das eine angeforderte
   Feature isoliert testen.
5. Erst nach 1.-4. den Ship-Workflow starten. Bei einem gefundenen Problem:
   fixen, Checkliste erneut komplett durchlaufen, nicht nur den einen
   reparierten Punkt.

### Regressions-Checkliste Marktzyklen-Chart

Bei jeder Änderung an `index.html`, die diesen Chart selbst oder
gemeinsam genutzten Code (`buildLineChart`, `animateMatrix`,
`computeZoomMatrix`, `fitChartTypography` usw.) berührt:

- [ ] Log/Linear-Toggle (X- und Y-Achse einzeln): Preislinie interpoliert
      sichtbar über ≥2 Zwischenframes
- [ ] Range-Wechsel rein-zoomen (z. B. 10J → 1J): Zwischenframe zeigt eine
      echte Nicht-Identitäts-Matrix auf `.cyc-zoom-group`
- [ ] Range-Wechsel raus-zoomen (z. B. 1J → 10J)
- [ ] 2-Finger-Pan auf mobil (inkrementelle `touchmove`-Schritte, kein
      einzelner großer Sprung - reproduziert zuverlässiger)
- [ ] Doppeltipp zoomt zur angetippten Stelle, nicht immer zu "heute"
- [ ] "Zurück zu heute"-Button
- [ ] Zyklus-/Kurs-Toggle
- [ ] Fullscreen enter/exit, mehrfach hintereinander, inkl. Escape-Taste
- [ ] Ein Rebuild *während* Fullscreen auslösen (z. B. Zyklus-Toggle
      klicken während offen) - Buttons danach immer noch klickbar?
- [ ] `grep -n "#cycleChartPanel" index.html` durchgesehen - kein neu
      eingefügtes Element steht vor einem bestehenden ungezielten Selector
- [ ] Screenshots Desktop/Dark/Mobile geprüft, nicht nur Konsole

## Methodik-Sektion aktuell halten

`index.html` hat unten auf der Seite ein `<details id="detailsPanel">` mit
der Überschrift "Methodik, Formeln & Datenquelle" - erklärt in normaler
Prosa, wie jede Kennzahl/jeder Chart berechnet wird (Formeln, Schwellenwerte,
Datenquelle). Bei **jeder** inhaltlichen Änderung, die diesen Text
veraltet oder unvollständig macht, muss er im selben Batch mit-aktualisiert
werden - nicht als separater Nachtrag später:

- eine neue Kachel/ein neues Chart hinzugefügt
- eine bestehende Berechnung/Schwelle geändert (Beispiel: der
  75-%-Schwellenwert für bestätigte Zyklus-Hochs/-Tiefs bei Marktzyklen)
- eine Datenquelle oder ihr Abruf-Mechanismus geändert

Stil: kurzer, fetter Begriff gefolgt von einem prägnanten Erklärsatz,
gleiche Tonlage wie die vorhandenen Absätze (siehe `<b>MVRV</b>`,
`<b>NUPL</b>` usw. als Vorlage) - keine Marketingsprache, keine
Wiederholung dessen, was der Chart selbst schon zeigt.

## Sonstiges

- Farbentscheidungen (z. B. `--bitcoin-accent`) nie direkt festlegen,
  wenn der Nutzer "zeig mir Varianten" sagt - erst mehrere
  Screenshot-Varianten liefern, dann auf explizite Auswahl warten.
- Bei Unklarheiten über eine frühere Design-Entscheidung: den
  Git-Verlauf/PR-Historie tatsächlich nachschlagen (`git log`, GitHub),
  nicht raten oder aus dem Session-Gedächtnis rekonstruieren - das
  Session-Gedächtnis kann durch Kompaktierung lückenhaft sein, die
  Historie nicht.
