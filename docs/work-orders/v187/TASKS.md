# V187 work orders: Freeform F5, point editing and blends

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/drawing/nurbs-edit.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v187/v187.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v187/v187.test.mjs
    node --check src/js/engine/drawing/nurbs-edit.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimNeKnotInsert(c, u)`

- **It must:** SPEC 5 WO-01: null unless knots[deg] < u < knots[n]. The span s with knots[s] <= u < knots[s+1]; in homogeneous coordinates (x w, y w, z w, w): Q_i = P_i for i <= s - p, Q_i = P_(i-1) for i > s, else a P_i + (1 - a) P_(i-1) with a = (u - k_i)/(k_(i+p) - k_i); the knot u inserted after k_s; back to points and weights (w only when the input had w).
- **May use:** nothing.
- **Files:** `src/js/engine/drawing/nurbs-edit.js`, `docs/work-orders/v187/v187.test.mjs`
- **Budget:** 70
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v187/v187.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-02 [Cline] `bimNeMovePoint(c, i, d)`

- **It must:** SPEC 5 WO-02: a new curve with point i moved by d, every array copied; null for an index out of range.
- **May use:** nothing.
- **Files:** `src/js/engine/drawing/nurbs-edit.js`, `docs/work-orders/v187/v187.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v187/v187.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimNeBlend(p0, t0, p1, t1, k)`

- **It must:** SPEC 5 WO-03: the cubic {deg: 3, pts: [p0, p0 + t0/|t0| s, p1 - t1/|t1| s, p1], knots: [0,0,0,0,1,1,1,1]}, s = k when positive, else |p1 - p0| / 3 (a zero tangent counts as length 1).
- **May use:** nothing.
- **Files:** `src/js/engine/drawing/nurbs-edit.js`, `docs/work-orders/v187/v187.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v187/v187.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimNeElevate(P)`

- **It must:** SPEC 5 WO-04: Bezier points raised one degree: Q_0 = P_0, Q_i = (i/(n+1)) P_(i-1) + (1 - i/(n+1)) P_i for i = 1..n, Q_(n+1) = P_n.
- **May use:** nothing.
- **Files:** `src/js/engine/drawing/nurbs-edit.js`, `docs/work-orders/v187/v187.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v187/v187.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimNeReverse(c)`

- **It must:** SPEC 5 WO-05: points and weights reversed, knots reversed and each as 1 - k; copies.
- **May use:** nothing.
- **Files:** `src/js/engine/drawing/nurbs-edit.js`, `docs/work-orders/v187/v187.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v187/v187.test.mjs`. **Score:** 0.

---

## [ ] WO-06 [Claude] Control-point editing and Blend

Claude's: control-point grips on curves, Insert knot, Reverse, Blend curve commands, undo; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-07 [Claude] The records

PIPELINE row 187, Notion.
