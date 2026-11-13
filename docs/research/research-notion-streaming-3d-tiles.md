# Streaming — OGC 3D Tiles in and out

Research date: 2026-11-13. Phase: Later: Streaming, after the LOD track; no V phase number assigned. This report addresses the specific streaming task, not point-cloud reconstruction or H5. Status: standards/source research and a numeric fixture, not independently reviewed and not a complete app implementation audit, browser benchmark or work-order approval.

## 1. Abstract

3D Tiles 1.1 describes a hierarchical geospatial dataset with bounding volumes, geometric-error-driven refinement and glTF-oriented tile content. A city can be visualized incrementally, but importing a tileset is not automatically importing editable BIM objects; both native import and export need explicit support boundaries, provenance and georeferencing. Recommend a staged read-only reference viewer for a defined explicit-tree/glTF subset, evaluated against a conforming viewer, followed by feature metadata and explicit export; implicit tiling, legacy tile formats, textures, compression and access mechanisms are separate tested capabilities. This is a proposed delivery strategy, not a reduction of the original in-and-out scope. Exact support, limits, licensing, renderer strategy and owner choices remain open.

A local binary32 experiment shows why global Earth-centered coordinates need careful treatment: near 6,378,137 m a 0.01 m displacement disappears if each coordinate is independently rounded to float32; the same 0.01 m local offset remains approximately 0.0099999998 m. This is a numeric illustration, not proof of a particular rendering defect. The existing task's 32-hour estimate is unvalidated.

## 2. Hypotheses

| Hypothesis | Finding | Evidence and confidence |
| --- | --- | --- |
| H1: 3D Tiles is a single glTF file with zoom | False. A tileset is a spatial hierarchy with metadata, bounding volumes and streamed content; glTF is a primary content format. | OGC 1.1, P, high. |
| H2: all geographic tilesets use ECEF | False. Global coordinates often use WGS84 ECEF but a local system is permitted. | OGC 6.6, P, high. |
| H3: tiled geometry inherently remains editable BIM | Unsupported. Renderable content/metadata do not guarantee original parametric definitions or a lossless BIM round-trip. | OGC scope and logical comparison, P for format and U for app implementation. |
| H4: ADD and REPLACE can always be drawn the same way | False. ADD retains the parent; REPLACE substitutes children. Loading behavior is client policy and needs tests. | OGC 6.7.1.3, P, high. |
| H5: raw global float32 preserves a centimeter displacement near Earth radius | False for our numeric fixture. | Experiment P for the exact numbers, not for a specific GPU implementation. |
| H6: the current app's existing XYZ map tile cache implements 3D Tiles | Not established. The pipeline describes raster map tiles, not a 3D Tiles hierarchy. | P for the pipeline description, U for exhaustive current-code analysis. |
| H7: a renderer claiming 3D Tiles support meets every requirement | Not established. Compatibility varies by version, extensions and content. | NASA renderer describes exceptions; no version-specific compatibility test. |

## 3. Method and evidence

Read task and current pipeline; primary OGC 3D Tiles 1.1 community standard 22-025r4; OGC adoption summary; CesiumJS and NASA 3DTilesRendererJS project documentation; Khronos presentation on 3D Tiles and large-coordinate precision. Search terms: “OGC 3D Tiles 1.1 specification”, “3D Tiles implicit tiling georeferencing refinement”, “Cesium 3D Tiles 1.1 metadata”. Executed a local Python float32 conversion fixture. No app source-line review of streaming/render code, public dataset downloaded, live CORS probe, browser viewer, phone, WebGL/WebGPU performance test or independent re-reading. P = primary source or direct fixture, U = unverified feasibility. Vendor claims are not an independent verification. Sources were accessed on 2026-11-13.

## 4. Core standard findings

A tileset JSON defines a root tile and top-level geometricError, which determines when its root is considered. A tile's own geometricError determines when its children should be considered; these two errors are not interchangeable. Geometric error is nonnegative in meters; screen-space error is measured in pixels and depends on camera/view/screen and implementation. Do not treat geometricError as a guaranteed survey accuracy or engineering tolerance: it is a selection metric chosen for that tileset. Geometric error may reflect simplification, density or other source-specific criteria.

Each tile has a bounding volume, and content can have its own volume. Box, sphere and geographic region require different tests. A region is [west,south,east,north,minHeight,maxHeight]; longitude and latitude are radians and heights are meters relative to WGS84 ellipsoid, not degrees and not necessarily orthometric elevations. Handle antimeridian and polar cases and dataset-specific vertical datums rather than silently treating ellipsoidal and local heights as interchangeable. Region bounds are specified in EPSG:4979 and are not transformed by the tile transform. For a geographic dataset the global frame is often EPSG:4978 ECEF, but local Cartesian data is valid; do not assume every tileset is georeferenced.

