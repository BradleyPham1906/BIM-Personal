# The physical world: loads from the place, dynamics, member checks, form-finding and runoff

Research note, 2026-11-21, by Claude, following `docs/research/research-protocol.md`. The work behind it is
in `docs/research/research-physical-world/` (four topic notes written by parallel research agents and the
independent check) and `docs/research/experiments/physical-world/` (seven scripts and three saved answers of
the USGS service). This note is written from them; each finding names the topic note that holds its
sources, search log and arithmetic.

## 1. Abstract

The owner asked how the app can "understand the real world": gravity, wind, earthquakes, weight, stress,
concrete cracking, and water on the site, so that algorithmic design runs against physics and not only
geometry. A search engine's overview had proposed a rigid-body game engine (Jolt, Rapier), "geodetic
gravity vectors", OpenFOAM and FEA workers. The question is what an engineer would actually sign, what
can run in the app's contract (ES5, offline, one file, vetted libraries only), and in what order.

**The answer.** Engineering does not simulate the world freely: it applies the loads a code assigns to the
place (ASCE 7-22 for the United States), analyses the structure under them, and checks each member against
a material code (ACI 318-19, AISC 360-22). The app already has a linear 3D frame solver with self-weight
(V125); what it lacks is everything that comes from the place. All of it can be built as small pure
functions in our own ES5, without a library: every worked example in the research was reproduced here to
the published digits, and the heaviest computations (a 120-degree-of-freedom eigenproblem, a 200 x 200
runoff grid) take 0.2 s and 45 ms. The rigid-body engines compute no stress and are not needed; geodetic
gravity changes loads by at most 0.27 % (e02); OpenFOAM cannot run in a browser and V221's lattice
Boltzmann is the right path for wind flow.

**Recommendation.** Nine phases, V239 to V247, each one file of pure functions for Cline plus Claude's
wiring: floor loads (V239), wind loads (V240), earthquake loads with the USGS service (V241), modes and
the response spectrum (V242), concrete cracking and strength (V243), steel checks (V244), the building
under a ground motion (V245), form-finding (V246), and stormwater runoff (V247). They feed the model graph
(V230) and design-space exploration (V231) as analyses, so a generator's output can be scored on drift,
steel weight, utilisation and runoff.

## 2. The question and the hypotheses

The question: which physical behaviour can the app compute honestly, from which standards and free data,
with which algorithms, inside its contract; and what must stay out.

| # | Hypothesis (falsifiable) | Outcome | Evidence |
|---|---|---|---|
| H1 | Modelling gravity's direction and strength from latitude and height changes design loads by less than 1 % | **Held**: within +/- 0.27 % of 9.80665 anywhere on Earth; direction turns 0.009 degrees over 1 km | e02 (WGS 84 normal gravity) |
| H2 | A plain-JS eigen solver is fast enough for modal analysis on storey degrees of freedom (3 per storey) | **Held** to about 120 dof (0.18 s, exact to 1e-12); 240 dof takes 1.6 s, so the full 3D frame must be reduced | e01 |
| H3 | A free, keyless, browser-readable source gives the ASCE 7-22 seismic values for any US site | **Held**: the USGS service, `access-control-allow-origin: *`, with two traps (a cached copy without the header; errors returned with HTTP 200) | seismic note 4.4, independent check S10 |
| H4 | A free, keyless, documented source gives the ASCE 7-22 basic wind speed | **Failed**: ATC's closed on 2024-12-31; ASCE's API needs a paid key; ASCE's map server answers but is undocumented and has no terms | wind note 4.3 |
| H5 | NOAA Atlas 14 rainfall intensity can be fetched from the browser | **Failed**: keyless and public domain, but no CORS header and the preflight returns 500 | runoff note B.3, independent check F6 |
| H6 | Every code value the functions use can be read at level P | **Failed**: ASCE 7-22, ACI 318-19 and AISC 360-22 are sold or refused here; every value is S, confirmed by two or more independent secondary sources and by the second reader | independent check |
| H7 | A rigid-body physics engine is needed for loads, stress or cracking | **Failed**: they compute contacts and motion of rigid bodies, no internal stress; the frame solver and the material codes do the work | this note, part 5 |
| H8 | Dynamic relaxation with kinetic damping reaches the force density method's shape on the same net | **Held**: 81 iterations, 8e-10 (viscous damping: 398) | form-finding note e01; here 81 in ES5 |

