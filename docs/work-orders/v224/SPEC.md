# V224 spec: Track E, field work: positions without GPS and step-by-step instructions

Notion: Later: Track E, field work and autonomy. Research: `docs/research/research-field-autonomy.md`, `docs/research/research-field-autonomy-supplement.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- The first slice locates a phone or a target from sightings to known points (bearings that meet), with the spread between pairs as its uncertainty; photo-based localisation waits for a field test with the owner's hardware and data.
- Field instructions are ordered steps with prerequisites; a step is offered only when its prerequisites are done.
- Nothing leaves the device; results are labelled field aids, not survey.

## 2. What it does for the user

In the field: take bearings to two or more known points and the app places you on the plan with its spread; follow the next step of a task list that knows what must come first.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/site/field-guide.js` | new, after `js/engine/site/shadows.js` in `src/index.html` (header done) | 4 pure functions (part 5) | Cline, WO-01 to WO-04 |
| `docs/work-orders/v224/v224.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-05, WO-06 |

## 5. Functions, `src/js/engine/site/field-guide.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimFeBearing(a, b)`**: the azimuth from a to b in degrees clockwise from north (plan x east, y north), 0 to 360.
- **WO-02 `bimFeIntersect(p1, az1, p2, az2)`**: the meeting point of the rays from p1 along az1 and p2 along az2 (directions (sin az, cos az)); null when parallel (|cross| < 1e-9) or when it lies behind either point.
- **WO-03 `bimFeResect(target, obs)`**: obs [{from, az}]: each pair's meeting point (WO-02); null when none; else {p: their mean, spread: the largest distance of one from the mean, pairs: how many}.
- **WO-04 `bimFeNext(steps, done)`**: steps [{id, after: [ids]}] in order: the first not done whose prerequisites are all done as next (null when none); blocked lists the not-done steps passed over before it.

## 6. Order of the work

WO-01 to WO-04 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-05** field mode; **WO-06** the records.

## 7. Not in this phase

Gps-free photo localisation before a field test; drones; sending data off the device.
