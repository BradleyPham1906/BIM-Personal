# V227 work orders: Track D, the drone bridge project: flight planning

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/site/drone-plan.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v227/v227.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v227/v227.test.mjs
    node --check src/js/engine/site/drone-plan.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimDpGsd(sw, f, iw, h)`

- **It must:** SPEC 5 WO-01: sensor width mm, focal length mm, image width px, height m: sw h 100 / (f iw) cm per pixel; null unless all positive.
- **May use:** nothing.
- **Files:** `src/js/engine/site/drone-plan.js`, `docs/work-orders/v227/v227.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v227/v227.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimDpHeight(gsd, sw, f, iw)`

- **It must:** SPEC 5 WO-02: the inverse: gsd f iw / (sw 100) m; null unless gsd, sw and iw are positive.
- **May use:** nothing.
- **Files:** `src/js/engine/site/drone-plan.js`, `docs/work-orders/v227/v227.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v227/v227.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimDpFootprint(sw, sh, f, h)`

- **It must:** SPEC 5 WO-03: {w: sw h / f, h: sh h / f} in metres; null unless f is positive.
- **May use:** nothing.
- **Files:** `src/js/engine/site/drone-plan.js`, `docs/work-orders/v227/v227.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v227/v227.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimDpSpacing(len, overlap)`

- **It must:** SPEC 5 WO-04: len (1 - overlap) for 0 <= overlap < 1, else null.
- **May use:** nothing.
- **Files:** `src/js/engine/site/drone-plan.js`, `docs/work-orders/v227/v227.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v227/v227.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimDpLines(width, spacing)`

- **It must:** SPEC 5 WO-05: ceil(width / spacing - 1e-9) + 1; null unless spacing is positive.
- **May use:** nothing.
- **Files:** `src/js/engine/site/drone-plan.js`, `docs/work-orders/v227/v227.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v227/v227.test.mjs`. **Score:** 0.

---

## [ ] WO-06 [Claude] The capture planner

Claude's: the bridge footprint from the model, the camera presets, the flight lines drawn and exported as waypoints for the owner's flight app. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-07 [Claude] The records

PIPELINE row 227, Notion.
