# V211 work orders: Walkthrough W5, record and replay

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/walk/walk-record.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v211/v211.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v211/v211.test.mjs
    node --check src/js/engine/walk/walk-record.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimRecAngle(a, b)`

- **It must:** SPEC 5 WO-01: the signed turn from a to b in -pi..pi: (b - a) mod 2 pi, less 2 pi when over pi, plus 2 pi when under -pi.
- **May use:** nothing.
- **Files:** `src/js/engine/walk/walk-record.js`, `docs/work-orders/v211/v211.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v211/v211.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimRecAdd(path, pose, t, minDist, minTurn)`

- **It must:** SPEC 5 WO-02: a copy of the path, with {t, p (copied), yaw, pitch (0 when absent)} added unless there is a last pose and the move is under minDist (0.05), the yaw turn (bimRecAngle) under minTurn (0.02) and the pitch change under minTurn.
- **May use:** bimRecAngle (WO-01).
- **Files:** `src/js/engine/walk/walk-record.js`, `docs/work-orders/v211/v211.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v211/v211.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimRecAt(path, t)`

- **It must:** SPEC 5 WO-03: null for no path; the first pose at or before the first time, the last after the last; else between the two poses around t, u = (t - a.t)/(b.t - a.t): positions and pitch linear, yaw a.yaw + bimRecAngle(a.yaw, b.yaw) u.
- **May use:** bimRecAngle (WO-01).
- **Files:** `src/js/engine/walk/walk-record.js`, `docs/work-orders/v211/v211.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v211/v211.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-04 [Cline] `bimRecInfo(path)`

- **It must:** SPEC 5 WO-04: {length: the sum of the 3D steps, duration: last t - first t, poses: the count}; zeros for no path.
- **May use:** nothing.
- **Files:** `src/js/engine/walk/walk-record.js`, `docs/work-orders/v211/v211.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v211/v211.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Claude] Wiring into Walk

Claude's: the mode in V203's Walk (its menu, keys and touch controls, the rendered view), saving where needed; the test to tests/unit/; npm run modules; the browser check on phone, tablet and desktop.

---

## [ ] WO-06 [Claude] The records

PIPELINE row 211, Notion.
