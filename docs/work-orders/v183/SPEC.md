# Freeform F1 to F7 and the Parametric Design Foundation (outline)

Notion: V181-V187 Freeform (F1-F7); Parametric Design Foundation. PIPELINE: 183 to 189. Research: `docs/research/research-freeform-f1-f7.md`, `docs/research/research-parametric-history.md`, `docs/research/research-parametric-app-audit.md`, `docs/research/solidcraft-integration-map.md`, `docs/research/plan-parametric-design.md`, `docs/research/research-rhino-guide-gap.md`. Written by Claude, 2026-11-14, as an outline: not yet Cline-ready; the next spec sprint turns its first slice into work orders with tests.

## 0. Status

Next spec sprint (F1's first slice below). The exact kernel (SMLib, OCCT or none) stays a gate before F2's solids.

## 1. The owner's decisions, 2026-11-14, as recommended

- F1 starts with our own ES5 NURBS curves (evaluation, derivatives, sampling) behind a narrow adapter; no binary kernel yet;
- mesh-only operations are allowed as labelled previews and exports, never called exact NURBS;
- a B-rep kernel (SMLib's e02 or OCCT) is chosen on one shared, independently defined test corpus before F2's trimmed surfaces and solids; that choice is the owner's, with its licence under the library rule;
- the Parametric Design Foundation (sketch, Pad, Pocket, persistent feature history) extends the app's own history (`history/`) with SolidCraft as a design reference, not copied code, until its integration map is verified;
- on a failed regeneration the last valid shape is kept and the failing feature is marked, never silently dropped.

## 2. What it does for the user

NURBS curves drawn and edited by control points (F1), then surfaces from curves, sweeps, analysis, point editing, picture planes and Make2D (F2 to F7), and a parametric sketch to Pad to Pocket workflow whose features can be edited and replayed.

## 3. The first slice (pure functions in `src/js/engine/drawing/nurbs.js`, ES5, no other file's names)

- `bimNurbsKnots(n, p)`: a clamped uniform knot vector for n control points of degree p: p+1 zeros, the inner knots evenly spaced, p+1 ones; [] when n <= p.
- `bimNurbsBasis(i, p, u, knots)`: the Cox-de Boor basis value N(i,p)(u), with u at the last knot belonging to the last span.
- `bimNurbsPoint(ctrl, w, knots, p, u)`: the rational curve point from control points [x,y,z], weights and knots.
- `bimNurbsDeriv(ctrl, w, knots, p, u)`: the first derivative, by the quotient rule on the weighted sums.
- `bimNurbsSample(curve, tol)`: points along the curve, subdividing spans until the chord error is within tol.
- `bimNurbsInterp(points, p)`: a curve through the given points (chord-length parameters, averaged knots, solved by Gaussian elimination).

Tests: Points and derivatives against values computed independently (a quarter circle as a rational quadratic: every sampled point at radius 1 within 1e-12; The NURBS Book's worked examples).

## 4. Not in this phase

Trimmed surfaces and solids before the kernel decision; a full feature tree for every existing tool; make2d's exact hidden lines (f7) before the kernel.
