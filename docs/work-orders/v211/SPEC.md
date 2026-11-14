# V211 spec: Walkthrough W5, record and replay

Notion: Later: Walkthrough W2-W5, drive, fly, swim, record. Research: `docs/research/research-walkthrough.md`, `docs/research/research-scenario-3d-skills.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- W5 records the walk, drive, drone or swim as a path of poses (time, position, heading, pitch), a pose kept only when it moved 5 cm or turned 0.02 rad, saved with the project; replayed by interpolating (positions linearly, headings the short way).
- A recorded path exports as a video through the rendered view, frame by frame (Claude's task).

## 2. What it does for the user

Record in any walk mode, stop, then Play: the camera follows the same path; save it with the project and export it as a video.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/walk/walk-record.js` | new, after `js/engine/walk/walk-swim.js` in `src/index.html` (header done) | 4 pure functions (part 5) | Cline, WO-01 to WO-04 |
| `docs/work-orders/v211/v211.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-05, WO-06 |

## 5. Functions, `src/js/engine/walk/walk-record.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimRecAngle(a, b)`**: the signed turn from a to b in -pi..pi: (b - a) mod 2 pi, less 2 pi when over pi, plus 2 pi when under -pi.
- **WO-02 `bimRecAdd(path, pose, t, minDist, minTurn)`**: a copy of the path, with {t, p (copied), yaw, pitch (0 when absent)} added unless there is a last pose and the move is under minDist (0.05), the yaw turn (bimRecAngle) under minTurn (0.02) and the pitch change under minTurn.
- **WO-03 `bimRecAt(path, t)`**: null for no path; the first pose at or before the first time, the last after the last; else between the two poses around t, u = (t - a.t)/(b.t - a.t): positions and pitch linear, yaw a.yaw + bimRecAngle(a.yaw, b.yaw) u.
- **WO-04 `bimRecInfo(path)`**: {length: the sum of the 3D steps, duration: last t - first t, poses: the count}; zeros for no path.

## 6. Order of the work

WO-01 to WO-04 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-05** wiring into walk; **WO-06** the records.

## 7. Not in this phase

Editing a path's poses; music and titles; a video codec of our own (the browser's mediarecorder).
