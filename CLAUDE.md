# Regeln für Claude-Sessions in diesem Verzeichnis (Repo-Root / Landing Page)

Dieses Dokument hält Konventionen fest, die eine einzelne Session sonst
leicht übersieht. Vor Arbeiten an der Landing Page (`index.html`) oder an
`.github/workflows/deploy-pages.yml`: diese Datei lesen. Nach dem
Etablieren einer neuen, wiederholbaren Regel: hier ergänzen.

Die Unterordner (`mvrv-dashboard/`, `btc/`, `bitcoin-3d/`,
`bitcoin-whitepaper-explained/`, `bitcoin-source-code-explained/`) haben
je eigene `CLAUDE.md` mit projektspezifischen Regeln - diese Datei ist nur
für die Landing Page und den gemeinsamen Deploy-Workflow zuständig.

## "Aktualisiert"/"Commits"-Badges: nie nur serverseitig backen

`index.html` zeigt pro Projekt-Kachel `Aktualisiert: {{UPDATED:<ordner>}}`
und `Commits: {{COMMITS:<ordner>}}`. `deploy-pages.yml` ersetzt diese
Platzhalter beim Deploy per `sed` direkt im HTML - das allein reicht
**nicht**, weil ein Browser- oder CDN-Cache danach trotzdem eine alte
Kopie der Seite ausliefern kann, ohne dass irgendetwas auf der Seite
darauf hinweist. Im schlimmsten Fall (nie gestempelte Kopie, z.B. lokaler
Checkout) bleibt sogar der rohe, unbefüllte Platzhalter `{{UPDATED:...}}`
sichtbar.

**Deshalb zusätzlich, nicht ersatzweise:** derselbe Workflow-Schritt
schreibt `project-status.json` (`{"<ordner>":{"updated":"...",
"commits":N}, ...}`) an die Repo-Wurzel. `index.html` lädt diese Datei
beim Seitenaufruf per `fetch(..., {cache:"no-store"})` mit
Zeitstempel-Query nach und überschreibt die Badges live - das umgeht
HTML-Dokument-Caching komplett und zeigt so immer den echten aktuellsten
Deploy-Stand, selbst wenn die umgebende Seite selbst aus einem stale
Cache kam. Schlägt der Fetch fehl, bleibt der eingebackene Text stehen;
war der nie gestempelt (noch `{{...}}` enthalten), wird stattdessen ein
ehrlicher "nicht verfügbar"-Hinweis gezeigt statt des rohen Platzhalters.

Exakt dasselbe Muster (Baustein `deploy-info.json` + `loadDeployInfo()`)
gibt es bereits für den Versions-Stempel `{{VERSION}}`/`{{DEPLOY_DATE}}`
auf jeder Projektseite selbst, siehe z.B.
`mvrv-dashboard/index.html`. Neue Caching-anfällige, server-gebackene
Werte sollten künftig direkt nach diesem Muster gebaut werden, nicht als
reiner `sed`-Stempel ohne Laufzeit-Fallback.

**Beim Hinzufügen einer neuen Projekt-Kachel** in `index.html`:
- `<span class="updated">Aktualisiert: {{UPDATED:<ordner>}}</span>` und
  `<span class="commits">Commits: {{COMMITS:<ordner>}}</span>` wie bei
  den bestehenden Kacheln verwenden - der Workflow erkennt neue Ordner
  automatisch über ein `grep` auf `{{UPDATED:...}}` in `index.html`,
  keine Liste manuell pflegen.
- Das `href` der Kachel (z.B. `href="neuer-ordner/"`) muss exakt dem
  Ordnernamen entsprechen (ohne führenden/anhängenden Slash außer dem
  einen abschließenden) - die Landing-Page-JS leitet den Schlüssel für
  `project-status.json` aus genau diesem `href` ab.