Refinement is inherited where unspecified; root specifies it. ADD renders parent plus children; REPLACE uses children in place of the parent. Keep a visible fallback while required children load as a product policy, but test correctness for holes, partial children and errors: the standard's abstract rule does not prescribe a particular network scheduler. Frustum culling and spatial bounds can avoid unnecessary work, but cameras inside bounds, offscreen shadows and content outside incorrectly authored volumes require robust cases.

Transforms compose from parent to child. First apply glTF node transforms, then the specified glTF y-up to tiles z-up rotation about x of +π/2, then tile and ancestor transforms. Scale affects geometricError by the largest scale factor. Normal transforms use the inverse transpose of the linear transform for nonuniform scale. Geographical region bounding volumes are an exception to transformation. Define explicit column-major conventions and numerical tolerances in tests; order is non-commutative.

Implicit quadtree/octree tiling derives descendants and uses availability information grouped in subtrees; absence of a tile is not equivalent to an empty fetched payload. External tilesets form a hierarchy of trees; the OGC constraints disallow cycles and specify composition of parent and external-root transforms. 1.1 may have multiple contents and metadata. glTF can require extensions such as compression; document exactly which are supported rather than making an unqualified '1.1 support' claim.

## 5. Current app and integration constraints

Pipeline describes a local site origin and true-north orientation, WGS84 ellipsoid placement, raster XYZ basemap with in-flight and cache limits, local site context buildings and a WebGL/WebGPU rendering fallback. These descriptions are useful context but not proof of reusable function signatures, binary precision, 3D tile format support, view picking, export or current browser behavior. Repository engine directory includes `map/`, `render/`, `io/`, `site/`, `terrain/` and `views/`; inspect exact current code and tests before a work order. The existing LOD-C through G tasks concern point clouds, roof/facade reconstruction and splats; a tiled reference can contain derived or external data and must not overwrite user-authored geometry.

Model-to-tile placement requires a documented horizontal/vertical CRS, datum/epoch, origin, north direction, units and a reversible transform chain. If the source CRS is missing, offer an explicit placement flow rather than claiming geographic accuracy. Preserve source URI, tileset version, license/attribution, transform, selection and cache policy as a reference record; do not dump the entire remote city into saved project JSON. Different source snapshots can change beneath a URL: retain immutable version identifiers or warn that reproducibility cannot be guaranteed. Offline reopen should describe whether cached data is incomplete and respect license and expiration conditions.

## 6. Alternatives and tradeoffs

| Option | Benefits | Limitations and decision criteria |
| --- | --- | --- |
| A. Small app-native subset reader | Can integrate existing renderer and offline format; feature scope controlled | Significant implementation and maintenance burden: transforms, content, metadata, cache, request priority, validation and conformance. Must list every unsupported extension. |
| B. NASA 3DTilesRendererJS adapter | Existing renderer, examples and documented dataset adapters; likely useful evaluation candidate | Depends on rendering ecosystems; its README names supported engines and exceptions. License, exact release, bundle size and coexistence with app render paths must be verified; no current integration test. |
| C. CesiumJS view | Mature WGS84 globe and streaming; Apache 2.0 library according to its repository | WebGL-focused separate runtime/view, integration and shared picking/camera costs; Cesium ion is a separate commercial service and not required for every source. |
| D. Offline preprocessing into app assets | Predictable offline use and simpler display | Not live streaming; large output, potential semantic loss, licensing and stale data; cannot substitute for both in and out. |

Recommendation: compare A/B/C on a pinned corpus and existing renderer constraints; start with a read-only reference capability, not an unapproved permanent exclusion of export. Library choice is open, with no measured winning option. Do not copy code before reviewing exact license, notices and compatibility.

## 7. A bounded input and output contract

Input must report tileset version and supported content, explicit/implicit tree, compression, metadata, coordinate assumptions, attribution, limits and recoverable errors. Resolve relative content URLs correctly against each tileset URL, restrict allowed schemes and untrusted inputs, validate lengths and JSON, and limit recursion, cycles, bytes, requests and concurrency. A third-party URL can expose the user's IP and request pattern; ask for an explicit data-source action and show attribution. A server-side proxy, if proposed, adds SSRF, legal and credentials concerns and needs its own review. CORS, access tokens, rate limits and remote terms vary by provider; no dataset or keyless endpoint was tested here.

Export must select project content and CRS intentionally, define output tree strategy and geometric-error derivation, tile bounds, glTF axis conversion, source feature identity and metadata, resource naming, attribution and data rights. Preserve authorized stable IDs as metadata only if the chosen export mapping supports it; 3D Tiles visual content is not an IFC round trip. A minimum valid export should be read by at least one independent viewer and validated against OGC schemas. Geometric error should reflect measured simplification or be conservatively documented; a zero error for non-leaf simplified geometry would falsely indicate no error. Exported file paths and URIs must not include secrets. A partial or failed export must not look complete.

## 8. Experiment and calculations

