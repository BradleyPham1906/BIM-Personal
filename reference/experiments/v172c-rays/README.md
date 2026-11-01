# V172c experiments: the rays, and the whole pipeline in Chromium, 2026-11-01

Data, not suites. Node 22.23.4 (one thread) and Chromium 153.0.8010.12 headless (Playwright, the preinstalled
browser), Linux x86-64. `S` is the scratch folder of `../v172c-sky/README.md`; `dome.py` writes `S/exp/dome.json`
(Ladybug's Tregenza and Reinhart vectors and solid angles: both sum to 2 pi).

**What the matrix is** (P, ladybug-radiance 0.2.12 `intersection.py`): Radiance's `rcontrib -I -ab 0` with each
direction a 0.533 degree source of radiance 1, scaled by 14713 (about 1 over the source's solid angle): an entry is
the cosine between the face's normal and the direction when the direction is not blocked, else 0; the ground's
directions are the sky's reversed. The scripts build exactly that.

| Script | What it measures |
|---|---|
| `rays_exact.js REPO S/exp/dome.json` | the app's own `bimRayBox`, `bimRayTri`, `bimRayBlocked`, read from `src/js/engine/analysis/simulation.js` at run time, against geometry with exact answers, entry by entry |
| `rays_speed.js REPO dome.json` | the app's rays over city blocks (`scene.js`: n boxes 24 m square, 12 to 40 m high, 40 m apart; every face but the bottom a sensor) |
| `rays_bvh.js REPO dome.json [N]` | `bvh.js` (a bounding-volume hierarchy, the same Moller-Trumbore test and thresholds) against the app's rays, ray by ray up to N boxes, and its time |
| `chromium_run.js` with `web/` served over http | the whole pipeline in a classic worker: Pyodide, the five wheels, numpy, `gendaymtx.wasm`, Ladybug's `SkyMatrix`, the BVH rays, Ladybug's `RadiationStudy.compute()` (its numpy sum) |

## Results (single runs)

**Exactness** (`rays_exact.js`): every entry equals the exact answer, none on an edge.

| Case | Tregenza (290 entries) | Reinhart (1154) | Sky view factor T / R | Closed form |
|---|---|---|---|---|
| open ground, facing up | 0 differ | 0 differ | 0.9999 / 1.0002 | 1 |
| canyon floor, W = H = 10 m, 200 m long | 0 | 0 | 0.4674 / 0.4557 | 0.4472 for an endless canyon (cos atan 2H/W); this one is open at its ends |
| canyon wall at 3 m, facing across | 0 | 0 | 0.2013 / 0.2115 | |
| courtyard 20 m square, 12 m high, centre | 0 | 0 | 0.4821 / 0.4642 | 0.4642 (point to a parallel square, four corners) |

So the rays are exact; what differs from the closed form is the sky's resolution: Tregenza 3.9% high in the
courtyard, Reinhart within 0.0001.

**Speed, the app's rays** (`rays_speed.js`, Tregenza): they test every solid's box for every ray, so the rate falls
as the model grows.

| Boxes | Faces | Rays cast | ms | Rays/s |
|---|---|---|---|---|
| 20 | 100 | 13,940 | 167 | 83,473 |
| 100 | 500 | 69,700 | 3,257 | 21,400 |
| 400 | 2,000 | 278,800 | 48,366 | 5,764 |

**Speed, the BVH** (`rays_bvh.js`, Node): the same answer as the app's rays for all 362,440 rays compared.

| Boxes | Faces | Triangles | Build ms | Rays | ms | Rays/s | Compared |
|---|---|---|---|---|---|---|---|
| 20 | 100 | 240 | 5 | 13,940 | 23 | 606,087 | 0 differ |
| 100 | 500 | 1,200 | 11 | 69,700 | 52 | 1,340,385 | 0 differ |
| 400 | 2,000 | 4,800 | 21 | 278,800 | 210 | 1,327,619 | 0 differ |
| 1,000 | 5,000 | 12,000 | 36 | 697,000 | 588 | 1,185,374 | not compared (the app's rays would take minutes) |
| 4,000 | 20,000 | 48,000 | 148 | 2,788,000 | 2,526 | 1,103,721 | not compared |

**Chromium's worker** (`chromium_run.js`), run again with the release build of `gendaymtx.wasm` (rad6R0P1a; see
`../v172c-sky/README.md` for why): Pyodide 2,604 ms to start; numpy 591 ms; `gendaymtx.wasm` compiled in 6 ms;
Ladybug's sky 1,374 ms, **its largest difference from the native reference (the same release) 0**.

| Faces | BVH ms | Rays ms | Ladybug's sum ms | Total kWh (sum over faces of kWh/m2) | With the first, misaligned build |
|---|---|---|---|---|---|
| 500 | 12 | 59 | 478 (numpy's first call) | 319,338.8 | 320,557.7 |
| 5,000 | 165 | 692 | 57 | 3,043,671.5 | 3,057,240.3 |
| 20,000 | 186 | 2,921 | 64 | 12,046,376.9 | 12,105,029.0 |

(The misaligned sky changed the totals by about 0.4%; on single facades by more, as the sun moved one patch.)

So a 20,000-face model takes about 3.5 s after a first start of about 5 s, on the Tregenza sky; the Reinhart sky
casts four times the rays.

Not run: Safari, Firefox, a phone; a real building model (boxes stand in); direct-sun hours (the same rays, the sun's
hourly vectors in place of the patches).
