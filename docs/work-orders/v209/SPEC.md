# V209 spec: Walkthrough W3, fly and drone

Notion: Later: Walkthrough W2-W5, drive, fly, swim, record. Research: `docs/research/research-walkthrough.md`, `docs/research/research-scenario-3d-skills.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- W1 already has Fly (no gravity); W3 adds the drone: altitude kept between 2 m and 120 m above the ground below (the usual small-drone ceiling, as a setting, not a rule), an orbit about a picked target, and a waypoint route flown at a speed.
- Collision with the model stays W1's (Jolt).

## 2. What it does for the user

Drone (in the Walk menu): fly above the site within an altitude band, orbit a picked building, or fly a route of clicked waypoints.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/walk/walk-drone.js` | new, after `js/engine/walk/walk-drive.js` in `src/index.html` (header done) | 4 pure functions (part 5) | Cline, WO-01 to WO-04 |
| `docs/work-orders/v209/v209.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-05, WO-06 |

## 5. Functions, `src/js/engine/walk/walk-drone.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimDrnClamp(p, minAlt, maxAlt, ground)`**: p with its height clamped to ground + minAlt .. ground + maxAlt (minAlt 2 unless 0 or more, maxAlt 120 unless positive, ground 0 unless a number).
- **WO-02 `bimDrnOrbit(c, r, h, t, period)`**: the angle 2 pi t / period (30 s unless positive); {eye: [cx + r cos, cy + h, cz + r sin], target: a copy of c}.
- **WO-03 `bimDrnRoute(pts)`**: {segs: the 3D length of each leg, length: their sum}.
- **WO-04 `bimDrnAt(pts, route, dist)`**: the point dist along the route, dist clamped to 0..length, interpolated on its leg (the last leg takes any remainder); null for no points.

## 6. Order of the work

WO-01 to WO-04 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-05** wiring into walk; **WO-06** the records.

## 7. Not in this phase

Airspace rules; camera gimbal; photo planning (track d, v227).
