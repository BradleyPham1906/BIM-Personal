# V243 work orders: Concrete members: cracking and strength

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/structure/rc-checks.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v243/v243.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v243/v243.test.mjs
    node --check src/js/engine/structure/rc-checks.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimRcMat(fc, lambda)`

- **It must:** SPEC 5 WO-01: lambda is 1 when not finite. {error: 'bad input'} unless fc > 0 and 0 < lambda <= 1. Ec = 4700 sqrt(fc), fr = 0.62 lambda sqrt(fc), beta1 = 0.85 for fc <= 28, 0.65 for fc >= 55, else 0.85 - 0.05 (fc - 28) / 7. Returns {Ec, fr, beta1}. Example: 30 gives {25742.96, 3.39588, 0.83571}.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/rc-checks.js`, `docs/work-orders/v243/v243.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v243/v243.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimRcSection(b, h, d, As, Es, Ec, fr)`

- **It must:** SPEC 5 WO-02: {error: 'bad input'} unless every argument is positive and d < h. Ig = b h^3 / 12, yt = h / 2, Mcr = fr Ig / yt / 1e6 (kN m), n = Es / Ec; kd is the positive root of b kd^2 / 2 = n As (d - kd), that is (-n As + sqrt((n As)^2 + 2 b n As d)) / b; Icr = b kd^3 / 3 + n As (d - kd)^2. Returns {Ig, yt, Mcr, n, kd, Icr}. Example: (300, 500, 450, 942, 200000, 25742.96, 3.39588) gives Mcr 42.448, kd 125.774, Icr 9.68303e8.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/rc-checks.js`, `docs/work-orders/v243/v243.test.mjs`
- **Budget:** 14
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v243/v243.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimRcIe(Mcr, Ma, Ig, Icr)`

- **It must:** SPEC 5 WO-03: with M = |Ma|: NaN unless Mcr > 0, Ig > 0, 0 < Icr <= Ig and M is finite; Ig when M <= 2/3 Mcr; else Icr / (1 - ((2/3) Mcr / M)^2 (1 - Icr / Ig)). Example: (42.4485, 60, 3.125e9, 9.683e8) gives 1.1439e9.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/rc-checks.js`, `docs/work-orders/v243/v243.test.mjs`
- **Budget:** 10
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v243/v243.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimRcState(Ma, Mcr)`

- **It must:** SPEC 5 WO-04: with M = |Ma|: 'none' unless Mcr > 0 and M is finite; 'uncracked' when M <= 2/3 Mcr; 'reduced' when M <= Mcr; else 'cracked'.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/rc-checks.js`, `docs/work-orders/v243/v243.test.mjs`
- **Budget:** 10
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v243/v243.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimRcFlexure(b, d, As, fy, fc, Es)`

- **It must:** SPEC 5 WO-05: {error: 'bad input'} unless every argument is positive. beta1 as in WO-01 (written here again: no call); a = As fy / (0.85 fc b); c = a / beta1; {error: 'over-reinforced: the neutral axis is below the steel'} when c >= d; epst = 0.003 (d - c) / c; ety = fy / Es; phi = 0.9 when epst >= ety + 0.003, 0.65 when epst <= ety, else 0.65 + 0.25 (epst - ety) / 0.003; Mn = As fy (d - a/2) / 1e6 (kN m). Returns {a, c, epst, phi, Mn, phiMn}. Example: (300, 450, 942, 420, 30, 200000) gives phiMn 151.03.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/rc-checks.js`, `docs/work-orders/v243/v243.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v243/v243.test.mjs`. **Score:** 0.

---

## [ ] WO-06 [Cline] `bimCheckBand(r)`

- **It must:** SPEC 5 WO-06: 'none' for null, undefined, a value that is not finite or below 0; 'low' below 0.5; 'mid' below 0.9; 'high' up to and including 1; 'over' above 1.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/rc-checks.js`, `docs/work-orders/v243/v243.test.mjs`
- **Budget:** 10
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v243/v243.test.mjs`. **Score:** 0.

---

## [ ] C-07 [Claude] The wiring

Material and type fields, the check, the colours. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] C-08 [Claude] The records

PIPELINE row 243, the engineering log, Notion.
