# V191 spec: LOD-D, LOD1.3 and LOD2.2 roofs from LiDAR

Notion: V189 LOD-D: LOD2.2 from LiDAR. Research: `docs/research/research-notion-v189-roofs.md`, `docs/research/research-lod-reconstruction.md`. The owner's decisions, 2026-11-14: all as the research recommends (the owner, 2026-11-14: "all as recommended"; overrule any here). Implementation target: local `main`. Written by Claude, 2026-11-14.

## 1. The decisions this spec follows

- 3DBAG's published method (its definitions of LOD1.3 and LOD2.2), never roofer's GPL code.
- Footprints from the open data already loaded, their source kept; points from V190's classified clouds (class 6, Building).
- Each building gets roof planes by least squares with their RMS, and the share of its footprint the points cover; under 50% coverage it stays LOD1.2 and says why.
- Processing in the browser, in a worker for large clouds.

## 2. What it does for the user

Select buildings with a cloud under them: roof planes are fitted, the building is rebuilt with them, and Properties shows each plane's RMS and the coverage.

## 3. The pieces

| File | New or changed | What it holds | Built by |
|---|---|---|---|
| `src/js/engine/map/roofs-lidar.js` | new, after `js/engine/map/pointcloud.js` in `src/index.html` (header done) | 5 pure functions (part 5) | Cline, WO-01 to WO-05 |
| `docs/work-orders/v191/v191.test.mjs` | new | their tests | Claude (done) |
| the app's own files | changed | wiring, the interface, saving and undo | Claude, WO-06, WO-07 |

## 5. Functions, `src/js/engine/map/roofs-lidar.js`

ES5. Every function is pure: it never changes what it is given and uses no name from another file.

- **WO-01 `bimRoofJacobi(A)`**: the eigen-decomposition of a symmetric 3x3 by cyclic Jacobi rotations (at most 50; stop when the largest off-diagonal is under 1e-15): {values: the diagonal, vectors: the columns of the accumulated rotation, as three [x, y, z]}; the input unchanged.
- **WO-02 `bimRoofPlane(pts)`**: centroid c, the covariance (divided by n), its eigenvector of the smallest eigenvalue as n, flipped so n[2] >= 0; rms the root mean square of the points' signed distances to the plane. {c, n, rms}; null for fewer than 3 points.
- **WO-03 `bimRoofInRing(pts, ring)`**: the points whose (x, y) is inside the ring (even-odd), in order.
- **WO-04 `bimRoofCoverage(pts, ring, cell)`**: cells of size cell (1 when not positive) from the ring's minimum corner, kept while their centre is before the maximum; those whose centre is in the ring are the footprint's; the share of them holding at least one point (by floor((x - x0)/cell), floor((y - y0)/cell)); 0 for none.
- **WO-05 `bimRoofZ(pl, x, y)`**: c[2] - (n[0](x - c[0]) + n[1](y - c[1])) / n[2]; null when |n[2]| < 1e-12.

## 6. Order of the work

WO-01 to WO-05 in order (a later one may use an earlier one, as its task says). Then Claude: **WO-06** region growing and the rebuilt buildings; **WO-07** the records.

## 7. Not in this phase

Texture; non-planar roofs beyond a flagged fallback; buildings without a footprint.
