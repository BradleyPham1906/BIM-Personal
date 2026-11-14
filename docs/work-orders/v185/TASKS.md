# V185 work orders: Freeform F3, sweeps, pipes and caps

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/drawing/sweeps.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v185/v185.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v185/v185.test.mjs
    node --check src/js/engine/drawing/sweeps.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimSwpPerp(t)`

- **It must:** SPEC 5 WO-01: with the helpers bimSwpNorm(a) (unit vector, [0,0,0] for length under 1e-15) and bimSwpCross(a, b) written just above it: the unit perpendicular normalise(t x e), e the world axis whose |component| of t is smallest (x before y before z on a tie).
- **May use:** bimSwpNorm, bimSwpCross (this task).
- **Files:** `src/js/engine/drawing/sweeps.js`, `docs/work-orders/v185/v185.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v185/v185.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimSwpFrames(rail)`

- **It must:** SPEC 5 WO-02: one frame per rail point: t the normalised difference of the neighbours (one-sided at the ends); the first n bimSwpPerp(t); each next n by the double reflection: v1 = p_i - p_(i-1), reflect the previous n and t in v1 (r - 2(v1.r)/(v1.v1) v1), v2 = t_i - reflected t, reflect the reflected n in v2 (no reflection when v2.v2 < 1e-30; keep the previous n when v1.v1 < 1e-30), normalised; b = t x n. [] for fewer than 2 points.
- **May use:** bimSwpNorm, bimSwpCross, bimSwpPerp (WO-01).
- **Files:** `src/js/engine/drawing/sweeps.js`, `docs/work-orders/v185/v185.test.mjs`
- **Budget:** 80
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v185/v185.test.mjs`. **Score:** 0+1+0+0+2+0 = 3, tier B.

---

## [ ] WO-03 [Cline] `bimSwpSweep(profile, rail, closed)`

- **It must:** SPEC 5 WO-03: vertices frame by frame, each profile point [x, y] at p + x n + y b; faces [a, b, b + m, a + m] with a = i m + j, b = i m + (j + 1) % m, for j < m (closed) or m - 1. null for fewer than 2 frames or profile points.
- **May use:** bimSwpFrames (WO-02).
- **Files:** `src/js/engine/drawing/sweeps.js`, `docs/work-orders/v185/v185.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v185/v185.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-04 [Cline] `bimSwpCircle(r, n)`

- **It must:** SPEC 5 WO-04: n (16 when under 3; floored) points [r cos, r sin] at angles 2 pi i / n.
- **May use:** nothing.
- **Files:** `src/js/engine/drawing/sweeps.js`, `docs/work-orders/v185/v185.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v185/v185.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimSwpCap(mesh, start, count, flip)`

- **It must:** SPEC 5 WO-05: a new mesh: the vertices plus their centroid over the ring start .. start + count - 1, the faces plus a fan [centre, start + i, start + (i+1) % count], or [centre, start + (i+1) % count, start + i] when flip; the input unchanged.
- **May use:** nothing.
- **Files:** `src/js/engine/drawing/sweeps.js`, `docs/work-orders/v185/v185.test.mjs`
- **Budget:** 30
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v185/v185.test.mjs`. **Score:** 0.

---

## [ ] WO-06 [Claude] Sweep, Pipe and Cap commands

Claude's: the commands on F1's curves (samples to rails and profiles), caps on closed ends, kept and rebuilt; the test to tests/unit/; npm run modules; the browser check.

---

## [ ] WO-07 [Claude] The records

PIPELINE row 185, Notion.
