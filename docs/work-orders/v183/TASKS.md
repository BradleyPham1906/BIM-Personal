# V183 work orders: Freeform F1, NURBS curves

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/drawing/nurbs.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v183/v183.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v183/v183.test.mjs
    node --check src/js/engine/drawing/nurbs.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimNurbsKnots(n, p)`

- **It must:** SPEC 5 WO-01: p+1 zeros, then i/(n-p) for i = 1 .. n-p-1, then p+1 ones; [] unless n > p >= 1.
- **May use:** nothing.
- **Files:** `src/js/engine/drawing/nurbs.js`, `docs/work-orders/v183/v183.test.mjs`
- **Budget:** 24
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v183/v183.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimNurbsSpan(n, p, u, k)`

- **It must:** SPEC 5 WO-02: The NURBS Book A2.1: n-1 when u >= k[n]; p when u <= k[p]; else the binary search for k[mid] <= u < k[mid+1].
- **May use:** nothing.
- **Files:** `src/js/engine/drawing/nurbs.js`, `docs/work-orders/v183/v183.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v183/v183.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-03 [Cline] `bimNurbsBasis(span, u, p, k)`

- **It must:** SPEC 5 WO-03: The NURBS Book A2.2: the p+1 non-zero basis values N[0..p] at u for that span, by the left/right triangular scheme.
- **May use:** nothing.
- **Files:** `src/js/engine/drawing/nurbs.js`, `docs/work-orders/v183/v183.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v183/v183.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-04 [Cline] `bimNurbsPoint(c, u)`

- **It must:** SPEC 5 WO-04: the rational point: sum of pts[span-p+i] * w * N[i] divided by sum of w * N[i], weights 1 when c.w is absent.
- **May use:** bimNurbsSpan (WO-02), bimNurbsBasis (WO-03).
- **Files:** `src/js/engine/drawing/nurbs.js`, `docs/work-orders/v183/v183.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v183/v183.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-05 [Cline] `bimNurbsTangent(c, u, h)`

- **It must:** SPEC 5 WO-05: the central difference (P(b) - P(a)) / (b - a) with a = max(0, u - h), b = min(1, u + h), h 1e-6 when not positive.
- **May use:** bimNurbsPoint (WO-04).
- **Files:** `src/js/engine/drawing/nurbs.js`, `docs/work-orders/v183/v183.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v183/v183.test.mjs`. **Score:** 0.

---

## [ ] WO-06 [Cline] `bimNurbsSample(c, tol)`

- **It must:** SPEC 5 WO-06: points at parameters from 0 to 1: split each interval [a, b] in half while (the midpoint's distance from the chord P(a)P(b) is over tol, or b - a > 0.25) and b - a > 1e-6, depth first left to right; the point at 0 then the end of each kept interval. tol 0.001 when not positive.
- **May use:** bimNurbsPoint (WO-04).
- **Files:** `src/js/engine/drawing/nurbs.js`, `docs/work-orders/v183/v183.test.mjs`
- **Budget:** 60
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v183/v183.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-07 [Claude] The Curve tool

Claude's: the tool (control points and through points by an interpolation work order of its own), the curve object saved with the project, drawn from bimNurbsSample, its control points as grips; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-08 [Claude] The records

PIPELINE row 183, Notion.
