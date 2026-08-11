# Bitcoin-Whitepaper Erklärt

## Live-URL
https://hofmiker.github.io/altcoin-dashboard/bitcoin-whitepaper-explained/

## Was das ist
Eine originalgetreue Nachbildung des Bitcoin-Whitepapers ("Bitcoin: A
Peer-to-Peer Electronic Cash System", Satoshi Nakamoto, 2008) als
Lese-App: Serifenschrift, Papier-Layout, Blocksatz — wie eine echte
Publikation, kein "Tool-Look". Der komplette Originaltext (32
Absätze/Blöcke über alle 12 Kapitel + Abstract + Referenzen) liegt
zweisprachig vor (eigene deutsche Übersetzung + Original-Englisch,
umschaltbar oben rechts unter "Aa"), inklusive einer eigenen
SVG-Nachbildung der vier mathematischen Original-Formeln aus Kapitel 11
(q_z-Formel, λ-Erwartungswert, Poisson-Summe, umgeformte Summe — als
Vektorgrafik nach den Original-PDF-Seiten 6/7 nachgezeichnet, inkl.
geschweifter Klammern für die Fallunterscheidungen).

Drei Interaktionsebenen:
1. **Text markieren** → kurze Glossar-Definition (Popover) für ca. 40
   kuratierte Fachbegriffe (Hash, Nonce, Proof-of-Work, Merkle Tree, …),
   erkannt in Deutsch und Englisch.
2. **Absatz anklicken** → ausführliche ELI5-Erklärung im Panel rechts
   (auf Mobilgeräten als Bottom-Sheet-Overlay), bei zentralen Konzepten
   mit eigenem SVG-Schaubild (Transaktionskette, Hash-Kette,
   Proof-of-Work-Block, Merkle-Baum, SPV, Transaktions-Ein-/Ausgänge,
   Privacy-Modell).
3. **"Aa"-Einstellungen** oben rechts: Schriftgröße (14–24px, Kindle-
   Paperwhite-artig — größere Schrift lässt Zeilen im festen
   Papier-Spaltenmaß kürzer umbrechen), Hell-/Dunkel-Umschalter
   (Hell ist Standard), Sprachumschalter DE/EN.

Der Originaltext stammt aus dem PDF (`pdftotext -layout`); die
Original-Diagramme wurden NICHT im Dokumentfluss nachgebaut (nur die vier
mathematischen Formeln), um die Textwiedergabe möglichst 1:1 zu halten —
schematische Illustrationen zu den Diagramm-Stellen erscheinen
ausschließlich im Erklärungs-Panel.

## Dateien
- `index.html` — komplette Seite (Dokument-Renderer, Formeln,
  Sprachumschaltung, Glossar-Selection, Klick-Erklärungen, Diagramme,
  Scroll-/Seiten-Tracking), Vanilla JS, kein Build-Schritt
- `vendor/fonts/tinos-*.woff2` — Tinos 5.3.0 (Times-New-Roman-Metrik-
  Klon, Google Fonts/Fontsource), für den Dokumenttext
- `vendor/fonts/space-grotesk-*.woff2` — Space Grotesk 5.3.0, für
  Headlines/UI (technische Alternative zu Monospace)
- `vendor/fonts/inter-*.woff2` — Inter (aus dem Repo-Root übernommen),
  Fließtext der Erklärungs-Ebene und UI-Chrome
- `vendor/fonts/jetbrains-mono-*.woff2` — JetBrains Mono 5.3.0, nur noch
  für Code-Block und mathematische Formel-Legenden
- alle Fonts lokal vendored via `npm pack @fontsource/...` (CDN-Hosts
  sind in der Sandbox-Umgebung per Netzwerk-Policy blockiert,
  npm-Registry aber erreichbar)
- `vendor/icons/*.svg` — ausgewählte Icons aus lucide-static 1.31.0
  (ISC-Lizenz), Pfade als JS-Objekt `ICONS` inline in `index.html`

## Design
- Helles Papier-UI als Standard (warmes Off-White, Tinos-Serife,
  Blocksatz mit Einzug bei Folgeabsätzen), Dunkel-Modus umschaltbar;
  Akzentfarbe Blackberry-Rot (`--accent`, hell `#b3123f` / dunkel
  `#ff4d76`)
- Absätze sind nur dezent hervorgehoben (Hover-Tönung, kein Kasten) und
  tragen im Rand eine schwache "¶NN"-Markierung — bewusst zurückhaltend,
  damit das Dokument wie die echte Publikation wirkt
- Seiten-Indikator oben rechts ("SEITE X / 9") folgt beim Scrollen den
  echten Seitenumbrüchen des 9-seitigen Original-PDFs
- 3-Spalten-Layout ≥1280px (Rail/Dokument/Panel), 2 Spalten 880–1280px,
  Panel wird <880px zum Bottom-Sheet-Overlay

## Tech-Stack
- Vanilla JS/CSS/HTML, kein Build-Schritt, kein Framework
- Keine externen Laufzeit-Requests (Fonts/Icons vendored, keine
  Live-Daten nötig)
- Formeln sind handgezeichnete Inline-SVGs (Bezier-Pfade für die
  geschweiften Klammern, Text-/Tspan-Elemente für Brüche, Exponenten,
  Summenzeichen) — kein MathML/KaTeX, um exakte Kontrolle über Look &
  Feel (Tinos-Schrift, Light/Dark-Farbvariablen) zu behalten

## Thumbnail
`screenshots/bitcoin-whitepaper-explained.png` ist ein echter Screenshot
der App (960×600) im Hell-Modus mit geöffnetem Erklärungs-Panel zu
Kapitel 11 (Gambler's Ruin).
