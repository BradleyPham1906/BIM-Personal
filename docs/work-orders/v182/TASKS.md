# V182 work orders: Interiors I4, sightlines and views

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/bim/interiors-views.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v182/v182.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v182/v182.test.mjs
    node --check src/js/engine/bim/interiors-views.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimIsoHit(p, dx, dz, segs)`

- **It must:** SPEC 5 WO-01: the smallest t > 1e-9 with p + t(dx, dz) on a segment [[x,z],[x,z]] (its parameter u within -1e-9..1+1e-9), by the 2D cross products; parallel segments (|den| < 1e-12) are skipped; Infinity when none.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors-views.js`, `docs/work-orders/v182/v182.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v182/v182.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-02 [Cline] `bimIsovist(p, segs, n, maxR)`

- **It must:** SPEC 5 WO-02: n rays (360 when n is under 3; floored) at angles 2 pi i / n from +x toward +z, each point p + min(hit, maxR) times its direction (maxR 50 when not positive).
- **May use:** bimIsoHit (WO-01).
- **Files:** `src/js/engine/bim/interiors-views.js`, `docs/work-orders/v182/v182.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v182/v182.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimIsoArea(poly)`

- **It must:** SPEC 5 WO-03: the absolute shoelace area; 0 for no polygon.
- **May use:** nothing.
- **Files:** `src/js/engine/bim/interiors-views.js`, `docs/work-orders/v182/v182.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v182/v182.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimIsoSees(p, q, segs)`

- **It must:** SPEC 5 WO-04: true when p and q coincide (under 1e-12 apart) or the nearest hit along p to q is at least their distance - 1e-9.
- **May use:** bimIsoHit (WO-01).
- **Files:** `src/js/engine/bim/interiors-views.js`, `docs/work-orders/v182/v182.test.mjs`
- **Budget:** 10
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v182/v182.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimIsoWindows(p, windows, segs, samples)`

- **It must:** SPEC 5 WO-05: for each window {id, a, b} in order, {id, fraction}: the share of 'samples' points (5 when under 1; floored) at (k + 0.5)/samples along a to b that bimIsoSees.
- **May use:** bimIsoSees (WO-04).
- **Files:** `src/js/engine/bim/interiors-views.js`, `docs/work-orders/v182/v182.test.mjs`
- **Budget:** 18
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v182/v182.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-06 [Claude] The view tool on the plan

Claude's: wall segments cut at eye height from the model, the isovist drawn with its area, windows from the openings; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-07 [Claude] The records

PIPELINE row 182, Notion.
