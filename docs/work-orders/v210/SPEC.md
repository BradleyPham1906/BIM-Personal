# V210 spec: Walkthrough W4, swim

Notion: Later: Walkthrough W2-W5, drive, fly, swim, record. Research: `docs/research/research-walkthrough.md`, `docs/research/research-scenario-3d-skills.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- W4 swims under V143's water and V220's ponds: under water when the eye is below the surface; motion by thrust, linear drag and buoyancy (2, 0.3 and 1.5 by default), a blue haze with depth (clear at 8 m), kept 0.2 m under the surface while swimming on it.
- Above water W1's walk carries on unchanged.

## 2. What it does for the user

Walk into a pond: below the surface the view turns blue with depth, the swimmer drifts up gently, and Space and C rise and dive.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/walk/walk-swim.js` | new, after `js/engine/walk/walk-drone.js` in `src/index.html` (header done) | 4 pure functions (part 5) | Cline, WO-01 to WO-04 |
| `docs/work-orders/v210/v210.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-05, WO-06 |

## 5. Functions, `src/js/engine/walk/walk-swim.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimSwmUnder(eyeY, waterY)`**: true when waterY is a number and eyeY < waterY.
- **WO-02 `bimSwmStep(v, inp, dt, P)`**: each axis i: v_i + (inp_i thrust - drag v_i + (buoy on the y axis)) dt; drag 2 and thrust 1.5 unless positive, buoy 0.3 unless a number; a missing input is 0.
- **WO-03 `bimSwmFog(depth, clear)`**: depth / clear (8 unless positive) clamped to 0..1.
- **WO-04 `bimSwmSurface(pos, waterY, eye)`**: when pos[1] > waterY - eye (eye 0.2 unless positive), the point at waterY - eye; else a copy.

## 6. Order of the work

WO-01 to WO-04 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-05** wiring into walk; **WO-06** the records.

## 7. Not in this phase

Waves and currents; drowning or breath; water rendering itself (v220).
