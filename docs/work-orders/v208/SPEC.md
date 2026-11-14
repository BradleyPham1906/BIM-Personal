# V208 spec: Walkthrough W2, drive

Notion: Later: Walkthrough W2-W5, drive, fly, swim, record. Research: `docs/research/research-walkthrough.md`, `docs/research/research-scenario-3d-skills.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- W2 drives a car on the model and V171's streets: a kinematic bicycle model (wheelbase 2.7 m, steering up to 0.6 rad, 50 km/h top speed by default), not a physics engine's vehicle, so it runs on any device; Jolt's wheeled vehicle (V203's pinned Jolt) later if the owner asks.
- A chase camera 6 m behind and 2.5 m up; speed shown in km/h.
- The same controls as W1 on phone, tablet and desktop: W/S throttle and brake, A/D steer, the joystick on touch.

## 2. What it does for the user

Drive (in the Walk menu): a car on the streets, steered with the keys or the joystick, the camera behind it, the speed on screen.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/walk/walk-drive.js` | new, after `js/engine/walk/walk-math.js` in `src/index.html` (header done) | 4 pure functions (part 5) | Cline, WO-01 to WO-04 |
| `docs/work-orders/v208/v208.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-05, WO-06 |

## 5. Functions, `src/js/engine/walk/walk-drive.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimDrvStep(s, inp, dt, P)`**: state {x, z, heading, speed}, input {throttle 0..1, brake 0..1, steer -1..1}, params {wheelbase 2.7, maxSteer 0.6, accel 3, decel 7, drag 0.05, vmax 13.9} (each when not given or not positive; drag when not given): speed + (throttle accel - drag speed) dt, then less brake decel dt (never under 0), clamped to 0..vmax; steering angle steer maxSteer clamped to +-maxSteer; heading + speed / wheelbase tan(angle) dt; position + speed (cos h, sin h) dt with the new heading.
- **WO-02 `bimDrvTurnRadius(L, steer)`**: L / tan|steer|; Infinity when |steer| < 1e-9.
- **WO-03 `bimDrvChase(s, dist, height)`**: {eye: [x - dist cos h, height, z - dist sin h], target: [x, 0.4 height, z]}.
- **WO-04 `bimDrvKmh(ms)`**: Math.round(ms 3.6).

## 6. Order of the work

WO-01 to WO-04 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-05** wiring into walk; **WO-06** the records.

## 7. Not in this phase

Traffic interaction; gears and engine sound; off-road physics.
