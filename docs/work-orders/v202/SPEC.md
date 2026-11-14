# V202 spec: Walkthrough W1, walk

Research: `docs/research/research-walkthrough.md` (the owner's decisions D1 to D7, 2026-11-14, in its part 11).
Implementation target: local `main`. Written by Claude, 2026-11-14. Cline reads this with TASKS.md; keep it exact and plain.

## 1. What it does for the user

**Walk** (the command `WALK`, a button in the View menu and on the view's toolbar) puts the user into their own
model as a person, at a person's eye height, in whatever visual style the view is in (wireframe, shaded, rendered,
and the rest: walking is a way of moving, not a style). Walls stop them; they climb stairs, ramps and curbs a code
stair allows and no higher; gravity holds them to the floor and they fall off an edge. They look around with the
mouse and move with W, A, S, D; on a phone or tablet with a joystick under the left thumb and a drag anywhere else.

They can switch, with a key or a button:
- **first person** (their own eyes) and **third person** (behind and above their figure, a V169 person), V;
- **Walk** and **Fly** (no gravity, Space rises, C sinks), F;
- **through walls** while Alt is held (or the ghost button is on).

Esc, or the Leave button, ends the walk and puts the camera back where it was. The figure is the registry's mean
adult by default; Walk's settings in Properties change it (a man, a woman, a child, their own height, or a
wheelchair user, who steps no step and climbs no slope steeper than 1:12).

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/walk/walk-math.js` | new (its header in place) | the pure arithmetic: step, capsule, look, move, the two cameras, the joystick, the keys | Cline, WO-01 to WO-08 |
| `tools/jolt/build_jolt.mjs`, `tools/jolt/package.json` | new | Jolt 1.1.1 bundled unchanged into one classic script, as `tools/three` does three.js | Claude, C-02 |
| `runtime/jolt/1.1.1/bim-jolt.min.js`, `LICENSE` | new | the pinned engine (global `BIMJOLT`) | Claude, C-02 |
| `runtime/MANIFEST.json`, `THIRD_PARTY_NOTICES.md` | changed | its size, SHA-256 and credit | Claude, C-02 |
| `src/js/engine/standards/registry.js` | changed | `stair.riser` (IRC, IBC, Philadelphia) and `walk.rules` (the walker's slope, run factor) | Claude, C-03 |
| `src/js/engine/walk/walk-physics.js` | new | the Jolt adapter: load, the world, a body per element, the character, the step, the ray for the third-person camera, disposal | Claude, C-04 |
| `src/js/engine/walk/walk-mode.js` | new | `WALK`: enter and leave, the frame loop, the modes, the camera, the figure, the start point | Claude, C-05 |
| `src/js/engine/walk/walk-controls.js` | new | keys, pointer lock, the joystick and buttons on the page | Claude, C-06 |
| `src/css/workspace/walk.css` | new | the joystick, the buttons, the hint, at phone, tablet and desktop | Claude, C-06 |
| `src/js/engine/render/webgl.js` | changed | the near plane 0.05 m while walking | Claude, C-05 |
| `src/js/engine/render/rendered-view.js`, `rendered-core.js` | changed | the moving mode: one pass a frame, shadows framed around the walker, refining when still | Claude, C-07 |
| `tests/unit/walk.test.mjs` | new | WO-01 to WO-08's tests moved in, and the adapter's | Claude, C-08 |
| `tests/e2e/bim_phase202_walk_check.mjs` | new | the phase's one browser check | Claude, C-08 |

## 3. Data

- **A walker's body** (`B`, from `bimEntBody` in `assets/scale-assets.js`, or the wheelchair record): `{top: 1.75,
  eye: 1.63, sh: 0.46, chair: false}`, metres. `top` the height, `eye` the eye height, `sh` the shoulder width.
- **The rules** (`R`, from the registry, C-03): `{stepUp: 0.206, slopeDeg: 35, chairSlope: 1/12}`.
- **The capsule** (`bimWalkCapsule`): `{h, r, half, eye, step, slope}`: height, radius, the cylinder's half
  height, the eye height, the step it climbs (m), the steepest slope it climbs (radians).
- **What is held** (`bimWalkKeys`): `{f, s, run, up, ghost}`: forward and right in -1..1, running, rising (1),
  sinking (-1) or neither (0), passing through walls.
- **The joystick** (`bimWalkJoy`): `{s, f}` in the unit circle.
- **A camera** (`bimWalkCamFirst`, `bimWalkCamThird`): the app's own camera fields `{tx, ty, tz, yaw, pitch, dist}`,
  so a walk is seen by every view and saved views and project tabs keep working.
- **The walk's state** (`A3D_WALK`, C-05): `{on, mode: 'walk'|'fly', view: 'first'|'third', ghost, yaw, pitch, p:
  [x, y, z] (the feet), cap, saved (the camera before), held, joy, last (the frame time)}`.

## 4. Functions

Conventions, from the app's camera (`core/mesh-primitives.js` `camVecs`): y is up; `d = [cos(pitch) sin(yaw),
sin(pitch), cos(pitch) cos(yaw)]`; the eye is the focus plus `d * dist`, so one looks along `-d`. Walking forward
is `[-sin(yaw), 0, -cos(yaw)]`, walking right `[cos(yaw), 0, -sin(yaw)]`. A positive pitch looks down.

### `bimWalkStepUp(riserIn, varIn)` - walk-math.js - WO-01
- **Takes:** the steepest riser in inches; the variation a flight may have, in inches.
- **Returns:** `(riserIn + varIn)` in metres, rounded to the millimetre: `Math.round((r + v) * 25.4) / 1000`.
- **Rules:** a riser that is not a number above 0 returns 0; a variation that is not a number above 0 counts as 0.
- **Example:** `bimWalkStepUp(7.75, 0.375)` returns `0.206`.

### `bimWalkCapsule(B, R)` - walk-math.js - WO-02
- **Returns:** `{h, r, half, eye, step, slope}`. `h` = `B.top` when above 0, else 1.75. `r` = `B.sh / 2` kept
  between 0.2 and 0.35 (a missing `sh` counts as 0). `half` = `(h - 2r) / 2`, at least 0.05. `eye` = `B.eye` when
  above 0, else `h - 0.12`. `step` = 0 for `B.chair`, else `R.stepUp`. `slope` = `Math.atan(R.chairSlope)` for
  `B.chair`, else `R.slopeDeg * Math.PI / 180`.
- **Example:** `bimWalkCapsule({top: 1.75, eye: 1.63, sh: 0.46}, {stepUp: 0.206, slopeDeg: 35, chairSlope: 1/12})`
  returns `{h: 1.75, r: 0.23, half: 0.645, eye: 1.63, step: 0.206, slope: 0.6109}`.

### `bimWalkLook(v, dx, dy, k)` - walk-math.js - WO-03
- **Takes:** `{yaw, pitch}`; the mouse's or finger's movement in pixels; radians per pixel.
- **Returns:** a new `{yaw, pitch}` (the argument is not changed): `yaw - dx * k` wrapped into (-pi, pi]; `pitch + dy * k`
  kept within -1.5 and 1.5.
- **Example:** `bimWalkLook({yaw: 0, pitch: 0}, 100, 50, 0.002)` returns `{yaw: -0.2, pitch: 0.1}`.

### `bimWalkMove(inp, yaw, speed, fly)` - walk-math.js - WO-04
- **Returns:** `[vx, vy, vz]` in m/s: the horizontal `inp.f * forward + inp.s * right`, scaled down to length 1 when
  longer (never up), times `speed`, times 2 when `inp.run`; `vy` = `inp.up * speed` (times 2 running) when `fly`,
  else 0 (gravity is the physics').
- **Example:** `bimWalkMove({f: 1, s: 0, run: false, up: 0}, 0, 1.34, false)` returns `[0, 0, -1.34]`.

### `bimWalkCamFirst(p, eye, yaw, pitch)` - walk-math.js - WO-05
- **Takes:** the feet `[x, y, z]`; the eye height; the look.
- **Returns:** `{tx, ty, tz, yaw, pitch, dist: 1}` with the focus `[p0, p1 + eye, p2] - d`, so the camera's eye is the
  walker's eyes.
- **Example:** `bimWalkCamFirst([2, 0, 3], 1.6, 0, 0)` returns `{tx: 2, ty: 1.6, tz: 2, yaw: 0, pitch: 0, dist: 1}`.

### `bimWalkCamThird(p, eye, yaw, pitch, boom, hit)` - walk-math.js - WO-06
- **Takes:** as WO-05, plus the boom's length (m) and the distance to the first thing behind the walker's eyes along
  `d` (a number, or `null` / `Infinity` when nothing is hit).
- **Returns:** `{tx: p0, ty: p1 + eye, tz: p2, yaw, pitch, dist}`; `dist` = `boom`, or `max(0.3, hit - 0.2)` when `hit`
  is a finite number and `hit - 0.2 < boom`.
- **Example:** `bimWalkCamThird([0, 0, 0], 1.6, 0, 0, 3, 1.5).dist` is `1.3`.

### `bimWalkJoy(cx, cy, x, y, R, dead)` - walk-math.js - WO-07
- **Takes:** the ring's middle and the finger in page pixels; the ring's radius; the dead zone as a fraction.
- **Returns:** `{s: (x - cx) / R, f: (cy - y) / R}` scaled down to length 1 when longer; `{s: 0, f: 0}` when its length is
  under `dead`, or `R` is not above 0.
- **Example:** `bimWalkJoy(100, 100, 100, 75, 50, 0.12)` returns `{s: 0, f: 0.5}`.

### `bimWalkKeys(held, joy)` - walk-math.js - WO-08
- **Takes:** an object of `KeyboardEvent.code` to `true` for each key held (a `false` is not held; `null` is none
  held); the joystick's `{s, f}` or `null`.
- **Returns:** `{f, s, run, up, ghost}`: `f` = (KeyW or ArrowUp) - (KeyS or ArrowDown) + `joy.f`, kept within -1 and 1;
  `s` = (KeyD or ArrowRight) - (KeyA or ArrowLeft) + `joy.s`, kept within -1 and 1; `run` = ShiftLeft or ShiftRight;
  `up` = Space - KeyC; `ghost` = AltLeft or AltRight. Booleans are `true` or `false`.
- **Example:** `bimWalkKeys({KeyW: true, KeyD: true}, null)` returns `{f: 1, s: 1, run: false, up: 0, ghost: false}`.

### Claude's (C-02 to C-08), in outline

- **`bimWalkLoad()`** (walk-physics.js): loads `runtime/jolt/1.1.1/bim-jolt.min.js` as `bimRvLoad` loads three.js
  (`render/rendered-view.js:76`: the page's own `runtime/` under `file://`, then Pages with SRI), then `BIMJOLT.default()`;
  a promise of Jolt. A failure is warned and toasted; the walk does not start.
