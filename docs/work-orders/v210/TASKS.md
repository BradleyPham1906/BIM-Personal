# V210 work orders: Walkthrough W4, swim

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/walk/walk-swim.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v210/v210.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v210/v210.test.mjs
    node --check src/js/engine/walk/walk-swim.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimSwmUnder(eyeY, waterY)`

- **It must:** SPEC 5 WO-01: true when waterY is a number and eyeY < waterY.
- **May use:** nothing.
- **Files:** `src/js/engine/walk/walk-swim.js`, `docs/work-orders/v210/v210.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v210/v210.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimSwmStep(v, inp, dt, P)`

- **It must:** SPEC 5 WO-02: each axis i: v_i + (inp_i thrust - drag v_i + (buoy on the y axis)) dt; drag 2 and thrust 1.5 unless positive, buoy 0.3 unless a number; a missing input is 0.
- **May use:** nothing.
- **Files:** `src/js/engine/walk/walk-swim.js`, `docs/work-orders/v210/v210.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v210/v210.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimSwmFog(depth, clear)`

- **It must:** SPEC 5 WO-03: depth / clear (8 unless positive) clamped to 0..1.
- **May use:** nothing.
- **Files:** `src/js/engine/walk/walk-swim.js`, `docs/work-orders/v210/v210.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v210/v210.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimSwmSurface(pos, waterY, eye)`

- **It must:** SPEC 5 WO-04: when pos[1] > waterY - eye (eye 0.2 unless positive), the point at waterY - eye; else a copy.
- **May use:** nothing.
- **Files:** `src/js/engine/walk/walk-swim.js`, `docs/work-orders/v210/v210.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v210/v210.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Claude] Wiring into Walk

Claude's: the mode in V203's Walk (its menu, keys and touch controls, the rendered view), saving where needed; the test to tests/unit/; npm run modules; the browser check on phone, tablet and desktop.

---

## [ ] WO-06 [Claude] The records

PIPELINE row 210, Notion.
