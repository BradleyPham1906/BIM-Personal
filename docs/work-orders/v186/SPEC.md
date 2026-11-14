# V186 spec: Freeform F4, surface analysis

Notion: V183-V189 Freeform (F1-F7). Research: `docs/research/research-freeform-f1-f7.md`, `docs/research/research-rhino-guide-gap.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- Analysis runs on the surface's mesh (F2, F3) and is shown in Analyze as colours: zebra stripes, draft angle against a pull direction, and Gaussian curvature by angle deficit.
- Values are labelled as of the mesh at its sampling tolerance, not the exact surface.
- Ten zebra stripes and a pull direction of +Y (the app's up) by default, both editable.

## 2. What it does for the user

Pick a surface and an analysis in Analyze: zebra stripes to judge smoothness, draft angles coloured against a limit, and curvature as a colour ramp with its legend.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/analysis/surface-analysis.js` | new, after `js/engine/analysis/analyze-tab.js` in `src/index.html` (header done) | 5 pure functions (part 5) | Cline, WO-01 to WO-05 |
| `docs/work-orders/v186/v186.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-06, WO-07 |

## 5. Functions, `src/js/engine/analysis/surface-analysis.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimAnFaceNormal(v, face)`**: Newell's method over the face's vertex indices: n = sum over edges a to b of ((ay - by)(az + bz), (az - bz)(ax + bx), (ax - bx)(ay + by)); {n: n normalised ([0, 0, 0] when its length is under 1e-15), area: |n| / 2}.
- **WO-02 `bimAnVertexNormals(m)`**: for each vertex, the sum of n * area of the faces using it, normalised (left as is when under 1e-15).
- **WO-03 `bimAnDraft(n, pull)`**: 90 - the angle in degrees between the unit normal and the pull direction (normalised; the cosine clamped to -1..1).
- **WO-04 `bimAnZebra(n, view, stripes)`**: the reflected view r = 2 (n . view) n - view; k = floor((r[1] + 1) / 2 * stripes) clamped to 0 .. stripes - 1; k % 2. stripes 10 when under 1 (floored).
- **WO-05 `bimAnGauss(m)`**: {deficit, area} per vertex: 2 pi minus the sum of the corner angles at it over every face (the angle between the edges to the previous and next vertex of the face), and the sum of each face's area / its vertex count.

## 6. Order of the work

WO-01 to WO-05 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-06** the analyses in analyze; **WO-07** the records.

## 7. Not in this phase

Exact curvature from the nurbs surface; thickness analysis; edge continuity analysis.