## 3. Method

- **Parallel research** (protocol step 10): four agents, one per side, each with its own search log,
  sources by kind, hypotheses, edges and open items: `loads-wind-gravity.md`, `seismic-dynamics.md`,
  `member-checks-cracking.md`, `formfinding-runoff.md`.
- **Experiments** (step 5): `e01_eigen_speed.mjs`, `e02_gravity.py` (here); `wind_loads.py`,
  `seismic.py`, `member_checks.py`, `formfinding.py`, `runoff.py` (the agents); three USGS answers saved.
  Then every function of the nine phases was written as an ES5 reference (not committed) and run against
  the scripts' numbers before its tests were written; each phase's test file passes against its reference
  and fails, case by case, against the empty file.
- **Independent check** (step 9): a fifth agent re-read the sources behind 33 facts the code uses and
  re-ran every script: 32 confirmed, 0 not confirmed, 1 unreachable (Ke's formula, dropped from the code).
  Its corrections are applied in part 4. `research-physical-world/independent-check.md`.
- **Refused hosts** (recorded in the topic notes): fema.gov (403), aisc.org (403), codes.iccsafe.org
  (403), archive.org, CSI's wiki, vibrationdata.com, awc.org, windspeed.atcouncil.org, nrc.gov, wbdg.
  FEMA P-2082 and P-2192 were read through other hosts (nibs.org).

## 4. Findings, by topic

Levels as the protocol defines them; "S2" means two or more independent secondary sources agree.

### 4.1 Gravity and floor loads (loads-wind-gravity.md 3.1 to 3.4)

- Live loads by occupancy: IBC 2021 Table 1607.1 read in Seattle's adopted code (P for the IBC, S for
  ASCE 7-22 Table 4.3-1, which it mirrors): offices 2.40 kPa, corridors above the first floor 3.83,
  residential 1.92, assembly 2.87 to 4.79, retail 3.59 to 4.79, light storage 5.99, roofs 0.96. High.
- Reduction: L = Lo (0.25 + 4.57/sqrt(KLL AT)) when KLL AT >= 37.16 m2, not below 0.5 Lo (one floor) or
  0.4 Lo (two or more); none above 4.79 kPa except 20 % for two or more floors; garages likewise;
  assembly never. KLL 4 for columns, 3 or 2 for cantilever-slab edge and corner columns, 2 for beams,
  1 otherwise. P (IBC) / S2 (7-22). Reproduces ENERCALC's published 45.131 psf. High.
- Roof live load 4.8: Lr = Lo R1 R2 held between 0.58 and 0.96 kPa. P (IBC) / S. High.

### 4.2 Wind (loads-wind-gravity.md 3.5 to 3.7, independent check W1 to W7)

- 7-22 velocity pressure q = 0.613 Kz Kzt Ke V^2 (Pa) without Kd; p = q Kd G Cp - qi Kd (GCpi). S2,
  confirmed. One 2023 slide still writes Kd inside q (counter-evidence recorded; p is the same).
- Kz = 2.41 (z/zg)^(2/alpha), z at least 15 ft; 7-22 constants B 7.5/3280 ft, C 9.8/2460 ft, D 11.5/1935
  ft. The formula matches all published B and C values, and the second reader found the 7-22 D column
  (Ghosh slide 145) matching it too: **the wind note's H7 (D disagrees) is reversed**. High.