- **`bimWalkWorld(items)`**: one static Jolt mesh body per element, from the same records the rendered view keeps
  (`rendered-core.js:220`, keyed by element, rebuilt when its signature changes): opaque triangles only (glass is
  solid: it is opaque here), two-sided. Built element by element across frames so a large model never blocks the page.
- **`bimWalkCharacter(cap)`**, **`bimWalkStep(v, dt)`**: Jolt's `CharacterVirtual` with `ExtendedUpdate`, its stairs
  step-up `cap.step` and floor stick 0.3 m, its steepest slope `cap.slope`; Walk adds gravity, Fly none; ghost moves the
  feet without the character. Every Jolt object the adapter makes, it destroys (`Jolt.destroy`) when the walk ends.
- **`bimWalkRay(from, dir, max)`**: the first hit along a ray, for the third-person boom.
- **`bimWalkStart()`**: the feet on the first floor below the view's focus (a ray down), or the ground at the focus;
  never inside a solid (a ray up from below confirms the space is clear).
- **The frame** (walk-mode.js): every animation frame, with `dt` capped at 1/20 s: the keys and joystick to
  `bimWalkKeys`, to `bimWalkMove`, to the physics, to `bimWalkCamFirst` or `bimWalkCamThird` into `A3D.cam`, then the
  view redrawn. The figure (`bimEntPersonMesh`, `bimEntChairMesh`) drawn at the feet, turned to the yaw, in third
  person only.
- **The near plane** (`webgl.js:33`): 0.05 m while walking, as before otherwise.
- **The rendered view's moving mode** (C-07): while the camera moves, one pass a frame with filtered (PCF) shadows framed
  around the walker; when still for 300 ms, it refines as it does now.

## 5. Order of the work

1. **C-01** (done in the spec's pull request): `walk-math.js` exists, with its header, in `src/index.html`'s order.
2. **WO-01 to WO-08** (Cline), in any order: each one function in `walk-math.js` with its tests. Nothing calls them yet,
   so nothing changes in the app.
3. **C-02** Jolt pinned; **C-03** the registry's records (reading the IRC and Philadelphia at the source first).
4. **C-04** the adapter, tried in Node against e01's course before it is wired.
5. **C-05, C-06**: `WALK` works in every view on desktop, then phone and tablet. The owner can walk from here.
6. **C-07** the rendered view's moving mode. **C-08** the tests into `tests/unit`, the guide's page, the browser check.

## 6. Not in this phase

Driving, the drone, swimming and recording a path (W2 to W5). Opening doors. Other walkers or cars colliding with the
user. Footstep sounds. VR headsets. A walk saved with the project (only the camera, as now).
