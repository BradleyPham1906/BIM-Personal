## V190 — Facade imagery, rectification and provenance

**Decision status:** Research synthesis; no owner approval or production validation. **Evidence date:** 2026-11-13. Scope: use user-supplied facade images or appropriately authorized panoramas to produce an inspectable planar facade image linked to a LoD2 wall. Current app interfaces and a live provider were not tested; the task's 16-hour allowance is not a validated estimate.

### Research question and model

A wall is a finite plane in the project coordinate system. A useful facade image must associate image pixels with that plane, not simply stretch a photograph onto an arbitrary rectangle. The project needs the source image's identity, rights, date, orientation/calibration where known, wall plane and metric extent, control-point correspondences, rectification transform, residuals, crop/occlusion mask, and user approval. Keep the original image and the generated image independently traceable. An image can be visually persuasive yet geometrically wrong because of perspective, lens distortion, wrong control points, non-planar projections, vegetation, or changed building conditions.

[OpenCV's homography explanation](https://docs.opencv.org/4.11.0/d9/dab/tutorial_homography.html) describes a 3×3 projective transform defined up to scale and its use on planar views. At least four appropriate non-collinear correspondences are required to solve a planar homography; in practice, use additional well-distributed controls and independently held-out checks. Four coplanar corner controls do not correct non-planar facade features, wrong CRS or unmodeled distortion. When a known calibration exists, undistortion and camera projection must be consistent with it; do not invent camera parameters.

[Texture2LoD3](https://wenzhaotang.github.io/Texture2LoD3/) describes matching georeferenced panoramas to low-LOD models and facade processing, including rectification and segmentation. Its reported benchmark improvement belongs to its datasets and pipeline; it is not evidence of this application's expected accuracy or provider coverage. Equirectangular panorama pixels encode spherical viewing directions: obtain rays using the panorama projection and pose, then map onto a known wall plane or produce a defined perspective view before applying a planar transform. Treating an entire panorama as an ordinary planar photo can introduce systematic errors.

### Acquisition and rights

Three paths must be distinguished: user-uploaded photographs; panoramas from a separately verified source; and a provisional image placeholder. For any provider such as Panoramax, inspect the exact photo's metadata, author, acquisition date, allowed use and license, service terms, API limitations, CORS and attribution requirements before use or redistribution. Do not assume one blanket license applies to every image or that imagery may be downloaded, stored or republished solely because it is visible online. Record this evidence; if rights or availability cannot be verified, use an owner-provided legal fixture and block automatic ingestion.

### Alternatives and recommendation

| Path | Strength | Risk |
| --- | --- | --- |
| Manual four-or-more control points on one owner-provided facade photo | Transparent and testable without a provider | Manual effort; susceptible to poor controls and lens distortion |
| Panorama pose and wall ray intersection | Reuses existing street imagery where permitted | Requires correct camera location/orientation/projection; occlusion and rights vary per image |
| Uncalibrated texture stretch | Cheap visual placeholder | Not metric, no defensible opening measurement; label accordingly |
| Fully automatic facade matching | Scalable when validated | Requires robust pose/matching, real diverse imagery and significant error analysis not yet demonstrated |

**Proposed first slice:** a local, rights-cleared image and manual control workflow with a metric wall plane and held-out checks. The user may explicitly accept a visual-only texture with an accuracy warning; it must not be presented as measurement-grade or automatically drive geometry. Preserve the option for provider adapters without claiming they work.

### Proposed data and operation contract

- Input: immutable image identifier/checksum, image dimensions and source metadata; wall identifier, plane origin and two orthogonal metric axes; control points mapping image positions to wall coordinates; optional validated camera calibration.
- Validate non-collinearity, spatial distribution and numerical conditioning; warn for controls clustered in one area and reject a singular transform. Compute a candidate using documented projection/rectification order; sample with defined interpolation and clip to a user-defined facade region.
- Capture fit error and independent check-point error in meters and pixels; display maximum and distribution with units and the spatial locations of controls. Never imply that a four-control exact fit measures real-world accuracy. Explain whether values use withheld data.
- Include a visibility/occlusion mask and flag near-parallel camera rays or points behind the camera. No implied recovery of geometry behind trees, cars or neighboring structures.
- Output: the image/texture and transform, local wall coordinates, wall association, quality report, rights/attribution, timestamp, validation status, and link to the original. Preserve edits and provenance; avoid destructive overwriting of source or wall geometry.
- If wall geometry or registration changes, mark dependent images stale and require review. Store the reprojection method and version to permit reproducibility; do not assume a changed building has the same facade as an older photograph.

### Experiment: withheld points and calibration perturbation

The attached reproducible script created a synthetic planar 10 m × 6 m wall, applied a known homography, fitted using four corners, and evaluated nine withheld positions. Perfect synthetic controls produced a maximum error of approximately **2.38 × 10⁻⁷ m**. Perturbing one image control by (+3, −3) pixels produced **0.01137 m mean** and **0.02871 m maximum** withheld error. This demonstrates sensitivity in one noise-free artificial setup; it is not a real-camera accuracy guarantee or an accepted threshold. It omits lens distortion, photographic uncertainty, image occlusion, CRS, panorama projection and changes over time.

### Verification matrix — proposed, not performed

1. Synthetic known homographies, grid coordinates and held-out locations: compare error and inverse mapping; test degenerate, coincident and clustered controls.
2. Wall plane with rotated axes, nonzero origin, units conversion and multiple model-space coordinates: independently verify image-to-wall and wall-to-image directions.
3. A rights-cleared calibration image with measured facade controls and independently measured checkpoints: report residuals and limitations; compare against an independent implementation.
4. Curved/nonplanar facade, deep window recess, image distortion, vehicle/vegetation occlusion and slanted camera: visually and numerically disclose failure rather than silently invent geometry.
5. For a proposed panorama adapter, test pose, spherical rays, behind-camera and near-parallel cases; verify actual API, image-specific licensing, attribution and CORS on the chosen provider.
6. Source and generated image persist/reload, wall edits invalidate dependencies, undo restores prior state, and unsupported or missing rights cannot become silently approved.
7. Define and measure a use-specific owner-approved uncertainty threshold before V191 is allowed to derive actionable dimensions; visually accepted textures alone are insufficient.

### Open decisions

Initial image source, allowed rights/storage, whether visual-only textures are allowed, required metric tolerance, supported projections and calibration formats, whether a provider is in scope, and privacy/retention rules. Independent reviewer, actual code contract audit, real calibration, live provider validation, accessibility and app-level integration tests remain open. This document informs a specification but does not close those gates.


---
Research evidence files: [`experiments/notion-lod/`](experiments/notion-lod/). Original scripts and results reflect only the experiments described above.
