# V172c, Ladybug L2: sun-hours and radiation on the model -- research

Started 2026-11-01 ("start v172c"). Follows `reference/research-protocol.md` and
`reference/reuse-first-integration.md`. The frame is the owner's decisions of 2026-10-26
(`reference/research-ladybug-tools.md`, 6): Ladybug's own Python, unchanged, in Pyodide; AGPL accepted;
no Honeybee; numpy only "if its sky needs it". **Status: first pass; the owner's decisions asked (part 11)
before the experiments and the independent check.**

## 1. Abstract

The question: how the app can give Ladybug's direct-sun hours and incident radiation on the model's faces, in the
browser, without Radiance. The answer so far: ladybug-radiance 0.2.12 (the package Ladybug uses for both studies)
cannot run in Pyodide as it is, because **both** of its expensive steps call Radiance programs through
`subprocess`: the sky matrix (`gendaymtx`) and the ray intersection (`oconv`, `rcontrib`). Its other parts are
plain Python over numpy and can run: the Tregenza and Reinhart patch vectors (in ladybug-core), the radiation
sum (`intersection_matrix . (sky + ground)`), the direct-sun count, and the studies' result objects.
So two pieces must come from somewhere else: the sky per patch, and the rays. The recommendation, to be confirmed
by the experiments in part 6: the Perez all-weather sky computed per patch in Python, a port of `gendaymtx`'s method
(Radiance's licence is BSD-style), fed into ladybug-radiance's own `SkyMatrix` and `RadiationStudy`; the rays cast
by the app's own JS (V143's Moller-Trumbore with boxes, in a worker), handed to the study as its intersection matrix.

## 2. The question and the hypotheses

Question: what V172c builds so that sun-hours and annual radiation on the model's faces are Ladybug's method, with
the year of weather V172b already holds, in a browser, at a speed a designer accepts.

| # | Hypothesis (falsifiable) | Outcome so far |
|---|---|---|
| H1 | ladybug-radiance runs in Pyodide unchanged | **Failed** (P): `skymatrix.py` 541-566 runs `gendaymtx`; `intersection.py` 77-180 runs `oconv`, `obj2mesh`, `rcontrib`; both `assert` a Radiance install first. Pyodide has no `subprocess` programs. |
| H2 | ladybug-core has a sky model that gives per-patch radiation | **Failed** (P): `ladybug/skymodel.py` (0.44.63) has ASHRAE clear sky (2009, revised), Zhang-Huang, DIRINT, DISC, illuminance from irradiance, sky temperature; none distributes radiation over sky patches. `ladybug/viewsphere.py` has the patches (Tregenza 145, Reinhart 577) and their solid angles, not the radiance. |
| H3 | ladybug-radiance's sums run once given a sky and an intersection matrix | Held on reading (P): `RadiationStudy.compute()` (radiation.py 249-277) uses only `sky_matrix.data` and `_intersection_matrix`; `SkyMatrix.data` reads `_direct_values` and `_diffuse_values`. Not yet run. |
| H4 | A Python port of `gendaymtx`'s Perez sky agrees with `gendaymtx` within 1% per patch, annual total | Open: needs `gendaymtx` built here as the reference (part 11, question 2). |
| H5 | The app's JS rays give the same intersection matrix as Radiance's `rcontrib` for a test scene, every patch | Open: same reference needed; a geometric check (a box, a canyon) can be computed by hand meanwhile. |
| H6 | A typical model (5,000 faces, 145 + 145 patches) runs in under 30 s in a worker | Open: to be measured. |

## 3. Method

Sources so far, by kind: two upstream packages read as text (ladybug-radiance 0.2.12's wheel, ladybug-core 0.44.63's
wheel, as committed in `runtime/wheels/`); Radiance's `gendaymtx.c` and its licence (GitHub, LBNL-ETA/Radiance,
`master` at `5b2a2154`, 2026-10-27); Pyodide 0.29.5's `pyodide-lock.json`; the app's code. Still to do (part 10):
the Perez papers, Radiance's manual page, Ladybug's own documentation and forum on the incident radiation component,
prior art (Ladybug Legacy's GenCumulativeSky, ClimateStudio, Autodesk Forma's sun hours), the experiments, and the
independent second reader.

