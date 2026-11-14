# V189 spec: Freeform F7, Make2D (hidden-line drawings)

Notion: V183-V189 Freeform (F1-F7). Research: `docs/research/research-freeform-f1-f7.md`, `docs/research/research-rhino-guide-gap.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- Make2D works on the meshes at their sampling tolerance: boundary, silhouette and crease edges (over 30 degrees by default), each cut into visible runs by sampling against the triangles nearer the eye; labelled as of the mesh, not exact.
- The result is plain 2D lines on a layer per kind (visible; hidden lines optional), ready for sheets.
- Exact hidden lines on NURBS wait for the kernel decision; F7's rendering is the rendered view (V194).

## 2. What it does for the user

Choose a view and Make2D: the selected objects become a flat line drawing of what is seen, silhouettes and creases kept, hidden parts removed, placed beside the model or on a sheet.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/drawing/make2d.js` | new, after `js/engine/drawing/flow-picture.js` in `src/index.html` (header done) | 4 pure functions (part 5) | Cline, WO-01 to WO-04 |
| `docs/work-orders/v189/v189.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-05, WO-06 |

## 4. Data

A view {right, up, dir} of unit vectors; a point goes to [p . right, p . up, p . dir], smaller depth nearer the eye. Triangles [[x,y,z] x3].

## 5. Functions, `src/js/engine/drawing/make2d.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimM2Project(p, view)`**: [p . right, p . up, p . dir].
- **WO-02 `bimM2Edges(m, dir, creaseDeg)`**: each face's unit normal by Newell's method; each edge (smaller index first) with the faces using it, in first-met order: not exactly two faces: [a, b, 'boundary']; the two normals' dot products with dir of different sign (one < 0, one not): 'silhouette'; else the normals' dot under cos(creaseDeg) (30 when not positive): 'crease'; else left out.
- **WO-03 `bimM2Hidden(p, tris, view, eps)`**: true when some triangle, projected, contains p's projection strictly (all three barycentric weights >= eps, 1e-6 by default; degenerate ones skipped) and its interpolated depth there is less than p's depth - eps.
- **WO-04 `bimM2Visible(a, b, tris, view, samples)`**: the segment in samples (16 when under 1) equal pieces, each kept when its midpoint is not hidden; consecutive kept pieces joined into runs; each run as its two ends projected [[x, y], [x, y]].

## 6. Order of the work

WO-01 to WO-04 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-05** the make2d command; **WO-06** the records.

## 7. Not in this phase

Exact nurbs hidden lines; perspective make2d (parallel views first); hatching cut faces.
