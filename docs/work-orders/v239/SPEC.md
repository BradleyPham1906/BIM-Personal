# V239 spec: heights on one datum, and a reader for cloud-optimised GeoTIFFs

Research: `docs/research/research-terrain-surface.md` (experiments in
`docs/research/experiments/terrain-surface/`). **Status: written 2026-11-21. The owner's decisions D1 and D3
(the note's part 11) are still to be answered.** The tasks below follow the recommendations; a different answer
changes only the parts marked with its D-number. Implementation target: local `main`. Written by Claude.

## 1. What it does for the user

- Every height the app fetches says which datum it is on. Today 3DEP (NAVD88), the city's base heights (NAVD88),
  Terrarium (NAVD88 in the US, EGM96 elsewhere) and, from V240, GEM-15 (EGM96) are mixed as if they were one. At
  30th Street an EGM96 height reads 1.295 m higher than NAVD88 for the same point.
- **Project > Location** gains a row, *Heights above*: NAVD88 in the US, EGM96 elsewhere (D3), with the geoid used.
  A fetched height on another datum is moved onto it, and the toast says so: *GEM-15 moved from EGM96 to NAVD88
  (-1.30 m here)*.
- The geoid comes from PROJ's public grids (`cdn.proj.org`, CORS open, read by HTTP ranges): GEOID18 for NAVD88,
  EGM96, EGM2008. Credit: "Geoid grids: NOAA NGS (GEOID18), NGA (EGM96, EGM2008), via PROJ".
- No new panel. Phone, tablet and desktop: the row and the toast are the existing ones.

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/map/cog-datum.js` | new (scaffolded) | the five pure functions below, then the fetches | Cline (WO-01 to WO-05), Claude (WO-06 to WO-08) |
| `src/js/engine/standards/registry.js` | changed | `geo.datums`: each datum's id, name, EPSG, grid file, credit | Claude (WO-06) |
| `src/js/engine/map/site-context.js`, `measured-context.js` | changed | each ground source records its datum; heights moved on fetch | Claude (WO-07) |
| `docs/work-orders/v239/v239.test.mjs` | new | the tests of WO-01 to WO-05 | Claude (written, checked against a reference) |

## 3. Data

- **An IFD** (`bimTiffIfd`): `{big, le, w, h, tw, th, spp, bps, fmt, comp, pred, planar, offsets, counts, nodata, scale, tie, epsg}`.
  `scale` is `[sx, sy]` from ModelPixelScale (33550), `tie` is `[i, j, x, y]` from the first ModelTiepoint (33922),
  `epsg` from GeoKeyDirectory (34735) key 3072 (projected) or else 2048 (geographic), `nodata` the number in
  GDAL_NODATA (42113; `'nan'` gives NaN), each `null` when absent.
- **A tile** (`bimCogTiles`): `{t, col, row, off, len}`, `t = row * ceil(w / tw) + col`.
- **A geoid grid** (`bimGeoidAt`): `{w, h, x0, y0, dx, dy, data}`. `x0, y0` is the first node, in degrees (for a
  PixelIsPoint file, the tie point itself, measured 2026-11-21). `dx > 0`, `dy < 0` (rows from the north). `data` is
  a Float32Array of `w * h`.
- **Geoid heights at a point** (`bimDatumShift`'s `N`): `{navd88, egm96, egm2008}` in metres; the ellipsoid is 0.

## 4. Functions, in `cog-datum.js`

### `bimTiffIfd(bytes)` - WO-01
- **Takes:** a Uint8Array holding at least the file's first IFD and the arrays it points to.
- **Rules:**
  - `II` little-endian, `MM` big-endian. Magic 42 is classic: the first IFD offset is a 4-byte value at 4, entries
    are 12 bytes, the entry count is 2 bytes, values of 4 bytes or less are inline. Magic 43 is BigTIFF: the bytesize
    at 4 must be 8, the first IFD offset is 8 bytes at 8, entries are 20 bytes, the count is 8 bytes, values of 8
    bytes or less are inline.
  - Types read: 1 BYTE, 2 ASCII, 3 SHORT, 4 LONG, 12 DOUBLE, 16 LONG8. Other types are skipped. An 8-byte integer is
    read as `hi * 4294967296 + lo`.
  - Defaults: SamplesPerPixel 1, BitsPerSample 1, SampleFormat 1, Compression 1, Predictor 1, PlanarConfiguration 1.
  - **Returns null** for: not `II` or `MM`, another magic, a BigTIFF whose bytesize is not 8, an IFD or any value
    array past the end of `bytes`, or a missing ImageWidth, ImageLength, TileWidth, TileLength, TileOffsets or
    TileByteCounts (a striped TIFF is not read).
- **Example:** the test's 600 x 300 BigTIFF gives `offsets [1000, ..., 6000]`, `scale [15, 15]`, `epsg 32618`, `nodata NaN`.

### `bimCogTiles(ifd, x0, y0, x1, y1)` - WO-02
- The window is clipped to `[0, w) x [0, h)`. Every tile the window touches, row by row and then column by column,
  as `{t, col, row, off: offsets[t], len: counts[t]}`. `[]` for an empty window or a missing `ifd`.

### `bimTiffUnpredict(u8, tw, th, spp, pred)` - WO-03
- **Takes:** a tile's bytes after DEFLATE (the caller inflates them with `DecompressionStream('deflate')`).
- **Returns:** a Float32Array of `tw * th * spp` samples, row by row, pixel by pixel, sample by sample.
- `pred` 1: the bytes are little-endian float32 (the files read here are all `II`).
- `pred` 3 (TIFF Technical Note 3): for each row of `m = tw * spp` samples (`4m` bytes), first undo the byte
  differences: `row[b] = (row[b] + row[b - spp]) & 255` for `b` from `spp` up. Then sample `k`'s four bytes are
  `row[k]`, `row[m + k]`, `row[2m + k]`, `row[3m + k]`, most significant first (big-endian), whatever the file's byte order.
- `null` when `u8` holds fewer than `4 * tw * th * spp` bytes, or `pred` is neither 1 nor 3.
- **Checked:** the reference decodes GEOID18 at 30th Street to -32.9789 m (NGS: -32.979).

### `bimGeoidAt(g, lon, lat)` - WO-04
- Brings `lon` into `[x0, x0 + 360)` by adding or subtracting 360. `fx = (lon - x0) / dx`, `fy = (lat - y0) / dy`,
  `i = floor(fx)`, `j = floor(fy)`. Bilinear between nodes `(i, j)`, `(i+1, j)`, `(i, j+1)`, `(i+1, j+1)`. On the last
  column or row (`tx` or `ty` 0) the same node stands in for the next.
- NaN when `g` is missing, `lon` or `lat` is not finite, `(i, j)` is off the grid, a needed node is past the grid,
  or any of the four nodes is NaN.

### `bimDatumShift(h, from, to, N)` - WO-05
- `h + N[from] - N[to]`, with `N.ellipsoid` taken as 0 whatever `N` holds. NaN when `h` is not finite, `N` is missing,
  or either datum's N is not a finite number.
- **Example:** at 30th Street `bimDatumShift(10, 'egm96', 'navd88', {egm96: -34.274, navd88: -32.979})` is 8.705.

### Claude's work (WO-06 to WO-08)
- `bimCogRead(url, window)`: reads the IFD, the tiles, inflates each tile with `DecompressionStream('deflate')`,
  calls `bimTiffUnpredict`, and assembles the window. It has a 20 s timeout, and resolves `{ok:false}` on failure.
- `bimGeoidFetch(id, area)`: reads the tiles of the registry's grid that cover the area and the 1-node border
  around it. It caches the grid in `A3D_CTX` for the session.
- The datum on each source (D3): Terrarium is `navd88` inside the US and `egm96` outside; 3DEP and the city are
  `navd88`; GEM-15 (V240) is `egm96`.
- GEOID18 (NAVD88) holds only in CONUS, Puerto Rico and the Virgin Islands, from NAD83(2011) ellipsoid heights.
  Alaska, Hawaii and Guam stay on GEOID12B, and 3DEP uses local datums there. Outside CONUS the project datum falls
  back to EGM96, and the registry records these limits (the second reader, 2026-11-21).

## 5. Order of the work

1. WO-00 (Claude, done): the scaffold, the include line, `window.__a3dGroundData`.
2. WO-01 to WO-05 (Cline), in any order: independent and pure.
3. WO-06 (Claude): audit, the registry's `geo.datums`, and moving the tests into `tests/unit/`.
4. WO-07 (Claude): the reader and geoid fetches; datums on every source; the Project row.
5. WO-08 (Claude): one browser check at 30th Street. A GEM-15 height and a 3DEP height of the same open ground must
   agree within GEM-15's measured bias, after the shift.

## 6. Not in this phase

- NAD83 to WGS84 (about 1 m horizontally here): the model and its context share WGS84, so they agree. A surveyor's
  datum transformation belongs in the survey track.
- Tidal datums (MLLW and the like, NOAA VDatum): no free, keyless browser source was found.
- Compression other than DEFLATE (LZW, ZSTD, LERC): none of the files needed uses them. A file that does is
  refused, with its compression named in the toast.