Search log, 2026-11-01:

| Where | What | Kept |
|---|---|---|
| PyPI JSON, `ladybug-radiance` | latest 0.2.12, AGPL-3.0, needs `ladybug-core>=0.41.30`, `numpy>=1.21.6` | the wheel, SHA-256 `66d57a56...defa028a9e629`, 51,148 bytes |
| the wheel, read | 3,122 lines in 11 files; `subprocess` in `skymatrix.py`, `intersection.py`, `config.py` | parts 4.1, 4.2 |
| ladybug-core wheel (runtime) | `skymodel.py` functions; `viewsphere.py` patch tables | part 4.3 |
| raw.githubusercontent.com, LBNL-ETA/Radiance | `src/gen/gendaymtx.c` (1,329 lines), `License.txt` (Radiance Software License 2.0, BSD-3 style) | part 4.4 |
| git clone LBNL-ETA/Radiance | the default branch `cvsimport` holds only a README; the code is on `master` | the branch noted |
| local build of `gendaymtx` | refused by this session's sandbox (running code from outside) | asked of the owner, part 11 |
| `pyodide-lock.json` 0.29.5 | numpy 2.2.5, `numpy-2.2.5-cp313-cp313-pyemscripten_2025_0_wasm32.whl`, SHA-256 `800c98ed...7f05c` | not yet in `runtime/` |

## 4. Findings

**4.1 The sky (P, high).** `SkyMatrix.compute_sky()` writes a Wea and runs `gendaymtx -m 1|2 -d|-s -O1 -A`, once for
the direct part and once for the diffuse, then turns each patch's RGB radiance into broadband
(0.265074126 R + 0.670114631 G + 0.064811243 B), times the patch row's solid angle, times the hours, over 1000:
kWh/m2 per patch. The ground patch is dropped; `RadiationStudy` adds a ground of the mean sky times the ground
reflectance (0.2 by default) for every downward vector.

**4.2 The rays (P, high).** `sky_intersection_matrix` reverses the patch vectors for the ground (so 2 x 145 vectors on a
Tregenza sky), writes every context face as a black Radiance polygon and every vector as a 0.533 degree source, and
has `rcontrib` give, per sensor, the cosine (numericalize) or seen/not seen. Nothing Radiance-specific is in the
result: a list per sensor, one number per vector.

**4.3 Ladybug's core (P, high).** The patch geometry the app needs is there: `view_sphere.tregenza_dome_vectors`,
`reinhart_dome_vectors`, rows (30, 30, 24, 24, 18, 12, 6 + 1) and solid angles per row. The sun path for direct-sun
hours is `ladybug.sunpath`, already in the runtime.

**4.4 gendaymtx (P on the code read; the numbers untested).** Perez all-weather sky (Perez, Seals and Michalsky 1993,
with its erratum) and the Perez irradiance model's luminous efficacy (Perez, Ineichen, Seals, Michalsky and Stewart
1990) for the distribution; the sun's energy put in the patches nearest the sun (`AddDirect`); Radiance's own
`sun.c` for the position. Licence BSD-3 style: a port may be shipped with the notice kept.

**4.5 The app (P, its code).** `src/js/engine/analysis/simulation.js`: `bimSunHours` (24-71) rasterises shadows on the
ground for one day; `bimSolarRun` (186-) gives roofs and facades a year of an assumed clear sky (DNI from an air mass
formula, the sky as 0.1 DNI, isotropic; lines 75-90, 152-164), shading by `bimRayBlocked` (Moller-Trumbore with a box
per solid, 118-150), in 40 ms slices on the main thread. V172b's worker (`src/js/engine/ladybug/`,
`src/py/bim_ladybug.py`) holds a year of DNI and DHI from an EPW or Open-Meteo. Result layers (V148,
`analysis/results-layers.js`) already show sun hours on the ground.

