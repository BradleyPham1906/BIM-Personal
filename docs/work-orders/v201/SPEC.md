# V201 spec: site context C3, measured heights, ground and bridges

Research: `docs/research/research-site-context-accuracy.md` (experiments in
`docs/research/experiments/site-context-accuracy/`). **Status: draft, waiting for the owner's
decisions D1 to D5 (the note's part 11).** The defaults below are the recommended answers; a
different answer changes only the parts marked with its D-number. Implementation target: local
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
| `docs/work-orders/v201/v201.test.mjs` | new | the tests for WO-01 to WO-05 | Claude (written) |

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
  - The candidates are the features whose `ring` contains that centre (`bimPointInPoly`). If several contain it, the one with the smallest area (shoelace) wins.
  - `h = a[rec.roof]*rec.unit`, rounded to 0.01. It is null (no pick) when it is not finite or not above 0.
  - `top` is worked out the same way from `a[rec.top]`, and is null when missing or not above `h`.
  - `base` comes from `a[rec.base]*rec.unit`, rounded to 0.01, and is null when not finite.
  - `from` is `'city'` and `id` is `rec.id`.
- **Example:** a 10 m square at the origin inside a city ring with `approx_hgt:170, max_hgt:558.2, base_elevation:34.5`, with `unit:0.3048`, returns `{h:51.82, top:170.14, base:10.52, from:'city', id:'phl-li-footprints'}`.
- **Uses:** `bimPointInPoly` (`bim/rooms.js`).

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

- LiDAR point clouds, roof shapes from LiDAR, and class-17 decks: V188 and V189.
- Cities other than Philadelphia: each is a registry record added after its own probe (D2).
- Tunnels' depths: no free source measured here gives them.
- Retaining walls, utilities, and bridge structure (girders, bearings): out of scope. The owner's bridge modelling goes through the OpenBridge research (`docs/research/research-openbridge.md`).
- Any key, token or paid source.
