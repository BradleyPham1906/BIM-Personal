# Research: site context at true scale (V202): measured heights, ground and bridges

Claude, 2026-11-13. Builds on V133 (`research-site-context.md`), V157 (bridges and surfaces) and the
owner's Notion research of 2026-11-13 (V188 point clouds and V189 roofs from LiDAR, which PIPELINE numbers V190 and V191). Experiments:
`docs/research/experiments/site-context-accuracy/` (four probes and their `results*.json`).

## 1. Abstract

The owner asked how professionals build a site context with true sizes and elevations, since the
app's context from OpenStreetMap looks generic and wrong, and bridges and other infrastructure are
missing or misplaced. On the owner's own site (Dilworth Park and City Hall, Philadelphia), the
measurements show why. Only 31% of OSM's buildings carry a measured height; 24% have no height at
all and get the app's 6 m default. None of the 63 bridges carries an elevation, so the app can only
guess `layer x 6 m`. The ground comes from 30 m-class tiles that are up to 4.4 m off the 1 m
national model. Professionals do not use OSM for this. They use a survey for the site itself, and
for the surroundings they use authoritative, measured public data: the city's building footprints
with LiDAR heights, the national 1 m terrain model, and the bridge inventory. All three exist for
this site, are free and keyless, and answer a browser (CORS `*`), as measured here.
**Recommendation:** V202, "Site context C3: measured", which adds three sources behind narrow adapters
and keeps OSM as the fallback:
(a) the USGS 3DEP 1 m DEM for the ground, wherever it covers;
(b) a city's measured building heights, as a registry record per city, with Philadelphia first;
(c) the National Bridge Inventory for each bridge's deck width, length and clearance.
Each object records where its numbers came from, and an estimated number says it is estimated.
LiDAR point clouds (V190/V191) remain the general, worldwide-in-principle answer for heights and
bridge decks; they are a bigger phase and stay after V202.

## 2. The question and the hypotheses

Question: for a real site, which free, keyless sources give true building heights, ground
elevations and bridge geometry, and can the app's page read them directly?

