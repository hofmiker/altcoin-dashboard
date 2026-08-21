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
