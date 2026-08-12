# Bitcoin: Der Quellcode erklärt

## Live-URL
https://hofmiker.github.io/altcoin-dashboard/bitcoin-source-code-explained/

## Was das ist
Ein Schwesterprojekt zu `bitcoin-whitepaper-explained`: statt des
Whitepaper-Texts steht hier der **allererste veröffentlichte
Bitcoin-Quellcode** (v0.1.0, von Satoshi Nakamoto am 8. Januar 2009 über
die Cryptography-Mailingliste und SourceForge verteilt) im Zentrum,
links im Original-Wortlaut mit Syntax-Highlighting, rechts Absatz für
Absatz (hier: Codeblock für Codeblock) in einfachen Worten erklärt —
gleiches Interaktionsmuster wie beim Whitepaper (Klick auf einen
Codeblock öffnet rechts die Erklärung, teils mit eigenem SVG-Schaubild),
nur mit Code statt Fließtext links.

**Bewusst als Testausschnitt gebaut** (User-Anfrage: "Nutze erstmal
einen kleinen Ausschnitt zu Test"): aufbereitet ist aktuell nur eine
Funktion, `CBlock::CheckBlock()` (main.cpp, Zeilen 1154–1190) — die
Torwächter-Prüfung, die jeder neue Block bestehen muss. Die Rail links
listet fünf weitere Kandidatenfunktionen (`BuildMerkleTree()`,
`BitcoinMiner()`, `CheckTransaction()`, `ConnectInputs()`,
`AddToWallet()`) als deaktivierte "bald"-Einträge — das Grundgerüst
(Tokenizer, Regionen-System, Panel) ist bereits generisch genug, um sie
später einfach als weitere Einträge in `CODE_LINES`/`REGIONS`
nachzutragen.

Der Coverage-Kasten unter dem Code beantwortet explizit die Frage "wie
viel vom Original-Code lässt sich so aufbereiten": von den 2.660 Zeilen
in `main.cpp` sind grob ~18 % gut visualisierbare Kernalgorithmen
(Blockprüfung, Merkle-Baum, Mining-Schleife, Transaktionsprüfung,
Coinbase-Reward), ~27 % erklärbare, aber eher Ablauf- als
Konzept-Logik (Wallet-Scan, Netzwerk-Sync, IRC-Peer-Discovery), und
~55 % Plumbing ohne Whitepaper-Bezug (die Windows-GUI in `ui.cpp`/
`uibase.cpp`, Datenbank-Boilerplate, Serialisierung).

## Quelle des Codes
`bitcoin0.1/src/main.cpp` aus dem Community-Archiv
[0xMagnuz/Bitcoin-v0.1](https://github.com/0xMagnuz/Bitcoin-v0.1) — kein
offizielles Bitcoin-Repo (das gibt es für v0.1.0 nicht mehr; Satoshis
Original-Archiv wurde 2009 auf SourceForge verteilt, lange bevor
`bitcoin/bitcoin` auf GitHub entstand). Das Archiv dokumentiert seine
Herkunft mit MD5-Hashes und Link zur echten Mailinglisten-Ankündigung
vom 8. Januar 2009. Der eingebettete Codeausschnitt ist wortwörtlich
übernommen (nur CRLF→LF normalisiert); Farben, Formatierung, Gliederung
in Regionen und alle Erklärtexte/Diagramme sind eigene Ergänzung.

Zur Einordnung (steht auch so im UI): Der von `bitcoin/bitcoin` auf
GitHub bekannte Git-Verlauf beginnt selbst erst mit einem Import vom
30. August 2009 — Monate nach dem echten v0.1.0-Release. Für den "echten
ersten Code" muss man auf genau solche Community-Archive der
ursprünglichen SourceForge-Distribution zurückgreifen.

## Vier Interaktionsebenen (analog zum Whitepaper-Projekt)
1. **Codeblock anklicken** → Erklärung im Panel rechts (Mobile:
   Bottom-Sheet-Overlay), bei den zwei konzeptionell wichtigsten Blöcken
   (Proof-of-Work-Prüfung, Merkle-Root-Gegenprüfung) mit eigenem
   farbig-illustrativem SVG-Schaubild.
2. **Whitepaper-Link** im Panel: jede Erklärung verlinkt auf
   `../bitcoin-whitepaper-explained/`, um die Code-Ebene mit der
   Konzept-Ebene zu verknüpfen.
3. **"Aa"-Button**: nur Textgröße (13–22px, skaliert Code und
   Erklärtext proportional mit). Kein Sprachumschalter — der Code selbst
   bleibt englisch (Original), nur die Erklärungen sind Deutsch.
4. **Design bleibt bewusst fix dunkel für den Code** — das Editor-Panel
   sieht immer wie ein dunkles IDE-Theme aus (VS-Code-Dark+-artige
   Token-Farben: lila Keywords, grün Strings, gedämpftes Grau für
   Kommentare), unabhängig vom Hell-/Dunkel-Toggle der restlichen Seite
   (Chrome/Panel folgen dem Toggle, der Code-Block nicht) — genau das
   vom User referenzierte Screenshot-Aussehen.

## Dateien
- `index.html` — komplette Seite (Tokenizer, Code-Renderer,
  Regionen-/Panel-Logik, Diagramme, Einstellungen), Vanilla JS, kein
  Build-Schritt
- `vendor/fonts/jetbrains-mono-*.woff2` — Code-Schrift
- `vendor/fonts/space-grotesk-*.woff2` — Headlines/UI
- `vendor/fonts/inter-*.woff2` — Erklärtext/UI-Chrome
  (alle drei 1:1 aus `bitcoin-whitepaper-explained/vendor/fonts/`
  übernommen, jedes Projekt bleibt selbstständig/self-contained)

## Tech-Stack
- Vanilla JS/CSS/HTML, kein Build-Schritt, kein Framework
- Eigener, kleiner Regex-Tokenizer für C++-Syntax-Highlighting
  (`highlightCpp()`): Kommentar/String/Zahl/Keyword/Type/Funktionsaufruf/
  Bezeichner als eine Alternation, ein Durchlauf pro Zeile — keine
  externe Highlighting-Bibliothek nötig für diesen begrenzten Anwendungsfall
- Diagramme sind handgezeichnete Inline-SVGs im gleichen Stil wie beim
  Whitepaper-Projekt (`DIAGRAMS`-Objekt, CSS-Variablen für Farbe)

## Thumbnail
`screenshots/bitcoin-source-code-explained.png`: 1440×900-Screenshot
(auf 960×600 zugeschnitten/skaliert) im Dunkel-Modus mit ausgewählter
Proof-of-Work-Region — zeigt Code links, Erklärung + Diagramm rechts.
