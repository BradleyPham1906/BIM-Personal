# V182 spec: Interiors I4, sightlines and views

Notion: Interiors I1-I4 (V179-V182). Research: `docs/research/research-notion-v177-v180-interiors.md`, `docs/research/research-ladybug-sun-radiation.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- I4 delivers geometric visibility only: isovists, sightlines and the share of each window seen from a point, at an eye height the owner sets (1.2 m seated by default); labelled 'geometry, not daylight'.
- Daylight (sky, glazing, materials) stays a separate product through Ladybug (V172c), not a quality level of the same number.
- Obstructions are the walls and opaque elements cut at the eye height; missing geometry shows a warning.
- 360 rays and 5 samples a window by default.

## 2. What it does for the user

Click a point in a room: its isovist (what can be seen) is drawn with its area, and each window shows how much of it is visible from there.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/bim/interiors-views.js` | new, after `js/engine/bim/interiors-routes.js` in `src/index.html` (header done) | 5 pure functions (part 5) | Cline, WO-01 to WO-05 |
| `docs/work-orders/v182/v182.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-06, WO-07 |

## 5. Functions, `src/js/engine/bim/interiors-views.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimIsoHit(p, dx, dz, segs)`**: the smallest t > 1e-9 with p + t(dx, dz) on a segment [[x,z],[x,z]] (its parameter u within -1e-9..1+1e-9), by the 2D cross products; parallel segments (|den| < 1e-12) are skipped; Infinity when none.
- **WO-02 `bimIsovist(p, segs, n, maxR)`**: n rays (360 when n is under 3; floored) at angles 2 pi i / n from +x toward +z, each point p + min(hit, maxR) times its direction (maxR 50 when not positive).
- **WO-03 `bimIsoArea(poly)`**: the absolute shoelace area; 0 for no polygon.
- **WO-04 `bimIsoSees(p, q, segs)`**: true when p and q coincide (under 1e-12 apart) or the nearest hit along p to q is at least their distance - 1e-9.
- **WO-05 `bimIsoWindows(p, windows, segs, samples)`**: for each window {id, a, b} in order, {id, fraction}: the share of 'samples' points (5 when under 1; floored) at (k + 0.5)/samples along a to b that bimIsoSees.

## 6. Order of the work

WO-01 to WO-05 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-06** the view tool on the plan; **WO-07** the records.

## 7. Not in this phase

Daylight metrics (sda, ase) here; 3d view analysis; glare.
