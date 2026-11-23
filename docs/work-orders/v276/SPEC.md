# V276 spec: the input layer and the simulated hand

Research: `docs/research/research-xr-interaction.md` (H4, E3, E4) with `research-xr-interaction/devices.md` and
`gestures.md`, and `docs/research/research-devices-xr.md` (XR-2: MediaPipe in a worker, the One Euro filter, the
calibration; measured on the owner's iPhone 13: 35 to 39 hand frames a second). The owner's decisions, 2026-11-23:
E1 to E8, E4 changed by the owner ("i need the skeleton and actual hand simulated so it can accurately interact with
models"); D2 (MediaPipe 1.2.3 vendored) and D3 (Jolt reused) from the cardboard research. Experiment E5 (this spec):
where the WebXR generic hand's metacarpal joints sit, `docs/research/experiments/xr-interaction/hand_bind_pose.py`.
Implementation target: local `main`. Written by Claude, 2026-11-23.

## 1. What it does for the user

Hands become an input on every device, the same way a mouse is. On a phone or a computer with a camera, the app tracks
the hands (MediaPipe, in the background) and shows them as real hands: a skinned hand model bending at every knuckle,
driven by a 25-joint skeleton, the same skeleton a Quest or Vision Pro reports (V277). Each bone carries a physics
capsule, so a fingertip presses, the side of a hand pushes, and a pinch grabs. Pinch with the palm toward you is never
an action (the system menu gesture on headsets). A mouse, a touch, a hand ray and (V277) a headset pinch all reach the
app's commands through one pointer: press, drag, release, click, cancel; two hands together move, turn about the
vertical and scale the model. A one-time calibration (hold up an open hand at a set distance) fixes the camera's focal
length and the hand's span, so depth from one camera is a few centimetres, not tens.

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/xr/hand-model.js` | new, after `js/engine/render/headset.js` in `src/index.html` (header done) | 8 pure functions (part 4) | Cline, WO-01 to WO-08 |
| `docs/work-orders/v276/v276.test.mjs` | new | their tests | Claude (done) |
| `runtime/mediapipe/1.2.3/`, `runtime/webxr-hands/1.0.20/`, `tools/three/build_three.mjs` | new, changed | MediaPipe and its hand model; the generic hand models; `XRHandMeshModel` in the three.js bundle | Claude, WO-09, WO-10 |
| the camera worker, the Jolt hand, the pointer wiring, the calibration | new, changed | Claude, WO-11, WO-12 |

## 3. Data

- **MediaPipe points** `lm`: 21 `[x, y, z]` in MediaPipe's order (0 wrist; 1 to 4 thumb CMC, MCP, IP, tip; 5 to 8
  index MCP, PIP, DIP, tip; 9 to 12 middle; 13 to 16 ring; 17 to 20 pinky), in metres once placed in the world.
- **The skeleton** `j`: 25 `[x, y, z]` in the WebXR Hand Input order: 0 wrist; 1 to 4 thumb metacarpal, proximal,
  distal, tip; then for index (5 to 9), middle (10 to 14), ring (15 to 19), pinky (20 to 24): metacarpal, proximal,
  intermediate, distal, tip. Each joint's parent: the wrist for every metacarpal, else the joint before it.
- **The metacarpal fractions** (E5, the generic hand, both sides): index 0.37 (0.398 left, 0.341 right), middle 0.32,
  ring 0.33, pinky 0.50 of the way from the wrist to the knuckle; at most 6.7 mm off that line.
- **A capsule** `{from, to, a: [x, y, z], b: [x, y, z], r}` metres.
- **A pointer state** `{phase: 'idle' | 'down' | 'drag', start: point or null}`; a pointer event
  `{type: 'down' | 'move' | 'up' | 'cancel', p: point}` (2D pixels or 3D metres; the threshold is in the same unit).

## 4. Functions, `src/js/engine/xr/hand-model.js`

ES5. Pure: none changes what it is given; none uses another file's names.

### WO-01 `bimHdFrom21(lm)`
- **Returns:** the 25 joints (new arrays): the wrist; the thumb's four from MediaPipe 1 to 4; for each finger, its
  metacarpal at `wrist + (knuckle - wrist) * f` with `f` 0.37 (index), 0.32 (middle), 0.33 (ring), 0.5 (pinky), the
  knuckle being MediaPipe 5, 9, 13, 17; then the finger's four MediaPipe points in order. Null unless 21 points.

### WO-02 `bimHdEuro(state, x, t, opts)`
- **The One Euro filter** (Casiez, Roussel and Vogel, CHI 2012), one number. `opts` `{minCutoff (Hz, default 1),
  beta (default 0), dCutoff (Hz, default 1)}`; `t` seconds. `alpha(fc, dt) = 1 / (1 + (1 / (2 pi fc)) / dt)`.
- **Returns:** `{state, value}`. No state: `{state: {x: x, dx: 0, t: t}, value: x}`. `dt = t - state.t`; when not above
  0, the last value and a copy of the state. Else `dx = (x - state.x) / dt`;
  `edx = state.dx + alpha(dCutoff, dt) (dx - state.dx)`; `fc = minCutoff + beta |edx|`;
  `value = state.x + alpha(fc, dt) (x - state.x)`; the new state `{x: value, dx: edx, t: t}`.

### WO-03 `bimHdPinch(prev, d, enter, exit)`
- **Returns:** whether the thumb and index tips (`d` metres apart) pinch: when `prev`, `d < exit`, else `d < enter`;
  `enter` 0.015 and `exit` 0.025 by default (three.js's thresholds, confirmed by the check); false when `d` is not a
  finite number (tracking lost lets go).

### WO-04 `bimHdDepth(spanM, spanPx, fPx)`
- **Returns:** the hand's distance from the camera, `spanM * fPx / spanPx` metres; null unless all three are above 0.

### WO-05 `bimHdPalmFacing(j, hand, eye, cosMin)`
- **Returns:** whether the palm faces the eye: the normal `n = (j[6] - j[0]) x (j[21] - j[0])` (index knuckle and pinky
  knuckle from the wrist), reversed for `hand === 'left'`; true when the cosine between `n` and the direction from the
  palm centre (the mean of j[0], j[6], j[21]) to `eye` is above `cosMin` (default 0.5, 60 degrees); false when either
  length is under 1e-12.
- **Why:** a right hand palm down with fingers forward has its index knuckle at -X and pinky at +X, and that cross
  product points down, out of the palm.

### WO-06 `bimHdCapsules(j, radii)`
- **Returns:** 24 capsules, one for each joint 1 to 24 in order, from its parent to it: `a` the parent's position, `b`
  the joint's, `r` the joint's radius from `radii` (WebXR gives one per joint) when a number above 0, else 0.008. `[]`
  unless 25 joints.

### WO-07 `bimInTwoHand(a0, b0, a1, b1)`
- **The handle bar** (Song et al. 2012; MRTK3's code): the two hands at the start (`a0`, `b0`) and now (`a1`, `b1`).
- **Returns:** `{s: |b1 - a1| / |b0 - a0|, rot, t}`: `rot` the change in the plan heading `atan2(dz, dx)` of the
  vector from a to b, brought into (-pi, pi]; `t` the move of the midpoint. Null when the hands started under 2 cm apart
  or are now on top of each other.

### WO-08 `bimInPointerNext(state, ev, threshold)`
- **Returns:** `{state, emit}` (a new state, never the given one). `threshold` default 0.01 (metres; pass pixels for
  2D). From idle: down gives phase 'down' with `start` a copy of `ev.p` and `['press']`; move or up gives nothing.
  From down: a move farther than the threshold from `start` gives 'drag' and `['dragstart', 'drag']`, nearer gives
  nothing; up gives idle and `['release', 'click']`. From drag: move gives `['drag']`; up gives idle and
  `['release', 'dragend']`. Cancel from down or drag gives idle and `['cancel']`. A down while not idle, and any other
  event, change nothing.

## 5. Order of the work

WO-01 to WO-08 in any order (WO-05's and WO-06's tests use WO-01). Then Claude:

- **WO-09 MediaPipe vendored** (D2, the library rule): `@mediapipe/tasks-vision` 1.2.3 (Apache-2.0) and the float16
  `hand_landmarker.task` (SHA-256 `fbc2a300...07cde1`) under `runtime/mediapipe/1.2.3/`, pinned in `MANIFEST.json`
  with their licences, loaded only when hands are turned on; a module worker (GPU, CPU on failure; GPU in a worker
  tested by feature for iOS 17); the One Euro filter on each joint.
- **WO-10 the hand mesh** (E4): `XRHandMeshModel` added to `tools/three/build_three.mjs`'s bundle (three.js's own MIT
  code, rebuilt and re-pinned), the generic `left.glb` and `right.glb` from `@webxr-input-profiles/assets` 1.0.20 (MIT)
  under `runtime/webxr-hands/1.0.20/`, loaded from there, never the CDN; the skeleton drives it.
- **WO-11 the simulated hand in Jolt** (D3): beside `walk/walk-physics.js`, a capsule body for each of WO-06's bones,
  driven by velocity toward its joint each step (a speed cap, continuous collision, put back when more than 10 cm
  behind); a pinch near an element grabs it (a constraint), release keeps the hand's speed; the model's elements
  static unless marked movable.
- **WO-12 the pointer wiring and the calibration**: mouse, touch, the hand ray and pinch into WO-08's pointer; WO-07's
  two-hand transform on the model; WO-05 gating every pinch; the calibration (an open hand at a marked distance) for
  WO-04's focal length and span.
- **WO-13** the tests to `tests/unit/`, `npm run modules`, the build, the one browser check (CLAUDE.md Rule #1).
- **WO-14** the records.

## 6. Not in this phase

Headset sessions and their joints (V277); 3D menus (V277); BIM tasks in the headset (V278); custom hand poses beyond
pinch, poke and palm-up; hand tracking of more than two hands.
