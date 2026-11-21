# Research: the ground and the surface, from the TerraLab / GEM-15 post (V202 part C, V241, V242)

Claude, 2026-11-21, for the owner, who asked: "check this post on LinkedIn where it might solve the problem of
model reconstruction and physical model. Check if our app is missing anything, then fill in the gap, create work
order packages for later phases." Levels as in `research-protocol.md`: P primary (read or measured here),
S dependable secondary with the gap said, U a pointer only. Experiments: `experiments/terrain-surface/`.

## 1. Abstract

The post (TerraLab R&D) puts three elevation sources side by side: Google's new GEM-15 (15 m, a surface model
with five statistics per cell and a bare-earth model), Copernicus GLO-30 (30 m) and IGN LiDAR HD (0.5 m, France).
It argues that the statistics inside a cell (the 5th, 50th and 95th percentiles and the spread) are worth as much
as resolution, that surface minus terrain gives building and tree heights where none are tagged, and that sources
on different vertical datums (EGM96, EGM2008, a national one) must be brought onto one before they are mixed.

Measured here at 30th Street Station:
- GEM-15's files are open to a browser: keyless, with `Access-Control-Allow-Origin: *`. A third-party viewer's
  note says otherwise, and that note is wrong today.
- GEM-15 can measure the station: its roof stands 34 m above GEM-15's terrain.
- GEM-15 reads 2.1 m below USGS 3DEP. The datums alone would make it read 1.3 m above. So GEM-15 has a local
  bias of about -3.4 m, inside the -4.8 m to +1.9 m Google reports.
- The app has no notion of a vertical datum at all.

The app has slope, aspect, contours, cut and fill, isovists, shadows and FEMA flood zones. It has none of these:
- datums;
- a surface model (DSM);
- heights from a surface model;
- curvature or ruggedness;
- a viewshed over the ground;
- runoff: where water runs and where it gathers.

Following the owner's decisions (part 11), the datums and the GEM-15 surface model became V202's part C, read
through geotiff.js. The shape of the ground (V241) and water on the ground (V242) follow later. Each has Cline tasks
that are pure functions, tested and checked against a reference here.

## 2. The question and the hypotheses

**Question:** which of the post's ideas would make the app's site model more correct, which data can a browser
reach for free without a key, and what does the app lack?

| # | Hypothesis | Outcome |
|---|---|---|
| H1 | GEM-15 can be read by the browser without a key, by HTTP ranges | **Held** (P, measured): CORS `*`, ranges served, STAC catalog public |
| H2 | GEM-15's surface minus terrain gives a usable building height at a mid-rise station | **Held for the station** (34.0 m, spread 0.5 m); **failed for towers**: two towers over 100 m read 0.3 and 11.8 m (U: the points were not surveyed), as Google itself warns of buildings above about 50 m |
| H3 | Mixing GEM-15 with 3DEP without a datum shift gives errors of a metre or more | **Held**: the datums alone differ by 1.295 m here; GEM-15's own bias adds -3.4 m |
| H4 | Copernicus GLO-30 and Meta/WRI's 1 m canopy heights can be read by the browser | **Failed**: both S3 buckets send no CORS header (P, measured). They are named, not proxied (the owner's standing choice) |
| H5 | The geoid grids can be read by the browser | **Held**: PROJ's CDN (`cdn.proj.org`) serves EGM96, EGM2008 and GEOID18 with CORS `*`; NGS's own geoid API does not |
| H6 | The app's own TIFF reader (V202 WO-01) can read these files | **Failed**: it reads uncompressed strips only; GEM-15 is BigTIFF + DEFLATE in 512 px tiles, GEOID18 uses the floating-point predictor (P, measured) |

## 3. Method

- **Search log (2026-11-21):**
  - The web: GEM-15; Copernicus GLO-30 on AWS; Meta/WRI canopy height; USGS 3DEP lidar EPT; NOAA GEOID18 and EGM2008 grids.
  - Read by a fetch agent: GEM-15's Earth Engine catalog page, Google's `google-research/gem_15` README, and the third-party viewer `bertt/gem15`.
  - Read here: GEM-15's STAC catalog (`.../gem-15/stac/catalog.json`) and its group and item files.
