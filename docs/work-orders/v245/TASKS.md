# V245 work orders: The building under a ground motion

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/structure/time-history.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v245/v245.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v245/v245.test.mjs
    node --check src/js/engine/structure/time-history.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimRayleigh(wi, wj, z)`

- **It must:** SPEC 5 WO-01: {error: 'bad input'} unless wi > 0, wj > 0, wi differs from wj and z >= 0. Returns {a0: z 2 wi wj / (wi + wj), a1: z 2 / (wi + wj)} (C = a0 M + a1 K). Example: (12.3607, 32.3607, 0.05) gives a0 0.894428, a1 0.00223607.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/time-history.js`, `docs/work-orders/v245/v245.test.mjs`
- **Budget:** 6
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v245/v245.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimNewmarkSdof(o)`

- **It must:** SPEC 5 WO-02: o {m, c, k, p (forces at steps 0, dt, 2 dt ...), dt, u0, v0 (0 when missing), gamma (0.5 when not finite), beta (0.25 when not finite)}. {error: 'bad input'} unless m > 0, k > 0, c >= 0, dt > 0 and p is not empty. u[0] = u0, v[0] = v0, a[0] = (p[0] - c v0 - k u0) / m; kh = k + gamma/(beta dt) c + m/(beta dt^2); A = m/(beta dt) + gamma/beta c; B = m/(2 beta) + dt (gamma/(2 beta) - 1) c. For each step: dp = p[i+1] - p[i] + A v[i] + B a[i]; du = dp / kh; dv = gamma/(beta dt) du - gamma/beta v[i] + dt (1 - gamma/(2 beta)) a[i]; da = du/(beta dt^2) - v[i]/(beta dt) - a[i]/(2 beta); add them. Returns {u, v, a}, each as long as p (Chopra, Table 5.4.2).
- **May use:** nothing.
- **Files:** `src/js/engine/structure/time-history.js`, `docs/work-orders/v245/v245.test.mjs`
- **Budget:** 22
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v245/v245.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-03 [Cline] `bimThSolve(A, b)`

- **It must:** SPEC 5 WO-03: solves A x = b by Gaussian elimination with partial pivoting on a copy (A and b not changed); null when a pivot's absolute value is not above 1e-300. Returns x. Example: [[0, 2, 1], [1, 1, 0], [3, 0, 1]], [5, 3, 4] gives [1, 2, 1].
- **May use:** nothing.
- **Files:** `src/js/engine/structure/time-history.js`, `docs/work-orders/v245/v245.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v245/v245.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimNewmarkMdof(o)`

- **It must:** SPEC 5 WO-04: o {M, C, K (n x n), ag (ground acceleration at each step, m/s2), dt, iota (n influence values)}. {error: 'bad input'} unless n > 0, ag is not empty, dt > 0 and iota has n entries. Average acceleration (gamma 1/2, beta 1/4), starting at rest: P[s] = -M iota ag[s]; a[0] = M^-1 P[0] (bimThSolve; {error: 'singular'} when null); Kh = K + gamma/(beta dt) C + M/(beta dt^2), Am = M/(beta dt) + gamma/beta C, Bm = M/(2 beta) + dt (gamma/(2 beta) - 1) C; each step as WO-02 with matrices: du = Kh^-1 (P[s+1] - P[s] + Am v + Bm a) ({error: 'singular'} when null), dv and da as in WO-02 per entry. Returns {u, v, a}: arrays over the steps of arrays of n values.
- **May use:** bimThSolve (WO-03).
- **Files:** `src/js/engine/structure/time-history.js`, `docs/work-orders/v245/v245.test.mjs`
- **Budget:** 40
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v245/v245.test.mjs`. **Score:** 0+0+0+0+2+0 = 2.

---

## [ ] WO-05 [Cline] `bimGroundRead(text)`

- **It must:** SPEC 5 WO-05: reads a record: each line's text after a '#' is dropped and the rest trimmed; empty lines skipped; a line is split on spaces, tabs, commas or semicolons and needs two numbers, time (s) and acceleration (g): else {error: 'line N: two numbers expected'} or {error: 'line N: not a number'} (N the line's number from 1). {error: 'fewer than two samples'} under two; {error: 'time must rise'} unless dt = t1 - t0 is positive; {error: 'line N: uneven time step'} where t[i] - t[i-1] differs from dt by more than 1e-6 max(1, |dt|) (N the line count of that sample, counting from 1 over the samples kept). Returns {dt, a: [the accelerations], n}. text that is not a string is read as ''.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/time-history.js`, `docs/work-orders/v245/v245.test.mjs`
- **Budget:** 22
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v245/v245.test.mjs`. **Score:** 0.

---

## [ ] C-06 [Claude] The wiring

The run, the loader, the animation and plots. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] C-07 [Claude] The records

PIPELINE row 245, the engineering log, Notion.
