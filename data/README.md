# Scan-Datenbank

Dieser Ordner ist das historische Archiv aller täglichen Pump-Signal-Scans. Er wird von der
Routine "Täglicher Krypto Pump-Scanner" bei jedem Lauf um einen Eintrag erweitert und ist
**nicht** Teil der veröffentlichten GitHub-Pages-Seite (siehe `.github/workflows/deploy-pages.yml`,
der Build-Schritt schließt `data/` explizit aus dem Artefakt aus).

## Struktur

- `index.json` — Liste aller vorhandenen Scan-Daten (chronologisch), verweist auf die jeweilige Datei in `scans/` und trägt die zu diesem Lauf gehörige `version`.
- `scans/<YYYY-MM-DD>.json` — vollständiger Snapshot des **gesamten Watchlist-Stands** nach dem Lauf an diesem Datum (nicht nur die an diesem Tag neu gefundenen Kandidaten — siehe unten):
  - `date`: Datum des Scans (YYYY-MM-DD)
  - `version`: fortlaufende Versionsnummer des Dashboards (siehe unten)
  - `generatedAt`: ISO-Zeitstempel der Erstellung
  - `market`: Markt-Strip-Werte (Bitcoin-Preisspanne, Altcoin Season Index, BTC-Dominanz)
  - `coins`: vollständiges Coins-Array wie in `index.html` nach diesem Lauf veröffentlicht
  - `sources`: an diesem Tag zitierte Quellen (Fußnoten)

Jeder Lauf legt eine neue Datei an (bestehende Tage werden nicht überschrieben), sodass sich
über die Zeit eine durchsuchbare Historie ergibt, wie sich die Watchlist Tag für Tag entwickelt hat.

## Rolling Watchlist (seit 08.07.2026)

`index.html` zeigt keine reine Tages-Momentaufnahme mehr, sondern eine **akkumulierende Watchlist**:
Bestehende Kandidaten bleiben über mehrere Tage sichtbar, statt bei jedem Lauf komplett ersetzt zu
werden — das Ziel ist, keine potenziellen Pumps zu verpassen, nur weil ein Coin nicht am selben Tag
neu gescreent wurde. Konkret:

- Die Routine **ergänzt** das `coins`-Array um neue Funde, statt es zu ersetzen. Bereits vorhandene
  Ticker werden bei erneutem Auftauchen aktualisiert (Score, Stats, Signale, Chart-Daten), nicht dupliziert.
- Bestehende Einträge bleiben erhalten, auch wenn sie an einem Tag nicht erneut recherchiert wurden.
  Entfernt wird ein Coin nur, wenn er eindeutig invalidiert ist (z. B. bestätigter Scam, Delisting,
  oder die Chance ist offensichtlich vorbei) — nicht einfach wegen Alters.
- Die Anzeige (Kacheln + Tabelle) sortiert automatisch client-seitig nach Score absteigend — die
  vielversprechendsten Kandidaten stehen also immer oben, unabhängig von der Reihenfolge im Array.
- Sanfte Obergrenze: Wächst die Liste über ~20 Einträge, sollen die am niedrigsten bewerteten zuerst
  entfernt werden (sie stünden ohnehin ganz unten). Das ist ein Praktikabilitäts-Kompromiss, kein
  Alters-Cutoff — bei Bedarf anpassbar.
- Neu hinzugefügte Coins bekommen ein `firstSeen`-Feld (Format "TT.MM.JJJJ", z. B. "08.07.2026"),
  angezeigt als "Auf der Liste seit …" unter dem Namen. Bei bereits vorhandenen Coins bleibt
  `firstSeen` unverändert, auch wenn ihre Daten aktualisiert werden.

## Versionsnummer

`index.html` zeigt in der Subline neben dem Datum eine Versionsnummer (`DASHBOARD_VERSION`-Konstante
im `<script>`-Block, z. B. "v3"). Sie wird bei jedem inhaltlichen Dashboard-Update um 1 erhöht — sowohl
bei manuellen Änderungen als auch bei jedem Lauf der Scan-Routine. Der aktuelle Stand steht immer im
`version`-Feld des jeweils neuesten Eintrags in `index.json`; die Routine liest ihn dort aus, zählt 1
hoch und trägt den neuen Wert sowohl in `index.html` (`DASHBOARD_VERSION`, sichtbare Subline) als auch
im neuen `scans/<Datum>.json`-Eintrag ein.
