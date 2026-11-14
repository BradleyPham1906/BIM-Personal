# V209 work orders: Walkthrough W3, fly and drone

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/walk/walk-drone.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v209/v209.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v209/v209.test.mjs
    node --check src/js/engine/walk/walk-drone.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimDrnClamp(p, minAlt, maxAlt, ground)`

- **It must:** SPEC 5 WO-01: p with its height clamped to ground + minAlt .. ground + maxAlt (minAlt 2 unless 0 or more, maxAlt 120 unless positive, ground 0 unless a number).
- **May use:** nothing.
- **Files:** `src/js/engine/walk/walk-drone.js`, `docs/work-orders/v209/v209.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v209/v209.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimDrnOrbit(c, r, h, t, period)`

- **It must:** SPEC 5 WO-02: the angle 2 pi t / period (30 s unless positive); {eye: [cx + r cos, cy + h, cz + r sin], target: a copy of c}.
- **May use:** nothing.
- **Files:** `src/js/engine/walk/walk-drone.js`, `docs/work-orders/v209/v209.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v209/v209.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimDrnRoute(pts)`

- **It must:** SPEC 5 WO-03: {segs: the 3D length of each leg, length: their sum}.
- **May use:** nothing.
- **Files:** `src/js/engine/walk/walk-drone.js`, `docs/work-orders/v209/v209.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v209/v209.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimDrnAt(pts, route, dist)`

- **It must:** SPEC 5 WO-04: the point dist along the route, dist clamped to 0..length, interpolated on its leg (the last leg takes any remainder); null for no points.
- **May use:** nothing.
- **Files:** `src/js/engine/walk/walk-drone.js`, `docs/work-orders/v209/v209.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v209/v209.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Claude] Wiring into Walk

Claude's: the mode in V203's Walk (its menu, keys and touch controls, the rendered view), saving where needed; the test to tests/unit/; npm run modules; the browser check on phone, tablet and desktop.

---

## [ ] WO-06 [Claude] The records

PIPELINE row 209, Notion.
