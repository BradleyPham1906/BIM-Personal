# V180 spec: Interiors I2, clearance and ergonomics

Notion: Interiors I1-I4 (V179-V182). Research: `docs/research/research-notion-v177-v180-interiors.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- Each furniture and fixture model has a body (its footprint) and a functional clearance zone in front of it, set per kind in the standards registry (V167) with its edition; nothing guessed from a mesh.
- A zone is blocked by another item's body or a wall; zones may overlap each other (the research: blanket zone-on-zone collision gives false failures).
- A width or turning space is a measurement against a registry rule (its clause and edition shown), never a compliance finding; unknown inputs are 'not evaluated'.
- The first rules: 2010 ADA Standards 404.2.3 (32 in door clear width), 304 (60 in turning circle), 305 (30 by 48 in clear floor space), entered as data the owner can edit.

## 2. What it does for the user

Select furniture or fixtures: each shows its clearance zone; zones blocked by a wall or another piece turn red with the reason. A room shows whether a turning circle fits. Each check names its rule's clause and edition.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/bim/interiors-clearance.js` | new, after `js/engine/bim/interiors.js` in `src/index.html` (header done) | 6 pure functions (part 5) | Cline, WO-01 to WO-06 |
| `docs/work-orders/v180/v180.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-07, WO-08 |

## 5. Functions, `src/js/engine/bim/interiors-clearance.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimClrRect(c, w, d, rot)`**: the corners of a w by d rectangle centred on c=[x,z], turned by rot radians, in the order (-w/2,-d/2), (w/2,-d/2), (w/2,d/2), (-w/2,d/2) of its own axes, each turned by (x cos - z sin, x sin + z cos).
- **WO-02 `bimClrZone(it, front, side)`**: the zone in front of an item {center, w, d, rot}: a rectangle 'front' deep along the item's local +z, starting at its front face, as wide as the item plus 'side' each side, turned with it: centre = center + (-sin rot, cos rot) * (d/2 + front/2). null when front is not above 0.
- **WO-03 `bimClrOverlap(a, b)`**: true when two convex polygons overlap, by the separating axis test on every edge normal of both; projections that only touch (within 1e-9) do not overlap. false when either has fewer than 3 points.
- **WO-04 `bimClrConflicts(items, obstacles)`**: for each item {id, body, zone} with a zone, in order: each other item whose body overlaps the zone, then each obstacle {id, poly} that does, as {item, with}. Zones are never tested against zones.
- **WO-05 `bimClrCircleFits(poly, c, r)`**: true when the centre is inside the polygon (even-odd) and its distance to every edge segment is at least r - 1e-9; false for r not above 0 or fewer than 3 points.
- **WO-06 `bimClrRule(rule, m)`**: {clause, edition} (strings, else '') plus status: 'not evaluated' unless rule.minIn and m are numbers; else 'meets' when m / 0.0254 >= minIn - 1e-9, else 'below', and measuredIn rounded to 2 places.

## 6. Order of the work

WO-01 to WO-06 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-07** registry rules, item kinds and the check on the model; **WO-08** the records.

## 7. Not in this phase

Egress (i3); daylight (i4); scans and roomplan; compliance determinations.