- Kd 0.85, G 0.85 (rigid, n1 >= 1 Hz), GCpi +/-0.18, windward Cp 0.8 (q_z), leeward -0.5/-0.3/-0.2 by
  L/B (q_h), side -0.7; load cases 2 to 4 of Fig. 27.3-8 (75 %, e = 0.15 B; 0.563). S2; the case
  figure is P in the public ASCE 7-02 text. High.
- **Ke's exponential formula: one copy only (U). Not in the code**; Ke = 1.0 is always permitted and the
  user may enter a value.
- Basic wind speed: no documented keyless source (H4). The user enters V and Risk Category; the app links
  to the ASCE Hazard Tool.
- Worked example: 3 storeys, 30 x 20 m, V 50 m/s, C: storey forces 137.79, 144.98, 76.21 kN (re-derived
  by the second reader). V240's tests.

### 4.3 Earthquakes (seismic-dynamics.md 4.1 to 4.4)

- FEMA P-2082 (NEHRP 2020, the basis of 7-22's seismic chapters) read: multi-period spectrum, SDS and
  SD1 as 90 % of its peaks (21.4), the two-period spectrum's branches, site classes BC, CD, DE. P (NEHRP)
  / S (7-22). High.
- ELF in 7-22: Method 1 (new, Cs = Sa(T)/(R/Ie) from the multi-period spectrum) or Method 2 (SDS/SD1
  form); lower bounds 0.044 SDS Ie >= 0.01 and 0.5 S1/(R/Ie) where S1 >= 0.6 apply to both. Neither is
  always larger (Rudra and Ghosh); in the example Method 1 is 11 % lower. S2, confirmed. High.
- Ta = Ct hn^x (ft table: 0.028/0.8, 0.016/0.9, 0.030/0.75, 0.020/0.75); Cu 1.4 to 1.7 by SD1, whether
  to interpolate is U, so the code takes the lower Cu between rows (shorter T, larger Cs: conservative);
  k from 1 to 2 between 0.5 and 2.5 s. S2. High. Equation numbers differ between sources (P-2192 vs the
  note): kept out of labels.
- R, Cd, Omega0: steel SMF 8, 5.5, 3 (Cd moved to S by the second reader: an ATC/AISC 7-22 design
  report); others U, so the registry holds only the confirmed system and the user types the rest.
- Drift: Delta = Cd delta / Ie; limits 0.025/0.020/0.015 hsx (4 storeys or less) and 0.020/0.015/0.010
  (others) by risk category; divided by rho for moment frames in SDC D to F. P (NEHRP) / S. High.
- The USGS service: `https://earthquake.usgs.gov/ws/building-codes/asce7-22/calculate` (the old
  `/ws/designmaps/` path redirects through http: blocked on https). Keyless; `*` CORS, but a copy cached
  from a request without Origin is served without the header: a unique `title` per request avoids it;
  OPTIONS 405, so plain GETs only; an out-of-range point is HTTP 200 with `request.status` "error". P
  (tested twice, two agents). High.
- Worked example: 4-storey steel SMF in Los Angeles, Site C: Ta 0.5982 s, Cs 0.1463, V 1170.2 kN, k
  1.0491, Fx 111.3 to 476.4 kN; Method 1 V 1043.9 kN. V241's tests.

### 4.4 Modes, spectra, time history (seismic-dynamics.md 4.5 to 4.8)

- K phi = w2 M phi with lumped masses; Jacobi on M^-1/2 K M^-1/2 is exact (e01, 2-dof closed form,
  10-storey closed form). Participation: Gamma = phi' M iota / phi' M phi; effective mass sums to the
  total. P (PyNite, Frame3DD code read) / measured. High.
- 7-22 asks for modes reaching 100 % of the mass (with a residual mode) or at least 90 %; spectrum
  results scaled to 100 % of the ELF shear (85 % in 7-10). S. High.
- CQC (Der Kiureghian 1981) with r = wj/wi, 5 %; OpenSeesPy's official example passes w2 instead of w (a
  bug found here: rho 0.0013 instead of 0.0089). S + measured. High.
