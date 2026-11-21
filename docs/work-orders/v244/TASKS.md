# V244 work orders: Steel members: AISC 360-22 checks

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/structure/steel-checks.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v244/v244.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v244/v244.test.mjs
    node --check src/js/engine/structure/steel-checks.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimStIProps(d, bf, tf, tw)`

- **It must:** SPEC 5 WO-01: {error: 'bad input'} unless every argument is positive, 2 tf < d and tw <= bf. h = d - 2 tf, ho = d - tf; A = 2 bf tf + h tw; Ix = (bf d^3 - (bf - tw) h^3) / 12; Iy = (2 tf bf^3 + h tw^3) / 12; Zx = bf tf (d - tf) + tw h^2 / 4; Zy = bf^2 tf / 2 + h tw^2 / 4; Sx = Ix / (d/2); Sy = Iy / (bf/2); rx, ry = sqrt(I / A); J = (2 bf tf^3 + ho tw^3) / 3; Cw = Iy ho^2 / 4; rts = sqrt(sqrt(Iy Cw) / Sx). Returns {A, Ix, Iy, Zx, Zy, Sx, Sy, rx, ry, J, Cw, ho, rts, h}.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/steel-checks.js`, `docs/work-orders/v244/v244.test.mjs`
- **Budget:** 18
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v244/v244.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimStCompact(bf, tf, h, tw, Fy, E)`

- **It must:** SPEC 5 WO-02: {error: 'bad input'} unless every argument is positive. s = sqrt(E / Fy), lf = bf / (2 tf), lw = h / tw. flange: 'compact' when lf <= 0.38 s, 'noncompact' when lf <= s, else 'slender'; web: 'compact' when lw <= 3.76 s, 'noncompact' when lw <= 5.70 s, else 'slender'; flangeComp: 'nonslender' when lf <= 0.56 s, else 'slender'; webComp: 'nonslender' when lw <= 1.49 s, else 'slender'. Returns {flange, web, flangeComp, webComp}.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/steel-checks.js`, `docs/work-orders/v244/v244.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v244/v244.test.mjs`. **Score:** 0.

---

## [ ] WO-03 [Cline] `bimStPhiPn(A, r, Lc, Fy, E)`

- **It must:** SPEC 5 WO-03: {error: 'bad input'} unless every argument is positive. slender = Lc / r; Fe = pi^2 E / slender^2; Fn = 0.658^(Fy/Fe) Fy when slender <= 4.71 sqrt(E/Fy), else 0.877 Fe; Pn = Fn A / 1000 (kN); phiPn = 0.9 Pn. Returns {slender, Fe, Fn, Pn, phiPn}. Example: the W10x49 (A 9290 mm2, ry 64.5 mm), Lc 4000, Fy 345 gives phiPn 2177.5 kN.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/steel-checks.js`, `docs/work-orders/v244/v244.test.mjs`
- **Budget:** 10
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v244/v244.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimStLpLr(ry, rts, J, Sx, ho, Fy, E)`

- **It must:** SPEC 5 WO-04: {error: 'bad input'} unless every argument is positive. Lp = 1.76 ry sqrt(E/Fy); with t = J / (Sx ho) and u = 0.7 Fy / E (c = 1), Lr = 1.95 rts (E / (0.7 Fy)) sqrt(t + sqrt(t^2 + 6.76 u^2)). Returns {Lp, Lr} in mm. Example: the W10x49 gives 2733.9 and 9631.3.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/steel-checks.js`, `docs/work-orders/v244/v244.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v244/v244.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimStPhiMn(o)`

- **It must:** SPEC 5 WO-05: o {Zx, Sx, Fy, E, Lb, Lp, Lr, Cb (1 when not finite), rts, J, ho}. {error: 'bad input'} unless Zx, Sx, Fy, E, Lp are positive, Lb >= 0 and Lr > Lp. Mp = Fy Zx. Lb <= Lp: Mn = Mp, zone 'plastic'. Lb <= Lr: Mn = min(Cb (Mp - (Mp - 0.7 Fy Sx)(Lb - Lp)/(Lr - Lp)), Mp), zone 'inelastic'. Else s = Lb / rts, Fcr = Cb pi^2 E / s^2 sqrt(1 + 0.078 J / (Sx ho) s^2), Mn = min(Fcr Sx, Mp), zone 'elastic'. Returns {Mp, Mn, phiMn = 0.9 Mn, zone}, moments in kN m (N mm / 1e6). Example: the W10x49 at Lb 4000, Cb 1 gives phiMn 286.61.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/steel-checks.js`, `docs/work-orders/v244/v244.test.mjs`
- **Budget:** 18
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v244/v244.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-06 [Cline] `bimStCb(Mmax, MA, MB, MC)`

- **It must:** SPEC 5 WO-06: 12.5 |Mmax| / (2.5 |Mmax| + 3 |MA| + 4 |MB| + 3 |MC|), MA, MB, MC the moments at the quarter, middle and three-quarter points of the unbraced segment; 1 when the denominator is 0. Example: (1, 0.25, 0.5, 0.75) gives 1.6667.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/steel-checks.js`, `docs/work-orders/v244/v244.test.mjs`
- **Budget:** 6
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v244/v244.test.mjs`. **Score:** 0.

---

## [ ] WO-07 [Cline] `bimStH1(Pr, Pc, Mrx, Mcx, Mry, Mcy)`

- **It must:** SPEC 5 WO-07: {error: 'bad input'} unless Pc, Mcx and Mcy are positive. p = |Pr| / Pc, m = |Mrx| / Mcx + |Mry| / Mcy; when p >= 0.2 {ratio: p + 8/9 m, eq: 'H1-1a'}, else {ratio: p / 2 + m, eq: 'H1-1b'}. Example: (1000, 2177.54, 100, 286.61, 0, 100) gives 0.7694, 'H1-1a'.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/steel-checks.js`, `docs/work-orders/v244/v244.test.mjs`
- **Budget:** 8
- **Test:** the cases named `WO-07 ...` in `docs/work-orders/v244/v244.test.mjs`. **Score:** 0.

---

## [ ] C-08 [Claude] The wiring

Fields, the check, the colours. The test to tests/unit/; npm run modules; the browser check.

---

## [ ] C-09 [Claude] The records

PIPELINE row 244, the engineering log, Notion.
