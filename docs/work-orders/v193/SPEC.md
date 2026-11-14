# V193 spec: LOD-F, LOD3 openings on rectified facades

Notion: V191 LOD-F: LOD3 openings. Research: `docs/research/research-notion-v191-openings.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- Openings are drawn by hand first, rectangular only; Regularise lines up sills, heads and centres within a tolerance (5 cm by default) only on request, showing how far each moved.
- Machine proposals (Segment Anything in the browser, Apache-2.0) only later, on request, each confirmed by the owner, after its own research under the library rule.
- An approved opening is cut into the wall with the app's existing opening code and keeps its source image, transform and error; one at sill height 5 cm or less is a door.

## 2. What it does for the user

On a rectified facade (V192), draw windows and doors; Regularise lines them up; Apply cuts them into the wall as real openings.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/bim/facade-openings.js` | new, after `js/engine/bim/interiors-views.js` in `src/index.html` (header done) | 5 pure functions (part 5) | Cline, WO-01 to WO-05 |
| `docs/work-orders/v193/v193.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-06, WO-07 |

## 4. Data

An opening on the facade {x, y, w, h} in metres: x along the wall from its start, y up from its base.

## 5. Functions, `src/js/engine/bim/facade-openings.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimOpnCluster(values, tol)`**: indices sorted by value (then index); a new cluster starts when a value is more than tol (0.05 when negative or absent) above the previous member; each {members (indices, ascending), mean}.
- **WO-02 `bimOpnSnap(values, tol)`**: a copy of the values with each replaced by its cluster's mean.
- **WO-03 `bimOpnRegularise(rects, tol)`**: sills (y), heads (y + h) and centres (x + w/2) each snapped (WO-02); each new rect {x: centre - w/2, y: sill, w, h: head - sill, moved: the largest of the changes of x, y and the head}.
- **WO-04 `bimOpnOverlap(rects)`**: pairs [i, j], i < j, whose interiors overlap (strictly, by 1e-9).
- **WO-05 `bimOpnToWall(r, len, height)`**: null unless w and h are positive and the rect lies within 0..len along and 0..height up (height checked when positive); else {along: x + w/2, sill: y, width: w, height: h, kind: 'door' when y <= 0.05, else 'window'}.

## 6. Order of the work

WO-01 to WO-05 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-06** drawing, regularise and apply on the facade; **WO-07** the records.

## 7. Not in this phase

Non-rectangular openings; automatic detection; reveals and depth.
