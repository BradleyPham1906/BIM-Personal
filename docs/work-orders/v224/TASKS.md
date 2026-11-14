# V224 work orders: Track E, field work: positions without GPS and step-by-step instructions

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/site/field-guide.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v224/v224.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v224/v224.test.mjs
    node --check src/js/engine/site/field-guide.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimFeBearing(a, b)`

- **It must:** SPEC 5 WO-01: the azimuth from a to b in degrees clockwise from north (plan x east, y north), 0 to 360.
- **May use:** nothing.
- **Files:** `src/js/engine/site/field-guide.js`, `docs/work-orders/v224/v224.test.mjs`
- **Budget:** 5
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v224/v224.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimFeIntersect(p1, az1, p2, az2)`

- **It must:** SPEC 5 WO-02: the meeting point of the rays from p1 along az1 and p2 along az2 (directions (sin az, cos az)); null when parallel (|cross| < 1e-9) or when it lies behind either point.
- **May use:** nothing.
- **Files:** `src/js/engine/site/field-guide.js`, `docs/work-orders/v224/v224.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v224/v224.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-03 [Cline] `bimFeResect(target, obs)`

- **It must:** SPEC 5 WO-03: obs [{from, az}]: each pair's meeting point (WO-02); null when none; else {p: their mean, spread: the largest distance of one from the mean, pairs: how many}.
- **May use:** bimFeIntersect (WO-02).
- **Files:** `src/js/engine/site/field-guide.js`, `docs/work-orders/v224/v224.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v224/v224.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimFeNext(steps, done)`

- **It must:** SPEC 5 WO-04: steps [{id, after: [ids]}] in order: the first not done whose prerequisites are all done as next (null when none); blocked lists the not-done steps passed over before it.
- **May use:** nothing.
- **Files:** `src/js/engine/site/field-guide.js`, `docs/work-orders/v224/v224.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v224/v224.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Claude] Field mode

Claude's: the compass and camera bearings on the phone, known points from the model, the task list with photos; a field test plan for photo localisation with the owner. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-06 [Claude] The records

PIPELINE row 224, Notion.