- **Experiments** (scripts beside the raw numbers in `experiments/terrain-surface/`):
  - `probe_sources.sh`: CORS and range requests to every source.
  - `gem15_vs_3dep.py`: GEM-15 against 3DEP on 81 points, and the surface statistics at named buildings.
  - `geoid_offsets.py`: EGM96, EGM2008 and GEOID18 at the site.
  - A reference reader written here in JavaScript (not committed: it is the answer to Cline's tasks) decoded a GEOID18 tile and a GEM-15 DTM and DSM tile. Its values agree with NGS's API to 0.1 mm and with rasterio to 0.01 m.
- **Second reader:** a separate research agent re-checks the formulas the code uses (part 4.6). Its verdicts are recorded in part 4.7.

## 4. Findings, by topic

### 4.1 GEM-15 (high confidence on access and format, medium on accuracy)
- **What it is.** Google, 2026, experimental. A DSM built at 0.5 m from sub-metre stereo imagery (63% from
  Pleiades Neo 2022 to 2024), and a DTM predicted at 1 m by a learned model. Both are aggregated to 15 m. It covers
  60 S to 84 N, without Russia, China, Mongolia, Greenland or Antarctica. Licence CC BY 4.0, credit "This dataset is
  produced by Google". Paper: Batchu et al. 2026, EarthArXiv doi:10.31223/X55N75. (S: Earth Engine catalog and
  Google's README, read by an agent; the paper itself not read.)
- **Files** (P, measured):
  - Address: `https://storage.googleapis.com/climate-and-sustainability/gem-15/<group>/<cell>/{dsm,dtm}/zall/mosaic.tif`.
  - Group: the 10-degree tile, `p30_m80`. Cell: `w<lon>s<lat>` from the cell's south-west corner, with `m` for negative, e.g. `wm76s39`, `w0s50`, `w172sm35`.
  - Each cell is 8192 x 8192 px at 15 m, in its UTM zone (EPSG 32618 here). BigTIFF, DEFLATE, no predictor, float32, nodata NaN, tiles 512 x 512, four overviews.
  - The DSM has five pixel-interleaved bands in this order: dsm (mean), p5, p50, p95, std.
  - Sizes: the DSM is 868 MB a cell and the DTM 168 MB. A site of 600 m needs two to four 512 px tiles from each: under 3 MB.
- **Datum.** EGM96 orthometric metres, EPSG:5773 (S: Earth Engine page).
- **Known limits** (S, Google's own):
  - Regional offsets of -4.8 m to +1.9 m against lidar.
  - A weaker DTM under closed canopy.
  - Tall buildings (roughly over 50 m) are often missed.
  - Water, snow and low-texture surfaces are masked.

### 4.2 Other sources (high confidence)
| Source | Resolution, datum | Browser, keyless | Use here |
|---|---|---|---|
| USGS 3DEP ImageServer | 1 m (US), NAVD88 | yes (CORS `*`) | the ground, V202 |
| Terrarium (AWS) | about 30 m in town, mixed by source | yes | the ground, today |
| Copernicus GLO-30 (AWS) | 30 m, EGM2008, a DSM (X-band radar) | **no CORS** | named only |
| Meta/WRI canopy height (AWS) | 1 m, height above ground | **no CORS** | named only |
| USGS 3DEP lidar EPT (AWS) | points, NAVD88 | yes (catalog CORS `*`) | V190's later slices; Philadelphia's set not found in the EPT catalog (open) |
| PROJ CDN geoid grids | EGM96 15', EGM2008 2.5', GEOID18 1' | yes (CORS `*`, ranges) | V202 part C |
| NGS geoid API | GEOID18 at a point | **no CORS** | checked once here |
| IGN LiDAR HD (France) | 0.5 m | not tested (outside the owner's sites) | open |

### 4.3 Vertical datums (high confidence; P measured, S for the definitions)
- Each source's heights are orthometric on its own geoid:
  - 3DEP and the City of Philadelphia's base elevations: NAVD88, realised in CONUS by GEOID18 from NAD83(2011) ellipsoid heights.
  - GEM-15: EGM96.
  - Copernicus: EGM2008.
  - Terrarium: NED (NAVD88) in the US, SRTM (EGM96) elsewhere (S: Terrarium's documentation).
- To move a height between two of them: `H_to = H_from + N_from - N_to`.
- At 30th Street the geoid heights are -34.274 (EGM96), -33.843 (EGM2008) and -32.979 (GEOID18). So an EGM96 height
  reads 1.295 m higher than NAVD88 for the same point, and an EGM2008 height 0.864 m higher.
- The WGS84 and NAD83 ellipsoids differ by about a metre horizontally and a few decimetres vertically. That is under
  the noise of 15 m data, but it matters to a surveyor: recorded as an edge (part 7), not corrected in V202 part C.

### 4.4 Heights from the surface model (medium confidence)
- Surface minus terrain (an nDSM) is the standard way to get a building or canopy height from elevation alone (S).
- GEM-15 gives no nDSM itself, but its 95th percentile of the 0.5 m surface in each 15 m cell is near the roof's top.
- The post's other statistics:
  - The 5th percentile shows ground seen through the canopy: "canopy openness".
  - The spread (std) separates a flat roof (0.5 m at the station) from trees (3.2 m in the park).
- **Levelling.** GEM-15's terrain must first be levelled to the local ground by a median offset over open cells.
  Here that means -3.4 m against 3DEP after the datum shift. Without that, every height from it is off by the bias.

### 4.5 The shape of the ground and water (high confidence on the methods; S until the second reader confirms)
- **Curvature:** profile curvature (along the slope: where flow speeds up or slows) and plan curvature (across it:
  where flow gathers or spreads), from the 3 x 3 quadratic of Zevenbergen and Thorne (1987). It is the method
  ArcGIS and GDAL use.
- **Ruggedness:** Riley et al. (1999) TRI, the root of the summed squared differences to the eight neighbours.
- **Viewshed:** sight lines from an eye over the ground grid (the R3 method, one sight line for each target cell,
  Franklin and Ray 1994: S, the paper not read). It differs from the app's isovist, which stops each ray at a building's outline in plan.
- **Water:**
  1. Fill the hollows by priority-flood with epsilon (Barnes, Lehman and Mulla 2014), so every cell drains.
  2. Give each cell its steepest neighbour, D8 (O'Callaghan and Mark 1984; diagonals over the square root of 2, as in
     Jenson and Domingue 1988, ArcGIS and TauDEM).
  3. Count the accumulation.
  4. Take a cell's catchment from the reversed graph.
- These are the steps of every GIS hydrology toolset: ArcGIS, GRASS r.watershed, WhiteboxTools, RichDEM (S).

### 4.6 What the post proposes that is left out (high confidence)
- **Radio propagation and off-road vehicle physics:** not the app's work.
- **Procedural detail below the DEM's resolution, scaled by the cell's spread:** the app draws measured ground, not
  invented ground (the owner's "no placeholders"). The spread is shown as data instead, in V202 part C.
- **AI agents and vehicles:** out of scope.

### 4.7 The second reader (a separate research agent, 2026-11-21)

It read the libtiff, RichDEM, TauDEM and spatialEco source as text, the Priority-Flood paper (arXiv 1511.04463),
OGC GeoTIFF 1.1 (19-008r4), GDAL's gdaldem page, Esri's articles and the datum pages.

| Claim | Verdict | What changed |
|---|---|---|
| Zevenbergen and Thorne's D, E, F, G, H and their curvatures | **Partly** | The formulas are right (RichDEM `terrain_attributes.hpp` lines 216 to 220, spatialEco). They are ZT's original signs: positive profile curvature is upwardly convex. ArcGIS and RichDEM flip both signs and multiply by 100 (Esri technical article 000005086). V241 keeps ZT's signs in the functions; the board states the meaning in words ("water speeds up / slows"), not by sign, and shows 1/100 m. ZT's axes have y to the north; the app's rows run south, so the window's `z2` is the row above (north), which keeps ZT's signs (checked in the test with `z = ... + 0.02 x z`). |
| Riley's TRI and GDAL | **Wrong on GDAL** | Since GDAL 3.3, Riley (the root of the summed squares) is gdaldem's default for land; Wilson (mean absolute difference) is the option, for bathymetry. The formula itself is confirmed. |
| Priority-flood with epsilon | **Partly** | The paper seeds edge cells only and drains no-data through a "pit" queue. Seeding the cells beside no-data is RichDEM's choice, and V242 makes it too (so missing ground drains, as the paper's result does). The paper prefers `nextafter` to a fixed epsilon. V242 uses a fixed `1e-4 m` in float64 (heights under 10 km keep about 1e-12 m of resolution), and the toast warns if a filled hollow rises more than 0.5 m from epsilon alone. |
| D8, diagonals over the square root of 2 | **Confirmed as practice** | Cited to Jenson and Domingue (1988), ArcGIS's Flow Direction and TauDEM `d8.cpp`. O'Callaghan and Mark (1984), who introduced D8, were not read (paywalled). |
| TIFF's floating-point predictor | **Confirmed** | libtiff `tif_predict.c` (`fpAcc`, `fpDiff`): byte planes most significant first, differences with a stride of SamplesPerPixel, once per row of the tile. |
| GeoTIFF PixelIsPoint | **Confirmed** | OGC 19-008r4, 7.2.1 and B.6: the tie point is the first node's centre. It matches the 2 cm found here. |
| The datums | **Confirmed, with two additions** | Copernicus GLO-30 is a DSM (buildings and trees in it). GEOID18 holds only with NAD83(2011) epoch 2010.0 ellipsoid heights; Alaska, Hawaii and Guam stay on GEOID12B; 3DEP outside CONUS uses local datums. V239's registry records these limits; outside CONUS the project datum falls back to EGM96. |

The ZT and Riley papers themselves were not read by either reader (S). The implementations agree with each other.

### 4.8 geotiff.js, the library the owner chose (2026-11-21; P unless marked)

This is the research the 2026-11-13 library rule asks for. It was done after the owner chose the library (D1).
- **What:** geotiff.js 3.0.5, the newest release (npm, published 2026-03-11; 3.1.0 is a beta). MIT, EOX IT Services.
  It reads tiled and striped TIFF and BigTIFF, by HTTP ranges with `fromUrl` and `readRasters({window})`.
- **Its browser build** `dist-browser/geotiff.js` is one UMD file setting `globalThis.GeoTIFF`: 550,900 bytes, or
  199,327 gzipped. It bundles:
  - lerc (Apache-2.0; its package ships no licence file);
  - pako (MIT and Zlib);
  - zstddec (MIT and BSD-3-Clause);
  - quick-lru, parse-headers and @petamoriken/float16 (MIT);
  - xml-utils (CC0-1.0);
  - web-worker (Apache-2.0).

  All are compatible with the repository's Apache-2.0. Their licence texts are in
  `runtime/geotiff/3.0.5/THIRD-PARTY.txt`.
- **Measured here**, the browser build loaded as a classic script in Node 22 (scratch script, not committed):
  - GEM-15 at the station: DTM 13.21, DSM bands 46.24, 45.46, 46.26, 47.21 and 0.50. rasterio reads the same.
  - GEOID18 by bilinear interpolation: -32.9789 m, against NGS's -32.979.
  - The GEM-15 reads took 972 ms and the GEOID18 read 459 ms.
  - The raster-type key reads 2 (PixelIsPoint), so the tie point is the first node.
- **Vendored:** `runtime/geotiff/3.0.5/geotiff.min.js` is the browser build unchanged, pinned by size and SHA-256 in
  `runtime/MANIFEST.json`. The source tarball is `sha512-OWcL9S9+...`. It is loaded only when a fetch needs a GeoTIFF;
  the app opens, edits and saves without it.
- **Against our own reader:** geotiff.js covers every compression (LZW, ZSTD, LERC, JPEG), not only GEM-15's DEFLATE.
  It is maintained, and needs no task. The price is 551 KB loaded on demand, against about 150 lines.
- **V202's WO-01** (`bimTiffF32`, 3DEP's uncompressed export) stays, so the ground loads without the library.

## 5. The alternatives compared

The table is as it stood before the owner's answers. The owner chose option B for reading COGs (geotiff.js, D1),
and option A for the rest (part 11).

| Need | Option A (recommended) | Option B | Option C |
|---|---|---|---|
| Read COGs | Our own reader (as first planned): tiled, classic and BigTIFF, DEFLATE by the browser's `DecompressionStream('deflate')`, predictors 1 and 3; about 150 lines of ES5; no library | geotiff.js (MIT, mature, every compression); a library under the 2026-11-13 rule: vendored, pinned, its own research and approval | GDAL in WebAssembly: tens of MB, far beyond the need |
| Building heights where OSM and the city give none | GEM-15's p95 less the levelled terrain, after OSM height and the city, before levels and the default; marked *from GEM-15 (15 m)* | Leave the 6 m default | Meta's canopy maps for trees: no CORS |
| Datums | Every height source records its datum; the project picks one (NAVD88 in the US, EGM96 elsewhere by default); heights are moved on fetch | Ignore (today) | Ask the user each time |
| Hydrology | D8 on the filled grid (V242) | D-infinity (Tarboton 1997): smoother, more code; later if the owner asks | A full rainfall-runoff model (SWMM): outside the app |

## 6. The experiments

All are in `experiments/terrain-surface/`, with the raw numbers in `results-2026-11-21.json`.

1. **Access.** Every source was probed with an `Origin` header. Two buckets (Copernicus, Meta) send no CORS header.
   GEM-15, 3DEP, Terrarium and PROJ's grids do.
2. **GEM-15 against 3DEP**, on 81 points 120 m apart around the station (73 had both):
   - GEM-15 DTM minus 3DEP: median -2.08 m, mean -1.82 m, standard deviation 2.07 m, range -6.84 to +4.76 m.
   - Less the datum difference (+1.295 m): a local GEM-15 bias of -3.38 m.
3. **Surface statistics at named points:**

   | Point | p95 minus DTM | std |
   |---|---|---|
   | The station | 34.0 m | 0.5 m |
   | The park (trees in the cell) | 11.2 m | 3.2 m |
   | Cira Centre | 11.8 m | |
   | FMC Tower | 0.3 m | |

   The two towers' points were taken from memory, not surveyed, so their misses are U. They agree with Google's
   warning about tall buildings, and V202's WO-30 browser check measures them properly.
4. **The reference reader:**
   - GEOID18 at the site: -32.9789 m, against NGS's -32.979.
   - GEM-15 DTM 13.21 m; DSM bands 46.24, 45.46, 46.26, 47.21 and 0.50. rasterio reads the same.
   - PixelIsPoint grids: the tie point is the first node. A half-pixel shift gave 2 cm of error before it was fixed.

## 7. Edges

- **A site across two GEM-15 cells, or two UTM zones:** the fetch reads each cell's tiles in its own zone. V202's WO-29 handles it.
- **NaN in GEM-15** (water, masked): the cell is skipped. A footprint with under three cells gets no height.
- **Longitudes in the geoid grids:** they run 230 to 300 (GEOID18) or -180 to 180 (EGM96). WO-04 takes longitudes round by 360.
- **Flat ground in curvature:** where the gradient is under 1e-6, the curvature is 0, not a division by zero.
- **Flats in D8:** -1, no direction, until filled with epsilon. Epsilon must stay above the float's resolution at the
  site's heights (1e-4 m at 100 m in float64 is safe).
- **Missing ground in the hydrology:** cells next to missing ground are outlets, as at the grid's edge (Barnes et al.).
- **NAD83 against WGS84:** about 1 m horizontally in Philadelphia. It is not corrected. The app's model and its
  context are both placed by WGS84 coordinates, so they agree with each other.

## 8. What the app already has

- **The ground grid** `{nx, nz, cell, H, ok, x0, z0}`: `bimLandGround`, `src/js/engine/site-analysis/land-water.js:127`.
- **Slope and aspect by Horn:** `bimLandHorn`, `land-water.js:172`.
- **Contours, slope and aspect runs:** `bimDgContoursRun`, `bimDgSlopeRun`, `bimDgAspectRun`, `land-water.js:434-495`.
- **Cut and fill:** `bimCutFill`, `src/js/engine/terrain/terrain-tin.js:124`.
- **Isovists** (plan sight lines stopped by buildings): `bimDgViewsRun`, `src/js/engine/site-analysis/model-analyses.js:318`.
- **FEMA flood zones:** `land-water.js:37`, `:612`.
- **The context's heights** (OSM height, levels, assumed): `bimOsmHeight`, `src/js/engine/map/site-context.js:151`.
  V202 adds the city's measured heights and 3DEP ground.
- **A TIFF reader** for uncompressed strips (V202 WO-01): `bimTiffF32`, `src/js/engine/map/measured-context.js`.
- **Missing:** datums, a COG reader, a DSM, curvature, ruggedness, a ground viewshed, and hydrology. A grep for `geoid`, `EGM`,
  `NAVD`, `DSM`, `curvature` (outside freeform surfaces), `TRI`, `flow accumulation`, `watershed` and `viewshed`
  in `src/` finds nothing.

## 9. Risks and threats to validity

- GEM-15 is experimental ("under review"). Its files or their addresses may change. The STAC catalog is the way to
  find them, and V202 part C reads names from the cell rule with the catalog as a check.
- One site was measured. The bias at 30th Street says nothing about another city's, so V202 part C levels against 3DEP
  where 3DEP exists, and reports *not levelled* elsewhere.
- The tower points were from memory (U). The station point is on the building, but the building's true height was not
  read from a primary source.

## 10. What is still open (U)

- GEM-15's paper (accuracy by land cover) is not read.
- Philadelphia's 3DEP lidar in EPT form: not in the catalog under the names tried.
- IGN LiDAR HD: untested (France).
- geotiff.js's size and licence, if the owner prefers option B.

## 11. The owner's decisions (asked and answered 2026-11-21)

- **D1. The COG reader:** geotiff.js (the owner's choice, against the recommendation of our own; it is also the
  owner's approval of the library). Researched in part 4.8, vendored in `runtime/geotiff/3.0.5/`.
- **D2. GEM-15 heights:** "you did the research": as recommended. The order is the city, OSM height, GEM-15, OSM
  levels, the default. Never for a building whose levels give over 15 storeys.
- **D3. The project's datum:** by the location of the address the user enters: NAVD88 (GEOID18) inside CONUS, EGM96
  elsewhere.
- **D4. Order:** "later, or in V202 if it fits": the datums and the surface model fit V202 ("measured heights,
  ground") and are its part C (WO-21 to WO-30). Curvature, ruggedness and the viewshed (V241), and water on the
  ground (V242), follow later.

## 12. References

- Batchu, Neumann, Li, Allen, Zhang, Van Arsdale (2026). GEM-15. EarthArXiv, doi:10.31223/X55N75 (U, not read).
- Google Earth Engine catalog, `projects/climate-and-sustainability/assets/gem-15/v1` (S, read by an agent, 2026-11-21).
- `google-research/google-research`, `gem_15/README.md` (S, read by an agent, 2026-11-21).
- GEM-15 STAC catalog, `storage.googleapis.com/climate-and-sustainability/gem-15/stac/` (P, read here, 2026-11-21).
- PROJ data CDN, `cdn.proj.org` (P, read here): `us_nga_egm96_15.tif`, `us_nga_egm08_25.tif`, `us_noaa_g2018u0.tif`.
- NOAA NGS, GEOID18 downloads and geoid API (P, read here, 2026-11-21).
- AWS Registry of Open Data: Copernicus DEM, `dataforgood-fb-forests`, `usgs-lidar` (S, read by search, 2026-11-21).
- Zevenbergen and Thorne (1987); Riley, DeGloria and Elliot (1999); Franklin and Ray (1994); O'Callaghan and Mark
  (1984); Barnes, Lehman and Mulla (2014); TIFF Technical Note 3; OGC GeoTIFF 1.1. Their formulas are checked by the
  second reader (part 4.7).
- TerraLab R&D, LinkedIn post, "0 m, 15 m, 0.5 m: beyond elevation data" (U: the owner's paste, 2026-11-21).
