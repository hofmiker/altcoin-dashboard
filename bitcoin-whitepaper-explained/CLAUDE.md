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
umschaltbar oben rechts), inklusive eigener SVG-Nachbildungen aller
Original-Abbildungen aus dem PDF, direkt im Dokumentfluss an derselben
Stelle wie im Original: die vier mathematischen Formeln aus Kapitel 11
(q_z-Formel, λ-Erwartungswert, Poisson-Summe, umgeformte Summe — nach
den Original-PDF-Seiten 6/7 nachgezeichnet) sowie die sieben
Original-Diagramme aus den Kapiteln 2–10 (Transaktionskette,
Zeitstempel-Kette, Block mit Prev-Hash/Nonce, Merkle-Baum vor/nach
Pruning, SPV/Merkle-Zweig, Transaktion mit mehreren Ein-/Ausgängen,
Privacy-Modell), pixelgenau nach den Original-PDF-Seiten 2–6
nachgebaut und mit italic-Bildunterschrift versehen wie eine echte
Publikations-Abbildung. Der einzige Monospace-Einsatz im Original — der
C-Code-Block in Kapitel 11 — ist entsprechend auch hier in JetBrains
Mono gesetzt; der restliche Fließtext bleibt durchgängig Serife.

Vier Interaktionsebenen:
1. **Text markieren** → kurze Glossar-Definition (Popover) für ca. 40
   kuratierte Fachbegriffe (Hash, Nonce, Proof-of-Work, Merkle Tree, …),
   erkannt in Deutsch und Englisch.
2. **Absatz anklicken** → ausführliche ELI5-Erklärung im Panel rechts
   (auf Mobilgeräten als Bottom-Sheet-Overlay), bei zentralen Konzepten
   mit eigenem, farbig-illustrativem SVG-Schaubild (Transaktionskette,
   Hash-Kette, Proof-of-Work-Block, Merkle-Baum, SPV, Transaktions-Ein-/
   Ausgänge, Privacy-Modell, Netzwerk-Knoten/Broadcast, Blockchain-
   Gabelung/längste-Kette-gewinnt) — bewusst separat von den
   originalgetreuen Diagrammen im Dokument links: dort schwarz-weiß wie
   im PDF, hier farbig vereinfacht zum Verstehen. Jedes Schaubild ist
   anklickbar und öffnet vergrößert in einer Lightbox (Marker-IDs werden
   beim Klonen umbenannt, um SVG-`<marker>`-Kollisionen mit dem
   Panel-Original zu vermeiden).
3. **Interaktive Graphen** bei den Kapitel-11-Formeln: Kapitel „Gambler's
   Ruin" (q_z) und „Warum sich mehrere Bestätigungen lohnen" zeigen je
   einen live berechneten Graphen (echte JS-Portierung der
   `AttackerSuccessProbability`-C-Funktion bzw. der einfachen
   q_z=(q/p)^z-Formel) mit Schieberegler für den Angreifer-Rechenanteil
   q; Kurve, Marker bei z=6 und Live-Ablesewert aktualisieren sich sofort.
4. **"Aa"-Button** oben rechts: nur Schriftgröße (14–24px, Kindle-
   Paperwhite-artig — größere Schrift lässt Zeilen im festen
   Papier-Spaltenmaß kürzer umbrechen) und Hell-/Dunkel-Umschalter
   (Hell ist Standard). Der Sprachumschalter DE/EN ist ein eigener
   Segmented-Button direkt daneben in der Top-Bar, bewusst nicht im
   "Aa"-Formatierungs-Popup.

Der Originaltext stammt aus dem PDF (`pdftotext -layout`); die sieben
Original-Diagramme wurden anhand hochaufgelöster Renderings der
PDF-Seiten (`pdftoppm`) koordinatengenau als eigenständiges
`ORIG_DIAGRAMS`-Objekt nachgebaut (eigene Icon-/Box-/Pfeil-Grammatik
`.od`, ausschließlich CSS-Variablen für Farbe, damit Hell-/Dunkelmodus
funktionieren) und werden im Dokument direkt nach dem jeweiligen Absatz
gerendert (`item.origDiagram`), mit kursiver Bildunterschrift wie eine
echte Publikationsabbildung — unabhängig von den farbigen
Illustrationen im Erklärungs-Panel (`item.diagram`, aus dem separaten
`DIAGRAMS`-Objekt). Die Bedienungsanleitung ("So funktionierts") lebt
bewusst nicht im Dokument, sondern als Standardinhalt des leeren Panels
rechts, weil sie im Original nicht vorkommt. Zitatmarker wie `[1]` oder
`[7][2][5]` im Fließtext sind anklickbar und springen mit
Flash-Highlight zur Quellenliste am Ende.

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
- Im Dunkelmodus vier klar gestufte Flächen-Ebenen (`--bg` dunkelster
  Seitenhintergrund → `--surface` Top-Bar/Rail/Panel → `--paper-bg`
  Papier-Karte, deutlich heller, damit sie als eigene Ebene abhebt →
  `--surface-raised` für Chips/Boxen obendrauf), statt vorher fast
  gleich dunkler Flächen ohne erkennbare Hierarchie
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
der App (960×600) im Hell-Modus: links das Original-Diagramm zu Kapitel 7
(Merkle-Baum) im Dokumentfluss, rechts das geöffnete Erklärungs-Panel.
