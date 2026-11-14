# V216 work orders: Hub H4, share and sync through GitHub

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/history/hub-files.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v216/v216.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v216/v216.test.mjs
    node --check src/js/engine/history/hub-files.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimHubCanonical(x)`

- **It must:** SPEC 5 WO-01: JSON with object keys sorted, keys whose value is undefined left out, numbers as String(Number(x.toPrecision(12))), non-finite numbers and null and undefined as null, strings and booleans by JSON.stringify, arrays in order.
- **May use:** nothing.
- **Files:** `src/js/engine/history/hub-files.js`, `docs/work-orders/v216/v216.test.mjs`
- **Budget:** 50
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v216/v216.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimHubHash(s)`

- **It must:** SPEC 5 WO-02: 32-bit FNV-1a over the string's char codes (offset 0x811c9dc5, prime 16777619, written as the shifts h + (h<<1) + (h<<4) + (h<<7) + (h<<8) + (h<<24), unsigned), as 8 lower-case hex digits.
- **May use:** nothing.
- **Files:** `src/js/engine/history/hub-files.js`, `docs/work-orders/v216/v216.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v216/v216.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimHubPath(el)`

- **It must:** SPEC 5 WO-03: 'elements/' + (bim.type, else t, else 'object') with characters outside A-Z a-z 0-9 _ - as _ + '/' + id with characters outside A-Z a-z 0-9 _ . - as _ + '.json'.
- **May use:** nothing.
- **Files:** `src/js/engine/history/hub-files.js`, `docs/work-orders/v216/v216.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v216/v216.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimHubManifest(els, schema)`

- **It must:** SPEC 5 WO-04: {schema (1 when absent), elements: {id: bimHubHash(bimHubCanonical(element))}} with ids in sorted order.
- **May use:** bimHubCanonical (WO-01), bimHubHash (WO-02).
- **Files:** `src/js/engine/history/hub-files.js`, `docs/work-orders/v216/v216.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v216/v216.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimHubOrphans(els)`

- **It must:** SPEC 5 WO-05: for each element, each of hostWallId, levelId, sourceId, buildingId (read from bim, else the element) that is a non-empty string naming no element: {id, field, missing}.
- **May use:** nothing.
- **Files:** `src/js/engine/history/hub-files.js`, `docs/work-orders/v216/v216.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v216/v216.test.mjs`. **Score:** 0.

---

## [ ] WO-06 [Claude] Push, Pull and the three-way view

Claude's: the GitHub contents API through a token kept for the session, the files and manifest written and read, non-force updates, the three-way comparison with H1's history, orphans shown as conflicts. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-07 [Claude] The records

PIPELINE row 216, Notion.