## 5. The alternatives compared

Criteria, set before the table: Ladybug's method (the owner's decision 2); runs in the browser offline of PyPI;
agrees with Radiance; speed; size added to `runtime/`; licence.

| | Sky per patch | Rays | Ladybug's method | Size | Risk |
|---|---|---|---|---|---|
| A | Perez port in Python (from `gendaymtx`) | app's JS, in a worker | Ladybug's studies and sums, the sky ported | numpy about 3 MB, or none (H3's plain-float path) | the port's agreement (H4) |
| B | `gendaymtx` compiled to WebAssembly | app's JS | the same program as Ladybug desktop | a new toolchain (Emscripten), a binary in `runtime/` | a build the app has never had |
| C | Isotropic sky + the sun from each hour's DNI | app's JS | the studies' sums only | none | differs from Ladybug on facades (anisotropy), by an amount to measure |
| D | Perez port | numpy Moller-Trumbore in Pyodide | as A | numpy | slower than JS for large models, to measure |

Recommendation for now: **A**, with C kept as the check it should beat. What would change it: H4 failing by more
than a few percent (then B), or H6 failing (then rays on the GPU).

## 6. The experiments (planned, not run)

1. `reference/experiments/v172c_sky.py`: the Perez port and `gendaymtx` on the same EPW (two climates), per patch and
   annual, needing question 2.
2. `v172c_rays`: a box, an urban canyon and a courtyard: the JS matrix against the closed-form view factors.
3. Speed: 500, 5,000 and 20,000 faces, in Chromium 1243.

## 7. Edges

The sun below the horizon but DHI above zero (dawn); DNI with the sun under 5 degrees (Perez's `gendaymtx` clamps);
a polar day and night; leap years (V172b's `leap`); half-hour time zones (V172b gives UTC hours); faces facing down;
a sensor on a face that touches another (the offset); north rotated (`SkyMatrix.north`).

## 8. What the app already has

Part 4.5, by file and line.

## 9. Risks and threats to validity

Only the code was read so far, nothing run. The Perez coefficients' transcription is the main risk of a port; the
reference run is what removes it. Safari and phones: Pyodide's limits from V172b still apply.

## 10. Still open (U)

The Perez papers themselves; Radiance's `gendaymtx` manual page; prior art; the measured speed; the independent check;
which faces are sensors (the model's faces as they are, or a grid on each, as Ladybug's `study_mesh` is).

## 11. The owner's decisions (asked 2026-11-01)

1. The approach: A (Perez port in Python + the app's rays), B (`gendaymtx` in WebAssembly), or C (isotropic, simpler).
2. May `gendaymtx` be compiled and run here, in the scratchpad only, as the reference the port is measured against?
   (The sandbox refused it without the owner's word.)
3. numpy added to `runtime/` (about 3 MB, pinned by SHA-256), or the plain-float path ladybug-radiance also has.
4. What replaces V143's clear-sky SOLAR and V148's ground sun hours: kept beside the Ladybug studies, or replaced.

Answers: (awaited)

## 12. References

| Source | URL | Read | Date | Level |
|---|---|---|---|---|
| ladybug-radiance 0.2.12 wheel | https://pypi.org/project/ladybug-radiance/0.2.12/ | every file, as text | 2026-11-01 | P |
| ladybug-core 0.44.63 wheel | `runtime/wheels/` | `skymodel.py`, `viewsphere.py` | 2026-11-01 | P |
| Radiance `gendaymtx.c`, `License.txt` | https://github.com/LBNL-ETA/Radiance (master, 5b2a2154) | the header, function list, licence | 2026-11-01 | P |
| Pyodide 0.29.5 `pyodide-lock.json` | `runtime/pyodide/0.29.5/` | numpy's entry | 2026-11-01 | P |
| The app | `src/js/engine/analysis/simulation.js`, `src/js/engine/ladybug/` | as cited | 2026-11-01 | P |
