# V208 work orders: Walkthrough W2, drive

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/walk/walk-drive.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v208/v208.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v208/v208.test.mjs
    node --check src/js/engine/walk/walk-drive.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimDrvStep(s, inp, dt, P)`

- **It must:** SPEC 5 WO-01: state {x, z, heading, speed}, input {throttle 0..1, brake 0..1, steer -1..1}, params {wheelbase 2.7, maxSteer 0.6, accel 3, decel 7, drag 0.05, vmax 13.9} (each when not given or not positive; drag when not given): speed + (throttle accel - drag speed) dt, then less brake decel dt (never under 0), clamped to 0..vmax; steering angle steer maxSteer clamped to +-maxSteer; heading + speed / wheelbase tan(angle) dt; position + speed (cos h, sin h) dt with the new heading.
- **May use:** nothing.
- **Files:** `src/js/engine/walk/walk-drive.js`, `docs/work-orders/v208/v208.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v208/v208.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-02 [Cline] `bimDrvTurnRadius(L, steer)`

- **It must:** SPEC 5 WO-02: L / tan|steer|; Infinity when |steer| < 1e-9.
- **May use:** nothing.
- **Files:** `src/js/engine/walk/walk-drive.js`, `docs/work-orders/v208/v208.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v208/v208.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimDrvChase(s, dist, height)`

- **It must:** SPEC 5 WO-03: {eye: [x - dist cos h, height, z - dist sin h], target: [x, 0.4 height, z]}.
- **May use:** nothing.
- **Files:** `src/js/engine/walk/walk-drive.js`, `docs/work-orders/v208/v208.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v208/v208.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimDrvKmh(ms)`

- **It must:** SPEC 5 WO-04: Math.round(ms 3.6).
- **May use:** nothing.
- **Files:** `src/js/engine/walk/walk-drive.js`, `docs/work-orders/v208/v208.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v208/v208.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Claude] Wiring into Walk

Claude's: the mode in V203's Walk (its menu, keys and touch controls, the rendered view), saving where needed; the test to tests/unit/; npm run modules; the browser check on phone, tablet and desktop.

---

## [ ] WO-06 [Claude] The records

PIPELINE row 208, Notion.
