# V241 spec: Earthquake loads from the place

Research: `docs/research/research-physical-world.md` (part 4.3) and `docs/research/research-physical-world/seismic-dynamics.md`; the independent check in `docs/research/research-physical-world/independent-check.md`. The owner's decisions: as the research recommends, answered 2026-11-22 (standard and scalable) (part 11 of the note; the owner, 2026-11-21: "Do your research first, properly. And then develop the work orders"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-21.

## 1. The decisions this spec follows

- ASCE 7-22 equivalent lateral force procedure; Method 2 (SDS, SD1) by default, Method 1 (Sa(T) from the multi-period spectrum) beside it; the lower bounds apply to both (decision 6).
- Site values from the USGS service at `/ws/building-codes/asce7-22/calculate` (not the old `/ws/designmaps/` path, which redirects through http), a plain GET with a unique title, the answer cached in the project, credited "U.S. Geological Survey"; typed values outside its coverage (decision 7).
- An out-of-range point comes back as HTTP 200 with request.status "error": the reader checks the status, not the HTTP code.
- Cu between table rows: the lower value (shorter period, larger Cs), since interpolation is not confirmed (U).
- Seismic systems: the steel special moment frame (R 8, Cd 5.5, Omega0 3) in the registry; others typed by the user (decision 8). Equation numbers kept out of labels.
- Effective seismic weight per level: the frame's self-weight plus the level's dead load (12.7.2's storage and partition shares are not researched: later).

## 2. What it does for the user

Properties, Site: risk category and site class; Get the seismic values asks USGS and keeps the answer. Analyze, Structure: a load case E with each level's force at the level, the base shear, Cs and what governs, the period used, storey drifts against their limit, and the combinations 1.2D + Ev + E + L and 0.9D - Ev + E.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/structure/seismic-elf.js` | new, after `js/engine/structure/wind-loads.js` in `src/index.html` (header done) | 9 pure functions (part 5) | Cline, WO-01 to WO-09 |
| `docs/work-orders/v241/v241.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, C-10, C-11 |

## 4. Units

g for spectral values, s for periods, m for heights, kN for weights and forces; displacements in m.

## 5. Functions, `src/js/engine/structure/seismic-elf.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file. A later function may use an earlier one of this file, as its task says.

- **WO-01 `bimSeisSa(T, p)`**: the two-period design spectrum (11.4.5.2) at period T for p {sds, sd1, tl}: NaN unless T >= 0 and sds, sd1, tl are positive. T0 = 0.2 sd1/sds, Ts = sd1/sds. T below T0: sds (0.4 + 0.6 T/T0); up to Ts: sds; up to tl: sd1/T; above: sd1 tl / T^2. Example: T 1 with {1.46, 0.70, 8} gives 0.7.
- **WO-02 `bimSeisSaMulti(T, periods, sa, tl)`**: the multi-period design spectrum from the USGS periods (s, rising) and ordinates (g): NaN unless T >= 0, there are at least two periods and as many ordinates. At or below the first period its ordinate; between two periods linear interpolation; beyond the last period Te with ordinate se: se Te / T up to tl (or when tl is not positive), se Te tl / T^2 above tl. Example: the Los Angeles answer at T 0.5982 gives 1.0439.
- **WO-03 `bimSeisTa(system, hn)`**: the approximate period Ct (hn / 0.3048)^x with hn in m: 'steel-mrf' 0.028 and 0.8, 'concrete-mrf' 0.016 and 0.9, 'steel-ebf' and 'steel-brbf' 0.03 and 0.75, any other system 0.02 and 0.75; NaN unless hn > 0. Example: ('steel-mrf', 14) gives 0.5982.
- **WO-04 `bimSeisCu(sd1)`**: the upper limit coefficient of Table 12.8-1, taking the lower value between rows: NaN unless sd1 >= 0; 1.4 from 0.3; 1.5 from 0.2; 1.6 from 0.15; else 1.7. Example: 0.25 gives 1.5.
- **WO-05 `bimSeisCs(o)`**: o {sds, sd1, s1, tl, R, Ie, T, method, sa}. {error: 'bad input'} unless R/Ie, T, sds, sd1 and tl are positive (and, for method 1, sa >= 0). Method 1 (o.method === 1): cs = sa / (R/Ie), governs 'sa'. Otherwise (method 2): cs = sds / (R/Ie), governs 'sds'; the cap is sd1 / (T R/Ie) when T <= tl, else sd1 tl / (T^2 R/Ie); when the cap is lower it is cs and governs 'sd1' or 'tl'. Then for both: when cs is below max(0.044 sds Ie, 0.01) it is that, governs 'min'; then when s1 >= 0.6 and cs is below 0.5 s1 / (R/Ie) it is that, governs 's1'. Returns {cs, governs}. Example: {1.46, 0.70, 0.75, 8, R 8, Ie 1, T 0.5982} gives cs 0.14627, 'sd1'.
- **WO-06 `bimSeisFx(w, h, V, T)`**: the vertical distribution: w the levels' weights (kN), h their heights above the base (m), in any order, V the base shear, T the period. {error: 'bad input'} unless w and h have the same, non-zero length, V >= 0, T > 0, every w >= 0 and every h > 0; {error: 'no weight'} when the sum below is 0. k = 1 for T <= 0.5, 2 for T >= 2.5, else 1 + (T - 0.5)/2. cvx[i] = w[i] h[i]^k / the sum of them; F[i] = cvx[i] V; shear[i] = the sum of F of every level at or above h[i]. Returns {k, cvx, F, shear} in the input's order. Example: four levels of 2000 kN at 3.5, 7, 10.5, 14 m, V 1170.17, T 0.5982 gives F 111.3, 230.2, 352.3, 476.4.
- **WO-07 `bimSeisUsgsUrl(lat, lon, rc, site, title)`**: {url} for 'https://earthquake.usgs.gov/ws/building-codes/asce7-22/calculate?latitude=LAT&longitude=LON&riskCategory=RC&siteClass=SITE&title=' + encodeURIComponent(title), the numbers as JavaScript writes them. Errors, checked in this order: {error: 'bad location'} unless -90 <= lat <= 90 and -180 <= lon <= 180; {error: 'bad risk category'} unless rc is I, II, III or IV; {error: 'bad site class'} unless site is A, B, BC, C, CD, D, DE, E or Default; {error: 'bad title'} unless title is a non-empty string.
- **WO-08 `bimSeisUsgsRead(j)`**: reads the service's parsed JSON. When j is missing or j.request.status is not 'success': {error: j.response when it is a string (the service's message), else 'the service did not answer with values'}. {error: 'no data'} without j.response.data. For each of sds, sd1, ss, s1, tl, ts, t0 in that order, {error: 'missing ' + name} unless it is a finite number. Returns {sds, sd1, ss, s1, tl, ts, t0, sdc (the string, else ''), periods and sa (copies of multiPeriodDesignSpectrum.periods and .ordinates; both [] when either is missing or their lengths differ)}. j is not changed.
- **WO-09 `bimSeisDrift(dxe, h, Cd, Ie, limit)`**: storey drifts from the levels' elastic displacements dxe (m, from the lowest level up) at heights h (m): {error: 'bad input'} unless both have the same non-zero length and Cd, Ie, limit are positive; {error: 'levels must rise'} unless each storey height h[i] - h[i-1] (h[0] for the first) is positive. Storey i: drift = Cd (dxe[i] - dxe[i-1]) / Ie (dxe[-1] = 0), ratio = |drift| / storey height, ok = |drift| <= limit x storey height. Returns [{drift, ratio, ok}].

## 6. Order of the work

WO-01 to WO-09 in order. Then Claude: **C-10** the load case E (Eh at each level's columns, Ev = 0.2 SDS D) and the 2.3.6 combinations in the registry; the Site fields (risk category, site class), Get the seismic values (one GET with a unique title, the answer kept in the project, typed values otherwise), the steel SMF record; the effective weight per level from the analytical model; Analyze: V, Cs and what governs, Ta and Cu Ta, Fx, drift against Table 12.12-1; the test to tests/unit/; npm run modules; **C-11** the records.

## 7. Not in this phase

Response spectrum and modes (V242); accidental torsion and irregularities; redundancy rho beyond the drift limit; Omega0 load combinations; vertical spectra; site-specific spectra; SDC A's minimum forces (later).