- Newmark average acceleration (gamma 1/2, beta 1/4): unconditionally stable, no decay; free vibration
  gives exactly u_n = cos(n theta), theta = 2 atan(w dt/2) (verified to 4e-14 here); MDOF equals modal
  superposition to 3e-13. P (OpenSees code) / measured. High.
- Ground motions: no record is both keyless and clearly redistributable (CESMD needs a registered e-mail,
  PEER a login). The app reads user-supplied records and uses synthetic pulses.

### 4.5 Member checks and cracking (member-checks-cracking.md)

- ACI 318-19: Ec = 4700 sqrt(f'c), fr = 0.62 lambda sqrt(f'c), Mcr = fr Ig/yt, Ie by Table 24.2.3.5
  (Bischoff; Branson removed in 318-19), Icr from the transformed section, beta1, phi by the steel strain.
  S2 (five secondary sources, four open implementations). High. 318-25 (2025) changes shear and phi, not
  Mcr or Ie (S).
- "Cracking" honestly shown: uncracked below 2/3 Mcr, reduced stiffness between 2/3 Mcr and Mcr (318-19
  reduces Ie there for restraint and shrinkage, though the section has not cracked), cracked above. No
  crack widths: 318 gives none.
- AISC 360-22: E3 compression, F2 flexure (Lp, Lr, Cb), H1-1 interaction, B4.1 compactness. S2 (three
  open implementations agree). High. W10x49 worked: phi Pn 2178 kN, phi Mn 286.6 kN m, H1 0.769.
