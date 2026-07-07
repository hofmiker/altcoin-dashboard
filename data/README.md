# Scan-Datenbank

Dieser Ordner ist das historische Archiv aller täglichen Pump-Signal-Scans. Er wird von der
Routine "Täglicher Krypto Pump-Scanner" bei jedem Lauf um einen Eintrag erweitert und ist
**nicht** Teil der veröffentlichten GitHub-Pages-Seite (siehe `.github/workflows/deploy-pages.yml`,
der Build-Schritt schließt `data/` explizit aus dem Artefakt aus).

## Struktur

- `index.json` — Liste aller vorhandenen Scan-Daten (chronologisch), verweist auf die jeweilige Datei in `scans/`.
- `scans/<YYYY-MM-DD>.json` — vollständiger Snapshot eines Scans an diesem Datum:
  - `date`: Datum des Scans (YYYY-MM-DD)
  - `generatedAt`: ISO-Zeitstempel der Erstellung
  - `market`: Markt-Strip-Werte (Bitcoin-Preisspanne, Altcoin Season Index, BTC-Dominanz)
  - `coins`: vollständiges Coins-Array wie in `index.html` an diesem Tag veröffentlicht
  - `sources`: an diesem Tag zitierte Quellen (Fußnoten)

Jeder Lauf legt eine neue Datei an (bestehende Tage werden nicht überschrieben), sodass sich
über die Zeit eine durchsuchbare Historie aller Kandidaten, Scores und Marktkontexte ergibt.
