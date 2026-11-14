# V220 work orders: Water and presentation rendering

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/render/water-sim.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v220/v220.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v220/v220.test.mjs
    node --check src/js/engine/render/water-sim.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimWtrStep(h, v, n, damp)`

- **It must:** SPEC 5 WO-01: on an n x n grid: each interior cell's velocity becomes (v + (the mean of its four neighbours' heights - h) 2) damp (damp 0.995 unless in 0..1], 1 allowed), boundary velocities unchanged; then every height plus its new velocity. {h, v} new arrays.
- **May use:** nothing.
- **Files:** `src/js/engine/render/water-sim.js`, `docs/work-orders/v220/v220.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v220/v220.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-02 [Cline] `bimWtrDrop(h, n, x, y, r, s)`

- **It must:** SPEC 5 WO-02: a copy with, at each cell within distance r of (x, y) (d = distance / r < 1), s (0.5 + cos(pi d) / 2) added.
- **May use:** nothing.
- **Files:** `src/js/engine/render/water-sim.js`, `docs/work-orders/v220/v220.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v220/v220.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimWtrSchlick(n1, n2, cosT)`

- **It must:** SPEC 5 WO-03: f0 + (1 - f0)(1 - cosT)^5 with f0 = ((n1 - n2)/(n1 + n2))^2.
- **May use:** nothing.
- **Files:** `src/js/engine/render/water-sim.js`, `docs/work-orders/v220/v220.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v220/v220.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimWtrCaustic(oldA, newA)`

- **It must:** SPEC 5 WO-04: oldA / newA, Infinity when newA is not positive.
- **May use:** nothing.
- **Files:** `src/js/engine/render/water-sim.js`, `docs/work-orders/v220/v220.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v220/v220.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Claude] Water in the rendered view

Claude's: the GPU heightfield in three.js, the pond meshes, the fallback, the flood disclaimer. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-06 [Claude] The records

PIPELINE row 220, Notion.
