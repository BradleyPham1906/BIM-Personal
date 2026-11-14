# V213 work orders: Generators: massing, parking, lots

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/site-tools/generators.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v213/v213.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v213/v213.test.mjs
    node --check src/js/engine/site-tools/generators.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimGenAchievable(lot, far, cov, levels)`

- **It must:** SPEC 5 WO-01: plateCap = lot cov, capacity = plateCap levels, farLimit = lot far, achievable = the smaller; plates filled from the ground, each the smaller of plateCap and what is left (never under 0). {plateCap, capacity, farLimit, achievable, plates}.
- **May use:** nothing.
- **Files:** `src/js/engine/site-tools/generators.js`, `docs/work-orders/v213/v213.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v213/v213.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimGenStoreys(h, ftf)`

- **It must:** SPEC 5 WO-02: ftf 3.5 unless positive; {storeys: floor(h / ftf + 1e-9), top: storeys ftf}; {0, 0} when h is not positive.
- **May use:** nothing.
- **Files:** `src/js/engine/site-tools/generators.js`, `docs/work-orders/v213/v213.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v213/v213.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimGenStalls(needs)`

- **It must:** SPEC 5 WO-03: needs [{qty, per, ratio}] (ratio stalls per 'per' of qty): ceil(sum of qty / per ratio - 1e-9), lines with per or qty not positive left out; 0 (never -0) when the sum is 0.
- **May use:** nothing.
- **Files:** `src/js/engine/site-tools/generators.js`, `docs/work-orders/v213/v213.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v213/v213.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimGenParking(w, d, stall, aisle)`

- **It must:** SPEC 5 WO-04: stall {w 2.6, d 5.5} and aisle 7.2 unless positive; perRow = floor(w / stall.w + 1e-9); a double module is 2 stall.d + aisle deep; doubleModules = floor(d / module + 1e-9); singleRows 1 when the rest is at least stall.d + aisle; stalls = perRow (2 doubleModules + singleRows).
- **May use:** nothing.
- **Files:** `src/js/engine/site-tools/generators.js`, `docs/work-orders/v213/v213.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v213/v213.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimGenLots(frontage, target)`

- **It must:** SPEC 5 WO-05: [] unless both positive; n = max(1, floor(frontage / target + 1e-9)) lots of frontage / n.
- **May use:** nothing.
- **Files:** `src/js/engine/site-tools/generators.js`, `docs/work-orders/v213/v213.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v213/v213.test.mjs`. **Score:** 0.

---

## [ ] WO-06 [Claude] Wiring into the app

Claude's: the interface on phone, tablet and desktop, saving with the project and undo; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-07 [Claude] The records

PIPELINE row 213, Notion.
