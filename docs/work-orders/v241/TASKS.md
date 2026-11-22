# V241 work orders: Earthquake loads from the place

Spec: `SPEC.md` in this folder (part 5 has every function in full). Implementation target: local `main`.
One task at a time, top to bottom. `[ ]` open, `[x]` done (its tests pass), `[skipped]` left for Claude.

Every `[Cline]` task: add one function (and any table its task names, just above it) to `src/js/engine/structure/seismic-elf.js`, below the
file's header comment, and change nothing else: not another file, not the `import`/`export` lines, not
`canvas_v10.html`. ES5 only: `var`, `function`; no `let`, `const`, arrow functions, classes or template strings.
Use only the names listed; never a name from another file. Implement the whole function; never a placeholder.

The tests are in `docs/work-orders/v241/v241.test.mjs`, outside `npm test` while the orders are open, so main stays green. After each task:

    node --test --test-name-pattern="WO-01" docs/work-orders/v241/v241.test.mjs
    node --check src/js/engine/structure/seismic-elf.js
    npm test

Nothing calls these functions until Claude's first task after them. Scores are from `../ROUTING.md`.

---

## [ ] WO-01 [Cline] `bimSeisSa(T, p)`

- **It must:** SPEC 5 WO-01: the two-period design spectrum (11.4.5.2) at period T for p {sds, sd1, tl}: NaN unless T >= 0 and sds, sd1, tl are positive. T0 = 0.2 sd1/sds, Ts = sd1/sds. T below T0: sds (0.4 + 0.6 T/T0); up to Ts: sds; up to tl: sd1/T; above: sd1 tl / T^2. Example: T 1 with {1.46, 0.70, 8} gives 0.7.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/seismic-elf.js`, `docs/work-orders/v241/v241.test.mjs`
- **Budget:** 15
- **Test:** the cases named `WO-01 ...` in `docs/work-orders/v241/v241.test.mjs`. **Score:** 0.

---

## [ ] WO-02 [Cline] `bimSeisSaMulti(T, periods, sa, tl)`

- **It must:** SPEC 5 WO-02: the multi-period design spectrum from the USGS periods (s, rising) and ordinates (g): NaN unless T >= 0, there are at least two periods and as many ordinates. At or below the first period its ordinate; between two periods linear interpolation; beyond the last period Te with ordinate se: se Te / T up to tl (or when tl is not positive), se Te tl / T^2 above tl. Example: the Los Angeles answer at T 0.5982 gives 1.0439.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/seismic-elf.js`, `docs/work-orders/v241/v241.test.mjs`
- **Budget:** 18
- **Test:** the cases named `WO-02 ...` in `docs/work-orders/v241/v241.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-03 [Cline] `bimSeisTa(system, hn)`

- **It must:** SPEC 5 WO-03: the approximate period Ct (hn / 0.3048)^x with hn in m: 'steel-mrf' 0.028 and 0.8, 'concrete-mrf' 0.016 and 0.9, 'steel-ebf' and 'steel-brbf' 0.03 and 0.75, any other system 0.02 and 0.75; NaN unless hn > 0. Example: ('steel-mrf', 14) gives 0.5982.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/seismic-elf.js`, `docs/work-orders/v241/v241.test.mjs`
- **Budget:** 12
- **Test:** the cases named `WO-03 ...` in `docs/work-orders/v241/v241.test.mjs`. **Score:** 0.

---

## [ ] WO-04 [Cline] `bimSeisCu(sd1)`

