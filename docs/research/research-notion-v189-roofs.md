## V189 — Roof and building reconstruction from point clouds

**Decision status:** Research synthesis, not an approved specification. **Evidence date:** 2026-11-13. The task proposes LoD1.3/LoD2.2 building reconstruction from footprints and point clouds with planar roof segmentation and per-building error. Do not confuse a visual fit, complete watertight solid, CityJSON/CityGML conformance and survey-grade as-built geometry: these are separate claims requiring separate tests. Current code interfaces, dataset coverage and the task's 32-hour allowance remain unverified.

### Research question

How should the platform transform a trustworthy building footprint and suitable point cloud into a reviewable mass and roof, and when should it abstain? The minimum inputs are a footprint in a known projected CRS, point cloud with a validated corresponding CRS/vertical datum, metadata about acquisition and units, and a configurable processing extent. The roof overhang may make a measured roof outline differ from the ground footprint. Ground classification, vegetation, neighboring buildings, gaps and building age can all bias a fit. A facade or interior cannot be inferred from a roof alone.

### Evidence and reuse boundaries

[3DBAG roofer](https://github.com/3DBAG/roofer) is a GPL-3.0 reference implementation that reconstructs LoD 1.2, 1.3 and 2.2 from footprints/point clouds and emits CityJSONSeq. Its [architecture](https://github.com/3DBAG/roofer/blob/main/ARCHITECTURE.md) describes cropping, reconstruction, sorting and serialization, expects projected metric coordinates and treats each input footprint as either an output or an explicit failure. The architecture also notes limitations with low-density or occluded point clouds. Use it to learn pipeline concepts and to compare results on a suitable licensed fixture; do not copy or ship GPL code without the project's legal/owner review. Its formats and labels do not prove this app's current data model is conformant or that an identical outcome can be reproduced.

A footprint is an input constraint, not evidence that the roof projects exactly to its outline. A robust implementation must track the footprint source/date, cloud source/date, correspondence, coordinate operations, selection parameters, reconstruction version, fitted planes, residuals, failure reasons and user edits. Store measured evidence separately from inferred geometry and from the final accepted object.

### Options

| Method | Strength | Failure / boundary |
| --- | --- | --- |
| Flat extruded footprint | Transparent baseline and deterministic fallback | No roof facets; height-sensitive and not LoD2 merely because it is 3D |
| Region-growing planes + roof partition | Interpretable plane equations and per-segment residuals | Sparse returns, trees, dormers, adjacent roofs and choice of tolerances can cause under/over-segmentation |
| External reconstruction engine | Leverage mature research and independent comparison | License, deployment, reproducibility and browser/server requirements need review; no implicit dependency approval |
| Manual reconstruction | Highest explicit control for difficult buildings | Slow and depends on user judgment; should remain available when automated fitting abstains |

**Proposed approach:** Start with a deterministic extruded-footprint baseline and an explainable plane-based roof candidate. Preserve the baseline when a valid plane solution is unavailable, but mark it as fallback rather than silently labeling it a detailed roof. Use an implementation that satisfies the actual project's license and dependency rules.

### Proposed reconstruction pipeline

1. Validate polygon topology, units, CRS and vertical datum. Detect multipart footprints, holes, self-intersections and missing transforms. Do not assume a building with no overlapping points has zero height.
2. Crop with a documented footprint/roofprint buffer and record which points were used. Separate or down-weight known non-building classes where data supports it; classification is not ground truth. Do not let points from another roof or a tree silently drive the fit.
3. Estimate ground/reference elevation with explicit source and confidence. Select roof candidates with a documented strategy and minimum sample count/coverage. Fit candidate planes, reject outliers with a reproducible robust estimator, and report inliers, residual distribution, density, spatial coverage and uncertainty. A high global inlier count concentrated in one small patch is not sufficient.
4. Partition the roof, constrain shared edges and derive valid roof polygons. Check intersections, adjacency, slopes and numerical tolerances; resolve degeneracies explicitly rather than closing a broken mesh invisibly. Trim or parameterize roof overhangs separately from the wall footprint.
5. Generate an inspectable mass with labeled geometry provenance. Validate manifoldness, winding, intersections, closedness and units, and separately validate any intended interchange schema. An output must be either a candidate with diagnostics or a clear per-building failure; do not lose failed inputs.
6. Present the flat baseline and fitted candidate plus evidence overlay. Editing and acceptance are human actions. Preserve original footprint/point cloud; rebuild must be deterministic for identical inputs, settings and implementation version.

### Error metrics and limitations

Distinguish fit residual to points used in fitting from predictive accuracy on spatially held-out data. Report count, coverage, vertical residual distribution (including robust median and 95th percentile), RMSE where appropriate, and planar tilt or boundary error if a trusted reference exists. Avoid judging only against data the model fit. A numerical metric cannot certify that the building is current, semantically correct, watertight, or compliant with a particular LOD standard. A threshold must be selected for the intended data resolution and use; none is authorized here.

### Falsification: synthetic outlier stress test

One reproducible Python experiment generated 100 noisy points on `z = 0.2x - 0.1y + 5` and ten points 3 m above the plane. A least-squares fit evaluated on 1,000 synthetic reference positions yielded **0.30169 m RMSE** with the outliers and **0.00125 m** using only clean points. The latter is an oracle that knew the outlier labels in advance; it is not an implemented robust estimator, app result or expected field accuracy. It supports the narrow claim that unfiltered outliers can bias ordinary fitting in this setup. Test real robust estimators on unseen mixed roof, vegetation, sparse and gable cases before selecting one. The exact inputs, seed, environment and result accompany this record.

### Proposed acceptance matrix — not yet executed

- Independently compare input point coordinates and footprint transform against a trusted tool; fail clearly when CRS/datum is missing or mismatched.
- Flat, gabled, hipped, multi-facet, dormer and flat-adjacent-roof fixtures: report per-building input, candidate, failures and comparison with a named reference.
- Sparse, tree-obscured, footprint-offset, no-point and outlier fixtures: abstain or mark low confidence; no fabricated facades or silently accepted roof.
- Test self-intersecting/multipart polygons, holes, degenerate planes, footprint edges and roof overhangs; test watertightness and self-intersections independently of visual render.
- Fit determinism on repeated identical inputs; verify source lineage, parameter capture, edit history and undo.
- Establish a spatial held-out evaluation protocol and record an appropriate owner-approved threshold. Use authoritative fixture data, not the synthetic oracle, for acceptance.
- Measure time/memory by point count, building count and device; check that progress, cancellation and partial per-building failures work.
- Confirm the actual export/model-space contract and import into an independent viewer only when the export is in scope.

### Decisions and remaining gates

Owner choices: target LOD definitions, dataset and footprint provenance, geometry versus surface-only output, expected tolerance/use, minimum coverage, fallback semantics, processing location, and licensed reference-engine usage. Independent research review, actual app integration analysis, license assessment, real-dataset tests, expert verification and performance evaluation have not been completed. Do not convert the proposed 32 hours into a committed work order from this report alone.


---
Research evidence files: [`experiments/notion-lod/`](experiments/notion-lod/). Original scripts and results reflect only the experiments described above.
