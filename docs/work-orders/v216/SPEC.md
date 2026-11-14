# V216 spec: Hub H4, share and sync through GitHub

Notion: Later: Hub H4: share and sync. Research: `docs/research/research-notion-hub-h4-sharing.md`, `docs/research/research-bim-hub.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- GitHub as transport only: one canonical JSON file per element by its stable id, plus the project's metadata and a manifest of each element's hash.
- Every push is a non-force update; a rejected push is pulled and compared three ways, never overwritten.
- After any Git merge the app checks its own references (host walls, levels, sources, buildings): a clean text merge that orphans one is a conflict (the research's experiment).
- Opt-in per project; the token is kept by the browser for the session only.

## 2. What it does for the user

Share a project to a GitHub repository; Pull brings others' changes, compares, and shows conflicts and broken references to resolve.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/history/hub-files.js` | new, after `js/engine/history/branches-merge.js` in `src/index.html` (header done) | 5 pure functions (part 5) | Cline, WO-01 to WO-05 |
| `docs/work-orders/v216/v216.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-06, WO-07 |

## 5. Functions, `src/js/engine/history/hub-files.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimHubCanonical(x)`**: JSON with object keys sorted, keys whose value is undefined left out, numbers as String(Number(x.toPrecision(12))), non-finite numbers and null and undefined as null, strings and booleans by JSON.stringify, arrays in order.
- **WO-02 `bimHubHash(s)`**: 32-bit FNV-1a over the string's char codes (offset 0x811c9dc5, prime 16777619, written as the shifts h + (h<<1) + (h<<4) + (h<<7) + (h<<8) + (h<<24), unsigned), as 8 lower-case hex digits.
- **WO-03 `bimHubPath(el)`**: 'elements/' + (bim.type, else t, else 'object') with characters outside A-Z a-z 0-9 _ - as _ + '/' + id with characters outside A-Z a-z 0-9 _ . - as _ + '.json'.
- **WO-04 `bimHubManifest(els, schema)`**: {schema (1 when absent), elements: {id: bimHubHash(bimHubCanonical(element))}} with ids in sorted order.
- **WO-05 `bimHubOrphans(els)`**: for each element, each of hostWallId, levelId, sourceId, buildingId (read from bim, else the element) that is a non-empty string naming no element: {id, field, missing}.

## 6. Order of the work

WO-01 to WO-05 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-06** push, pull and the three-way view; **WO-07** the records.

## 7. Not in this phase

Per-element permissions (v217); hosts other than github; binary assets over a size limit.
