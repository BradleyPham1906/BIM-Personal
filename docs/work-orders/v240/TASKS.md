# V240 work orders: Wind loads from the place

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/structure/wind-loads.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v240/v240.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v240/v240.test.mjs
    node --check src/js/engine/structure/wind-loads.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimWindKz(z, exp)`

- **It must:** SPEC 5 WO-01: with BIM_WIND_EXP just above it, {B: [7.5, 3280], C: [9.8, 2460], D: [11.5, 1935]} (alpha, zg in ft): NaN for another exposure or a z that is not finite. zg in m = zg ft x 0.3048; z below 4.572 m is taken as 4.572; at or above zg, 2.41; else 2.41 (z/zg)^(2/alpha). Example: (7, 'C') gives 0.9285.
- **May use:** BIM_WIND_EXP (this task).
- **Files:** `src/js/engine/structure/wind-loads.js`, `docs/work-orders/v240/v240.test.mjs`
- **Budget:** 18
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v240/v240.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimWindQz(z, exp, V, Kzt, Ke)`

- **It must:** SPEC 5 WO-02: 0.613 x bimWindKz(z, exp) x Kzt x Ke x V^2, in Pa; Kzt and Ke are 1 when not finite. Example: (7, 'C', 50) gives 1422.9.
- **May use:** bimWindKz (WO-01).
- **Files:** `src/js/engine/structure/wind-loads.js`, `docs/work-orders/v240/v240.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v240/v240.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimWindCpLee(r)`

- **It must:** SPEC 5 WO-03: the leeward wall Cp for r = L/B: NaN unless r >= 0; -0.5 up to 1; -0.5 + 0.2 (r - 1) up to 2; -0.3 + 0.05 (r - 2) up to 4; -0.2 above. Example: 1.5 gives -0.4.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/wind-loads.js`, `docs/work-orders/v240/v240.test.mjs`
- **Budget:** 10
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v240/v240.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimWindStoreys(o)`

- **It must:** SPEC 5 WO-04: o {levels: [heights of the floor levels above the base, m, rising], B (width across the wind, m), L (depth along it), V, exp, Kzt, Ke, Kd (0.85 when not finite), G (0.85 when not finite)}. {error: 'bad input'} unless there is at least one level, B, L and V are positive and exp is B, C or D; {error: 'levels must rise above 0'} unless each level is above the one before (the first above 0). qh = bimWindQz at the top level; the leeward pressure pl = qh Kd G bimWindCpLee(L/B) for every level. Level i's band: from halfway to the level below (z0/2 for the first) to halfway to the level above (the top level's band ends at its height). For each level {z, Kz, qz (bimWindQz at z), pw = qz Kd G 0.8, pl, lo, hi, F = (pw - pl) B (hi - lo) / 1000 kN}. Returns {levels: [...], qh, total: the sum of F}. Internal pressure cancels in F. Example: levels [3.5, 7, 10.5], B 30, L 20, V 50, 'C' gives F 137.79, 144.98, 76.21 kN.
- **May use:** bimWindQz (WO-02), bimWindKz (WO-01), bimWindCpLee (WO-03).
- **Files:** `src/js/engine/structure/wind-loads.js`, `docs/work-orders/v240/v240.test.mjs`
- **Budget:** 32
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v240/v240.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-05 [Cline] `bimWindCases(Fx, Fz, Bx, Bz)`

- **It must:** SPEC 5 WO-05: the four load cases of ASCE 7-22 Figure 27.3-8 from the case 1 storey forces in X (Fx, wind along X, the building's width across it Bx) and Z (Fz, Bz), arrays of the same levels (a missing value is 0; the length is the longer one's). For each level {c1x: Fx, c1z: Fz, c2x: 0.75 Fx, c2z: 0.75 Fz, mt2x: 0.75 Fx 0.15 Bx, mt2z: 0.75 Fz 0.15 Bz, c3x: 0.75 Fx, c3z: 0.75 Fz, c4x: 0.563 Fx, c4z: 0.563 Fz, mt4: 0.563 (Fx 0.15 Bx + Fz 0.15 Bz)}. Example: Fx 137.79, Bx 30 gives mt2x 465.04 kN m.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/wind-loads.js`, `docs/work-orders/v240/v240.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v240/v240.test.mjs`. **Score:** 0.

---

## [ ] WO-06 [Cline] `bimWindNa(system, h)`

- **It must:** SPEC 5 WO-06: the approximate natural frequency in Hz from the height h in m, with hf = h / 0.3048: 'steel-mrf' 22.2 / hf^0.8, 'concrete-mrf' 43.5 / hf^0.9, 'other' 75 / hf; NaN for another system or h not positive. Example: ('steel-mrf', 10.5) gives 1.308.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/wind-loads.js`, `docs/work-orders/v240/v240.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v240/v240.test.mjs`. **Score:** 0.

---

## [ ] C-07 [Claude] The wiring

Load case W, the combinations, the Site fields, the storey table. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] C-08 [Claude] The records

PIPELINE row 240, the engineering log, Notion.
