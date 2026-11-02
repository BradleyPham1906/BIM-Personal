# V172c second reader: the facts the code uses, re-read in their primary sources, 2026-11-01

An independent re-check of `reference/research-ladybug-sun-radiation.md`. Every source was read as text in a scratch
folder outside the repository: the committed wheels unzipped (`runtime/wheels/ladybug_radiance-0.2.12`,
`ladybug_core-0.44.63`, `ladybug_geometry-1.35.7`), Radiance from raw.githubusercontent.com/LBNL-ETA/Radiance/master
(`src/gen/gendaymtx.c`, `src/gen/Rmakefile`, `src/gen/loadEPW.c`, `License.txt`, `doc/man/man1/gendaymtx.1`,
`doc/man/man1/rcontrib.1`, `src/rt/rcontrib.c`), PyPI's JSON for ladybug-radiance 0.2.12, Pyodide 0.29.5's committed
`pyodide-lock.json`, `pyodide.asm.js` and `pyodide.js`, Pyodide's `docs/usage/loading-packages.md` at tag 0.29.5, and
Howell's catalogue page B-3 (thermalradiation.net). Paths below: `lbr/` = `ladybug_radiance/`, `lbc/` = `ladybug/`
(ladybug-core). Nothing in the repository was changed but this file.

| # | Fact | Verdict | Where read | Note |
|---|---|---|---|---|
| 1a | `skymatrix.py` runs gendaymtx through `subprocess` with `-m <1\|2>`, `-d` / `-s`, `-O1`, `-A`, the Wea file | CONFIRMED | `lbr/skymatrix.py:13` (import), `:551` (density 2 if high_density else 1), `:554` (`-m`, density, `-d`, `-O1`, `-A`, wea_file), `:559` (same with `-s`) | `subprocess.Popen`, stdout piped |
| 1b | RGB to broadband 0.265074126 R + 0.670114631 G + 0.064811243 B, times the row's solid angle, times the Wea's hours, / 1000 | CONFIRMED | `lbr/skymatrix.py:613-616`; hours `:472` (`len(wea) / wea.timestep`), also `:435`; row coefficients `:65-68` from `view_sphere` | |
| 1c | It drops the ground patch | **NOT CONFIRMED** (with the gendaymtx this project built) | `lbr/skymatrix.py:582-584` (`data_lines[9:-1]`, comment "remove the header, ground patch"); `gendaymtx.c:642-656` (header), `:928-933` (patch 0 is the ground, the last patch the zenith) | The slice assumes an 8-line header. gendaymtx at master / `5b2a2154` writes 9 with `-A`: `#?RADIANCE`, the command, `LATLONG=`, `NROWS=`, `NCOLS=`, `NAVERAGED=` (printed when averaging, `:649-650`), `NCOMP=3`, `FORMAT=ascii`, blank. So line 9 is the ground, and the 145-patch loop (`:589-594`) takes ground + 144 sky patches and drops the zenith: every sky value sits one patch off. Measured below with the committed `runtime/radiance/gendaymtx.wasm`. Not checked: whether older Radiance releases (the ones Ladybug Tools installs) omit `NAVERAGED` (GitHub's API refused the history query, 403) |
| 2 | `RadiationStudy.compute()`: ground = mean of the sky patches x ground_reflectance (0.2 by default in SkyMatrix); radiation = intersection matrix . (sky + ground); numpy when available | CONFIRMED | `lbr/study/radiation.py:262-277` (`:265`/`:274` ground value, `:267`/`:276` concatenation, `:277` `np.dot`, `:263` plain-float path when `np is None`); default `lbr/skymatrix.py:76` | The ground vector is one value repeated for each reversed patch, in the order `sky_intersection_matrix` builds (`lbr/intersection.py:251-252`) |
| 3a | `sky_intersection_matrix` uses the dome vectors plus their reverses for the ground | CONFIRMED | `lbr/intersection.py:246-252` | Tregenza or Reinhart by `high_density`; rotated by `north` (`:248-250`) |
| 3b | `intersection_matrix`: oconv, rcontrib with `-I -ab 0`, each vector a 0.533 degree `source` of radiance 1, scaled by 14713 | CONFIRMED | `lbr/intersection.py:132-133` (`void light ... 3 1.0 1.0 1.0`; `source ... 4 <dir> 0.533`), `:159-160` (oconv), `:169` (`-V- -aa 0.0 -y N -I -faf -ab 0 -dc 1.0 -dt 0.0 -dj 0.0 -dr 0 -M`), `:174` (`rmtxop -c 14713 0 0`), `:197-198` (numpy: `[14713, 0, 0]`, the first channel only) | 1 / solid angle of a 0.533 degree disc = 1 / (2 pi (1 - cos 0.2665 deg)) = 14713.02, computed here |
| 3c | With numericalize=True an entry is the cosine between the sensor normal and the direction when unblocked; with False booleans | CONFIRMED (the cosine: Ladybug's docstring plus the arithmetic; the rcontrib step at S level) | `lbr/intersection.py:52-57` (docstring: "the cosine of the angle between the normal and each vector"), `:199-200` (booleans); `rcontrib.1:93-98` | rcontrib `-I` gives the irradiance from each source: radiance 1 x solid angle x cos theta; x 14713 = cos theta. The man page says that with `-I` the `-V-` coefficients "contain an additional factor of PI"; I did not trace in `rcontrib.c` how that factor cancels the Lambertian 1/pi of the irradiance ray, so the "exactly cos theta" step rests on Ladybug's docstring and the scale |
| 3d | RadiationStudy numericalize=True; DirectSunStudy numericalize=False, reversed sun vectors, hours = row sum / timestep | CONFIRMED | `lbr/study/radiation.py:355-357`; `lbr/study/directsun.py:300-303` (`v.reverse()`, `numericalize=False`), `:235-241` (`sum / t_step`) | |
| 4 | Tregenza rows (30,30,24,24,18,12,6) + zenith = 145; Reinhart 577; per-row solid angles; both sum to 2 pi | CONFIRMED | `lbc/viewsphere.py:34-35` (rows), `:37-43` (coefficients), `:120-121`, `:170-171` (+ the zenith row of 1) | Summed here from the file: Tregenza 145 patches, 6.2831853069; Reinhart 577, 6.28318529582; 2 pi = 6.28318530718 (differences 1e-10 and 1.1e-8) |
| 5 | Ladybug's `sun_vector` points from the sun toward the ground; north +Y, up +Z | CONFIRMED | `lbc/sunpath.py:1167-1172` (docstring: "daytime sun vectors point downward (z will be negative)"), `:1174-1180` (reversed points up), `:1226-1240` (north_vector (0,1,0), rotated about X by altitude, then by -azimuth in XY, then reversed), `:42-43` (north angle measured from +Y) | Worked out from `:1232-1234`: reversed = (cos e sin a, cos e cos a, sin e), east +X |
| 6 | The app's `bimSunVector` = [cos e sin a, sin e, -cos e cos a]; Ladybug (x,y,z) maps to the app as (x, z, -y) | CONFIRMED, for the vector toward the sun | `src/js/engine/site/shadows.js:7-10`; azimuth clockwise from true north `src/js/engine/site/sun-position.js:7` | `bimSunVector` points toward the sun (y = sin e > 0 by day), so it is Ladybug's `sun_vector_reversed` mapped by (x, z, -y), not `sun_vector`. Its azimuth includes `bimTrueNorthDeg()` (`src/js/engine/survey/survey-arithmetic.js:2-5`). The note's part 5 writes the inverse map, app (x,y,z) -> Ladybug (x, -z, y): consistent |
| 7a | gendaymtx.c implements the Perez all-weather sky (Perez, Seals and Michalsky 1993) and cites Perez 1990 for the irradiance / efficacy model | CONFIRMED | `gendaymtx.c:7` ("Perez Sky Model"), `:35-48` (Perez, Ineichen, Seals, Michalsky, Stewart 1990, Solar Energy 44(5):271-289; Perez, Seals, Michalsky 1993, Solar Energy 50(3):235-245, and its erratum 51(5):423), `:141-148` (sky coefficients, 1993), `:192-195`, `:218-240` (irradiance-component and luminous-efficacy coefficients, 1990) | |
| 7b | Rmakefile builds gendaymtx from gendaymtx.o sun.o loadEPW.o with -lrtrad | CONFIRMED | `Rmakefile:52-53` | `$(MLIB)` too |
| 7c | It reads the weather from stdin when no file is named | CONFIRMED | `gendaymtx.c:440-443` (`EPWopen(argv[i])`, `i == argc` allowed), `:449-454` ("reading weather tape from <stdin>"); `loadEPW.c:196-198` (NULL name -> `stdin`) | |
| 8 | Radiance's `License.txt` is the Radiance Software License 2.0, BSD-3 style (three conditions); copyright line | CONFIRMED | `License.txt:1` ("The Radiance Software License, Version 2.0"), `:3-5`, `:10-20` (conditions (1)-(3)) | Copyright line: "Radiance v6.1 Copyright (c) 1990 to 2025, The Regents of the University of California, through Lawrence Berkeley National Laboratory (subject to receipt of any required approvals from the U.S. Dept. of Energy). All rights reserved." |
| 9 | ladybug-radiance 0.2.12: AGPL-3.0; wheel SHA-256 66d57a56...defa028a9e629 | CONFIRMED | https://pypi.org/pypi/ladybug-radiance/0.2.12/json `info.license` = "AGPL-3.0", `urls[]` digest for the wheel; wheel `METADATA` "License: AGPL-3.0"; `dist-info/licenses/LICENSE` line 1 (GNU AGPL v3) | `sha256sum runtime/wheels/ladybug_radiance-0.2.12-py3-none-any.whl` gives the same 66d57a562c3e896e9ae55e685a4f45e0a0ada28a8948b749966defa028a9e629 |
| 10a | `pyodide-lock.json` pins numpy 2.2.5's wheel with sha256 800c98ed...7f05c; `runtime/pyodide/0.29.5/` holds it | CONFIRMED | `runtime/pyodide/0.29.5/pyodide-lock.json` `packages.numpy` (version, file_name, sha256); `sha256sum` of `runtime/pyodide/0.29.5/numpy-2.2.5-cp313-cp313-pyemscripten_2025_0_wasm32.whl` = 800c98edc0c864dfa49f07005680c699b4b42b84eae1f8cb19d35b3634e7f05c | |
| 10b | Pyodide 0.29.5's `loadPackage` verifies a package's sha256 when loading from indexURL | CONFIRMED in a browser (main thread or worker); **NOT CONFIRMED in Node** | `runtime/pyodide/0.29.5/pyodide.asm.js` line 8 (minified): `loadPackage(e,r={checkIntegrity:!0})`; `downloadPackage`: for a lock-file package `i="sha256-"+Xt(l.sha256)` (hex to base64), `r\|\|(i=void 0)`; `browser_getBinaryResponse`: `fetch(r, e?{integrity:e}:{})`; `node_getBinaryResponse` `function In(t,e)` reads the file or fetches **without** using `e` | In browsers the check is the Fetch API's Subresource Integrity on the lock's hash (default on). Under Node the hash is ignored, and on a local miss Node falls back to the CDN, also unchecked. `loading-packages.md` (0.29.5) mentions hash checks only for micropip (lines 74-75), not for `loadPackage`. So `reference/experiments/v172c-sky/np_load.js` (Node) did not check the SHA-256, despite its first comment |
| 11 | View factor, differential horizontal element to a parallel rectangle with one corner on its normal: F = (1/(2 pi)) [A/sqrt(1+A^2) atan(B/sqrt(1+A^2)) + B/sqrt(1+B^2) atan(A/sqrt(1+B^2))] | CONFIRMED | Howell, *A Catalog of Radiation Heat Transfer Configuration Factors*, https://www.thermalradiation.net/sectionb/B-3.html , configuration **B-3** ("Differential planar element to finite parallel rectangle. Normal to element passes through corner of rectangle"), equation image `images/B-3eq.gif` | Exact form: F_d1-2 = (1/2pi) { A/(1+A^2)^(1/2) tan^-1[B/(1+A^2)^(1/2)] + B/(1+B^2)^(1/2) tan^-1[A/(1+B^2)^(1/2)] }, A = a/c, B = b/c, c the distance from the element to the rectangle's plane. References given there: Hottel 1931; Hamilton and Morgan 1952. Courtyard (a = b = 10, c = 12): 4F = 0.464158, computed here |
| 12 | `bimRayTri` is Moller-Trumbore, \|det\| < 1e-12 rejected, t > 1e-6 accepted; `bimRayBlocked` tests each solid's box then its triangles, a linear scan over all solids | CONFIRMED | `src/js/engine/analysis/simulation.js:132-142` (`:136` det, `:141` t), `:143-150` (loop over every occluder, box then triangles, first hit returns), `:108-120` (`bimSolarOccluders`: every visible solid, one box each), `:122-131` (`bimRayBox`, slab test from t = 0) | Occluders are only `o.t === 'solid'` on shown layers |

## The re-run (read-only; output written only to the scratch folder)

`python3 -I reference/experiments/v172c-rays/dome.py <scratch>` wrote `<scratch>/exp/dome.json` (no output lines).
`node reference/experiments/v172c-rays/rays_exact.js /home/user/BIM-Personal <scratch>/exp/dome.json`:

    open ground    tregenza: 290 entries, 0 differ from the exact answer, 0 on an edge; sky view factor 0.9999
    canyon floor   tregenza: 290 entries, 0 differ from the exact answer, 0 on an edge; sky view factor 0.4674
                   infinite canyon, analytic: cos(atan(2H/W)) = 0.4472 (this one is 200 m long)
    canyon wall    tregenza: 290 entries, 0 differ from the exact answer, 0 on an edge; sky view factor 0.2013
    courtyard      tregenza: 290 entries, 0 differ from the exact answer, 0 on an edge; sky view factor 0.4821
                   courtyard, closed form: 4 x F(point to rectangle) = 0.4642
    open ground    reinhart: 1154 entries, 0 differ from the exact answer, 0 on an edge; sky view factor 1.0002
    canyon floor   reinhart: 1154 entries, 0 differ from the exact answer, 0 on an edge; sky view factor 0.4557
                   infinite canyon, analytic: cos(atan(2H/W)) = 0.4472 (this one is 200 m long)
    canyon wall    reinhart: 1154 entries, 0 differ from the exact answer, 0 on an edge; sky view factor 0.2115
    courtyard      reinhart: 1154 entries, 0 differ from the exact answer, 0 on an edge; sky view factor 0.4642
                   courtyard, closed form: 4 x F(point to rectangle) = 0.4642

The same numbers as `reference/experiments/v172c-rays/README.md`'s table. The closed form in `rays_exact.js:64` is
B-3 with A = B, and it agrees with my own evaluation of B-3 (0.464158).

## What contradicts the note

1. **The ground patch is not dropped; the zenith is (fact 1c).** Run of the committed
   `runtime/radiance/gendaymtx.wasm` (through `reference/experiments/v172c-sky/wasi-run.js`, `-m 1 -s -O1 -A`) on a
   two-hour Wea (lat 40, June 21, 12.5 and 13.5 h): 156 lines; lines 0-8 are the header (line 5 `NAVERAGED=2`,
   line 8 blank); line 9 `51.3 51.3 51.3` is the ground (patch 0, `gendaymtx.c:928`). Ladybug's own
   `SkyMatrix._parse_mtx_data` (0.2.12, imported unchanged) on that output: 146 lines after `[9:-1]`, 145 values
   returned, and value 0 (meant to be the first horizon patch) = 0.002234 = the ground line's broadband x row-0 solid
   angle / 1000; the real first sky patch gives 0.001817. On the `-d` output the sun's energy lands in file patches
   120, 121, 133, 134, 135, 142, 143, which are dome patches 119, 120, 132, 133, 134, 141, 142 (south and south-west
   at 65-76 degrees); Ladybug gives them to dome patches 120, 121, 133, 134, 135, 142, 143, one patch further on
   (as far as due west). Diffuse on a horizontal plane: 108.62 W/m2 with Ladybug's slice, 109.36 with the aligned one
   (the Wea's mean DHI is 110). The note's checks would not see this: `ref_sky.py` and `pyodide_sky.js` compare
   Ladybug's parse with Ladybug's parse of the same gendaymtx revision, and `check_horiz.py`'s horizontal totals
   barely move (0.7% here) when every patch shifts by one. It moves direct sun by one patch in azimuth, which matters
   for facades. Whether Ladybug Tools' own Radiance build prints `NAVERAGED` was not established.
2. **`loadPackage` checks the SHA-256 only in a browser (fact 10b).** The note's part 11 ("so that
   `loadPackage('numpy')` finds and checks it") and `np_load.js`'s comment hold for the app in a browser worker
   (Fetch integrity), not for the Node run that measured 777 ms: Node's loader ignores the hash.
3. Minor, not a contradiction: the 14713 scale is applied to the first colour channel only in the numpy path
   (`lbr/intersection.py:197`); with the grey light (1, 1, 1) the channels are equal, so the result is the same.
