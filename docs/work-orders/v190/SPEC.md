# V190 spec: LOD-C point clouds, first slice (local LAS and PLY)

Research: `docs/research/research-notion-v188-point-clouds.md` and its experiment `docs/research/experiments/notion-lod/`
(Notion's task is "V188 LOD-C"; PIPELINE numbers it 190). The owner's decisions, 2026-11-14, as recommended: local
files first, each remote format (COPC, EPT, USGS 3DEP) only after a repeatable test against a real endpoint; LAZ
through laz-perf (Apache-2.0) only after its research under the library rule, so this slice reads uncompressed LAS
and PLY and names a LAZ file as not yet supported; a cloud without a known CRS opens as a labelled "unregistered
preview", placed by the owner, never silently georeferenced; a point budget of 2,000,000 by default, set in
Properties; ground to a terrain surface is a separate, previewed action that the owner confirms, never automatic.
Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. What it does for the user

Import a `.las` or `.ply` file (Import, or drag it in). The cloud appears on its own layer, coloured by RGB when it
has colour, else by height; Properties lets the owner colour it by class (with ASPRS names: Ground, Building, High
vegetation, ...) or height, and hide classes. A cloud larger than the budget is sampled evenly and says so. Points
keep their survey precision: the app keeps a whole-metre origin in double precision and draws offsets from it, so a
centimetre stays a centimetre 500 km from the datum. "Ground to surface" previews the lowest ground point per cell
and, when confirmed, hands them to the terrain (V108) through V138's check.

## 2. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/map/pointcloud.js` | new, after `terrain-3d.js` (header done) | eleven pure functions (part 4) | Cline, WO-01 to WO-11 |
| `docs/work-orders/v190/v190.test.mjs` | new | their tests, with LAS and PLY files built byte by byte | Claude (done) |
| `io/import-entry.js`, `render/`, `layers/`, `properties/`, `terrain/` | changed | import, drawing points, the colour modes, ground to surface | Claude, WO-12 to WO-14 |

## 3. Data

- **A LAS header** `{versionMajor, versionMinor, headerSize, offsetToPoints, pointFormat, recordLength, count, scale:
  [3], offset: [3], min: [3], max: [3]}`, read little-endian at the byte offsets of ASPRS LAS 1.2 (version 24 and
  25, header size 94 uint16, offset to points 96 uint32, point format 104 uint8 masked by `0x3f`, record length 105
  uint16, legacy count 107 uint32, scale 131/139/147, offset 155/163/171, max X 179, min X 187, max Y 195, min Y 203,
  max Z 211, min Z 219, all float64); LAS 1.4's 64-bit count at 247 (low uint32) and 251 (high uint32) when the
  legacy count is 0 and the minor version is 4 or more.
- **Supported point formats and their minimum record lengths**: 0: 20, 1: 28, 2: 26, 3: 34, 6: 30, 7: 36, 8: 38.
  Class: formats 0 to 5 the byte at 15 masked by `0x1f`; formats 6 and up the byte at 16. RGB (three uint16, kept as
  their high byte): format 2 at 20, 3 at 28, 7 and 8 at 30.
- **A PLY header** `{format: 'ascii'|'binary_little_endian', count, props: [{name, type}], headerBytes}`: the vertex
  element's properties in order; `headerBytes` the index just after `end_header` and its line end (`\n` or `\r\n`).
- **A cloud** `{n, xyz: Float32Array(n*3), cls: Uint8Array(n) or null, rgb: Uint8Array(n*3) or null}`, xyz in the
  file's own axes (LAS: x east, y north, z up) minus the origin.

## 4. Functions, `src/js/engine/map/pointcloud.js`

- **WO-01 `bimPcSniff(b)`** (a Uint8Array): `'las'` for `LASF` (bytes 76 65 83 70), `'laz'` when also byte 104 has
  bit 6 or 7 set (`& 0xC0`); `'ply'` for `ply` followed by `\n` or `\r`; else `''` (also for under 4 bytes).
- **WO-02 `bimPcLasHeader(dv)`**, with `BIM_PC_MINLEN` above it: part 3. Errors in order: under 227 bytes `{error:
  'too short'}`; a format not in the table `'point format N not supported'`; a record length under the minimum
  `'record too short'`; `offsetToPoints < headerSize` or `offsetToPoints + count * recordLength` beyond the data
  `'truncated'`.
- **WO-03 `bimPcStep(count, max)`**: `max` floored when a number 1 or more, else `count`; 1 when `count <= max`, else
  `Math.ceil(count / max)`.
- **WO-04 `bimPcLasPoints(dv, h, max, origin)`**, with `BIM_PC_RGB` above it: every `step`-th point (`bimPcStep`),
  `n = Math.ceil(count / step)`; each coordinate `int32 * scale + offset - origin` computed in double, then stored in
  the Float32Array; class and RGB by part 3; `origin` `[0, 0, 0]` when not given.
- **WO-05 `bimPcOrigin(h)`**: `[floor((minX + maxX) / 2), floor((minY + maxY) / 2), floor(minZ)]`.
- **WO-06 `bimPcPlyHeader(text)`**: errors `'not text'`, `'not a PLY header'` (not starting `ply` or no
  `end_header`), `'a list property on vertices'`, `'format F not supported'` (F the word, or `missing`), `'no vertex
  element'`; checked in that order after the lines are read.
- **WO-07 `bimPcPlyRead(dv, at, type)`**, with `BIM_PC_PLYSIZE` above it: one little-endian value of a PLY type:
  `char`/`int8`, `uchar`/`uint8`, `short`/`int16`, `ushort`/`uint16`, `int`/`int32`, `uint`/`uint32`,
  `float`/`float32`, `double`/`float64`.
- **WO-08 `bimPcPlyPoints(bytes, h, max, origin)`**: `{error: 'no x, y, z'}` without those three properties; RGB when
  `red`, `green` and `blue` all exist. ASCII: the lines after the header, one vertex each, values by the properties'
  order. Binary: fixed stride, the sum of the property sizes; `'truncated'` when the data is shorter than
  `count * stride` (ASCII: when a sampled line is missing). Sampling and rebasing as WO-04; `cls` is `null`.
- **WO-09 `bimPcClassName(c)`**, with `BIM_PC_CLASS` above it: ASPRS LAS 1.4 standard classes 0 Never classified,
  1 Unclassified, 2 Ground, 3 Low vegetation, 4 Medium vegetation, 5 High vegetation, 6 Building, 7 Low point
  (noise), 9 Water, 10 Rail, 11 Road surface, 13 Wire guard, 14 Wire conductor, 15 Transmission tower, 17 Bridge
  deck, 18 High noise; any other `'Class ' + c`.
- **WO-10 `bimPcHeightColour(z, zmin, zmax)`**: `t = (z - zmin) / (zmax - zmin)` clamped to 0..1, 0.5 when
  `zmax <= zmin`; `[round(255 * min(1, 2t)), round(255 * min(1, 2(1 - t))), round(255 * (1 - t) * 0.5)]`.
- **WO-11 `bimPcGround(cloud, cell)`**: class 2 points only; per cell `floor(x / cell), floor(y / cell)` (cell 1
  when not a positive number) the lowest `z`; `[[x, y, z], ...]` in the order cells were first met. `[]` when the
  cloud has no classes.

## 5. Order of the work

WO-01 to WO-11 in order (WO-04 and WO-08 use WO-03; WO-08 uses WO-07). Then Claude: **WO-12** import (sniff, read in
a worker when large, the unregistered-preview label, the origin kept with the layer), drawing as GL points in
`render/` with the budget, saved with the project as the file's own bytes or a reference (decided in WO-12 by
size); **WO-13** colour by RGB, class or height in Properties, class visibility, and ground to surface (preview,
confirm, V108 through V138's check); the one browser check; **WO-14** the next slice's research and orders: laz-perf
under the library rule, then COPC and EPT against a named endpoint.

## 6. Not in this phase

LAZ, COPC, EPT and 3DEP streaming; CRS and vertical datum transformations (the owner places an unregistered cloud);
editing points; meshing a cloud; classification.
