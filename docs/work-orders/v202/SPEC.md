# V202 spec: site context C3, measured heights, ground and bridges

Research: `docs/research/research-site-context-accuracy.md` (experiments in
`docs/research/experiments/site-context-accuracy/`). **Status: the owner chose D1 to D5 as
recommended (2026-11-13; the note's part 11).** WO-00 is built; WO-01 to WO-05 are ready for Cline.
A later change of mind touches only the parts marked with its D-number. Implementation target: local
`main`. Written by Claude, 2026-11-13.

## 1. What it does for the user

**Site context** (V133/V157) still builds the surroundings in one press. Where measured public data
exists, it now uses that data instead of OpenStreetMap's guesses:

- **The ground** comes from the USGS 3DEP 1 m terrain model, sampled every 5 m (D1), anywhere in the
  US. Elsewhere, or when the service fails, it uses Terrarium as before. Kerbs, ramps, the park's
  steps and the slope down to the river now show; today they fall between 25 m samples of 30 m data.
- **Buildings** take the city's measured roof height where the city publishes one (Philadelphia
  first). City Hall's main block stands at 52 m, not 6 m. Each building's Properties says where
  its height came from: *measured (City of Philadelphia, read 2026-11-13)*, *OpenStreetMap height*,
  *storeys x 3 m* or *assumed 6 m*. It also shows the highest point (a tower's top) when the city
  gives one.
- **Bridges** on US highways take their deck width, length and the clearance under them from the
  National Bridge Inventory. The deck sits at the measured clearance above what it crosses, held
  level, not `layer x 6 m` above whatever ground lies under each point. Properties shows the NBI
  structure number, the year built, the spans and *clearance measured (NBI)*. A bridge with no NBI
  record keeps V157's rule and says *deck height estimated*.
- The toast after a fetch reports the numbers, for example: *73 measured heights (City of
  Philadelphia), 13 from OpenStreetMap; ground 3DEP 1 m at 5 m; 9 bridges from NBI, 54 estimated*.
- Credits: "USGS 3D Elevation Program", "City of Philadelphia (OpenDataPhilly)", "FHWA National
  Bridge Inventory (BTS NTAD)", added to the existing OSM and Terrarium credits.

Phone, tablet and desktop: no new panel. The Properties rows and the toast are the existing ones.

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/map/measured-context.js` | new | the pure functions below, and the fetches that use them | Claude (WO-00 scaffold, WO-07 to WO-09 fetches), Cline (WO-01 to WO-05) |
| `src/js/engine/standards/registry.js` | changed | the city record `ctx.heights` with Philadelphia's edition (D2) | Claude (WO-00) |
| `src/js/engine/map/site-context.js` | changed | the ground: 3DEP first, Terrarium as the fallback | Claude (WO-07) |
| `src/js/engine/map/surroundings-3d.js` | changed | the height precedence (D3); bridge decks from NBI | Claude (WO-08, WO-09) |
| `src/js/engine/testing/hooks-commands-site.js` | changed | exposes the pure functions to the tests | Claude (WO-00) |
| `docs/work-orders/v202/v202.test.mjs` | new | the tests for WO-01 to WO-05 | Claude (written) |

## 3. Data

- **An area** (`bimCtxArea()`'s shape, already in the app): `{w, s, e, n}` in degrees.
- **A DEM grid**: `{w, h, data, a}`. `w` and `h` are the columns and rows. `data` is a `Float32Array` of
  `w*h` metres, row 0 the northern row. `a` is the area it covers. A value below -1000 is nodata.
- **A city record** (registry, D2):
  `{id:'phl-li-footprints', name:'City of Philadelphia building footprints', url:'https://services.arcgis.com/fLeGjb7u4uXqeF9q/arcgis/rest/services/LI_BUILDING_FOOTPRINTS/FeatureServer/0', roof:'approx_hgt', top:'max_hgt', base:'base_elevation', unit:0.3048, credit:'City of Philadelphia (OpenDataPhilly)', read:'2026-11-13', bbox:[-75.29,39.86,-74.95,40.14]}`.
  `unit` turns the fields into metres. `bbox` (W, S, E, N) says where the record applies.
- **A city feature, in model terms**: `{ring:[[x,z],...], a:{approx_hgt:170, max_hgt:558.2, base_elevation:34.5, ...}}`.
- **An NBI structure, in model terms**: `{p:[x,z], a:{STRUCTURE_NUMBER_008, FACILITY_CARRIED_007, YEAR_BUILT_027, DECK_WIDTH_MT_052, STRUCTURE_LEN_MT_049, MAIN_UNIT_SPANS_045, VERT_CLR_UND_054B, VERT_CLR_UND_REF_054A}}`.
- **A building's height record** (`bimCityHeightPick`): `{h, top, base, from:'city', id}`, all in
  metres. `top` and `base` are null when the city does not give them.
- **A bridge's NBI record** (`bimNbiPick`): `{id, carried, year, width, length, spans, clear, clearRef, dist}`.
  A measured number the inventory does not hold is null.
- **Saved on each context object** (`o.context`, as V133 does): buildings add `heightFrom:'city'` and `heightTop`,
  and `heightSource` (the record's id and `read`). Bridges add `nbi` (the pick record), `deckFrom:'nbi'|'layer'`.
  Ground: `A3D_CTX` keeps `terrainFrom:'3dep'|'terrarium'` and the cell size.

## 4. Functions

### `bimTiffF32(bytes)` - `measured-context.js` - WO-01
- **Takes:** `bytes`, a `Uint8Array` holding a TIFF file.
- **Returns:** `{w, h, data}`, where `data` is a `Float32Array(w*h)` in rows from the top. Returns `null` for anything it cannot read exactly.
- **Rules:**
  - Byte order: `II` is little-endian and `MM` big-endian, and the magic number is 42. Only the first IFD is read.
  - Tag values may be SHORT (type 3) or LONG (type 4). A value that does not fit in 4 bytes is read at its offset.
  - Needs: ImageWidth (256), ImageLength (257), BitsPerSample (258) = 32, Compression (259) = 1 (or absent), SampleFormat (339) = 3, and SamplesPerPixel (277) = 1 (or absent). Anything else returns null.
  - Strips: StripOffsets (273), with RowsPerStrip (278, default `h`). Each strip holds `min(RowsPerStrip, rows left) * w` floats.
  - Tiles: TileWidth (322), TileLength (323) and TileOffsets (324), tiles row by row. A tile that runs past the image's right or bottom edge is padded, and the padding is skipped.
  - Null when `w` or `h` is 0, when `w*h` > 16,777,216, or when any float would be read past the end of `bytes`.
- **Example:** an 'II' TIFF, 2 x 1, one strip holding the floats 1.5 and -2, returns `{w:2,h:1,data:Float32Array[1.5,-2]}`.
- **Uses:** nothing (a `DataView` on `bytes.buffer`, with `bytes.byteOffset`).

### `bimDep3Url(a, cols, rows)` - `measured-context.js` - WO-02
- **Takes:** an area `{w,s,e,n}`, and the grid's `cols` and `rows`.
- **Returns:** the 3DEP `exportImage` address, or `null` when `a` is missing or `cols` or `rows` is not a whole number from 2 to 2000.
- **Rules:**
  - Web Mercator with R = 6378137: `x = R*lon*PI/180` and `y = R*ln(tan(PI/4 + lat*PI/360))`, each written with `toFixed(2)`.
  - The address is exactly `BIM_3DEP_URL + '/exportImage?bbox=' + x(w) + ',' + y(s) + ',' + x(e) + ',' + y(n) + '&bboxSR=3857&imageSR=3857&size=' + cols + ',' + rows + '&format=tiff&pixelType=F32&compression=None&interpolation=RSP_BilinearInterpolation&f=image'`.
  - `BIM_3DEP_URL` is `'https://elevation.nationalmap.gov/arcgis/rest/services/3DEPElevation/ImageServer'` (WO-00 declares it).
- **Example:** `bimDep3Url({w:1,s:1,e:2,n:2},2,2)` starts with `BIM_3DEP_URL+'/exportImage?bbox=111319.49,111325.14,222638.98,222684.21&'`.

### `bimDep3ElevAt(g, lon, lat)` - `measured-context.js` - WO-03
- **Takes:** a DEM grid `g`, and a longitude and latitude.
- **Returns:** metres, interpolated bilinearly between pixel centres in Web Mercator. Returns `NaN` off the grid or on nodata.
- **Rules:**
  - X0, X1, Y0 and Y1 are the mercator coordinates of `g.a.w`, `g.a.e`, `g.a.s` and `g.a.n`.
  - `fx = (X-X0)/(X1-X0)*g.w - 0.5` and `fy = (Y1-Y)/(Y1-Y0)*g.h - 0.5`.
  - A point with `X<X0`, `X>X1`, `Y<Y0` or `Y>Y1` returns NaN.
  - The four neighbours' indices are clamped to the grid, so the outer half-pixel takes the edge value.
  - If any of the four samples used is not finite or is below -1000, it returns NaN.
- **Example:** at the centre of pixel (0,0) it returns `g.data[0]`. At the centre of a 2 x 2 grid it returns the four values' mean.

### `bimCityHeightPick(ring, feats, rec)` - `measured-context.js` - WO-04
- **Takes:** an OSM footprint `ring` (model `[[x,z],...]`), the city's features `feats`, and the city record `rec`.
- **Returns:** a building's height record, or `null`.
- **Rules:**
  - The footprint's centre is the mean of its vertices.
  - The candidates are the features whose `ring` contains that centre (an even-odd crossing test written inside the function, as `bimPointInPoly` in `bim/rooms.js` does; no import). If several contain it, the one with the smallest area (shoelace) wins.
  - `h = a[rec.roof]*rec.unit`, rounded to 0.01. It is null (no pick) when it is not finite or not above 0.
  - `top` is worked out the same way from `a[rec.top]`, and is null when missing or not above `h`.
  - `base` comes from `a[rec.base]*rec.unit`, rounded to 0.01, and is null when not finite.
  - `from` is `'city'` and `id` is `rec.id`.
- **Example:** a 10 m square at the origin inside a city ring with `approx_hgt:170, max_hgt:558.2, base_elevation:34.5`, with `unit:0.3048`, returns `{h:51.82, top:170.14, base:10.52, from:'city', id:'phl-li-footprints'}`.
- **Uses:** nothing beyond `Math`: the file imports only what WO-00 gave it, and import lines are Claude's.

### `bimNbiPick(pts, bridges, maxD)` - `measured-context.js` - WO-05
- **Takes:** a bridge's centreline `pts` (model `[[x,z],...]`, two or more), the NBI structures `bridges`, and a distance `maxD` in metres (30 when it is not above 0).
- **Returns:** the NBI record of the nearest structure whose point lies within `maxD` of the polyline (distance to its segments), or `null`.
- **Rules:**
  - A measured number is kept only when it is finite and above 0. `clear` is also null when it is 99 or more: NBI codes "no restriction" as 99.99.
  - `id` is `String(a.STRUCTURE_NUMBER_008)` with the spaces trimmed, `carried` is `a.FACILITY_CARRIED_007` (string or null), and `year` is `a.YEAR_BUILT_027`.
  - `width` is `DECK_WIDTH_MT_052`, `length` is `STRUCTURE_LEN_MT_049`, `spans` is `MAIN_UNIT_SPANS_045`, `clear` is `VERT_CLR_UND_054B` and `clearRef` is `VERT_CLR_UND_REF_054A`.
  - `dist` is rounded to 0.01. Ties go to the first in `bridges`.
- **Example:** a line from (0,0) to (100,0) and a structure at (40,12) with clearance 6.43 returns that structure, with `dist:12` and `clear:6.43`.

### Claude's functions (WO-07 to WO-09), in `measured-context.js`
- `bimDep3Fetch(a, cell)`: chooses `cols = round(width_m/cell)` and the same for `rows` (2 to 2000), fetches `bimDep3Url`, reads `bimTiffF32`, and resolves a DEM grid. It resolves `{ok:false}` on any failure, or when more than half the cells are nodata (outside the US). There is a timeout of 15 s.
- `bimCityFetch(a, org)`: finds the registry's city records whose `bbox` holds the area's centre, and queries each one (`outFields` = its three fields, `outSR=4326`, `f=geojson`). It returns the city features in model terms. On failure it resolves `[]` and V133's OSM rule applies.
- `bimNbiFetch(a, org)`: NBI within the area plus 100 m, as NBI structures in model terms. On failure it resolves `[]`.
- The site-context fetch (`surroundings-3d.js`) starts these three beside Overpass and Terrarium (`Promise.all`). None of them can stop the others. Each failure is reported once in the toast.
- **Heights (D3):** city, then OSM `height`, then OSM levels, then the default. A `building:part` with its own tagged height keeps it (V139).
- **Decks:**
  - The deck's top is `ground(NBI point) + clear + bimCtxDeckT()`, held level along the bridge.
  - It is never lower than `ground + bimCtxDeckT()` at any vertex.
  - The deck's width is NBI's `width` when given.
  - Piers stop at the ground, as V157's do.

## 5. Order of the work

1. WO-00 (Claude) scaffolds the file, the registry record and the test hooks, so WO-01 to WO-05 have functions to fill.
2. WO-01 to WO-05 (Cline), in any order: they are independent and pure.
3. WO-06 (Claude) audits them. Then WO-07 (ground), WO-08 (heights), WO-09 (bridges).
4. WO-10 (Claude) runs the one browser check of the site-context fetch on the Dilworth Park site: heights, ground, decks, toast and Properties. Its script goes in `tests/e2e/`.

After step 3 the owner can press Site context on the Dilworth Park model and compare with the
screenshot of 2026-11-13.

## 6. Not in this phase

- LiDAR point clouds, roof shapes from LiDAR, and class-17 decks: V190 and V191.
- Cities other than Philadelphia: each is a registry record added after its own probe (D2).
- Tunnels' depths: no free source measured here gives them.
- Retaining walls, utilities, and bridge structure (girders, bearings): out of scope. The owner's bridge modelling goes through the OpenBridge research (`docs/research/research-openbridge.md`).
- Any key, token or paid source.

---

# Part B: the Site and Map interface, and the geometry fix (added 2026-11-21)

**The owner, 2026-11-21:** at 30th Street Station the surroundings were "all over the place", and "their
UI/UX is good and we should clean up our UI/UX and make it similar" (Google Earth's web app, from the
owner's screenshots). The owner's answers: add it to this phase; start with the Site and Map workspace,
not the whole app.

## B1. The geometry (V202b, done 2026-11-21, PR #116)

Three faults in `surroundings-3d.js`, fixed before the measured data arrives:
- A road or railway was built only at OpenStreetMap's points, so between them it cut through the ground
  or hung over it. Now every line has a point at least every 5 m (`bimCtxDense`).
- A bridge deck stood `layer x 6 m` over the ground at every point: it dipped into a river valley and
  ended in a 6 m wall. Now `bimCtxDeckProfile` runs the deck straight between the ground at its two
  ends, lifted as one just enough to clear by `layer x 6 m`, ramping down only at a real abutment (an
  end no other bridge way of the same layer shares, `bimCtxBridgeEnds`).
- Piers did not reach the deck. Now each stands from the ground to the deck, where the gap is over 2 m.

WO-09 keeps this profile and gives it NBI's measured clearance in place of `layer x 6 m`.

## B2. What changes for the user

Google Earth's web app is the pattern (the owner's screenshots, 2026-11-21); the app's own controls,
names and colours stay ours. No Google content, names or images are copied.

1. **The Site bar.** In the Site and Map workspace, one slim bar along the top of the drawing area, icon
   buttons in groups, each with its title as a tooltip, wrapping to a second row on a phone:
   *Find a place* (the address box and Find, today in Properties > Map) |
   *Data layers* (opens B2.2) | *Site analysis* (a menu: Contours, Slope, Aspect, Cut and fill, the
   existing `bimDgContoursRun`, `bimDgSlopeRun`, `bimDgAspectRun` and `bimCutFill`) | *Measure* |
   *Sun and time* (a date and time pop-over, today's Sun Date and Sun Time) | *Basemap* (Off and the
   styles). Each starts what already exists; none is a new analysis.
2. **The Data layers dialog,** in place of the checkbox grid in Properties > Site Context: a grid of cards,
   one per kind (`bimCtxCards`), each with its title, one sentence, its source, the number the last
   fetch brought, and a Select toggle. Footer: "N layers selected", Cancel, and **Add to project** (Get
   Context). Radius, Overpass and "On the terrain" go under *More options* in the same dialog. Remove
   Context, Check LODs and the CityJSON buttons stay in Properties.
3. **The place card.** Clicking a context object (a building, road, bridge, tree) opens a card on the right,
   over Properties: its title and kind, the facts of `bimPlaceFacts` (height and where it came from,
   levels, address, use, width, deck, built, operator, fetched), its credit, *Open in OpenStreetMap*,
   *Zoom to*, and a close button. Properties stays one click away (*All properties*).
4. **The map controls,** bottom right of the drawing area, a small column: compass (`bimCompass`; click
   to face north), 2D / 3D (plan from above or the last perspective), zoom in, zoom out. The view cube
   stays where it is.
5. **A quieter view.** Context objects draw without their edges by default (a *Context edges* switch in
   the Site bar's Basemap menu); the Views legend box folds to its title; site view labels ("VIEW:
   ...") show on hover and for the selection only.
6. **Phone and tablet:** the Site bar scrolls sideways when it is too wide; the dialog's cards are one
   column on a phone, two on a tablet; the place card is a bottom sheet on a phone.

## B3. Functions (WO-12 to WO-14), in `src/js/engine/map/site-ui.js`

### `bimCtxCards(kinds, labels, st, counts)` - WO-12
- **Returns:** an array, one card `{kind, title, say, source, on, count}` per kind of `kinds` that `labels`
  names, in `kinds`' order. `[]` when `kinds` is missing or empty.
- `title` is `labels[kind]`. `say` is one sentence of 11 to 90 characters (the table below).
  `source` is `'AWS Terrain Tiles (Terrarium)'` for terrain, `'OpenStreetMap'` otherwise.
  `on` is `true` only when `st.kinds[kind]` is truthy. `count` is `counts[kind]` when it is a number,
  else `null`.

| kind | say |
|---|---|
| buildings | Footprints raised to their height, with roofs where tagged |
| roads | Streets, footways and cycleways as surfaces on the ground |
| water | Rivers, lakes and the sea |
| green | Parks, woods and grass |
| trees | Single trees and rows of trees |
| rail | Tracks, platforms and stations |
| airports | Runways, taxiways and aprons |
| power | Pylons and power lines |
| landuse | What the land is used for, as a tint on the ground |
| terrain | The ground, from elevation tiles |

### `bimPlaceFacts(ctx, name)` - WO-13
- **Returns:** `{title, kind, rows, credit, osmUrl}`, or `null` when `ctx` is missing. `t` is `ctx.tags` (or `{}`).
- `title`: `t.name`, else `name`, else `'Unnamed'`.
- `kind`: `'Bridge'` when `ctx.bridge`, `'Tunnel'` when `ctx.tunnel`, else by `ctx.kind`: buildings Building,
  roads Road, water Water, green Green space, trees Tree, rail Railway, airports Airport, power Power,
  landuse Land use, terrain Terrain; anything else `'Context'`.
- `rows`, `[label, value]` pairs, in this order, each only when its value exists:
  - Height: `ctx.height` (a number) as `'<h> m'`, then `' (<from>)'` by `ctx.heightFrom`: city *measured*,
    height *OpenStreetMap height*, levels *storeys x 3 m*, assumed *assumed*; nothing for another value.
  - Levels: `t['building:levels']`.
  - Address: `t['addr:housenumber'] + ' ' + t['addr:street']`, trimmed, when the street exists.
  - Use: the first of `t.building`, `amenity`, `highway`, `railway`, `landuse`, `leisure`, `natural`,
    `waterway` that exists and is not `'yes'`, its underscores as spaces.
  - Width: `ctx.width` (a number) as `'<w> m'`.
  - Deck: when `ctx.bridge` and `ctx.deck` is a number, `'<d> m over the ground'`.
  - Built: `t.start_date`. Operator: `t.operator`. Fetched: `ctx.fetched`.
- `credit`: `ctx.credit`, else `null`. `osmUrl`: `'https://www.openstreetmap.org/' + ctx.osm + '/' + ctx.id`
  when both exist, else `null`.

### `bimCompass(yaw, trueNorth)` - WO-14
- **Takes:** the camera's `A3D.cam.yaw` (radians; 0 looks toward model -z, which is north when true north
  is 0; `camVecs` in `core/mesh-primitives.js`) and the project's true north in degrees.
- **Returns:** `{needle, heading, letter}`, or `null` when either is not finite.
  `needle = (yaw in degrees + trueNorth)` kept in 0 to under 360: the north needle's clockwise turn on
  screen. `heading = -needle`, kept in 0 to under 360: the way the camera faces, clockwise from north.
  `letter`: N, NE, E, SE, S, SW, W, NW, the nearest to `heading` (`round(heading / 45) mod 8`).

## B4. Order of the work

WO-11 (done), then WO-12 to WO-14 (Cline, any order, pure), then WO-15 to WO-19 (Claude, the DOM and
CSS that use them), then WO-20, the one browser check of the Site and Map workspace at desktop, tablet
and phone sizes. Part A's WO-01 to WO-10 are independent of part B and can be built in either order.

## B5. Not in part B

- The rest of the app's interface: after this workspace, if the owner likes it.
- Photos in the place card: none are free to show without a key (the owner's standing choice).
- Classify and Detect change (Google's imagery tools): there is no free imagery to run them on.

---

# Part C: heights on one datum, and the surface model (GEM-15) (added 2026-11-21)

Research: `docs/research/research-terrain-surface.md` (experiments in `docs/research/experiments/terrain-surface/`).
**The owner's decisions, 2026-11-21:**
- **D1:** read cloud-optimised GeoTIFFs with geotiff.js. Version 3.0.5, MIT, is vendored in `runtime/geotiff/3.0.5/`,
  pinned in `MANIFEST.json`. The research is in the note's part 4.8; this answer is the owner's approval of the library.
- **D2:** GEM-15's heights rank as the research recommends.
- **D3:** the project's datum follows the project's location: NAVD88 inside CONUS, EGM96 elsewhere.
- **D4:** this part belongs to V202 ("measured heights, ground"). The analyses on the ground follow later, as V241
  and V242.

These replace the separate V239 and V240 written earlier the same day.

## C1. What changes for the user

- **One datum.** Every height the app fetches says which datum it is on, and is moved onto the project's. Today 3DEP
  (NAVD88), the city's base heights (NAVD88), Terrarium (NAVD88 in the US, EGM96 elsewhere) and GEM-15 (EGM96) are
  mixed as if they were one. At 30th Street an EGM96 height reads 1.295 m higher than NAVD88 for the same point.
- **Project > Location** shows *Heights above: NAVD88 (GEOID18)*, set from the address's place (D3), and so does the
  toast when a source is moved: *GEM-15 moved from EGM96 to NAVD88 (-1.30 m here)*. The geoids are read from PROJ's
  public grids (`cdn.proj.org`, CORS open). Credit: "Geoid grids: NOAA NGS (GEOID18), NGA (EGM96, EGM2008), via PROJ".
- **The surface model.** Site context gains *Surface (GEM-15)*: Google's 15 m surface model (mean, p5, p50, p95,
  spread) and terrain model. Credit: "GEM-15: This dataset is produced by Google (CC BY 4.0)".
- **Levelled.** In the US, GEM-15's terrain is first levelled to 3DEP by the median offset over open cells: -3.38 m
  at 30th Street after the datum shift. The toast reports the offset and the number of cells. Elsewhere the toast
  says *GEM-15 not levelled*.
- **Heights (D2).** The order is: the city's measured height, OSM `height`, **GEM-15**, OSM levels, the default.
  GEM-15's height is the median p95 over the footprint, less the levelled ground. Properties says *34.0 m, from
  GEM-15 (15 m), 9 cells, spread 0.2 m*. A building whose OSM levels give over 15 storeys keeps its levels, because
  GEM-15 misses tall buildings (Google's warning, and two towers here).
- **Trees** with no tagged height take p95 less the ground, where the cell's spread is over 1 m.
- **Analyze** gains a *Surface and canopy* layer: the height above the ground, and the spread (*rough: trees, edges* /
  *smooth: roofs, paving*).

## C2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `runtime/geotiff/3.0.5/` | new (done) | geotiff.js's browser build unchanged, its licence, its bundled packages' licences | Claude |
| `src/js/engine/map/cog-datum.js` | new (scaffolded) | `bimGeoidAt`, `bimDatumShift`; then the adapter `bimCogRead` and `bimGeoidFetch` | Cline (WO-22, WO-23), Claude (WO-27, WO-28) |
| `src/js/engine/map/surface-model.js` | new (scaffolded) | `bimGemCell`, `bimSurfaceOffset`, `bimFootprintHeight`; then `bimGemFetch` | Cline (WO-24 to WO-26), Claude (WO-29) |
| `src/js/engine/standards/registry.js` | changed | `geo.datums`: id, name, EPSG, grid file, where it holds, credit | Claude (WO-27) |
| `src/js/engine/map/site-context.js`, `measured-context.js`, `surroundings-3d.js` | changed | datums on every source; the levelling; the height order | Claude (WO-28, WO-29) |
| `docs/work-orders/v202/v202-datum.test.mjs`, `v202-surface.test.mjs` | new | the tests of WO-22 to WO-26 | Claude (written, checked against a reference) |

## C3. Functions

### `bimGeoidAt(g, lon, lat)` - WO-22, `cog-datum.js`
- **Takes:** a geoid grid `{w, h, x0, y0, dx, dy, data}`.
  - `x0, y0` is the first node, in degrees. For a PixelIsPoint file this is the tie point itself, measured and
    confirmed in OGC GeoTIFF 1.1.
  - `dx > 0`, `dy < 0`: the rows run from the north.
- **Steps:**
  1. Bring `lon` into `[x0, x0 + 360)` by adding or subtracting 360.
  2. `fx = (lon - x0) / dx`, `fy = (lat - y0) / dy`, `i = floor(fx)`, `j = floor(fy)`.
  3. Interpolate bilinearly between nodes `(i, j)`, `(i+1, j)`, `(i, j+1)`, `(i+1, j+1)`. On the last column or row
     (`tx` or `ty` 0) the same node stands in for the next.
- **Returns NaN** when:
  - `g` is missing, or `lon` or `lat` is not finite;
  - `(i, j)` is off the grid, or a needed node is past it;
  - any of the four nodes is NaN.

### `bimDatumShift(h, from, to, N)` - WO-23, `cog-datum.js`
- `h + N[from] - N[to]`, with `ellipsoid` taken as 0.
- NaN when `h` is not finite, `N` is missing, or either datum's N is not a finite number.
- **Example:** at 30th Street `bimDatumShift(10, 'egm96', 'navd88', {egm96: -34.274, navd88: -32.979})` is 8.705.

### `bimGemCell(lon, lat)` - WO-24, `surface-model.js`
- `x = floor(lon)`, `y = floor(lat)`, `gx = floor(lon / 10) * 10`, `gy = floor(lat / 10) * 10`.
- `group` is `s(gy) + '_' + s(gx)`, where `s(v)` is `'m' + (-v)` for a negative `v`, else `'p' + v`.
- `cell` is `'w' + c(x) + 's' + c(y)`, where `c(v)` is `'m' + (-v)` for a negative `v`, else `'' + v`.
- `dsm` and `dtm` are `'https://storage.googleapis.com/climate-and-sustainability/gem-15/' + group + '/' + cell + '/dsm/zall/mosaic.tif'`
  (and `/dtm/`).
- `null` when either input is not finite, `lat < -61` or `lat >= 84`, or `lon` is outside `[-180, 180)`.
- **Checked** against GEM-15's catalog: `p30_m80/wm76s39`, `p50_m10/wm10s51`, `p50_p0/w0s50`, `m40_p170/w172sm35`,
  `m10_m80/wm71sm1`.

### `bimSurfaceOffset(pairs)` - WO-25, `surface-model.js`
- **Takes:** `[{ref, dtm, dsm, std}]`: the local ground, and GEM-15's terrain, surface and spread at the same points,
  all on the project's datum.
- Keeps only pairs with four finite numbers, `|dsm - dtm| <= 1` and `std <= 1`: open ground, with nothing standing
  on it.
- **Returns:** `{offset, n, mad}`.
  - `offset` is the median of `ref - dtm`. `mad` is the median of `|d - offset|`. Both are rounded to 0.01.
  - The median of an even count is the mean of the middle two.
  - `null` when fewer than five pairs are kept.

### `bimFootprintHeight(cells, ground)` - WO-26, `surface-model.js`
- Keeps the cells with a finite `p95`.
- `h` is their median `p95` less `ground`. `spread` is the median of `|p95 - median|`. Both are rounded to 0.1.
- **Returns:** `{h, n, spread, from:'gem15'}`; `null` when `ground` is not finite, fewer than three cells are kept,
  or `h < 2`.

### Claude's work
- **WO-27:** audit WO-22 to WO-26, add the registry's `geo.datums`, and move the tests into `tests/unit/`.
- **WO-28:** the datum code.
  - `bimGeotiffLoad()`: inserts `runtime/geotiff/3.0.5/geotiff.min.js` once, when first needed, as the rendered
    view loads three.js.
  - `bimCogRead(url, window, bands)`: geotiff.js's `fromUrl` and `readRasters`, with a 20 s timeout. It resolves
    `{ok:false}` on failure.
  - `bimGeoidFetch(id, area)`: the grid's nodes over the area plus one node all round, cached for the session.
  - The datum on each source (D3), and the Project row.
  - GEOID18 holds only in CONUS, from NAD83(2011) heights; elsewhere the project falls back to EGM96.
- **WO-29:** the surface model.
  - `bimGemFetch(area)`: each cell's DSM and DTM window, in its UTM zone, moved to the project's datum.
  - The levelling.
  - The height order in `surroundings-3d.js`, trees, Properties rows, the toast and the credit.
- **WO-30:** the *Surface and canopy* layer, and one browser check at 30th Street. The check covers:
  - the station's height;
  - the levelling offset;
  - a GEM-15 and a 3DEP height of the same open ground agreeing after the shift.

## C4. Not in this part

- A reader of our own: geotiff.js replaces it (D1). V202's WO-01 (`bimTiffF32`, 3DEP's uncompressed export) stays,
  so the ground can load without the library.
- Copernicus GLO-30 and Meta/WRI's canopy maps: their buckets send no CORS header (measured).
- NAD83 to WGS84, and tidal datums.
- Roof shapes from the surface model: 15 m is too coarse (V191 does them from LiDAR).