- The app lacks the inputs: no f'c, no Fy, no reinforcement, no Lb/K, a steel catalogue of nominal plates
  only (properties from plates are within 1.4 % of AISC's table, J 6.9 % low, which errs safe). Claude's
  wiring in V243 and V244 adds them.

### 4.6 Form-finding (formfinding-runoff.md part A)

- Force density method: (Ci' Q Ci) x = p - Ci' Q Cf xf per axis; one linear solve; singular when a free
  node has no path to a support. P (compas_fd and jax_fdm code, MIT). High.
- Dynamic relaxation: leapfrog with fictitious masses (Barnes: lam dt2/2 sum k; safe at lam 1, diverges
  below 0.854 here); kinetic damping restarts at each energy peak. The position correction (midpoint) is
  derived and measured (converges; without it, 200 000 iterations do not), its attribution to Barnes
  1999 is U; Oasys GSA's mass rule (2 x the sum of translational stiffness) recorded. High for the
  method, measured.
- Hand-over to the frame solver: gridshells (members with bending) only; a cable net needs a truss
  element and tension-only iteration (later).

### 4.7 Stormwater runoff (formfinding-runoff.md part B)

- Priority-Flood with epsilon (Barnes, Lehman, Mulla 2014, Algorithms 1 and 3 read) fills depressions so
  every cell drains; D8 with diagonals at sqrt 2 (WhiteboxTools code, MIT); accumulation in topological
  order. P. High. 200 x 200 in 45 ms here.
- Rational method Q = C i A / 360 (SI), composite C by area, under 80 ha: HEC-22 4th edition (FHWA,
  2024), read. P. High. C ranges differ by jurisdiction (TxDOT in six rows): a registry record with its
  edition.
- Rainfall: NOAA Atlas 14 PFDS, keyless, no CORS (H5): the user types the intensity or pastes the CSV.

## 5. The alternatives compared

Criteria, set before the comparison: (a) gives results an engineer recognises (code loads, member
ratios); (b) runs in the app's contract (ES5, offline, one file, no unapproved library); (c) cost to build
and to load; (d) testable against published examples.

| Option | (a) Engineering result | (b) Contract | (c) Cost | (d) Testable | Verdict |
|---|---|---|---|---|---|
| A. Code loads + the existing frame solver + member checks, our own ES5 (this note) | Yes: the same procedures as ETABS, RAM, SkyCiv | Yes | Nine small phases, no download | Yes: every example reproduced | **Recommended** |
| B. A rigid-body engine (Jolt or Rapier, WASM) | No stress, no code loads; contacts only | A new library and WASM in the one-file build | Large | Only motion | Not for structure; maybe construction sequencing later |
| C. PyNite or OpenSeesPy in the Pyodide worker | Yes for analysis; checks still ours | A new Python library (PyNite MIT; OpenSees non-commercial: refused by the rule) | Pyodide download (tens of MB) | Yes | Later, as a cross-check of V242 and for plates |
| D. OpenFOAM / CalculiX as a server | CFD and nonlinear FEA | Breaks offline and the one-file build | A server to run | Yes | Out; V221's lattice Boltzmann covers wind flow qualitatively |
| E. Geodetic gravity per element | Changes loads by under 0.27 % (e02) | Yes | Small but useless | - | Out |

What would change the recommendation: a need for plate and shell results (slabs, walls) would bring
option C forward; a nonlinear collapse study needs a solver this note does not cover.

## 6. The experiments

| Id | Script | What it measured | Result |
|---|---|---|---|
| e01 | `e01_eigen_speed.mjs` (Node 22) | cyclic Jacobi on shear buildings of 10 to 240 dof against the closed form | 2 ms (10), 20 (30), 18 (60), 182 (120), 1578 (240); error 4e-15 to 9e-12 |
| e02 | `e02_gravity.py` | WGS 84 normal gravity by latitude and height; the turn of the vertical | -0.268 % (equator) to +0.260 % (pole); 0.009 degrees per km |
| E1 to E5 | `seismic.py`, three `usgs-*.json` | the USGS service, ELF, eigenproblems, CQC, Newmark | as part 4.3 and 4.4 |
| - | `wind_loads.py` | Kz against 88 tabulated values, the 3-storey example, live load reduction | all asserts pass |
| - | `member_checks.py` | the RC beam and the W10x49 column | all asserts pass |
| - | `formfinding.py`, `runoff.py` | FDM, DR, D8, fill, rational method | all asserts pass |
| refs | not committed | the nine phases' functions in ES5 against the scripts' numbers | every value matched; tests pass against them, fail against the empty files |

## 7. Edges

The topic notes list them in full (each part 7). Those the tests are built on: z below 4.572 m and above
zg; L/B at 1, 2, 4; KLL AT at exactly 37.16 m2; Lo at exactly 4.79 kPa; the spectrum's T0, TS and TL
corners; S1 at 0.6; k at 0.5 and 2.5 s; Pr/Pc at exactly 0.2; Ma at exactly 2/3 Mcr and Mcr; the phi
transition zone; Lb at Lp and Lr; a free node without a support; flats after a fill without epsilon;
a cycle in flow directions; NoData cells as outlets; the USGS error with HTTP 200.

## 8. What the app already has

- `structure/analytical-model.js` 160-210: load kinds (line, point, lateral at a column top), cases D and
  L only, `bimStructLoads`; 80-158: the analytical model (Y up, kN, m); members carry rho, A, E, G.
- `structure/frame-solve.js` 107-219: the banded direct-stiffness solve, reactions, equilibrium check;
  246-286: member results (N positive in tension).
- `structure/tributary-loads.js`: Voronoi tributary areas and the column takedown (AT and the floors
  above: what live load reduction needs); it says reduction is not included.
- `structure/analysis-properties.js` 124: "Not included: Floor loads, wind, seismic"; 131-132: Dead and
  Live per level.
- `standards/registry.js` 209-212, 993-998: ASCE 7-22 2.3.1 combinations 1 and 2 only.
- `site-analysis/climate-data.js` 52, 255-265: the site's latitude and longitude, and a USGS earthquake
  catalogue fetch (events, not design values).
- `bim/section-profiles.js` 26: section properties from the profile's plates.
- `terrain/terrain-tin.js`: the TIN the runoff grid is sampled from.
- `analysis/lbm-ref.js` (V221) and `ladybug/`: wind flow and sun, as before.

## 9. Risks and threats to validity

- Every code value is S: the standards are sold (ASCE 7, ACI 318) or refused here (AISC). Two or more
  secondary sources agree on each and a second reader re-derived them, but errata and edition changes can
  only be caught from the text. The owner's copy of ASCE 7-22 would close the U cells (Table 12.2-1 beyond
  the steel SMF, the Cu interpolation, 2.3.6's snow factor, equation numbers).
- The worked examples come from the research's own scripts; Chopra's table was recalled, not read (the
  script's numbers are what the tests use).
- The USGS service's CORS was tested with curl, not from a real https page or `file://`.
- Member checks cover only compact W shapes and singly reinforced rectangles; everything else must be
  refused as "not checked", or a ratio will be shown where none applies.
- Linear analysis: no P-delta, no cracking feedback into stiffness, no tension-only members.

## 10. What is still open (U), and why

Ke's formula (one copy; the code uses Ke = 1 or the user's value); the Cu interpolation; Table 12.2-1
rows other than the steel SMF; the snow factor in 2.3.6 (0.2 or 0.15; no snow load in the app yet);
7-22's 12.9.2 response-history rules (ground-motion selection and scaling); ACI's SI coefficients for Vc
(the code leaves Vc out); AISC H1.2 in tension (the code checks compression only); the kinetic-damping
correction's attribution; NOAA's confidence-bound files; non-US rainfall and wind sources; CSI's
practice pages (refused).

## 11. The owner's decisions

The protocol asks them together at the end of research. The owner asked for the work orders to follow
the research in one sprint ("Do your research first, properly. And then develop the work orders",
2026-11-21), so the work orders were written on the recommendations below.

**Answered 2026-11-22** (the owner: "do what standards and easy to scale once the app got more
sophisticated"): each decision takes the choice that is standard practice and scales as the app grows. That
keeps twelve as recommended and amends three (4, 9, 11), marked **Amended** below. What makes it scale is
the same throughout: values that change with an edition or a place are registry data (V167), not code; each
analysis is a pure function the model graph (V230) can call; and each heavy step (eigensolver, section
properties, data sources) sits behind one interface, so a larger solver or a published table can replace it
without changing its callers.

1. **Order.** V239 floor, V240 wind, V241 earthquake, V242 modes, V243 concrete, V244 steel, V245 time
   history, V246 form-finding, V247 runoff, after the queue's V236. Recommended: as listed.
2. **Codes.** US first (ASCE 7-22, ACI 318-19, AISC 360-22); Eurocode later as registry editions.
   Recommended: yes.
3. **Wind speed.** The user enters V and Risk Category; a link to the ASCE Hazard Tool; ASCE's
   undocumented map server not used without ASCE's permission. Recommended: yes.
4. **Wind cases.** **Amended:** ASCE 7-22 requires all four cases of Figure 27.3-8, so all four are
   computed as data (`bimWindCases`). Cases 1 and 3 (translation, each direction and both at once) are
   applied to the frame now. Cases 2 and 4 are applied once V242's rigid floors take a torsion; until
   then, the result says they are not yet applied.
5. **Live load reduction.** A switch per project, off by default (the takedown's conservative default).
   Recommended: off by default.
6. **ELF method.** Method 2 by default, Method 1 beside it where the USGS answer has the multi-period
   spectrum. Recommended: yes.
7. **The USGS service.** Called from the browser with a unique title, its answer cached in the project so
   the app works offline, credited "U.S. Geological Survey"; outside the US, typed SDS, SD1, S1, TL.
   Recommended: yes.
8. **Seismic systems.** The registry carries the steel SMF (R 8, Cd 5.5, Omega0 3); other systems typed
   by the user until the owner's copy of Table 12.2-1 is read. Recommended: yes.
9. **Mass and modes.** **Amended:** lumped masses per storey (self-weight plus the level's dead load), three
   degrees of freedom per storey with rigid floors, and our own Jacobi now, as ETABS does. The
   eigensolver sits behind one interface (K and M in, modes out), so a subspace-iteration solver on the
   full frame (Bathe; Frame3DD's method) can replace it when models outgrow about 120 degrees of freedom
   (e01) without changing its callers. No library.
10. **Ground motions.** User-loaded records and synthetic pulses; no record shipped. Recommended: yes.
11. **Concrete and steel inputs.** **Amended:** f'c and Fy on the material cards (the solve keeps the
    card's E, and a mismatch with 4700 sqrt(f'c) is shown); reinforcement per beam type (bottom and top
    bars, cover); Lb = member length, K = 1, Cb = 1 by default with an override. Section properties come
    through one source that prefers a published table, the industry standard (AISC's Shapes Database,
    once its licence is read; other catalogues as further editions). It falls back to properties
    computed from the plates (`bimStIProps`), labelled as such.
12. **Colours.** Grey not checked; ratio bands under 0.5, 0.5 to 0.9, 0.9 to 1.0, over 1.0; cracking
    uncracked / reduced / cracked. Recommended: yes.
13. **Form-finding.** Force density first, dynamic relaxation second; a V230 graph node later; hand over
    gridshells only. Recommended: yes.
14. **Runoff.** Typed intensity or a pasted PFDS CSV; C from HEC-22 4th edition as a registry record;
    minimum tc 5 minutes; fill and show ponding; a grid of about 200 cells across the site, at least
    0.5 m. Recommended: yes.

## 12. References

All read 2026-11-21. The topic notes list every source with its URL, what was read and its level; the
principal ones:

| Source | What was read | Level |
|---|---|---|
| USGS Seismic Design Web Services, `earthquake.usgs.gov/ws/building-codes/asce7-22/calculate` and its swagger page | the answer's fields, errors, CORS, timing | P (tested) |
| FEMA P-2082-1 (NEHRP 2020 Provisions), via nibs.org | 11.4, 12.8, 12.9, 12.12, 21.4 and commentary | P (NEHRP), S (7-22) |
| FEMA P-2192 (2020 NEHRP design examples), nibs.org | ELF and drift examples citing 7-22 | S |
| IBC 2021 as adopted by Seattle | Table 1607.1, 1607.12, 1607.14 | P |
| ICC and S. K. Ghosh ASCE 7-22 course decks; Smith 2023; Oasis calculator code | 26.6 to 27.3, Tables 26.10-1, 26.11-1 | S |
| ASCE 7-02 (public text) | Fig. 6-6, 6-9, Eq. 6-17 | P (for 7-02) |
| ATC 154 steel SMF design report (femap2343.atcouncil.org) | R, Cd, Omega0 for the steel SMF under 7-22 | S |
| PyNite (MIT), Frame3DD (GPL-3, method only), OpenSees (method only), structural-frame-analysis (MIT) | modal analysis code | P (code) |
| StructurePoint, ideCAD, RISA, concrete-properties (MIT), structuralcodes (Apache-2.0) | ACI 318-19 values | S |
| libdenavit, efficalc, steel_calculator; AISC Shapes Database values as copied | AISC 360-22 E3, F2, H1, B4.1; W10x49 | S |
| compas_fd, jax_fdm (MIT); compas 1.x `dr.py`; Rodriguez et al. 2011; Oasys GSA | FDM and DR | P (code), S |
| Barnes, Lehman, Mulla 2014 (arXiv 1511.04463); Tarboton 1997; WhiteboxTools (MIT) | Priority-Flood, D8, D-infinity | P |
| FHWA HEC-22, 4th edition (FHWA-HIF-24-006, 2024) | eq. 4.1 to 4.5, Table 4.1 | P |
| NOAA HDSC PFDS and Atlas 15 page | the CSV endpoint, CORS, status | P (tested) |
| NIMA TR8350.2 (WGS 84) | normal gravity constants (e02) | S (constants as widely reproduced) |
