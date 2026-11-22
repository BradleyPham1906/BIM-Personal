# V239 work orders: Floor loads from the place

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/structure/floor-loads.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v239/v239.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v239/v239.test.mjs
    node --check src/js/engine/structure/floor-loads.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimLiveKll(kind)`

- **It must:** SPEC 5 WO-01: the live load element factor of Table 4.7-1 by the member's kind, a string: 'interior column' 4, 'exterior column' 4, 'edge column cantilever' 3, 'corner column cantilever' 2, 'edge beam' 2, 'interior beam' 2; anything else (another string, '', undefined, and names such as 'toString' that objects carry) 1. Example: bimLiveKll('edge beam') is 2.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/floor-loads.js`, `docs/work-orders/v239/v239.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v239/v239.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimLiveReduce(Lo, KLL, AT, floors, rule)`

- **It must:** SPEC 5 WO-02: {error: 'bad input'} unless Lo >= 0, KLL > 0 and AT >= 0. rule 'none' (assembly and the other rows of the table that are never reduced): {L: Lo, rule: 'none'}. rule 'garage', or Lo above 4.79 kPa: {L: 0.8 Lo when floors >= 2 else Lo, rule: 'garage' or 'heavy'}. KLL AT below 37.16 m2: {L: Lo, rule: 'small'}. Otherwise f = 0.25 + 4.57 / sqrt(KLL AT), L = Lo times f held between the lower limit (0.5 for one floor, 0.4 for two or more) and 1: {L, rule: 'reduced'}. Example: (2.40, 4, 128, 2) gives L 1.0847, 'reduced'; (2.40, 2, 16, 1) gives {L: 2.40, rule: 'small'}.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/floor-loads.js`, `docs/work-orders/v239/v239.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v239/v239.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-03 [Cline] `bimRoofLive(Lo, At, slope)`

- **It must:** SPEC 5 WO-03: NaN unless Lo >= 0, At >= 0 and slope >= 0. F = 12 slope (inches of rise per foot). R1 = 1 for At <= 18.58 m2, 1.2 - 0.011 At below 55.74 m2, 0.6 from 55.74 m2. R2 = 1 for F <= 4, 1.2 - 0.05 F below 12, 0.6 from 12. Returns Lo R1 R2 held between 0.58 and 0.96. Example: (0.96, 30, 0.5) gives 0.96 x 0.87 x 0.9 = 0.75168.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/floor-loads.js`, `docs/work-orders/v239/v239.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v239/v239.test.mjs`. **Score:** 0.

---

## [ ] C-04 [Claude] The wiring

The floors on the frame: occupancy, line loads on beams, reduction in the takedown. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] C-05 [Claude] The records

PIPELINE row 239, the engineering log, Notion.