- **It must:** SPEC 5 WO-04: the upper limit coefficient of Table 12.8-1, taking the lower value between rows: NaN unless sd1 >= 0; 1.4 from 0.3; 1.5 from 0.2; 1.6 from 0.15; else 1.7. Example: 0.25 gives 1.5.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/seismic-elf.js`, `docs/work-orders/v241/v241.test.mjs`
- **Budget:** 10
- **Test:** the cases named `WO-04 ...` in `docs/work-orders/v241/v241.test.mjs`. **Score:** 0.

---

## [ ] WO-05 [Cline] `bimSeisCs(o)`

- **It must:** SPEC 5 WO-05: o {sds, sd1, s1, tl, R, Ie, T, method, sa}. {error: 'bad input'} unless R/Ie, T, sds, sd1 and tl are positive (and, for method 1, sa >= 0). Method 1 (o.method === 1): cs = sa / (R/Ie), governs 'sa'. Otherwise (method 2): cs = sds / (R/Ie), governs 'sds'; the cap is sd1 / (T R/Ie) when T <= tl, else sd1 tl / (T^2 R/Ie); when the cap is lower it is cs and governs 'sd1' or 'tl'. Then for both: when cs is below max(0.044 sds Ie, 0.01) it is that, governs 'min'; then when s1 >= 0.6 and cs is below 0.5 s1 / (R/Ie) it is that, governs 's1'. Returns {cs, governs}. Example: {1.46, 0.70, 0.75, 8, R 8, Ie 1, T 0.5982} gives cs 0.14627, 'sd1'.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/seismic-elf.js`, `docs/work-orders/v241/v241.test.mjs`
- **Budget:** 25
- **Test:** the cases named `WO-05 ...` in `docs/work-orders/v241/v241.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-06 [Cline] `bimSeisFx(w, h, V, T)`

- **It must:** SPEC 5 WO-06: the vertical distribution: w the levels' weights (kN), h their heights above the base (m), in any order, V the base shear, T the period. {error: 'bad input'} unless w and h have the same, non-zero length, V >= 0, T > 0, every w >= 0 and every h > 0; {error: 'no weight'} when the sum below is 0. k = 1 for T <= 0.5, 2 for T >= 2.5, else 1 + (T - 0.5)/2. cvx[i] = w[i] h[i]^k / the sum of them; F[i] = cvx[i] V; shear[i] = the sum of F of every level at or above h[i]. Returns {k, cvx, F, shear} in the input's order. Example: four levels of 2000 kN at 3.5, 7, 10.5, 14 m, V 1170.17, T 0.5982 gives F 111.3, 230.2, 352.3, 476.4.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/seismic-elf.js`, `docs/work-orders/v241/v241.test.mjs`
- **Budget:** 22
- **Test:** the cases named `WO-06 ...` in `docs/work-orders/v241/v241.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-07 [Cline] `bimSeisUsgsUrl(lat, lon, rc, site, title)`

- **It must:** SPEC 5 WO-07: {url} for 'https://earthquake.usgs.gov/ws/building-codes/asce7-22/calculate?latitude=LAT&longitude=LON&riskCategory=RC&siteClass=SITE&title=' + encodeURIComponent(title), the numbers as JavaScript writes them. Errors, checked in this order: {error: 'bad location'} unless -90 <= lat <= 90 and -180 <= lon <= 180; {error: 'bad risk category'} unless rc is I, II, III or IV; {error: 'bad site class'} unless site is A, B, BC, C, CD, D, DE, E or Default; {error: 'bad title'} unless title is a non-empty string.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/seismic-elf.js`, `docs/work-orders/v241/v241.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-07 ...` in `docs/work-orders/v241/v241.test.mjs`. **Score:** 0.

---

## [ ] WO-08 [Cline] `bimSeisUsgsRead(j)`

- **It must:** SPEC 5 WO-08: reads the service's parsed JSON. When j is missing or j.request.status is not 'success': {error: j.response when it is a string (the service's message), else 'the service did not answer with values'}. {error: 'no data'} without j.response.data. For each of sds, sd1, ss, s1, tl, ts, t0 in that order, {error: 'missing ' + name} unless it is a finite number. Returns {sds, sd1, ss, s1, tl, ts, t0, sdc (the string, else ''), periods and sa (copies of multiPeriodDesignSpectrum.periods and .ordinates; both [] when either is missing or their lengths differ)}. j is not changed.
- **May use:** nothing.
- **Files:** `src/js/engine/structure/seismic-elf.js`, `docs/work-orders/v241/v241.test.mjs`
- **Budget:** 20
- **Test:** the cases named `WO-08 ...` in `docs/work-orders/v241/v241.test.mjs`. **Score:** 0+0+0+0+1+0 = 1.

---

## [ ] WO-09 [Cline] `bimSeisDrift(dxe, h, Cd, Ie, limit)`

- **It must:** SPEC 5 WO-09: storey drifts from the levels' elastic displacements dxe (m, from the lowest level up) at heights h (m): {error: 'bad input'} unless both have the same non-zero length and Cd, Ie, limit are positive; {error: 'levels must rise'} unless each storey height h[i] - h[i-1] (h[0] for the first) is positive. Storey i: drift = Cd (dxe[i] - dxe[i-1]) / Ie (dxe[-1] = 0), ratio = |drift| / storey height, ok = |drift| <= limit x storey height. Returns [{drift, ratio, ok}].
- **May use:** nothing.
- **Files:** `src/js/engine/structure/seismic-elf.js`, `docs/work-orders/v241/v241.test.mjs`
- **Budget:** 16
- **Test:** the cases named `WO-09 ...` in `docs/work-orders/v241/v241.test.mjs`. **Score:** 0.

---

## [ ] C-10 [Claude] The wiring

Load case E, the USGS button, the ELF table and drifts. The test to tests/unit/; npm run modules; the browser check, including the USGS request from the page.

---

## [ ] C-11 [Claude] The records

PIPELINE row 241, the engineering log, Notion.
