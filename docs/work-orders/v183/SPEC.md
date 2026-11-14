# V183 spec: Freeform F1, NURBS curves

Notion: V183-V189 Freeform (F1-F7). Research: `docs/research/research-freeform-f1-f7.md`, `docs/research/research-rhino-guide-gap.md`, `docs/research/research-parametric-history.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- F1 starts with our own ES5 NURBS curves (evaluation, tangents, sampling) behind a narrow adapter; no binary kernel yet.
- Mesh results from later phases are labelled previews of the exact curves and surfaces.
- A B-rep kernel (SMLib's e02 or OCCT) is chosen on one shared test corpus before trimmed solids (after F7), under the library rule.
- Curves are stored by their control points, weights, degree and knots, so they stay editable.

## 2. What it does for the user

A Curve tool draws a NURBS curve by control points (degree 3 by default) or through points; it stays a curve, drawn smooth at any zoom, and its control points can be moved.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/drawing/nurbs.js` | new, after `js/engine/drawing/drawing-input.js` in `src/index.html` (header done) | 6 pure functions (part 5) | Cline, WO-01 to WO-06 |
| `docs/work-orders/v183/v183.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-07, WO-08 |

## 4. Data

A curve {deg, pts: [[x, y, z]...], w: [weights] (optional, all 1), knots: [n + deg + 1 values, clamped 0..1]}. Algorithms from The NURBS Book (Piegl and Tiller), A2.1 and A2.2.

## 5. Functions, `src/js/engine/drawing/nurbs.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimNurbsKnots(n, p)`**: p+1 zeros, then i/(n-p) for i = 1 .. n-p-1, then p+1 ones; [] unless n > p >= 1.
- **WO-02 `bimNurbsSpan(n, p, u, k)`**: The NURBS Book A2.1: n-1 when u >= k[n]; p when u <= k[p]; else the binary search for k[mid] <= u < k[mid+1].
- **WO-03 `bimNurbsBasis(span, u, p, k)`**: The NURBS Book A2.2: the p+1 non-zero basis values N[0..p] at u for that span, by the left/right triangular scheme.
- **WO-04 `bimNurbsPoint(c, u)`**: the rational point: sum of pts[span-p+i] * w * N[i] divided by sum of w * N[i], weights 1 when c.w is absent.
- **WO-05 `bimNurbsTangent(c, u, h)`**: the central difference (P(b) - P(a)) / (b - a) with a = max(0, u - h), b = min(1, u + h), h 1e-6 when not positive.
- **WO-06 `bimNurbsSample(c, tol)`**: points at parameters from 0 to 1: split each interval [a, b] in half while (the midpoint's distance from the chord P(a)P(b) is over tol, or b - a > 0.25) and b - a > 1e-6, depth first left to right; the point at 0 then the end of each kept interval. tol 0.001 when not positive.

## 6. Order of the work

WO-01 to WO-06 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-07** the curve tool; **WO-08** the records.

## 7. Not in this phase

Surfaces (f2); trimming; curve offset.
