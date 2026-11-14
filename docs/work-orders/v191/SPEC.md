# LOD-D: LOD1.3 and LOD2.2 roofs from LiDAR (outline)

Notion: V189 LOD-D: LOD2.2 from LiDAR. PIPELINE: 191. Research: `docs/research/research-notion-v189-roofs.md`, `docs/research/research-lod-reconstruction.md`. Written by Claude, 2026-11-14, as an outline: not yet Cline-ready; the next spec sprint turns its first slice into work orders with tests.

## 0. Status

After V190 (point clouds) is built: this phase reads its classified points. Spec in the sprint after V190's WO-13.

## 1. The owner's decisions, 2026-11-14, as recommended

- LOD definitions as 3DBAG publishes them (LOD1.3 from the roof partition's heights, LOD2.2 as planar roof faces), its method only, never roofer's GPL code;
- footprints from the open data the app already loads (V166/OSM or the city's own), their source kept on each building;
- output is geometry with per-building RMSE to its points and the share of the footprint the points cover; under a minimum coverage (50% by default) the building stays LOD1.2 and says why;
- processing in a worker in the browser; no server.

## 2. What it does for the user

Pick buildings with a classified cloud under them: each gets planar roof faces fitted to its points, extruded to its footprint, with its RMSE and coverage in Properties.

## 3. The first slice (pure functions in `src/js/engine/map/roofs-lidar.js`, ES5, no other file's names)

- `bimRoofPlane(points)`: the least-squares plane through [x,y,z] points (centroid and the smallest eigenvector of the covariance, by Jacobi rotations), with its RMS distance.
- `bimRoofInFootprint(points, ring)`: the points whose x,y fall inside the footprint ring.
- `bimRoofGrow(points, normals, seed, angleDeg, dist)`: region growing: neighbours (by a grid) whose normals are within the angle and distance join the region.
- `bimRoofRmse(points, planes, labels)`: the RMS of each point's distance to its own plane.
- `bimRoofLod13(regions, ring)`: LOD1.3: the partition's heights as flat roof blocks.
- `bimRoofCoverage(points, ring, cell)`: the share of the footprint's grid cells holding at least one point.

Tests: Synthetic gabled and hipped roofs sampled with known noise: planes recovered within 1e-6 with no noise, RMSE equal to the added noise within 5%.

## 4. Not in this phase

Texture; lod3; buildings without a footprint; non-planar roofs (domes) beyond a flagged fallback.
