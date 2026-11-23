# V276 work orders: the input layer and the simulated hand

Spec: `SPEC.md` in this folder (part 4 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function to `src/js/engine/xr/hand-model.js`, below the file's header comment, and
change nothing else: not another file, not the `import`/`export` lines, not `canvas_v10.html`. ES5 only: `var`,
`function`; no `let`, `const`, arrow functions, classes or template strings. Use only the names listed; never a name
from another file. Implement the whole function; never a placeholder. Never change the objects or arrays passed in.

The tests are in `docs/work-orders/v276/v276.test.mjs`, outside `npm test` while the orders are open, so main stays
green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v276/v276.test.mjs
    node --check src/js/engine/xr/hand-model.js
    npm test

Nothing calls these functions until Claude's tasks after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimHdFrom21(lm)`

- **It must:** SPEC 4 WO-01: null unless `lm` has 21 points; else a new array of 25 new `[x, y, z]`: `lm[0]`; `lm[1]`
  to `lm[4]`; then for the fingers `[[5, 0.37], [9, 0.32], [13, 0.33], [17, 0.5]]` (knuckle index, fraction): the
  metacarpal `wrist + (lm[k] - wrist) * f` for each coordinate, then `lm[k]`, `lm[k + 1]`, `lm[k + 2]`, `lm[k + 3]`.
- **Example:** with the wrist at the origin and the index knuckle at `[-0.025, 0, -0.09]`, joint 5 is
  `[-0.00925, 0, -0.0333]`.
- **User path:** internal only.
- **May use:** nothing.
- **Files:** `src/js/engine/xr/hand-model.js`, `docs/work-orders/v276/v276.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v276/v276.test.mjs`.
- **Distinguishing case:** one fraction for every finger fails the pinky (0.5); returning the input's own arrays fails
  "the joints are copies".
- **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimHdEuro(state, x, t, opts)`

- **It must:** SPEC 4 WO-02's formulas exactly, with an inner function `alpha(fc, dt)`; defaults when an option is
  null or missing; never change `state`.
- **Example:** from `{x: 1, dx: 0, t: 0}`, `x = 2` at `t = 0.1` with the defaults gives
  `1 + 1 / (1 + (1 / (2 * Math.PI)) / 0.1)`.
- **User path:** internal only (WO-09 filters each joint).
- **May use:** `Math`.
- **Files:** `src/js/engine/xr/hand-model.js`, `docs/work-orders/v276/v276.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-02 ...`.
- **Distinguishing case:** filtering the speed with `minCutoff` instead of `dCutoff`, or ignoring `beta`, fails "beta
  follows speed".
- **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-03 [Cline] `bimHdPinch(prev, d, enter, exit)`

- **It must:** SPEC 4 WO-03: false when `d` is not a finite number; else `prev ? d < exit : d < enter`, with `enter`
  0.015 and `exit` 0.025 when null or missing.
- **User path:** every pinch (WO-12).
- **May use:** nothing.
- **Files:** `src/js/engine/xr/hand-model.js`, `docs/work-orders/v276/v276.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-03 ...`.
- **Distinguishing case:** one threshold for both fails "held until 2.5 cm".
- **Score:** 0.

---

## [ ] WO-04 [Cline] `bimHdDepth(spanM, spanPx, fPx)`

- **It must:** SPEC 4 WO-04: null unless all three are above 0; else `spanM * fPx / spanPx`.
- **User path:** internal only.
- **May use:** nothing.
- **Files:** `src/js/engine/xr/hand-model.js`, `docs/work-orders/v276/v276.test.mjs`
- **Budget:** 6
- **Test:** the cases named `WO-04 ...`.
- **Score:** 0.

---

## [ ] WO-05 [Cline] `bimHdPalmFacing(j, hand, eye, cosMin)`

- **It must:** SPEC 4 WO-05: `u = j[6] - j[0]`, `v = j[21] - j[0]`, `n = u x v` (`[uy vz - uz vy, uz vx - ux vz,
  ux vy - uy vx]`), reversed when `hand` is 'left'; the centre the mean of `j[0]`, `j[6]`, `j[21]`; `e = eye - centre`;
  false when `|n|` or `|e|` is under 1e-12; else `(n . e) / (|n| |e|) > cosMin` (0.5 when null or missing).
- **User path:** every pinch is gated by it (WO-12): a palm-toward-you pinch is the system menu on headsets.
- **May use:** `Math`.
- **Files:** `src/js/engine/xr/hand-model.js`, `docs/work-orders/v276/v276.test.mjs`
- **Budget:** 18
- **Test:** the cases named `WO-05 ...`.
- **Distinguishing case:** not reversing for the left hand fails the left-hand cases; `>= 0` instead of the cosine fails
  the slant case.
- **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-06 [Cline] `bimHdCapsules(j, radii)`

- **It must:** SPEC 4 WO-06: `[]` unless `j` has 25 joints; the parents
  `[-1, 0, 1, 2, 3, 0, 5, 6, 7, 8, 0, 10, 11, 12, 13, 0, 15, 16, 17, 18, 0, 20, 21, 22, 23]`; for each joint 1 to 24,
  `{from: parent, to: i, a: copy of j[parent], b: copy of j[i], r}` with `r = radii[i]` when `radii` is given and that
  is a number above 0, else 0.008.
- **User path:** internal only (WO-11 makes a body of each).
- **May use:** nothing.
- **Files:** `src/js/engine/xr/hand-model.js`, `docs/work-orders/v276/v276.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-06 ...`.
- **Distinguishing case:** leaving out the wrist-to-metacarpal bones gives 20 and fails.
- **Score:** 0.

---

## [ ] WO-07 [Cline] `bimInTwoHand(a0, b0, a1, b1)`

- **It must:** SPEC 4 WO-07: `d0 = |b0 - a0|`, `d1 = |b1 - a1|` (`Math.hypot`); null when `d0 < 0.02` or `d1 < 1e-9`;
  `rot = atan2(b1z - a1z, b1x - a1x) - atan2(b0z - a0z, b0x - a0x)`, then add or take `2 pi` until it is in (-pi, pi];
  `t` each coordinate `((a1 + b1) - (a0 + b0)) / 2`; return `{s: d1 / d0, rot: rot, t: t}`.
- **User path:** two hands on the model (WO-12).
- **May use:** `Math`.
- **Files:** `src/js/engine/xr/hand-model.js`, `docs/work-orders/v276/v276.test.mjs`
- **Budget:** 14
- **Test:** the cases named `WO-07 ...`.
- **Distinguishing case:** no wrap into (-pi, pi] fails "the short way".
- **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-08 [Cline] `bimInPointerNext(state, ev, threshold)`

- **It must:** SPEC 4 WO-08's table exactly; `state` null is `{phase: 'idle', start: null}`; the distance is over all
  of `ev.p`'s coordinates; every returned state is a new object with `start` copied.
- **User path:** every pointer: mouse, touch, hand ray (WO-12).
- **May use:** `Math`.
- **Files:** `src/js/engine/xr/hand-model.js`, `docs/work-orders/v276/v276.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-08 ...`.
- **Distinguishing case:** emitting a click after a drag fails the drag release case.
- **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-09 [Claude] MediaPipe vendored, in a worker, filtered

## [ ] WO-10 [Claude] The hand mesh: XRHandMeshModel in the bundle, the generic hands vendored

## [ ] WO-11 [Claude] The simulated hand in Jolt

## [ ] WO-12 [Claude] The pointer wiring, the two-hand transform, the calibration

## [ ] WO-13 [Claude] Tests into tests/unit, modules, the browser check

## [ ] WO-14 [Claude] The records
