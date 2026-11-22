# V245 spec: The building under a ground motion

Research: `docs/research/research-physical-world.md` (part 4.4) and `docs/research/research-physical-world/seismic-dynamics.md`; the independent check in `docs/research/research-physical-world/independent-check.md`. The owner's decisions: as the research recommends (part 11 of the note; the owner, 2026-11-21: "Do your research first, properly. And then develop the work orders"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-21.

## 1. The decisions this spec follows

- Newmark's average acceleration (gamma 1/2, beta 1/4): unconditionally stable, no decay; Rayleigh damping at 5 % in two chosen modes.
- Linear response of V242's storey model (3 dof per storey) to a ground acceleration along X or Z; peak storey displacements, drifts and base shear over time.
- Ground motions are the user's: a two-column text (time in s, acceleration in g) loaded from a file; a synthetic half-sine pulse for a first look; no record shipped (decision 10).
- A study, not a design check: 7-22's response-history rules (12.9.2: record selection, scaling, the number of records) are not researched and the result says so.

## 2. What it does for the user

Analyze, Structure, Ground motion: load a record or choose a pulse, run, and watch the building sway (scaled), with the roof displacement and the base shear over time and their peaks.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/structure/time-history.js` | new, after `js/engine/structure/steel-checks.js` in `src/index.html` (header done) | 5 pure functions (part 5) | Cline, WO-01 to WO-05 |
| `docs/work-orders/v245/v245.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, C-06, C-07 |

## 4. Units

m, s, t, kN; ground acceleration in g in a record, m/s2 inside (g = 9.80665).

## 5. Functions, `src/js/engine/structure/time-history.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file. A later function may use an earlier one of this file, as its task says.

- **WO-01 `bimRayleigh(wi, wj, z)`**: {error: 'bad input'} unless wi > 0, wj > 0, wi differs from wj and z >= 0. Returns {a0: z 2 wi wj / (wi + wj), a1: z 2 / (wi + wj)} (C = a0 M + a1 K). Example: (12.3607, 32.3607, 0.05) gives a0 0.894428, a1 0.00223607.
- **WO-02 `bimNewmarkSdof(o)`**: o {m, c, k, p (forces at steps 0, dt, 2 dt ...), dt, u0, v0 (0 when missing), gamma (0.5 when not finite), beta (0.25 when not finite)}. {error: 'bad input'} unless m > 0, k > 0, c >= 0, dt > 0 and p is not empty. u[0] = u0, v[0] = v0, a[0] = (p[0] - c v0 - k u0) / m; kh = k + gamma/(beta dt) c + m/(beta dt^2); A = m/(beta dt) + gamma/beta c; B = m/(2 beta) + dt (gamma/(2 beta) - 1) c. For each step: dp = p[i+1] - p[i] + A v[i] + B a[i]; du = dp / kh; dv = gamma/(beta dt) du - gamma/beta v[i] + dt (1 - gamma/(2 beta)) a[i]; da = du/(beta dt^2) - v[i]/(beta dt) - a[i]/(2 beta); add them. Returns {u, v, a}, each as long as p (Chopra, Table 5.4.2).
- **WO-03 `bimThSolve(A, b)`**: solves A x = b by Gaussian elimination with partial pivoting on a copy (A and b not changed); null when a pivot's absolute value is not above 1e-300. Returns x. Example: [[0, 2, 1], [1, 1, 0], [3, 0, 1]], [5, 3, 4] gives [1, 2, 1].
- **WO-04 `bimNewmarkMdof(o)`**: o {M, C, K (n x n), ag (ground acceleration at each step, m/s2), dt, iota (n influence values)}. {error: 'bad input'} unless n > 0, ag is not empty, dt > 0 and iota has n entries. Average acceleration (gamma 1/2, beta 1/4), starting at rest: P[s] = -M iota ag[s]; a[0] = M^-1 P[0] (bimThSolve; {error: 'singular'} when null); Kh = K + gamma/(beta dt) C + M/(beta dt^2), Am = M/(beta dt) + gamma/beta C, Bm = M/(2 beta) + dt (gamma/(2 beta) - 1) C; each step as WO-02 with matrices: du = Kh^-1 (P[s+1] - P[s] + Am v + Bm a) ({error: 'singular'} when null), dv and da as in WO-02 per entry. Returns {u, v, a}: arrays over the steps of arrays of n values.
- **WO-05 `bimGroundRead(text)`**: reads a record: each line's text after a '#' is dropped and the rest trimmed; empty lines skipped; a line is split on spaces, tabs, commas or semicolons and needs two numbers, time (s) and acceleration (g): else {error: 'line N: two numbers expected'} or {error: 'line N: not a number'} (N the line's number from 1). {error: 'fewer than two samples'} under two; {error: 'time must rise'} unless dt = t1 - t0 is positive; {error: 'line N: uneven time step'} where t[i] - t[i-1] differs from dt by more than 1e-6 max(1, |dt|) (N the line count of that sample, counting from 1 over the samples kept). Returns {dt, a: [the accelerations], n}. text that is not a string is read as ''.

## 6. Order of the work

WO-01 to WO-05 in order. Then Claude: **C-06** the run on V242's storey model (Rayleigh from its first two modes), the record loader and the pulse, the sway animation and the two plots, the "study, not a design check" note; the test to tests/unit/; npm run modules; **C-07** the records.

## 7. Not in this phase

Nonlinear response; record selection and scaling to 7-22 12.9.2; two components at once; soil-structure interaction; a shipped record.