Python packs IEEE binary32 values at a synthetic ECEF-scale coordinate. At base 6,378,137 m, separately quantized base and base+0.01 m are identical, giving 0.0 m observed delta. At local origin, float32(0.01)-float32(0) = 0.009999999776482582 m. Script and machine-readable result are attached. One arithmetic case, one runtime; no GPU, coordinate transformation library, browser or independent viewer tested. Different encodings, high/low splitting, floating origin, relative-to-center transforms and shader arithmetic can mitigate the problem, but must be compared with actual engine code and measurements. The fixture also records the expected y-up unit vector [0,1,0] rotated about x by +90° to [0,0,1]; that assertion is derived from the standard's matrix, not a renderer test.

## 9. Reproducible acceptance corpus

1. Explicit root plus child with both ADD and REPLACE, slow/missing child, retry and parent fallback: no false holes or double draw beyond the specified policy.
2. Box, sphere, EPSG:4979 region, nested matrices and nonuniform scale; a known point and normal; regions not transformed; inherited refinement.
3. Known y-up glTF axis, glTF node hierarchy and tile hierarchy with noncommuting transforms; check known expected world positions.
4. Synthetic ECEF-scale site with centimeter displacements and local origin; compare projected points with a double-precision independent reference, measure jitter and error by camera distance.
5. Implicit sparse quad/octree availability and subtree boundaries, multiple content, external tree, unsupported required extensions and malicious cycle; explicit rejection for unsupported subsets.
6. Metadata/feature selection and picking across LODs: identity may differ by tile; do not manufacture persistent BIM identity. Identify missing fields and privacy implications.
7. Network: CORS denied, 401/403/404/429/5xx, interrupted requests, expired credentials and quota; bounded retries, cancellation, no silent partial success, no token in logs.
8. Resource safety: huge JSON, malformed GLB, invalid bounds, recursive references, request storms, oversized buffers and cache eviction without use-after-dispose.
9. Export: create controlled tiles with known bounds and transformations, verify JSON and glTF using suitable validators, then load in an independent viewer; compare geometry positions and IDs, explicit losses and attribution.
10. Benchmarks: fixture size and license, hardware/browser/version, cold and warm cache, viewport and camera path, request count/bytes, time to first usable image, frame-time distribution, CPU/GPU memory, failures and cache size. Repeat runs; compare same visual tolerance. No invented limits.

## 10. Risks, edge cases, and policy questions

Render LOD may not match analysis quality; do not use visual meshes for engineering quantities or statutory checks without separate validated accuracy. Dataset vertical datums, terrain/roof offsets, local georeferencing, antimeridian handling, large coordinates and unregistered references can cause plausible-looking but wrong placement. Public streams may have restrictive caching, attribution, commercial-use or API-key terms. Authentication and private tile caches require H5 security analysis. Large-city datasets may overload constrained phones; test actual devices. Paid commercial tiles cannot be assumed publicly accessible or redistributable.

## 11. Open decisions and research exit gates

Owner decisions: source types and first dataset; supported import and export profiles; required metadata and editable conversion, if any; coordinate/datum expectations; renderer integration vs standalone view; online/offline behavior; performance targets and data licensing; export quality and source rights. Do not mark input/out support done because an example glTF displays. Before specs: examine app file-level integration and HLOD, pin libraries and verify licenses, obtain authorized public corpus and dataset terms, test CORS and browser on authorized endpoints, run conformance and measured independent-viewer comparisons, and arrange independent second-reader validation. These gates remain open; no execution code was modified.

## 12. References

- [Streaming task](https://app.notion.com/p/3fecbfcc3a3881e3a2c7f3e240ba7f89) and [current pipeline](https://github.com/BradleyPham1906/BIM-Personal/blob/main/docs/dev/PIPELINE.md).
- [OGC 3D Tiles 1.1, 22-025r4](https://docs.ogc.org/cs/22-025r4/22-025r4.html), sections 6.6–6.7, normative source; [OGC standard overview](https://www.ogc.org/standards/3dtiles).
- [OGC 1.1 adoption summary](https://www.ogc.org/announcement/ogc-adopts-3d-tiles-v1-1-as-community-standard), metadata and implicit-tiling background.
- [NASA 3DTilesRendererJS](https://github.com/NASA-AMMOS/3DTilesRendererJS), vendor/implementation description and stated exceptions; [CesiumJS](https://github.com/CesiumGS/cesium), Apache-2.0 license and renderer description.
- [Khronos, Scaling glTF with 3D Tiles](https://www.khronos.org/assets/uploads/developers/presentations/Scaling_glTF_with_3D_Tiles.pdf), practitioner presentation on precision and scaling.
- Attached Python numerical fixture and raw output, 2026-11-13; not independently reproduced.


---
Research evidence files: [`experiments/notion-streaming/`](experiments/notion-streaming/). Original scripts and results reflect only the experiments described above.
