# V187 spec: Freeform F5, point editing and blends

Notion: V183-V189 Freeform (F1-F7). Research: `docs/research/research-freeform-f1-f7.md`, `docs/research/research-rhino-guide-gap.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- Editing works on the curve's own data (control points, weights, knots), never on its samples: knot insertion (Boehm, The NURBS Book A5.1), moving a control point, degree elevation of Bezier segments, reversing.
- Blend curves are G1 (tangent continuous) cubics between two curve ends, their handle length a third of the gap by default, editable.
- Every edit makes a new curve object state for undo; the input is never changed in place.

## 2. What it does for the user

Show a curve's control points and drag them; insert a knot to add control; reverse a curve; blend two curve ends with a smooth cubic.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/drawing/nurbs-edit.js` | new, after `js/engine/drawing/sweeps.js` in `src/index.html` (header done) | 5 pure functions (part 5) | Cline, WO-01 to WO-05 |
| `docs/work-orders/v187/v187.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-06, WO-07 |

## 4. Data

Curves as in V183: {deg, pts, w (optional), knots}.

## 5. Functions, `src/js/engine/drawing/nurbs-edit.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimNeKnotInsert(c, u)`**: null unless knots[deg] < u < knots[n]. The span s with knots[s] <= u < knots[s+1]; in homogeneous coordinates (x w, y w, z w, w): Q_i = P_i for i <= s - p, Q_i = P_(i-1) for i > s, else a P_i + (1 - a) P_(i-1) with a = (u - k_i)/(k_(i+p) - k_i); the knot u inserted after k_s; back to points and weights (w only when the input had w).
- **WO-02 `bimNeMovePoint(c, i, d)`**: a new curve with point i moved by d, every array copied; null for an index out of range.
- **WO-03 `bimNeBlend(p0, t0, p1, t1, k)`**: the cubic {deg: 3, pts: [p0, p0 + t0/|t0| s, p1 - t1/|t1| s, p1], knots: [0,0,0,0,1,1,1,1]}, s = k when positive, else |p1 - p0| / 3 (a zero tangent counts as length 1).
- **WO-04 `bimNeElevate(P)`**: Bezier points raised one degree: Q_0 = P_0, Q_i = (i/(n+1)) P_(i-1) + (1 - i/(n+1)) P_i for i = 1..n, Q_(n+1) = P_n.
- **WO-05 `bimNeReverse(c)`**: points and weights reversed, knots reversed and each as 1 - k; copies.

## 6. Order of the work

WO-01 to WO-05 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-06** control-point editing and blend; **WO-07** the records.

## 7. Not in this phase

Surface point editing (after the kernel decision); g2 blends; blend surfaces.