| # | Hypothesis | Outcome |
|---|---|---|
| H1 | Most OSM buildings near a dense downtown site lack a measured height | **Supported:** 27 of 86 (31%) have `height`; 38 have only `building:levels`; 21 (24%) have neither |
| H2 | OSM bridges carry no vertical information beyond `layer` | **Supported:** 63 bridge ways, 61 with `layer`, 0 with `ele`, `height`, `min_height` or `maxheight` |
| H3 | Terrarium (today's ground) differs from 3DEP 1 m by more than 1 m on this site | **Supported:** RMSE 1.23 m over 25 points, worst 4.37 m |
| H4 | 3DEP 1 m DEM can return a dense grid quickly enough for one click, CORS-open | **Supported:** 5 m grid of the 470 x 450 m box in 1.37 s, 66 KB; 1 m in 6.3 s, 1.05 MB; CORS `*` |
| H5 | Philadelphia publishes footprints with measured heights, CORS-open | **Supported:** 73 of 73 footprints in the box carry `base_elevation`, `approx_hgt` and `max_hgt`; CORS `*` |
| H6 | Those heights are in feet above ground | **Supported:** City Hall 558 ft max (548 ft published to the statue's top); One Liberty Place 825 ft max (945 ft is the spire's tip, too thin for LiDAR); `base_elevation` 34.5 ft = 10.5 m against 3DEP's 10.9 m at the box centre |
| H7 | The National Bridge Inventory gives deck width, length, spans and under-clearance, CORS-open | **Supported:** 32 structures within ~1 km; fields `DECK_WIDTH_MT_052`, `STRUCTURE_LEN_MT_049`, `MAX_SPAN_LEN_MT_048`, `MAIN_UNIT_SPANS_045`, `VERT_CLR_UND_054B`; CORS `*` |
| H8 | 3DEP LiDAR (EPT) covers the site and a browser can read it | **Supported for access:** `USGS_LPC_DE_DelawareValley_HD_2015_LAS_2017` (41.4 billion points, EPSG:3857, LAZ, with `Classification`) covers City Hall; `ept.json` and the hierarchy answer CORS `*`. Decoding needs laz-perf (V190) |

## 3. Method

- Search log: the app's own V133/V157 code and notes; the owner's Notion pages (V157 task, V188
  and V189 syntheses and tasks, 3D Tiles research), read 2026-11-13; the services' own metadata
  (`?f=json`, `ept.json`); the S3 bucket listing of `usgs-lidar-public` (2,296 datasets).
- Experiments, all from this machine with a foreign `Origin` header, the way the app's page asks:
  - `probe.mjs`: the Philadelphia footprints, NBI, the 3DEP DEM `getSamples`, Terrarium decoded and
    compared at the same 25 points, and EPT datasets by name;
  - `probe2.mjs`: the height units against known buildings, and the full EPT listing with its
    coverage test;
  - `probe3.mjs`: OSM tag coverage through the app's Overpass mirrors, and CORS on EPT;
  - `probe4.mjs`: a 3DEP DEM raster, decoded as float32 TIFF at 1 m and 5 m.
- Independent check: H6 was checked against published heights (City Hall 548 ft, One Liberty Place
  945 ft), which are not from the dataset under test. H3 was checked against a second source:
  3DEP's own raster in `probe4.mjs` gives the same range (5 to 15 m) as its point samples.

## 4. Findings, by topic

### 4.1 How professionals build a site context (practice)

- **The site itself: a survey.** A boundary and topographic survey by a licensed surveyor gives the
  lines, spot levels, inverts, kerbs and trees. That is what is drawn on and permitted (P, practice;
  the app reads it through V108's survey points and V138's check). No open dataset replaces it.
- **The surroundings: measured public data.** Ground from the national or state LiDAR terrain model
  (in the US, USGS 3DEP; in PA, PAMAP or the city's flights). Building heights from the city's
  LiDAR-derived footprints or 3D model, or from the LiDAR itself (the height of roof returns above
  the ground). Bridges and roads from the DOT's records, or from plans when the work touches them.
  (S: practice as the owner's own V190/V191 notes and the services' metadata describe it.)
- **Commercial shortcuts** (Google's photorealistic 3D tiles, Cesium's buildings, Nearmap, Vexcel,
  Placemaker, CADMapper's paid tier) need keys or licences, and their terms limit extraction. The
  owner's rule (free, keyless) leaves them out.
- **OSM-based context tools** (the free tier of CADMapper, and the app's V133) inherit OSM's gaps:
  heights where mappers typed them, default heights elsewhere, bridges by layer only (H1, H2).

### 4.2 The ground (P, measured; confidence high)

- Today: Terrarium at zoom 15. On this site its sources header names `ned19_n40x00_w075x25_pa_northeast_2010`
  (1/9 arc-second NED), but the tiles are resampled and quantised: RMSE 1.23 m, worst 4.37 m against
  3DEP 1 m at the same points (H3). The app samples them on a 25 x 25 grid across the whole area, so
  a 300 m half-size gives 25 m between points: kerbs, ramps and park steps vanish.
- 3DEP DEM `exportImage` with `format=tiff&pixelType=F32&compression=None` returns a plain float32
  TIFF the app can read in about 40 lines of ES5 (`probe4.mjs` has the reader). The cell is 1 m
  (`pixelSizeX` 0.99999999). Times: 1.37 s at 5 m, 6.3 s at 1 m.
- Outside the US, 3DEP answers nodata; Terrarium stays the fallback, worldwide.

### 4.3 Building heights (P, measured; confidence high for Philadelphia)

- OSM on this site: 31% measured, 44% storeys x 3 m, 24% the 6 m default (H1). Where OSM has a
  height, it is good: Centre Square I 149 m (490 ft published).
- Philadelphia's `LI_BUILDING_FOOTPRINTS` (ArcGIS Online, OpenDataPhilly): every footprint has
  `approx_hgt` (the main roof, in feet), `max_hgt` (the highest point, in feet) and `base_elevation`
  (the ground, in feet). City Hall: 170 ft main roof, 558 ft tower; that is the building in the
  owner's screenshot, drawn today as one block.
- The app already reads this host: `data-layers.js:19-20` lists two Philadelphia layers from the
  same ArcGIS organisation.
- Other cities publish the same kind of layer (New York, Washington, Boston, among others). Their
  field names and units are not verified here (U), so each becomes a registry record only after a
  probe like `probe2.mjs`.

### 4.4 Bridges and infrastructure (P, measured; confidence medium)

- OSM: bridges are lines with `layer` (61 of 63), and no vertical numbers (H2). Tunnels: 81 ways
  under the box (SEPTA's concourses and the subway), likewise with no depths.
- NBI (FHWA, through BTS's NTAD service): one record per highway structure, a point at the
  structure, with deck width, length, longest span, the number of spans, the year built, the
  structure type, and the clearance under it (`VERT_CLR_UND_054B`, metres, with its reference:
  `H` highway, `R` railroad, `N` other). 99.99 means "no restriction" and is not a measurement. Example: 17th Street over the old Conrail
  line, 25 m long, 15.1 m deck, 6.43 m clear above the rail.
- The deck's top is therefore the ground under it, plus the clearance, plus the deck's depth.
  NBI does not give the depth; the app's V157 setting `bimCtxDeckT()` stays the estimate.
- NBI covers highway structures only: footbridges, rail-only bridges and private structures are
  absent; they keep V157's layer rule and say they are estimated.
- LiDAR class 17 (bridge deck, ASPRS LAS 1.4) would give every deck's surface directly; whether this
  2015 dataset uses class 17 is not checked (U, V190).

## 5. The alternatives compared

| Source | Heights | Ground | Bridges | Coverage | Cost to the app | Verdict |
|---|---|---|---|---|---|---|
| OSM tags (today) | 31% measured here | none | layer only | world | none | Keep as the fallback |
| Terrarium tiles (today) | none | 30 m-class, 1.2 m RMSE here | none | world | none | Keep as the fallback |
| **3DEP 1 m DEM** | none | **1 m bare earth** | none | US | small: a TIFF reader | **V202** |
| **City footprints (registry)** | **measured, all** | base only | none | per city | small: ArcGIS query (already read) | **V202**, Philadelphia first |
| **NBI** | none | none | **width, length, clearance** | US highway bridges | small: ArcGIS query | **V202** |
| 3DEP LiDAR (EPT/COPC) | measured, all | 0.5-1 m | class 17 decks | US, where flown | large: laz-perf WASM, point budget | V190/V191, after V202 |
| Overture / Microsoft footprints | ML heights, partial | none | none | world | large: GeoParquet | Not now |
| Google 3D tiles, Cesium | photoreal | yes | yes | world | key, paid terms | Excluded (keyless rule) |

## 6. The experiments (raw numbers in `results*.json`)

| Probe | Measure | Result |
|---|---|---|
| probe3 | OSM buildings in the box; with `height`; levels only; neither | 86; 27; 38; 21 |
| probe3 | OSM bridge ways; with layer; with any vertical tag | 63; 61; 0 |
| probe | Philadelphia footprints in the box; with all three height fields | 73; 73 |
| probe2 | City Hall `approx_hgt` / `max_hgt` / `base_elevation` (ft) | 170 / 558.2 / 34.5 |
| probe2 | One Liberty Place `approx_hgt` / `max_hgt` (ft) | 677 / 825.2 |
| probe | NBI structures within ~1 km; CORS | 32; `*` |
| probe | Terrarium - 3DEP at 25 points: RMSE, worst | 1.23 m, 4.37 m |
| probe4 | 3DEP raster 94 x 89 (5 m): time, bytes | 1,366 ms, 66,682 |
| probe4 | 3DEP raster 469 x 445 (1 m): time, bytes | 6,279 ms, 1,049,850 |
| probe2/3 | EPT covering City Hall; points; CORS on `ept.json` and hierarchy | DelawareValley_HD_2015; 41.4 billion; `*`, `*` |
| probe2/3 | Overpass reliability | overpass-api.de 502 then 200; kumi 504; private.coffee 429/504; mail.ru 504 |

## 7. Edges

- **Outside the US:** no 3DEP and no NBI; Terrarium and OSM stay. National LiDAR exists elsewhere
  (the Netherlands' AHN and 3DBAG, England's Environment Agency, Switzerland's swissALTI3D); each would be
  its own registry record after a probe (U).
- **A city without a measured layer:** OSM's rule stands, and the count of estimated heights is
  reported (V133 already toasts it).
- **City footprints and OSM footprints differ.** Philadelphia has 73 in the box and OSM 86 (parts
  and courtyards counted differently). The match is by the OSM footprint's centroid inside a city
  footprint; an unmatched OSM building keeps OSM's height and says so.
- **Towers and spires:** `approx_hgt` is the main roof and `max_hgt` the top. Extruding to `max_hgt` would
  make City Hall a 170 m block. The main roof drives the solid; the top is kept on the object, and
  OSM's `building:part` towers (V139) keep their own heights when they are tagged.
- **Datum:** 3DEP is NAVD88 metres; Philadelphia's `base_elevation` agrees within 0.4 m at City Hall.
  The app's datum stays V133's (`bimCtxDatum`): the survey base when set.
- **Bridges over water or deep cuts:** the ground under the deck is the water or the cut, and the
  clearance is measured from it, which is what the deck rule needs. A bridge whose NBI clearance is
  99.99 or 0 has no measured clearance; it keeps V157's estimate and says so.

## 8. What the app already has

- `src/js/engine/map/site-context.js:144-156` `bimOsmHeight`: height, else levels x `bimCtxLevelH()`,
  else `bimCtxDefaultH()`.
- `site-context.js:179-236` Terrarium fetch, decode and `bimCtxElevAt`; `BIM_CTX_GRID` 25.
- `src/js/engine/map/surroundings-3d.js:236-262` buildings placed, `c.heightFrom` kept on each.
- `surroundings-3d.js:344-358` `bimCtxSurface`: a bridge's deck is `layer x bimCtxDeck()` above the
  ground; `bimDeckMesh` (`:87`) builds the deck and piers.
- `src/js/engine/map/data-layers.js:19-41`: ArcGIS FeatureServer layers read, Philadelphia's among
  them.
- `src/js/engine/standards/registry.js`: standards as data with editions (V167), the place for the
  city records if the owner agrees (D2).

## 9. Risks and threats to validity

- One site. Downtown Philadelphia is well mapped in OSM; a suburb would show fewer OSM heights, so
  H1 likely understates the problem elsewhere.
- Service availability: every source here is a public server with no promised uptime. Overpass was
  at capacity during the probe. Each new source needs a timeout and a clean fallback.
- `approx_hgt`'s method and date are not stated in the layer's metadata read here (U). The values
  agree with published heights within a few percent.
- NBI's points sit at a structure's reference location, not along the deck: the matching distance
  must be generous, and a wrong match is possible where bridges are close together.

## 10. What is still open (U)

- Philadelphia's LiDAR vintage behind `approx_hgt`, and the city's own metadata page.
- Field names and units of other cities' layers.
- Whether the DelawareValley 2015 LiDAR uses class 17 for decks (V190).
- The 3DEP service's rate limits for repeated use.

## 11. The owner's decisions (asked 2026-11-13)

- **D1, the ground:** use 3DEP 1 m wherever it answers, at a grid of 5 m (1.4 s), and Terrarium
  elsewhere? Or offer 1 m (6 s) as a setting? *Recommended: 5 m by default, 1 m and 2 m as a setting.*
- **D2, city heights:** keep the city records in the standards registry (`registry.js`, with an
  edition: the date the layer was read) or in the new file? *Recommended: the registry, so a new city
  is data, not code.*
- **D3, precedence:** for a building: the city's measured height, then OSM `height`, then OSM levels,
  then the default? Or OSM `height` first when present? *Recommended: the city first; it is
  measured for every building, OSM only where someone typed it.*
- **D4, bridges:** NBI for highway bridges now, and the LiDAR deck (class 17) in V190? *Recommended:
  yes.*
- **D5, the phase number:** a new number, ahead of V190/V191.

**The owner's answer, 2026-11-13: "as recommended", D1 to D5.** D1: 3DEP at 5 m by default, 1 m and 2 m
as a setting, Terrarium elsewhere. D2: the registry (`ctx.heights`). D3: the city first, then OSM
`height`, levels, the default. D4: NBI now, LiDAR decks in V190. D5: asked as V201, which PIPELINE
already gives to MEP runs (and V200 to Gaussian splats). Claude's numbering mistake, corrected the
same day to **V202**, the first free number; the order the owner approved is unchanged.

## 12. References

| Source | URL | What was read | Date | Level |
|---|---|---|---|---|
| City of Philadelphia, LI building footprints | `services.arcgis.com/fLeGjb7u4uXqeF9q/arcgis/rest/services/LI_BUILDING_FOOTPRINTS/FeatureServer/0` | fields, 73 features, 4 named buildings | 2026-11-13 | P (measured) |
| FHWA NBI through BTS NTAD | `services.arcgis.com/xOi1kZaI0eWDREZv/arcgis/rest/services/NTAD_National_Bridge_Inventory/FeatureServer/0` | fields, 32 features | 2026-11-13 | P (measured) |
| USGS 3DEP elevation service | `elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer` | metadata, getSamples, exportImage | 2026-11-13 | P (measured) |
| AWS Terrain Tiles (Terrarium) | `s3.amazonaws.com/elevation-tiles-prod/terrarium/` | z15 tiles, sources header | 2026-11-13 | P (measured) |
| USGS 3DEP LiDAR, Entwine | `s3-us-west-2.amazonaws.com/usgs-lidar-public/` | listing, `ept.json`, root hierarchy | 2026-11-13 | P (measured) |
| OpenStreetMap through Overpass | `overpass-api.de/api/interpreter` and mirrors | tags in the box | 2026-11-13 | P (measured) |
| Published heights: City Hall 548 ft, One Liberty Place 945 ft | building records (CTBUH and the city) | the heights only, as the independent check | 2026-11-13 | S |
| The owner's Notion research: V188 point clouds, V189 roofs, V157 surroundings | Notion Documentation DB and Internal Task DB | the pages in full | 2026-11-13 | S |
| ASPRS LAS 1.4, class 17 bridge deck | `asprs.org` LAS specification R15 | the class table (as cited by V188) | 2026-11-13 | S |
