# V203 work orders: Walkthrough W1, walk

Spec: `SPEC.md` in this folder (part 4 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function to `src/js/engine/walk/walk-math.js`, below the file's header comment, and
change nothing else: not another file, not the header, no `import`/`export` lines, not `canvas_v10.html`. ES5 only:
`var`, `function`; no `let`, `const`, arrow functions, classes or template strings. The functions use **no other
engine name** and keep no state: only their arguments and `Math`. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v203/v203.test.mjs`, outside `npm test` until C-08, so main stays green. They load
`walk-math.js` by itself. After each task run its own cases, the file's syntax check and the unit tests (Rule #1, one
file of logic):

    node --test --test-name-pattern="WO-01" docs/work-orders/v203/v203.test.mjs
    node --check src/js/engine/walk/walk-math.js
    npm test

Nothing calls these functions until C-05, so rebuilding `canvas_v10.html` is not needed after each task.
Scores are from `../ROUTING.md` (files, logic, understanding, judgment, trickiness, check).

---

## [x] C-01 [Claude] `walk-math.js` in the page's order

Done with the spec (2026-11-14): the file with its header, its `<!-- @include -->` after `render/viewcube.js`, the
modules, the build. `npm test` 259 of 259.

---

## [x] WO-01 [Cline] `bimWalkStepUp(riserMm, varMm)`

- **It must:** return `Math.round(riserMm + varMm) / 1000` (millimetres in, metres out, to the millimetre). A `riserMm`
  that is not a number above 0 (a string, `NaN`, 0, negative) returns `0`. A `varMm` that is not a number above 0 counts as `0`.
- **Example:** `bimWalkStepUp(196, 9.5)` returns `0.206`; `bimWalkStepUp(178, undefined)` returns `0.178`.
- **May use:** `Math.round`.
- **Files:** `src/js/engine/walk/walk-math.js`, `docs/work-orders/v203/v203.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-01 ...`. **Score:** 0+0+0+0+0+0 = 0.

---

## [x] WO-02 [Cline] `bimWalkCapsule(B, R)`

- **It must:** return a new object `{h, r, half, eye, step, slope}`:
  - `h`: `B.top` when it is above 0, else `1.75`;
  - `r`: `B.sh / 2` (a missing `B.sh` counts as 0), kept within `0.2` and `0.35`;
  - `half`: `(h - 2 * r) / 2`, at least `0.05`;
  - `eye`: `B.eye` when it is above 0, else `h - 0.12`;
  - `step`: `0` when `B.chair` is true, else `R.stepUp`;
  - `slope`: `Math.atan(R.chairSlope)` when `B.chair` is true, else `R.slopeDeg * Math.PI / 180`.
- **Example:** `bimWalkCapsule({top: 1.75, eye: 1.63, sh: 0.46}, {stepUp: 0.206, slopeDeg: 35, chairSlope: 1 / 12})`
  returns `{h: 1.75, r: 0.23, half: 0.645, eye: 1.63, step: 0.206, slope: 0.6109}` (slope rounded here).
- **May use:** `Math.min`, `Math.max`, `Math.atan`, `Math.PI`.
- **Files:** `src/js/engine/walk/walk-math.js`, `docs/work-orders/v203/v203.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-02 ...`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-03 [Cline] `bimWalkLook(v, dx, dy, k)`

- **It must:** return a new object `{yaw, pitch}` and leave `v` unchanged. `yaw` = `v.yaw - dx * k`, then while it is
  above `Math.PI` take `2 * Math.PI` off, and while it is at or below `-Math.PI` add `2 * Math.PI`. `pitch` =
  `v.pitch + dy * k`, kept within `-1.5` and `1.5`.
- **Example:** `bimWalkLook({yaw: 0, pitch: 0}, 100, 50, 0.002)` returns `{yaw: -0.2, pitch: 0.1}`;
  `bimWalkLook({yaw: 3.1, pitch: 0}, -100, 0, 0.002).yaw` is `3.3 - 2 * Math.PI`.
- **May use:** `Math.PI`, `Math.min`, `Math.max`.
- **Files:** `src/js/engine/walk/walk-math.js`, `docs/work-orders/v203/v203.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-03 ...`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-04 [Cline] `bimWalkMove(inp, yaw, speed, fly)`

- **It must:** return `[vx, vy, vz]`:
  - `x = -Math.sin(yaw) * inp.f + Math.cos(yaw) * inp.s` and `z = -Math.cos(yaw) * inp.f - Math.sin(yaw) * inp.s`;
  - when `Math.sqrt(x * x + z * z)` is above 1, divide both by it (never scale up);
  - `m = speed * (inp.run ? 2 : 1)`; `vx = x * m`, `vz = z * m`;
  - `vy = inp.up * m` when `fly` is true, else `0`.
- **Example:** `bimWalkMove({f: 1, s: 0, run: false, up: 0}, 0, 1.34, false)` returns `[0, 0, -1.34]` (the 0 may be -0);
  `bimWalkMove({f: 1, s: 1, run: false, up: 0}, Math.PI / 2, 1, false)` returns about `[-0.7071, 0, -0.7071]`.
- **May use:** `Math.sin`, `Math.cos`, `Math.sqrt`.
- **Files:** `src/js/engine/walk/walk-math.js`, `docs/work-orders/v203/v203.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-04 ...`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-05 [Cline] `bimWalkCamFirst(p, eye, yaw, pitch)`

- **It must:** with `c = Math.cos(pitch)` and `d = [c * Math.sin(yaw), Math.sin(pitch), c * Math.cos(yaw)]`, return
  `{tx: p[0] - d[0], ty: p[1] + eye - d[1], tz: p[2] - d[2], yaw: yaw, pitch: pitch, dist: 1}`.
- **Why:** the app's camera puts its eye at the focus plus `d * dist`, so this eye is exactly at the walker's eyes.
- **Example:** `bimWalkCamFirst([2, 0, 3], 1.6, 0, 0)` returns `{tx: 2, ty: 1.6, tz: 2, yaw: 0, pitch: 0, dist: 1}`.
- **May use:** `Math.sin`, `Math.cos`.
- **Files:** `src/js/engine/walk/walk-math.js`, `docs/work-orders/v203/v203.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-05 ...`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] WO-06 [Cline] `bimWalkCamThird(p, eye, yaw, pitch, boom, hit)`

- **It must:** return `{tx: p[0], ty: p[1] + eye, tz: p[2], yaw: yaw, pitch: pitch, dist: D}`. `D` is `boom`, except
  when `hit` is a number, finite (`isFinite(hit)`), and `hit - 0.2 < boom`: then `D = Math.max(0.3, hit - 0.2)`.
- **Example:** `bimWalkCamThird([0, 0, 0], 1.6, 0, 0, 3, 1.5).dist` is `1.3`; with `hit` `0.2` it is `0.3`; with `hit`
  `null`, `10` or `Infinity` it is `3`.
- **May use:** `Math.max`, `isFinite`.
- **Files:** `src/js/engine/walk/walk-math.js`, `docs/work-orders/v203/v203.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-06 ...`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-07 [Cline] `bimWalkJoy(cx, cy, x, y, R, dead)`

- **It must:** return `{s: 0, f: 0}` when `R` is not a number above 0. Else `s = (x - cx) / R`, `f = (cy - y) / R` and
  `L = Math.sqrt(s * s + f * f)`; when `L < dead` return `{s: 0, f: 0}`; when `L > 1` divide both by `L`; return `{s: s, f: f}`.
- **Example:** `bimWalkJoy(100, 100, 100, 75, 50, 0.12)` returns `{s: 0, f: 0.5}`; `bimWalkJoy(100, 100, 103, 100, 50, 0.12)`
  returns `{s: 0, f: 0}`.
- **May use:** `Math.sqrt`.
- **Files:** `src/js/engine/walk/walk-math.js`, `docs/work-orders/v203/v203.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-07 ...`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-08 [Cline] `bimWalkKeys(held, joy)`

- **It must:** treat `held` `null` as `{}` and `joy` `null` as `{s: 0, f: 0}`. A key is held when `held[code]` is `true`.
  Return `{f, s, run, up, ghost}`:
  - `f` = (1 if `KeyW` or `ArrowUp` held) - (1 if `KeyS` or `ArrowDown` held) + `joy.f`, kept within -1 and 1;
  - `s` = (1 if `KeyD` or `ArrowRight` held) - (1 if `KeyA` or `ArrowLeft` held) + `joy.s`, kept within -1 and 1;
  - `run`: `ShiftLeft` or `ShiftRight` held; `ghost`: `AltLeft` or `AltRight` held (both `true` or `false`);
  - `up` = (1 if `Space` held) - (1 if `KeyC` held).
- **Example:** `bimWalkKeys({KeyW: true, KeyD: true}, null)` returns `{f: 1, s: 1, run: false, up: 0, ghost: false}`;
  `bimWalkKeys({}, {s: -0.25, f: 0.5})` returns `{f: 0.5, s: -0.25, run: false, up: 0, ghost: false}`.
- **May use:** `Math.min`, `Math.max`.
- **Files:** `src/js/engine/walk/walk-math.js`, `docs/work-orders/v203/v203.test.mjs`
- **Budget:** 25
- **Test:** the cases named `WO-08 ...`. **Score:** 0+0+0+0+1+0 = 1.

---

## [x] C-02 [Claude] Jolt Physics 1.1.1 pinned in `runtime/`

Done 2026-11-14: `runtime/jolt/1.1.1/bim-jolt.min.js` 4,011,306 bytes (951,172 gzipped), loaded from `file://` in
Chromium and `BIMJOLT.default()` started with `CharacterVirtual` present, no console errors; `check_runtime.py` 26 files.

`tools/jolt/` (package.json and lock pinning jolt-physics 1.1.1 and esbuild, `build_jolt.mjs` with `--check`, as
`tools/three`), the bundle (`external: ['node:*']`, experiment e02), its licence, `runtime/MANIFEST.json`,
`THIRD_PARTY_NOTICES.md`, `tools/check_runtime.py` passing. Protected paths; the build tools are always Claude's.
**Score:** 2+1+2+1+1+1 = 8, D.

## [x] C-03 [Claude] The registry's `stair.riser` and `walk.rules`

Done 2026-11-14: `stair.riser` (IRC R311.7.5.1: 196 mm and 9.5 mm, read in South Carolina's adoption, level S; the ICC's
own text and Philadelphia's amendment refuse scripts here, so Philadelphia's 210 mm is not applied) and `walk.rules`
(35 degrees, running at 2x; the app's assumption, level A). WO-01 now takes millimetres, the registry's own unit. The
wheelchair user's slope is `bimStd('ada.2010', 'ramp_slope')` where the site is in the US, else 1:12 (C-05).

Read the IRC R311.7.5.1, the IBC 1011.5.2 and Philadelphia's amendment at their sources first (the note's part 11
has them at S and U), then the records with their editions and places. Research and a shared file. **Score:** 1+1+2+2+1+1 = 8, D.

## [ ] C-04 [Claude] The Jolt adapter (`walk/walk-physics.js`)

SPEC part 4's outline; tried in Node on e01's course before wiring. WebAssembly, manual memory, async loading.
**Score:** 1+2+2+1+2+1 = 9, D.

## [ ] C-05 [Claude] `WALK`: the mode, the frame, the cameras, the figure (`walk/walk-mode.js`, `render/webgl.js`)

Shared state (`A3D.cam`), the render loop and the command catalogue. **Score:** 2+2+2+1+2+1 = 10, D.

## [ ] C-06 [Claude] The controls on the page (`walk/walk-controls.js`, `css/workspace/walk.css`)

Pointer lock, keys, the joystick and the buttons on phone, tablet and desktop. **Score:** 2+2+1+1+1+1 = 8, D.

## [ ] C-07 [Claude] The rendered view's moving mode

`rendered-view.js` and `rendered-core.js` (protected). **Score:** 2+1+2+1+2+2 = 10, D.

## [ ] C-08 [Claude] Tests, the guide, the browser check

WO-01 to WO-08's tests moved into `tests/unit/walk.test.mjs`; the adapter's tests; the guide's page; the phase's one
browser check (Rule #1: a phase's new interface, once, without asking), its script in `tests/e2e/`.
