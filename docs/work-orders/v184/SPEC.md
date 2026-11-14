# V184 spec: Freeform F2, surfaces from curves

Notion: V183-V189 Freeform (F1-F7). Research: `docs/research/research-freeform-f1-f7.md`, `docs/research/research-rhino-guide-gap.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- F2's surfaces are built from F1's sampled curves as meshes in the app's own {v, f} form (quads), labelled previews of the exact surface until the kernel decision.
- Extrude, revolve (any angle, about any axis), loft (two curves of the same sample count; F5 matches counts) and edge surfaces (Coons patches) first; planar surfaces use the app's existing pad mesh.
- The defining curves are kept on the object, so a changed curve rebuilds its surface.

## 2. What it does for the user

Select curves and choose Extrude, Revolve, Loft or Edge surface: a surface appears, rebuilt whenever its curves change.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/drawing/surfaces.js` | new, after `js/engine/drawing/nurbs.js` in `src/index.html` (header done) | 6 pure functions (part 5) | Cline, WO-01 to WO-06 |
| `docs/work-orders/v184/v184.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-07, WO-08 |

## 4. Data

A mesh {v: [[x, y, z]...], f: [[i, j, k, l]...]} as the app's solids hold it; curves as arrays of [x, y, z] (F1's samples).

## 5. Functions, `src/js/engine/drawing/surfaces.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimSrfGrid(rows, cols, closeU)`**: quads [a, b, b + cols, a + cols] with a = j*cols + i and b = j*cols + (i+1) % cols, for j < rows - 1 and i < cols - 1 (i < cols when closeU).
- **WO-02 `bimSrfExtrude(pts, vec)`**: {v: the points then the points moved by vec, f: bimSrfGrid(2, n, false)}; null for fewer than 2 points.
- **WO-03 `bimSrfRotate(p, o, ax, a)`**: p turned by a radians about the axis through o along ax (normalised), by Rodrigues' formula: x c + (k cross x) s + k (k dot x)(1 - c), x = p - o, plus o.
- **WO-04 `bimSrfRevolve(pts, o, ax, angle, segs)`**: segs (24 when under 1) steps; rings j = 0 .. segs (only 0 .. segs - 1 for a full turn, |angle| within 1e-9 of 2 pi) of the profile turned by angle j / segs; faces [a, a+1, b+1, b] with a = j n + i, b = ((j+1) % rings) n + i for j < segs, i < n - 1. null for fewer than 2 points.
- **WO-05 `bimSrfLoft(a, b, rows)`**: rows (1 when under 1) + 1 interpolated rings from a to b, faces by bimSrfGrid(rows + 1, n, false); null unless both have the same count, 2 or more.
- **WO-06 `bimSrfCoons(c0, c1, d0, d1)`**: the bilinear Coons patch: c0 (v = 0) and c1 (v = 1) with m points, d0 (u = 0) and d1 (u = 1) with k points, corners shared; vertex (j, i) with u = i/(m-1), w = j/(k-1): (1-w) c0[i] + w c1[i] + (1-u) d0[j] + u d1[j] minus the bilinear blend of the four corners; faces bimSrfGrid(k, m, false). null for mismatched counts or fewer than 2.

## 6. Order of the work

WO-01 to WO-06 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-07** the surface commands; **WO-08** the records.

## 7. Not in this phase

Trimming; exact nurbs surfaces (after the kernel decision); planar surfaces from curves (the app's pad mesh does it).
