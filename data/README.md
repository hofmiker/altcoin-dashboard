# Scan-Datenbank

Dieser Ordner ist das historische Archiv aller täglichen Pump-Signal-Scans. Er wird von der
Routine "Täglicher Krypto Pump-Scanner" bei jedem Lauf um einen Eintrag erweitert und ist
**nicht** Teil der veröffentlichten GitHub-Pages-Seite (siehe `.github/workflows/deploy-pages.yml`,
der Build-Schritt schließt `data/` explizit aus dem Artefakt aus).

## Struktur

- `index.json` — Liste aller vorhandenen Scan-Daten (chronologisch), verweist auf die jeweilige Datei in `scans/` und trägt die zu diesem Lauf gehörige `version`.
- `scans/<YYYY-MM-DD>.json` — vollständiger Snapshot eines Scans an diesem Datum:
  - `date`: Datum des Scans (YYYY-MM-DD)
  - `version`: fortlaufende Versionsnummer des Dashboards (siehe unten)
  - `generatedAt`: ISO-Zeitstempel der Erstellung
  - `market`: Markt-Strip-Werte (Bitcoin-Preisspanne, Altcoin Season Index, BTC-Dominanz)
  - `coins`: vollständiges Coins-Array wie in `index.html` an diesem Tag veröffentlicht
  - `sources`: an diesem Tag zitierte Quellen (Fußnoten)

Jeder Lauf legt eine neue Datei an (bestehende Tage werden nicht überschrieben), sodass sich
über die Zeit eine durchsuchbare Historie aller Kandidaten, Scores und Marktkontexte ergibt.

## Versionsnummer

`index.html` zeigt in der Subline neben dem Datum eine Versionsnummer (`DASHBOARD_VERSION`-Konstante
im `<script>`-Block, z. B. "v3"). Sie wird bei jedem inhaltlichen Dashboard-Update um 1 erhöht — sowohl
bei manuellen Änderungen als auch bei jedem Lauf der Scan-Routine. Der aktuelle Stand steht immer im
`version`-Feld des jeweils neuesten Eintrags in `index.json`; die Routine liest ihn dort aus, zählt 1
hoch und trägt den neuen Wert sowohl in `index.html` (`DASHBOARD_VERSION`, sichtbare Subline) als auch
im neuen `scans/<Datum>.json`-Eintrag ein.
