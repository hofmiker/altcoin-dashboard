# Bitcoin-Whitepaper Erklärt

## Live-URL
https://hofmiker.github.io/altcoin-dashboard/bitcoin-whitepaper-explained/

## Was das ist
Das komplette Original-Bitcoin-Whitepaper ("Bitcoin: A Peer-to-Peer
Electronic Cash System", Satoshi Nakamoto, 2008) als durchgehend
scrollbares Dokument (wie in einem PDF-Reader). Jeder Absatz ist als
eigener, dezent umrahmter Block gerendert und anklickbar. Ein Klick öffnet
rechts (auf Mobilgeräten als Bottom-Sheet-Overlay) eine leicht
verständliche deutsche Erklärung des Absatzes, bei den technisch
zentralen Stellen ergänzt um ein selbstgezeichnetes SVG-Schaubild
(Transaktionskette, Hash-Kette, Proof-of-Work-Block, Merkle-Baum, SPV,
Transaktions-Ein-/Ausgänge, Privacy-Modell).

Der Originaltext (31 Absätze/Blöcke über alle 12 Kapitel + Abstract +
Referenzen) stammt direkt aus dem PDF (`pdftotext -layout`) und wurde
1:1 übernommen; nur die stark verzerrten ASCII-Diagramme aus der
PDF-Extraktion wurden durch saubere, eigene SVG-Schaubilder ersetzt.

## Dateien
- `index.html` — komplette Seite (Dokument-Renderer, Klick-Erklärungen,
  Diagramme, Scroll-/Seiten-Tracking), Vanilla JS, kein Build-Schritt
- `vendor/fonts/jetbrains-mono-*.woff2` — JetBrains Mono 5.3.0, lokal
  vendored via `npm pack @fontsource/jetbrains-mono` (CDN-Hosts sind in
  der Sandbox-Umgebung per Netzwerk-Policy blockiert, npm-Registry aber
  erreichbar)
- `vendor/icons/*.svg` — ausgewählte Icons aus lucide-static 1.31.0
  (ISC-Lizenz), lokal vendored via `npm pack lucide-static`; die
  Icon-Pfade sind als JS-Objekt `ICONS` direkt in `index.html` inline
  eingebettet (kein Laufzeit-Fetch nötig)

## Design
- Reines Schwarz/Weiß-UI mit Blackberry-/Rot-Akzenten (`--accent:#e2244f`)
- Durchgängig JetBrains Mono (monospace) — bewusst "toolig"/IDE-artig:
  linke Navigations-Rail (wie ein Datei-Baum), mittig das Dokument (wie
  ein Editor) mit Absatznummern als "Zeilennummern" (¶01…¶31), rechts ein
  Inspector-Panel
- Seiten-Indikator oben rechts ("SEITE X / 9") folgt beim Scrollen den
  echten Seitenumbrüchen des 9-seitigen Original-PDFs
- 3-Spalten-Layout ≥1280px, 2 Spalten 880–1280px, Panel wird <880px zum
  Bottom-Sheet-Overlay

## Tech-Stack
- Vanilla JS/CSS/HTML, kein Build-Schritt, kein Framework
- Keine externen Laufzeit-Requests (Fonts/Icons sind vendored, keine
  Live-Daten nötig)

## Thumbnail
`screenshots/bitcoin-whitepaper-explained.png` ist ein echter Screenshot
der App (960×600) mit geöffnetem Erklärungs-Panel zu Kapitel 2.
